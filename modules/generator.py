import json
import re
import requests
from config import GROQ_API_KEY, MODEL_ACTIF as MODEL

def construire_prompt(texte: str, type_question: str, niveau: str, nombre: int) -> str:
    """Construit le prompt adapté selon les paramètres choisis."""

    instructions_type = {
        "QCM": """Génère des questions à choix multiples (QCM).
Chaque question doit avoir exactement 4 options (A, B, C, D) et une seule bonne réponse.
Format JSON attendu pour chaque question :
{
  "question": "...",
  "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
  "reponse_correcte": "A",
  "explication": "..."
}""",

        "Vrai/Faux": """Génère des questions de type Vrai ou Faux.
Format JSON attendu pour chaque question :
{
  "question": "...",
  "reponse_correcte": "Vrai",
  "explication": "..."
}""",

        "Question ouverte": """Génère des questions ouvertes qui nécessitent une réponse rédigée.
Format JSON attendu pour chaque question :
{
  "question": "...",
  "reponse_suggeree": "...",
  "points_cles": ["...", "...", "..."]
}"""
    }

    instructions_niveau = {
        "Facile": "Les questions doivent tester la mémorisation et la compréhension basique. Vocabulaire simple, concepts directs.",
        "Moyen": "Les questions doivent tester la compréhension et l'application des concepts. Quelques liens entre les idées.",
        "Difficile": "Les questions doivent tester l'analyse, la synthèse et l'évaluation critique. Concepts complexes et nuancés."
    }

    prompt = f"""Tu es un expert pédagogue chargé de créer des évaluations de qualité pour des étudiants.

TEXTE SOURCE :
\"\"\"
{texte[:4000]}
\"\"\"

CONSIGNES :
- Génère exactement {nombre} questions de type : {type_question}
- Niveau de difficulté : {niveau}
- {instructions_niveau[niveau]}
- {instructions_type[type_question]}
- Toutes les questions doivent être strictement basées sur le texte fourni.
- Réponds UNIQUEMENT avec un tableau JSON valide contenant les {nombre} questions.
- Ne mets aucun texte avant ou après le JSON.
- Assure-toi que le JSON est valide et bien formaté.

Exemple de format de réponse attendu :
[
  {{ question_1 }},
  {{ question_2 }},
  ...
]"""

    return prompt

def generer_questions(texte: str, type_question: str, niveau: str, nombre: int) -> list:
    """Appelle l'API Groq pour générer les questions."""
    
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY non trouvée")
    
    prompt = construire_prompt(texte, type_question, niveau, nombre)
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL,  # Utilise le modèle de config.py
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4096
    }
    
    try:
        print(f"🔄 Génération de {nombre} questions avec {MODEL}...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code != 200:
            raise Exception(f"Erreur API {response.status_code}: {response.text}")
        
        result = response.json()
        contenu = result['choices'][0]['message']['content']
        
        # Nettoyer le JSON
        contenu_propre = re.sub(r"```json\s*|\s*```", "", contenu)
        contenu_propre = contenu_propre.strip()
        
        # Extraire le tableau JSON
        if not (contenu_propre.startswith('[') and contenu_propre.endswith(']')):
            match = re.search(r'\[.*\]', contenu_propre, re.DOTALL)
            if match:
                contenu_propre = match.group(0)
        
        questions = json.loads(contenu_propre)
        
        if not isinstance(questions, list):
            raise ValueError("La réponse n'est pas une liste valide")
        
        print(f"✅ {len(questions)} questions générées")
        return questions
        
    except requests.exceptions.Timeout:
        raise Exception("L'API a mis trop de temps à répondre")
    except json.JSONDecodeError as e:
        raise Exception(f"Erreur de parsing JSON: {e}")
    except Exception as e:
        raise Exception(f"Erreur: {str(e)}")