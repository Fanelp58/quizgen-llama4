# 🎓 QuizGen IA - Générateur de Quiz Pédagogiques

## Description

QuizGen IA est une application web qui génère automatiquement des quiz pédagogiques à partir de documents PDF ou de texte brut. 
L'application utilise **LLaMA 4** (via Groq API) pour générer des questions de qualité adaptées au niveau de difficulté choisi.

### Fonctionnalités

-  **Extraction de texte** depuis PDF et DOCX
-  **Génération de questions** (QCM, Vrai/Faux, Question ouverte)
-  **3 niveaux de difficulté** (Facile, Moyen, Difficile)
-  **Mode examen** pour cacher les réponses
-  **Métriques de performance** (Précision, Rappel, F1-Score)
-  **Historique des quiz** sauvegardé localement
-  **Export CSV/JSON** des quiz

### Architecture NLP

- **Modèle**: LLaMA 4 (17B paramètres)
- **Architecture**: Transformer auto-régressif
- **Fine-tuning**: Instruction-tuned
- **API**: Groq (inférence optimisée)

## 🚀 Installation

### Prérequis

- Python 3.10 ou supérieur
- Clé API Groq ([Obtenir gratuitement](https://console.groq.com))

### Installation locale

```bash
# 1. Cloner le repository
git clone https://github.com/votre-username/quizgen-ia.git
cd quizgen-ia

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer la clé API
cp .env.example .env
# Éditer .env et ajouter votre clé GROQ_API_KEY

# 5. Lancer l'application
streamlit run app.py