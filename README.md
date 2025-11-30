# Уникализатор видео

Этот скрипт обрабатывает видео, применяя различные трансформации для создания уникальных копий. Полезен для Telegram ботов, чтобы избегать дублирования контента на платформе.

## Оптимизации производительности

Скрипт оптимизирован для высокой скорости:
- **Многопроцессорная обработка**: Использует все ядра CPU (до 16 потоков).
- **Батчевая обработка**: Обрабатывает кадры пачками для экономии памяти.
- **JIT-компиляция**: Numba для ускорения numpy операций.
- **Кэширование**: Водяной знак генерируется один раз.
- **GPU-поддержка**: Автоматическое использование CUDA (NVIDIA GPU) для cvtColor, resize, warpAffine.

### Требования для GPU
- NVIDIA GPU (RTX 3080 Ti или выше для 1800+ FPS).
- CUDA Toolkit 11+.
- OpenCV с CUDA: `pip install opencv-contrib-python`.

### Оценка производительности
- **CPU Xeon E5-2680 v4 (14 ядер)**: ~50-60 мин на 30 мин видео (20-30 FPS).
- **С RTX 3080 Ti**: ~20-30 сек на 30 мин видео (1500-2500 FPS).
- **На Mac M3 Pro**: ~40 мин на 30 мин видео (22 FPS).

## Возможности
- Сдвиг цветокоррекции (оттенок и насыщенность)
- Добавление малозаметных точек
- Водяной знак с настраиваемой позицией
- Пространственное смещение видео
- Поворот на маленький угол
- Видео-помехи и шум на кадрах
- Прогресс-бар обработки

## Установка

### Для Windows (Python 3.11+)
1. Установите Python с [python.org](https://www.python.org/downloads/) (обязательно отметьте "Add Python to PATH").
2. Откройте командную строку и выполните:
   ```
   pip install opencv-python-headless numpy tqdm
   ```
3. Скачайте файлы `video_uniquifier.py`, `config.py`, `gui.py` в папку.

**Если Python не в PATH:** В `build_exe.bat` замените `python` на полный путь, например `C:\Python311\python.exe`.

#### Запуск в 2 клика (рекомендуется)
1. **Самый простой способ: GitHub Actions**
   - Загрузите файлы в GitHub репозиторий с `.github/workflows/build.yml`.
   - GitHub автоматически соберет exe и предоставит скачать в Actions → Artifacts.
   - Скачайте `VideoUniquifier.exe` и используйте.

2. **Локальная сборка:**
   - Запустите `build_exe.bat` для сборки исполняемого файла (установит PyInstaller автоматически).
   - Двойной клик по `dist\VideoUniquifier.exe` откроет GUI для выбора папки.
   - Или используйте `run_uniquifier.bat` для обработки в текущей папке (требует Python и зависимости).

**Дополнительные установки:**
- Для exe: Ничего, exe включает все зависимости.
- Для Python-версии: Установите зависимости из раздела установки.
- Для GPU: CUDA Toolkit и OpenCV с CUDA (опционально).

### Для macOS
1. Установите Homebrew: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
2. Установите Python: `brew install python@3.11`
3. Установите зависимости:
   ```
   pip3 install opencv-python-headless numpy tqdm
   ```
4. Скачайте файлы `video_uniquifier.py` и `config.py`.

## Использование

1. Отредактируйте `config.py` для настройки параметров.
2. Поместите видео (.mp4, .avi, .mov, .mkv) в указанную папку.
3. Запустите: `python video_uniquifier.py` (на Mac: `python3 video_uniquifier.py`)
4. Скрипт обработает все видео, заменив оригиналы на уникальные.

## Настройки

Файл `config.py` содержит все параметры. Примеры значений:

- **hue_shift**: Сдвиг оттенка (-180 до 180).
- **saturation_shift**: Изменение насыщенности (-1.0 до 1.0).
- **watermark_text**: Текст знака.
- **watermark_hpos**: left/center/right
- **watermark_vpos**: top/middle/bottom
- **shift_offset_x/y**: Пиксели смещения при обрезке.
- **dots_density**: Плотность точек (0.00001 очень мало).
- **rotation_degrees**: Угол поворота.
- **glitch_density**: Вероятность помех (0.0-1.0).
- **noise_frequency**: Каждый N-й кадр с шумом.
- **process_directory**: Папка для видео (. - текущая).
- **recursive**: Обработка подпапок (False/True).

## Интеграция с Telegram ботом

### Пример для Python бота
```python
import subprocess
import os

def process_video_for_bot(video_path):
    # Сохранить оригинал если нужно
    # Запустить обработку
    result = subprocess.call(['python3', 'video_uniquifier.py'], cwd='/path/to/script')
    if result == 0:
        # Файл обработан, теперь можно отправлять
        await bot.send_video(chat_id, open(video_path, 'rb'))
    else:
        # Ошибка
        await bot.send_message(chat_id, "Ошибка обработки видео")

# В обработчике сообщения с видео
@bot.message_handler(content_types=['video'])
def handle_video(message):
    video_file = bot.get_file(message.video.file_id)
    downloaded_file = bot.download_file(video_file.file_path)
    video_path = f'/tmp/{message.video.file_id}.mp4'
    with open(video_path, 'wb') as f:
        f.write(downloaded_file)
    # Обработать
    process_video_for_bot(video_path)
    # Удалить временный файл
    os.remove(video_path)
```

### Интеграция асинхронно
Используйте `asyncio.create_subprocess_exec` для асинхронной обработки.

### Настройки для бота
Установите низкие плотности для быстроты, высокой плотности для уникальности при реулинге.

Для многопоточной обработки добавьте `async def process_video` с очередью.
