import json
import os
from datetime import datetime

FICHIER_QUIZ = "data/quizzes.json"


def charger_historique() -> list:
    """Charge l'historique des quiz sauvegardés."""
    if os.path.exists(FICHIER_QUIZ):
        with open(FICHIER_QUIZ, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def sauvegarder_quiz(questions: list, feedbacks: dict, type_q: str, niveau: str) -> None:
    """Sauvegarde le quiz avec les feedbacks dans le fichier JSON."""
    historique = charger_historique()

    entree = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "type": type_q,
        "niveau": niveau,
        "nombre_questions": len(questions),
        "questions": questions,
        "feedbacks": feedbacks,
        "score_qualite": calculer_score(feedbacks)
    }

    historique.append(entree)

    os.makedirs("data", exist_ok=True)
    with open(FICHIER_QUIZ, "w", encoding="utf-8") as f:
        json.dump(historique, f, ensure_ascii=False, indent=2)


def calculer_score(feedbacks: dict) -> float:
    """
    Calcule le score de qualité global basé sur les feedbacks 👍/👎.
    Retourne un pourcentage (0-100).
    """
    if not feedbacks:
        return 0.0

    positifs = sum(1 for v in feedbacks.values() if v == "👍")
    total = len(feedbacks)
    return round((positifs / total) * 100, 1)


def resume_feedbacks(feedbacks: dict) -> dict:
    """Retourne un résumé des feedbacks."""
    positifs = sum(1 for v in feedbacks.values() if v == "👍")
    negatifs = sum(1 for v in feedbacks.values() if v == "👎")
    return {
        "positifs": positifs,
        "negatifs": negatifs,
        "total": len(feedbacks),
        "score": calculer_score(feedbacks)
    }
