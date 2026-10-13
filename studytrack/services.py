"""Бизнес логика и валидация на учебните задачи."""

import re
from datetime import datetime
from pathlib import Path
from studytrack.database import (
    DEFAULT_DB_PATH,
    delete_task,
    insert_task,
    toggle_task_status,
    update_task,
)


def validate_task(title: str, subject: str, due_date: str) -> dict:
    """Проверява данните и връща подготвени стойности за запис."""
    title = title.strip()
    subject = subject.strip()
    due_date = due_date.strip()

    if not title:
        raise ValueError("Въведи заглавие на задачата.")

    if not subject:
        raise ValueError("Въведи предмет.")

    if not due_date:
        raise ValueError("Въведи краен срок.")

    if not re.fullmatch(r"[0-9]{2}\.[0-9]{2}\.[0-9]{4}", due_date):
        raise ValueError("Въведи датата във формат ДД.ММ.ГГГГ.")

    try:
        parsed_date = datetime.strptime(due_date, "%d.%m.%Y").date()
    except ValueError:
        raise ValueError("Въведи валидна календарна дата.") from None

    return {
        "title": title,
        "subject": subject,
        "due_date": parsed_date.isoformat(),
    }

def create_task(
    title: str,
    subject: str,
    due_date: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> int:
    """Валидира данните и записва задачата само ако са коректни."""
    task = validate_task(title, subject, due_date)

    return insert_task(
        title=task["title"],
        subject=task["subject"],
        due_date=task["due_date"],
        db_path=db_path,
    )

def edit_task(
    task_id: int,
    title: str,
    subject: str,
    due_date: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    """Валидира новите стойности и актуализира избраната задача."""
    task = validate_task(title, subject, due_date)

    update_task(
        task_id=task_id,
        title=task["title"],
        subject=task["subject"],
        due_date=task["due_date"],
        db_path=db_path,
    )

def remove_task(
    task_id: int,
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    """Изтрива избраната задача."""
    delete_task(task_id, db_path)

def change_task_status(
    task_id: int,
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    """Превключва задача между завършена и незавършена."""
    toggle_task_status(task_id, db_path)