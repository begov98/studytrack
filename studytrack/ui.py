import tkinter as tk
import sqlite3
from datetime import date
from tkinter import messagebox, ttk
from studytrack.database import get_all_tasks

from studytrack.services import (
    change_task_status,
    create_task,
    edit_task,
    filter_tasks,
    is_task_overdue,
    remove_task,
    sort_tasks_by_deadline,
)

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

        add_button = ttk.Button(
            toolbar,
            text="Добави задача",
            command=self.open_add_task_dialog,
        )
        add_button.pack(side=tk.LEFT, padx=(8, 0))

        edit_button = ttk.Button(
            toolbar,
            text="Редактирай",
            command=self.open_edit_task_dialog,
        )
        edit_button.pack(side=tk.LEFT, padx=(8, 0))

        delete_button = ttk.Button(
            toolbar,
            text="Изтрий",
            command=self.delete_selected_task,
        )
        delete_button.pack(side=tk.LEFT, padx=(8, 0))

        status_button = ttk.Button(
            toolbar,
            text="Промени статус",
            command=self.change_selected_task_status,
        )
        status_button.pack(side=tk.LEFT, padx=(8, 0))

        filters_frame = ttk.Frame(container)
        filters_frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(
            filters_frame,
            text="Предмет:",
        ).pack(side=tk.LEFT)

        self.subject_options = []

        self.subject_filter = ttk.Combobox(
            filters_frame,
            state="readonly",
            values=["Всички предмети"],
            width=25,
        )
        self.subject_filter.current(0)
        self.subject_filter.pack(side=tk.LEFT, padx=(6, 16))
        self.subject_filter.bind(
            "<<ComboboxSelected>>",
            lambda event: self.refresh_tasks(),
        )

        ttk.Label(
            filters_frame,
            text="Статус:",
        ).pack(side=tk.LEFT)

        self.status_filter = ttk.Combobox(
            filters_frame,
            state="readonly",
            values=["Всички", "Завършени", "Незавършени"],
            width=18,
        )
        self.status_filter.current(0)
        self.status_filter.pack(side=tk.LEFT, padx=(6, 0))
        self.status_filter.bind(
            "<<ComboboxSelected>>",
            lambda event: self.refresh_tasks(),
        )

        sorting_frame = ttk.Frame(container)
        sorting_frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(
            sorting_frame,
            text="Подреждане по срок:",
        ).pack(side=tk.LEFT)

        self.sort_order = ttk.Combobox(
            sorting_frame,
            state="readonly",
            values=[
                "Най-ранен първо",
                "Най-късен първо",
            ],
            width=22,
        )
        self.sort_order.current(0)
        self.sort_order.pack(side=tk.LEFT, padx=(6, 0))
        self.sort_order.bind(
            "<<ComboboxSelected>>",
            lambda event: self.refresh_tasks(),
        )


        table_frame = ttk.Frame(container)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("title", "subject", "due_date", "status", "overdue")

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

        self.task_table.heading("overdue", text="Просрочване")
        self.task_table.column("overdue", width=120, minwidth=100)

        self.task_table.tag_configure(
            "overdue",
            foreground="#a00000",
        )

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
        all_tasks = get_all_tasks()

        selected_index = self.subject_filter.current()
        selected_subject = None

        if 0 < selected_index <= len(self.subject_options):
            selected_subject = self.subject_options[selected_index - 1]

        self.subject_options = sorted(
            {task["subject"] for task in all_tasks},
            key=str.casefold,
        )

        self.subject_filter.configure(
            values=["Всички предмети"] + self.subject_options
        )

        if selected_subject in self.subject_options:
            self.subject_filter.current(
                self.subject_options.index(selected_subject) + 1
            )
        else:
            self.subject_filter.current(0)
            selected_subject = None

        status_index = self.status_filter.current()
        selected_status = {
            0: None,
            1: True,
            2: False,
        }.get(status_index)

        tasks = filter_tasks(
            all_tasks,
            subject=selected_subject,
            is_completed=selected_status,
        )

        tasks = sort_tasks_by_deadline(
            tasks,
            descending=self.sort_order.current() == 1,
        )

        for item in self.task_table.get_children():
            self.task_table.delete(item)

        today = date.today()

        for task in tasks:
            formatted_date = date.fromisoformat(
                task["due_date"]
            ).strftime("%d.%m.%Y")

            status = (
                "Завършена" if task["is_completed"] else "Незавършена"
            )
            overdue = is_task_overdue(task, today=today)

            self.task_table.insert(
                "",
                tk.END,
                iid=str(task["id"]),
                values=(
                    task["title"],
                    task["subject"],
                    formatted_date,
                    status,
                    "Просрочена" if overdue else "",
                ),
                tags=("overdue",) if overdue else (),
            )

        filters_active = (
            selected_subject is not None
            or selected_status is not None
        )

        if not tasks:
            message = (
                "Няма задачи по избраните критерии"
                if filters_active
                else "Няма добавени задачи"
            )
        else:
            message = (
                f"Показани задачи: {len(tasks)} от {len(all_tasks)}"
            )

        self.summary_label.config(text=message)

    def save_new_task(self, title: str, subject: str, due_date: str) -> int:
        """Записва нова задача и обновява таблицата след успех."""
        task_id = create_task(title, subject, due_date)
        self.refresh_tasks()
        return task_id

    def open_add_task_dialog(self):
        AddTaskDialog(self, on_save=self.save_new_task)

    def open_edit_task_dialog(self):
        selection = self.task_table.selection()

        if not selection:
            messagebox.showinfo(
                "Избор на задача",
                "Избери задача от списъка.",
                parent=self,
            )
            return

        task_id = int(selection[0])
        values = self.task_table.item(selection[0], "values")

        AddTaskDialog(
            self,
            on_save=lambda title, subject, due_date: self.save_edited_task(
                task_id, title, subject, due_date
            ),
            initial_values={
                "title": values[0],
                "subject": values[1],
                "due_date": values[2],
            },
        )

    def save_edited_task(
        self,
        task_id: int,
        title: str,
        subject: str,
        due_date: str,
    ) -> None:
        edit_task(task_id, title, subject, due_date)
        self.refresh_tasks()

        if self.task_table.exists(str(task_id)):
            self.task_table.selection_set(str(task_id))
            self.task_table.see(str(task_id))

    def delete_selected_task(self):
        selection = self.task_table.selection()

        if not selection:
            messagebox.showinfo(
                "Избор на задача",
                "Избери задача от списъка.",
                parent=self,
            )
            return

        task_id = int(selection[0])
        values = self.task_table.item(selection[0], "values")
        title = values[0]

        confirmed = messagebox.askyesno(
            "Изтриване на задача",
            f'Да изтрия ли задачата „{title}“?',
            parent=self,
            default=messagebox.NO,
        )

        if not confirmed:
            return

        try:
            remove_task(task_id)
        except ValueError as error:
            messagebox.showerror(
                "Изтриване на задача",
                str(error),
                parent=self,
            )
            self.refresh_tasks()
            return
        except sqlite3.Error:
            messagebox.showerror(
                "Грешка",
                "Задачата не може да бъде изтрита. Опитай отново.",
                parent=self,
            )
            return

        self.refresh_tasks()

    def change_selected_task_status(self):
        selection = self.task_table.selection()

        if not selection:
            messagebox.showinfo(
                "Избор на задача",
                "Избери задача от списъка.",
                parent=self,
            )
            return

        task_id = int(selection[0])

        try:
            change_task_status(task_id)
        except ValueError as error:
            messagebox.showerror(
                "Промяна на статус",
                str(error),
                parent=self,
            )
            self.refresh_tasks()
            return
        except sqlite3.Error:
            messagebox.showerror(
                "Грешка",
                "Статусът не може да бъде променен. Опитай отново.",
                parent=self,
            )
            return

        self.refresh_tasks()

        if self.task_table.exists(str(task_id)):
            self.task_table.selection_set(str(task_id))
            self.task_table.see(str(task_id))

