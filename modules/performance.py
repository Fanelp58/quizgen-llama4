# En tête du fichier
"""
MÉTRIQUES D'ÉVALUATION DES PERFORMANCES
=========================================

Architecture NLP utilisée : Transformer (LLaMA 4 17B via Groq API)

1. MÉTRIQUES STRUCTURELLES (qualité des questions générées)
   - Complétude: Vérifie la présence de tous les champs requis
   - Diversité: Mesure la variété lexicale (évite les répétitions)
   - Longueur: Équilibre des questions (ni trop courtes, ni trop longues)
   - Qualité des explications: Longueur et pertinence

2. MÉTRIQUES BASÉES SUR LES FEEDBACKS UTILISATEUR
   - Précision (Precision): TP / (TP + FP)
   - Rappel (Recall): TP / (TP + FN)
   - F1-Score: 2 * (Précision * Rappel) / (Précision + Rappel)

3. INTERPRÉTATION DES SCORES
   - 90-100%: Excellent
   - 70-89%: Bon
   - 50-69%: Moyen
   - <50%: À améliorer
"""

import json
import re
from typing import List, Dict, Any
from datetime import datetime

def evaluer_qualite_questions(questions: List[Dict], type_question: str) -> Dict:
    """
    Évalue la qualité des questions générées sur plusieurs critères.
    Retourne un dictionnaire avec les métriques de performance.
    """
    scores = {
        "date_evaluation": datetime.now().isoformat(),
        "type_question": type_question,
        "nombre_questions": len(questions),
        "score_global": 0,
        "metriques": {}
    }
    
    if not questions:
        return scores
    
    # 1. Complétude structurelle
    scores["metriques"]["completude"] = evaluer_completude(questions, type_question)
    
    # 2. Diversité lexicale
    scores["metriques"]["diversite"] = evaluer_diversite(questions)
    
    # 3. Longueur des questions
    scores["metriques"]["longueur"] = evaluer_longueur(questions)
    
    # 4. Qualité des explications (si présentes)
    if type_question in ["QCM", "Vrai/Faux"]:
        scores["metriques"]["explications"] = evaluer_explications(questions)
    
    # 5. Score global
    scores["score_global"] = calculer_score_global(scores["metriques"])
    
    return scores

def evaluer_completude(questions: List[Dict], type_question: str) -> Dict:
    """Vérifie que toutes les questions ont les champs requis."""
    champs_requis = {
        "QCM": ["question", "options", "reponse_correcte", "explication"],
        "Vrai/Faux": ["question", "reponse_correcte", "explication"],
        "Question ouverte": ["question", "reponse_suggeree", "points_cles"]
    }
    
    requis = champs_requis.get(type_question, [])
    valides = 0
    
    for q in questions:
        complet = all(champ in q and q[champ] for champ in requis)
        if complet:
            valides += 1
    
    return {
        "taux_validite": round((valides / len(questions)) * 100, 2) if questions else 0,
        "questions_valides": valides,
        "questions_invalides": len(questions) - valides
    }

def evaluer_diversite(questions: List[Dict]) -> Dict:
    """Calcule la diversité des questions (évite les répétitions)."""
    texte_questions = [q.get("question", "").lower() for q in questions]
    
    if len(texte_questions) <= 1:
        return {"score_diversite": 100, "questions_uniques": len(texte_questions), "ratio_vocabulaire": 100}
    
    uniques = len(set(texte_questions))
    score_diversite = (uniques / len(texte_questions)) * 100
    
    tous_mots = " ".join(texte_questions).split()
    mots_uniques = len(set(tous_mots))
    ratio_vocabulaire = (mots_uniques / len(tous_mots)) * 100 if tous_mots else 0
    
    return {
        "score_diversite": round(score_diversite, 2),
        "questions_uniques": uniques,
        "ratio_vocabulaire": round(ratio_vocabulaire, 2)
    }

def evaluer_longueur(questions: List[Dict]) -> Dict:
    """Évalue la longueur des questions."""
    longueurs = [len(q.get("question", "")) for q in questions]
    
    if not longueurs:
        return {"score_longueur": 0, "longueur_moyenne": 0, "ecart_type": 0, "min": 0, "max": 0}
    
    import numpy as np
    moyenne = np.mean(longueurs)
    ecart_type = np.std(longueurs)
    
    valides = sum(1 for l in longueurs if 50 <= l <= 200)
    score = (valides / len(longueurs)) * 100 if longueurs else 0
    
    return {
        "score_longueur": round(score, 2),
        "longueur_moyenne": round(moyenne, 2),
        "ecart_type": round(ecart_type, 2),
        "min": min(longueurs),
        "max": max(longueurs)
    }

def evaluer_explications(questions: List[Dict]) -> Dict:
    """Évalue la qualité des explications."""
    longueurs_exp = []
    exp_valides = 0
    
    for q in questions:
        exp = q.get("explication", "")
        if exp and len(exp) > 20:
            longueurs_exp.append(len(exp))
            exp_valides += 1
    
    if not longueurs_exp:
        return {"score_explications": 0, "taux_explications": 0, "longueur_moyenne": 0}
    
    import numpy as np
    moyenne = np.mean(longueurs_exp)
    taux = (exp_valides / len(questions)) * 100 if questions else 0
    
    score = taux
    if moyenne > 100:
        score = min(100, score + 10)
    
    return {
        "score_explications": round(score, 2),
        "taux_explications": round(taux, 2),
        "longueur_moyenne": round(moyenne, 2)
    }

def calculer_score_global(metriques: Dict) -> float:
    """Calcule un score global pondéré."""
    ponderation = {
        "completude": 0.35,
        "diversite": 0.25,
        "longueur": 0.20,
        "explications": 0.20
    }
    
    score_total = 0
    for key, poids in ponderation.items():
        if key in metriques:
            if "taux_validite" in metriques[key]:
                valeur = metriques[key]["taux_validite"]
            elif "score_diversite" in metriques[key]:
                valeur = metriques[key]["score_diversite"]
            elif "score_longueur" in metriques[key]:
                valeur = metriques[key]["score_longueur"]
            elif "score_explications" in metriques[key]:
                valeur = metriques[key]["score_explications"]
            else:
                valeur = 0
            score_total += valeur * poids
    
    return round(score_total, 2)

def comparer_modeles(quiz_llama: List[Dict], quiz_gpt: List[Dict] = None, 
                     quiz_claude: List[Dict] = None) -> Dict:
    """Compare les performances entre différents modèles."""
    comparaison = {
        "meta-llama/llama-4-scout-17b-16e-instruct": evaluer_qualite_questions(quiz_llama, "QCM")["score_global"],
    }
    
    if quiz_gpt:
        comparaison["gpt-4"] = evaluer_qualite_questions(quiz_gpt, "QCM")["score_global"]
    if quiz_claude:
        comparaison["claude-3"] = evaluer_qualite_questions(quiz_claude, "QCM")["score_global"]
    
    meilleur = max(comparaison, key=comparaison.get)
    comparaison["meilleur_modele"] = meilleur
    comparaison["difference_meilleur"] = max(comparaison.values()) - min(comparaison.values())
    
    return comparaison