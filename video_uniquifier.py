import os
import random
import cv2
import numpy as np
from tqdm import tqdm
from config import config
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
try:
    from numba import jit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# Кэш для водяного знака
watermark_cache = {}

def get_watermark_overlay(width, height):
    """
    Создает и кэширует изображение водяного знака.
    """
    key = (width, height, config['watermark_text'], config['fontsize'], tuple(config['watermark_color']), config['watermark_hpos'], config['watermark_vpos'])
    if key in watermark_cache:
        return watermark_cache[key]

    overlay = np.zeros((height, width, 3), dtype=np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = config['fontsize'] / 30.0
    thickness = 1
    text = config['watermark_text']
    color = tuple(config['watermark_color'][:3])
    text_size, baseline = cv2.getTextSize(text, font, font_scale, thickness)

    if config['watermark_hpos'] == 'left':
        x = 10
    elif config['watermark_hpos'] == 'center':
        x = (width - text_size[0]) // 2
    elif config['watermark_hpos'] == 'right':
        x = width - text_size[0] - 10
    else:
        x = width - text_size[0] - 10

    if config['watermark_vpos'] == 'top':
        y = baseline + 10
    elif config['watermark_vpos'] == 'middle':
        y = (height + text_size[1]) // 2
    elif config['watermark_vpos'] == 'bottom':
        y = height - 10
    else:
        y = height - 10

    cv2.putText(overlay, text, (x, y), font, font_scale, color, thickness)
    watermark_cache[key] = overlay
    return overlay

@jit(nopython=True)
def apply_hsv_shift(hsv, hue_shift, sat_shift):
    """
    JIT функция для сдвига HSV.
    """
    hsv[:, :, 0] = (hsv[:, :, 0] + hue_shift) % 180
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + sat_shift), 0, 255)
    return hsv

def apply_color_correction(frame):
    """
    Применяет небольшой сдвиг цветокоррекции (hue и saturation).
    """
    if cv2.cuda.getCudaEnabledDeviceCount() > 0:
        # GPU версия
        gpu_frame = cv2.cuda_GpuMat()
        gpu_frame.upload(frame)
        gpu_hsv = cv2.cuda.cvtColor(gpu_frame, cv2.COLOR_BGR2HSV)
        # Для HSV сдвига нужно скачать и обработать на CPU, так как cv2.cuda не имеет прямой поддержки
        hsv = gpu_hsv.download()
        hsv = apply_hsv_shift(hsv, config['hue_shift'], config['saturation_shift'])
        gpu_result = cv2.cuda_GpuMat()
        gpu_result.upload(hsv)
        result = cv2.cuda.cvtColor(gpu_result, cv2.COLOR_HSV2BGR)
        return result.download()
    else:
        # CPU версия
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv = apply_hsv_shift(hsv, config['hue_shift'], config['saturation_shift'])
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

@jit(nopython=True)
def apply_dots_numba(frame, positions, colors):
    """
    JIT функция для добавления точек.
    """
    for i in range(len(positions)):
        y, x = positions[i]
        frame[y, x] = colors[i]
    return frame

def add_subtle_dots(frame):
    """
    Добавляет малозаметные точки на кадры видео.
    """
    height, width = frame.shape[:2]
    num_dots = int(width * height * config['dots_density'])
    if num_dots == 0:
        return frame
    # Генерировать позиции и цвета
    positions = np.random.randint(0, [height, width], (num_dots, 2))
    colors = np.random.randint(config['dots_color_min'], config['dots_color_max'] + 1, (num_dots, 3), dtype=np.uint8)
    frame = apply_dots_numba(frame, positions, colors)
    return frame

def add_watermark(frame):
    """
    Добавляет водяной знак из кэша.
    """
    height, width = frame.shape[:2]
    overlay = get_watermark_overlay(width, height)
    # Наложить overlay
    mask = overlay > 0
    frame[mask] = overlay[mask]
    return frame

