from typing import List, Dict, Set
import re

def calculer_precision_recall_f1(questions: List[Dict], 
                                   feedbacks_utilisateurs: Dict) -> Dict:
    """
    Calcule les métriques de précision, rappel et F1-score
    basées sur les feedbacks utilisateurs.
    """
    # Considérons les feedbacks "👍" comme "positifs" (vrais positifs)
    vrais_positifs = sum(1 for v in feedbacks_utilisateurs.values() if v == "👍")
    faux_negatifs = sum(1 for v in feedbacks_utilisateurs.values() if v == "👎")
    
    # Total des questions
    total_questions = len(questions)
    total_feedbacks = len(feedbacks_utilisateurs)
    
    # Précision : Vrais Positifs / (Vrais Positifs + Faux Positifs)
    # Ici, nous n'avons pas de faux positifs directs, nous utilisons feedbacks
    precision = vrais_positifs / total_feedbacks if total_feedbacks > 0 else 0
    
    # Rappel : Vrais Positifs / (Vrais Positifs + Faux Négatifs)
    rappel = vrais_positifs / (vrais_positifs + faux_negatifs) if (vrais_positifs + faux_negatifs) > 0 else 0
    
    # F1-score : Moyenne harmonique
    f1 = 2 * (precision * rappel) / (precision + rappel) if (precision + rappel) > 0 else 0
    
    return {
        "precision": round(precision * 100, 2),
        "rappel": round(rappel * 100, 2),
        "f1_score": round(f1 * 100, 2),
        "matrice": {
            "TP": vrais_positifs,  # Vrais Positifs (👍)
            "FN": faux_negatifs    # Faux Négatifs (👎)
        }
    }

def evaluer_pertinence_semantique(questions: List[Dict], texte_source: str) -> Dict:
    """
    Évalue si les questions sont pertinentes par rapport au texte source.
    Utilise des métriques basées sur le vocabulaire commun.
    """
    # Nettoyer et tokeniser le texte source
    mots_source = set(re.findall(r'\b\w+\b', texte_source.lower()))
    
    scores_pertinence = []
    
    for q in questions:
        question = q.get("question", "").lower()
        mots_question = set(re.findall(r'\b\w+\b', question))
        
        # Intersection du vocabulaire
        intersection = mots_question.intersection(mots_source)
        union = mots_question.union(mots_source)
        
        # Similarité de Jaccard
        jaccard = len(intersection) / len(union) if union else 0
        scores_pertinence.append(jaccard)
    
    moyenne = sum(scores_pertinence) / len(scores_pertinence) if scores_pertinence else 0
    
    # Classification
    if moyenne >= 0.5:
        niveau = "Excellente"
    elif moyenne >= 0.3:
        niveau = "Bonne"
    elif moyenne >= 0.1:
        niveau = "Moyenne"
    else:
        niveau = "Faible"
    
    return {
        "score_pertinence": round(moyenne * 100, 2),
        "niveau": niveau,
        "questions_pertinentes": sum(1 for s in scores_pertinence if s >= 0.3),
        "total_questions": len(questions)
    }