# Academic RAG Assistant

Assistant académique intelligent combinant :
- un pipeline RAG pour interroger des notes de cours
- un agent léger piloté par LLM pour choisir le bon mode d’action
- plusieurs outils : calculatrice, recherche web, todo list
- un générateur automatique de quiz
- une interface conversationnelle avec Streamlit

## Fonctionnalités

- Questions/réponses sur des documents PDF, DOCX et TXT
- Réponses avec sources : nom du document + page si disponible
- Génération automatique de quiz à partir des notes
- Calculatrice
- Recherche web
- Todo list de révision
- Mémoire conversationnelle simple
- Routage agentique léger via LLM

## Architecture

1. Interface Streamlit
2. Orchestrateur LLM Router
3. Modules d’exécution :
   - RAG
   - Quiz Generator
   - Tools
   - Chat

## Installation

```bash
git clone <repo_url>
cd academic-rag-assistant
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt# academic-rag-assistant
