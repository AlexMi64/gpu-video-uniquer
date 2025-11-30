import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys

def run_uniquifier(directory):
    """
    Запускает уникализатор на выбранной директории.
    """
    if not os.path.exists(directory):
        messagebox.showerror("Ошибка", "Директория не существует!")
        return

    # Импорт и запуск
    try:
        from video_uniquifier import main
        main(directory, recursive=True)
        messagebox.showinfo("Готово", f"Обработка завершена в {directory}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка обработки: {str(e)}")

def select_directory():
    """
    Выбор директории через диалог.
    """
    directory = filedialog.askdirectory(title="Выберите папку с видео")
    if directory:
        run_uniquifier(directory)

# GUI
root = tk.Tk()
root.title("Уникализатор видео")
root.geometry("300x150")

label = tk.Label(root, text="Выберите папку с видео для обработки:")
label.pack(pady=20)

button = tk.Button(root, text="Выбрать папку и запустить", command=select_directory)
button.pack(pady=10)

root.mainloop()
