import tkinter as tk
from tkinter import ttk


class StudyTrackApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("StudyTrack")
        self.geometry("900x550")
        self.minsize(700, 400)

        self.create_widgets()

    def create_widgets(self):
        container = ttk.Frame(self, padding=24)
        container.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(
            container,
            text="StudyTrack",
            font=("Segoe UI", 22, "bold"),
        )
        title.pack(anchor=tk.W)

        subtitle = ttk.Label(
            container,
            text="Организирай учебните си задачи и крайни срокове.",
            font=("Segoe UI", 11),
        )
        subtitle.pack(anchor=tk.W, pady=(8, 24))

        message = ttk.Label(
            container,
            text="Приложението е подготвено за добавяне на функционалности.",
        )
        message.pack(anchor=tk.W)