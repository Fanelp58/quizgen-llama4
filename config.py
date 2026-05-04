import os
from dotenv import load_dotenv

load_dotenv()

# Clé API Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ========== ARCHITECTURES NLP DISPONIBLES ==========
# Modèle actuellement utilisé (Llama 4 via Groq)
MODEL_ACTIF = "meta-llama/llama-4-scout-17b-16e-instruct"

# Architecture: LLM (Large Language Model) de type Transformer
# - Meta Llama 4: Modèle génératif à 17B paramètres
# - Fine-tuned pour l'instruction suivante (instruction-tuned)

# Modèles alternatifs disponibles
MODELS_AVAILABLE = {
    "llama4": "meta-llama/llama-4-scout-17b-16e-instruct",  # Recommandé
    "llama3": "llama-3.3-70b-versatile",                    # Alternative
    "mixtral": "mixtral-8x7b-32768",                         # Mixture of Experts
    "qwen": "qwen/qwen3-32b",                                # Alibaba Qwen
    "gemma": "gemma2-9b-it"                                  # Google Gemma
}

TYPES_QUESTIONS = ["QCM", "Vrai/Faux", "Question ouverte"]
NIVEAUX = ["Facile", "Moyen", "Difficile"]
NOMBRE_QUESTIONS_OPTIONS = [5, 10, 15, 20]