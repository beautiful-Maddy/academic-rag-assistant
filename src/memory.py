from typing import List, Dict

def init_memory() -> List[Dict[str, str]]:
    return []

def add_message(history: List[Dict[str, str]], role: str, content: str) -> List[Dict[str, str]]:
    history.append({"role": role, "content": content})
    return history

def format_history(history: List[Dict[str, str]], max_turns: int = 6) -> str:
    recent = history[-max_turns:]
    return "\n".join([f"{m['role'].upper()}: {m['content']}" for m in recent])