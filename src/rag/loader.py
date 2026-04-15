from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader

def load_documents(doc_path: str):
    docs = []
    path = Path(doc_path)

    if not path.exists():
        return docs

    for file in path.glob("*"):
        suffix = file.suffix.lower()

        try:
            if suffix == ".pdf":
                loader = PyPDFLoader(str(file))
                docs.extend(loader.load())
            elif suffix == ".docx":
                loader = Docx2txtLoader(str(file))
                docs.extend(loader.load())
            elif suffix == ".txt":
                loader = TextLoader(str(file), encoding="utf-8")
                docs.extend(loader.load())
        except Exception as e:
            print(f"Erreur lors du chargement de {file.name}: {e}")

    return docs