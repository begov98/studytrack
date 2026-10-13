import tkinter as tk
from datetime import date
from tkinter import ttk

from studytrack.database import get_all_tasks


class StudyTrackApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("StudyTrack")
        self.geometry("900x550")
        self.minsize(700, 400)

        self.create_widgets()
        self.refresh_tasks()

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
        subtitle.pack(anchor=tk.W, pady=(8, 16))

        toolbar = ttk.Frame(container)
        toolbar.pack(fill=tk.X, pady=(0, 12))

        refresh_button = ttk.Button(
            toolbar,
            text="Обнови",
            command=self.refresh_tasks,
        )
        refresh_button.pack(side=tk.LEFT)

        table_frame = ttk.Frame(container)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("title", "subject", "due_date", "status")

        self.task_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        self.task_table.heading("title", text="Заглавие")
        self.task_table.heading("subject", text="Предмет")
        self.task_table.heading("due_date", text="Краен срок")
        self.task_table.heading("status", text="Статус")

        self.task_table.column("title", width=300, minwidth=150)
        self.task_table.column("subject", width=200, minwidth=100)
        self.task_table.column("due_date", width=120, minwidth=100)
        self.task_table.column("status", width=130, minwidth=100)

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.task_table.yview,
        )
        self.task_table.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.summary_label = ttk.Label(container, text="")
        self.summary_label.pack(anchor=tk.W, pady=(12, 0))

    def refresh_tasks(self):
        tasks = get_all_tasks()

        for item in self.task_table.get_children():
            self.task_table.delete(item)

        for task in tasks:
            formatted_date = date.fromisoformat(
                task["due_date"]
            ).strftime("%d.%m.%Y")

            status = (
                "Завършена" if task["is_completed"] else "Незавършена"
            )

            self.task_table.insert(
                "",
                tk.END,
                iid=str(task["id"]),
                values=(
                    task["title"],
                    task["subject"],
                    formatted_date,
                    status,
                ),
            )

        if tasks:
            self.summary_label.config(text=f"Общо задачи: {len(tasks)}")
        else:
            self.summary_label.config(text="Няма добавени задачи")