class AddTaskDialog(tk.Toplevel):
    def __init__(self, parent, on_save, initial_values=None):
        super().__init__(parent)

        self.on_save = on_save
        self.is_editing = initial_values is not None
        values = initial_values or {}

        self.title(
            "Редактиране на учебна задача"
            if self.is_editing
            else "Добавяне на учебна задача"
        )
        self.resizable(False, False)
        self.transient(parent)

        self.title_var = tk.StringVar(value=values.get("title", ""))
        self.subject_var = tk.StringVar(value=values.get("subject", ""))
        self.due_date_var = tk.StringVar(value=values.get("due_date", ""))
        self.error_var = tk.StringVar()

        self.create_widgets()

        self.bind("<Return>", self.handle_enter)
        self.bind("<Escape>", lambda event: self.destroy())
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.wait_visibility()
        self.grab_set()
        self.title_entry.focus_set()

    def create_widgets(self):
        container = ttk.Frame(self, padding=20)
        container.pack(fill=tk.BOTH, expand=True)
        container.columnconfigure(1, weight=1)

        ttk.Label(
            container,
            text="Заглавие:",
        ).grid(row=0, column=0, sticky=tk.W, padx=(0, 12), pady=6)

        self.title_entry = ttk.Entry(
            container,
            textvariable=self.title_var,
            width=40,
        )
        self.title_entry.grid(
            row=0, column=1, sticky=tk.EW, pady=6
        )

        ttk.Label(
            container,
            text="Предмет:",
        ).grid(row=1, column=0, sticky=tk.W, padx=(0, 12), pady=6)

        ttk.Entry(
            container,
            textvariable=self.subject_var,
            width=40,
        ).grid(row=1, column=1, sticky=tk.EW, pady=6)

        ttk.Label(
            container,
            text="Краен срок:",
        ).grid(row=2, column=0, sticky=tk.W, padx=(0, 12), pady=6)

        ttk.Entry(
            container,
            textvariable=self.due_date_var,
            width=40,
        ).grid(row=2, column=1, sticky=tk.EW, pady=6)

        ttk.Label(
            container,
            text="Формат: ДД.ММ.ГГГГ, например 15.10.2026",
        ).grid(row=3, column=1, sticky=tk.W, pady=(0, 8))

        ttk.Label(
            container,
            textvariable=self.error_var,
            foreground="#b00020",
            wraplength=380,
        ).grid(
            row=4,
            column=0,
            columnspan=2,
            sticky=tk.W,
            pady=(4, 12),
        )

        buttons = ttk.Frame(container)
        buttons.grid(
            row=5, column=0, columnspan=2, sticky=tk.E
        )

        self.cancel_button = ttk.Button(
            buttons,
            text="Отказ",
            command=self.destroy,
        )
        self.cancel_button.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(
            buttons,
            text="Запази" if self.is_editing else "Добави",
            command=self.submit,
        ).pack(side=tk.LEFT)

    def handle_enter(self, event=None):
        if self.focus_get() == self.cancel_button:
            self.destroy()
        else:
            self.submit()

        return "break"


    def submit(self, event=None):
        self.error_var.set("")

        try:
            self.on_save(
                self.title_var.get(),
                self.subject_var.get(),
                self.due_date_var.get(),
            )
        except ValueError as error:
            self.error_var.set(str(error))
            return
        except sqlite3.Error:
            self.error_var.set(
                "Възникна грешка при работа с базата данни. "
                "Затвори формата и обнови списъка, "
                "за да провериш дали задачата е записана."
            )
            return

        self.destroy()