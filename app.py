import os
import streamlit as st

from src.config import OPENAI_API_KEY, COURSES_PATH, CHROMA_PATH
from src.memory import init_memory, add_message, format_history
from src.rag.loader import load_documents
from src.rag.vectorstore import build_vectorstore, load_vectorstore
from src.router import route_question

st.set_page_config(page_title="Academic RAG Assistant", page_icon="🎓", layout="wide")

st.title("🎓 Academic RAG Assistant")
st.caption("Assistant académique : RAG + agent léger + quiz + outils + mémoire")

if not OPENAI_API_KEY:
    st.error("La clé OPENAI_API_KEY est manquante dans le fichier .env")
    st.stop()

if "history" not in st.session_state:
    st.session_state.history = init_memory()

if "vectorstore_ready" not in st.session_state:
    st.session_state.vectorstore_ready = False

with st.sidebar:
    st.header("⚙️ Contrôle")

    if st.button("Indexer les documents"):
        with st.spinner("Indexation des notes de cours..."):
            docs = load_documents(COURSES_PATH)
            if not docs:
                st.error("Aucun document trouvé dans data/courses")
            else:
                build_vectorstore(docs)
                st.session_state.vectorstore_ready = True
                st.success("Documents indexés avec succès.")

    if os.path.exists(CHROMA_PATH):
        if st.button("Charger l'index existant"):
            st.session_state.vectorstore_ready = True
            st.success("Index chargé.")

    if st.button("Réinitialiser la conversation"):
        st.session_state.history = init_memory()
        st.success("Conversation réinitialisée.")

    st.markdown("---")
    st.subheader("Exemples")
    st.markdown("""
- Selon le cours de machine learning, qu'est-ce que le surapprentissage ?
- Résume le chapitre sur la régression logistique
- Crée un quiz sur la régression logistique
- Fais-moi 5 questions sur le cours de SQL
- Calcule 15 + 9 * 3
- Recherche web définition récente du fine-tuning
- Ajoute à ma todo : réviser SQL joins
- Affiche ma todo
- Supprime la tâche 1
""")

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("Pose ta question académique...")

if question:
    add_message(st.session_state.history, "user", question)

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Réponse en cours..."):
            history_text = format_history(st.session_state.history)

            vectorstore = None
            if st.session_state.vectorstore_ready:
                try:
                    vectorstore = load_vectorstore()
                except Exception as e:
                    st.warning(f"Impossible de charger le vector store : {e}")

            result = route_question(question, vectorstore, history_text)

            st.markdown(f"**Mode utilisé :** {result['mode']}")
            if "decision_reason" in result:
                st.markdown(f"**Décision agentique :** {result['decision_reason']}")
            st.markdown(result["answer"])

            if result["sources"]:
                st.markdown("**Sources :**")
                for src in result["sources"]:
                    st.markdown(f"- `{src}`")

            assistant_message = f"Mode utilisé : {result['mode']}"
            if "decision_reason" in result:
                assistant_message += f"\nDécision agentique : {result['decision_reason']}"
            assistant_message += f"\n\n{result['answer']}"

            if result["sources"]:
                assistant_message += "\n\nSources:\n" + "\n".join(result["sources"])

            add_message(st.session_state.history, "assistant", assistant_message)