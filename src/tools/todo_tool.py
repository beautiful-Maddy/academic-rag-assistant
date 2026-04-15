import json
import os
from src.config import TODO_PATH

def _ensure_file():
    if not os.path.exists(TODO_PATH):
        with open(TODO_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def _load_tasks():
    _ensure_file()
    with open(TODO_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_tasks(tasks):
    with open(TODO_PATH, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def add_task(task: str) -> str:
    tasks = _load_tasks()
    tasks.append(task)
    _save_tasks(tasks)
    return f"Tâche ajoutée : {task}"

def list_tasks() -> str:
    tasks = _load_tasks()
    if not tasks:
        return "Aucune tâche de révision enregistrée."
    return "\n".join([f"{i+1}. {task}" for i, task in enumerate(tasks)])

def remove_task(index: int) -> str:
    tasks = _load_tasks()
    if index < 1 or index > len(tasks):
        return "Index invalide."
    removed = tasks.pop(index - 1)
    _save_tasks(tasks)
    return f"Tâche supprimée : {removed}"