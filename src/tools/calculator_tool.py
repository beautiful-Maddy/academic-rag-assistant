import math

ALLOWED_NAMES = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "pow": pow,
    "sqrt": math.sqrt,
}

def calculate(expression: str) -> str:
    try:
        result = eval(expression, {"__builtins__": {}}, ALLOWED_NAMES)
        return f"Résultat : {result}"
    except Exception as e:
        return f"Erreur calculatrice : {e}"