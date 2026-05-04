import csv
import io
import json


def exporter_csv(questions: list, type_question: str) -> str:
    """Génère un fichier CSV des questions pour téléchargement."""
    output = io.StringIO()
    writer = csv.writer(output)

    if type_question == "QCM":
        writer.writerow(["Question", "A", "B", "C", "D", "Réponse correcte", "Explication"])
        for q in questions:
            opts = q.get("options", {})
            writer.writerow([
                q.get("question", ""),
                opts.get("A", ""), opts.get("B", ""),
                opts.get("C", ""), opts.get("D", ""),
                q.get("reponse_correcte", ""),
                q.get("explication", "")
            ])

    elif type_question == "Vrai/Faux":
        writer.writerow(["Question", "Réponse correcte", "Explication"])
        for q in questions:
            writer.writerow([
                q.get("question", ""),
                q.get("reponse_correcte", ""),
                q.get("explication", "")
            ])

    elif type_question == "Question ouverte":
        writer.writerow(["Question", "Réponse suggérée", "Points clés"])
        for q in questions:
            writer.writerow([
                q.get("question", ""),
                q.get("reponse_suggeree", ""),
                " | ".join(q.get("points_cles", []))
            ])

    return output.getvalue()


def exporter_json(questions: list) -> str:
    """Génère un export JSON des questions."""
    return json.dumps(questions, ensure_ascii=False, indent=2)


def tronquer_texte(texte: str, max_chars: int = 500) -> str:
    """Tronque un texte pour l'aperçu."""
    if len(texte) <= max_chars:
        return texte
    return texte[:max_chars] + "..."