def apply_combined_transform(frame):
    """
    Комбинирует сдвиг (translation) и поворот в одну affine transform.
    """
    height, width = frame.shape[:2]
    center = (width / 2, height / 2)

    # Матрица сдвига (translation)
    shift_matrix = np.array([[1, 0, -config['shift_offset_x']],
                             [0, 1, -config['shift_offset_y']],
                             [0, 0, 1]], dtype=np.float32)

    # Матрица поворота
    rotation_matrix = cv2.getRotationMatrix2D(center, config['rotation_degrees'], 1.0)
    rotation_matrix = np.vstack([rotation_matrix, [0, 0, 1]])  # Сделать 3x3

    # Комбинированная матрица: rotation @ shift
    combined_matrix = rotation_matrix @ shift_matrix
    combined_matrix = combined_matrix[:2]  # Вернуть к 2x3 для OpenCV

    if cv2.cuda.getCudaEnabledDeviceCount() > 0:
        gpu_frame = cv2.cuda_GpuMat()
        gpu_frame.upload(frame)
        gpu_transformed = cv2.cuda.warpAffine(gpu_frame, combined_matrix, (width, height))
        return gpu_transformed.download()
    else:
        transformed = cv2.warpAffine(frame, combined_matrix, (width, height))
        return transformed

# Старая функция shift_video_space заменена на combined
def shift_video_space(frame):
    # Теперь интегрировано в combined
    return frame

def apply_rotation(frame):
    # Теперь интегрировано в combined
    return frame

def add_video_glitches(frame):
    """
    Добавляет небольшие видео-помехи на случайных кадрах.
    """
    if random.random() < config['glitch_density']:
        height, width = frame.shape[:2]
        x1 = random.randint(0, width//4)
        y1 = random.randint(0, height//4)
        size = random.randint(10, 50)
        x2 = min(x1 + size, width)
        y2 = min(y1 + size, height)
        frame[y1:y2, x1:x2] = np.bitwise_not(frame[y1:y2, x1:x2])
    return frame

def process_frame(frame, frame_count):
    """
    Обрабатывает один кадр: применяет все трансформации.
    """
    # Для аудио шума, добавлять иногда, но так как нет аудио, пропустить
    if frame_count % config['noise_frequency'] == 0:  # Добавлять шум каждый n-й кадр
        # Добавлять маленький шум на кадр как "эквивалент аудио" но это видео
        frame += np.random.normal(0, 2, frame.shape).astype(np.uint8)

    # Применить трансформации
    frame = apply_color_correction(frame)
    frame = add_subtle_dots(frame)
    frame = add_watermark(frame)
    frame = apply_combined_transform(frame)
    frame = add_video_glitches(frame)
    return frame

def process_video(input_path, output_path, batch_size=200):
    """
    Обрабатывает одно видео: применяет все трансформации и сохраняет.
    """
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    num_workers = min(mp.cpu_count(), 16)

    frame_count = 0
    with tqdm(total=total_frames, desc="Processing video") as pbar:
        while frame_count < total_frames:
            # Читать батч кадров
            batch_frames = []
            for _ in range(batch_size):
                if frame_count >= total_frames:
                    break
                ret, frame = cap.read()
                if not ret:
                    break
                batch_frames.append((frame, frame_count))
                frame_count += 1

            if not batch_frames:
                break

            # Обработать батч параллельно
            with ProcessPoolExecutor(max_workers=num_workers) as executor:
                futures = {executor.submit(process_frame, frame, count): count for frame, count in batch_frames}
                processed = {}
                for future in as_completed(futures):
                    processed[futures[future]] = future.result()

                # Записать в порядке
                for count in sorted(processed.keys()):
                    out.write(processed[count])
                    pbar.update(1)

    cap.release()
    out.release()
    print(f"Video processed: {output_path}")

def main(directory='.', recursive=False):
    """
    Основная функция: сканирует директорию, обрабатывает видео.
    """
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv')

    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.lower().endswith(video_extensions):
                input_path = os.path.join(root, filename)
                temp_output_path = input_path + '_temp.mp4'
                process_video(input_path, temp_output_path)
                os.rename(temp_output_path, input_path)
                print(f"Обработано: {filename}")
        if not recursive:
            break

if __name__ == "__main__":
    main(config['process_directory'], config['recursive'])
