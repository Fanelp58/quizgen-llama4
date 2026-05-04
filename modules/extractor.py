import fitz  # PyMuPDF
from docx import Document
import io


def extraire_texte_pdf(fichier) -> str:
    """Extrait le texte d'un fichier PDF uploadé via Streamlit."""
    try:
        contenu = fichier.read()
        doc = fitz.open(stream=contenu, filetype="pdf")
        texte = ""
        for page in doc:
            texte += page.get_text()
        doc.close()
        return texte.strip()
    except Exception as e:
        raise ValueError(f"Erreur lors de la lecture du PDF : {e}")


def extraire_texte_docx(fichier) -> str:
    """Extrait le texte d'un fichier DOCX uploadé via Streamlit."""
    try:
        contenu = fichier.read()
        doc = Document(io.BytesIO(contenu))
        texte = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        return texte.strip()
    except Exception as e:
        raise ValueError(f"Erreur lors de la lecture du DOCX : {e}")


def extraire_texte(fichier=None, texte_brut: str = "") -> str:
    """
    Point d'entrée principal.
    Accepte un fichier uploadé (PDF/DOCX) ou du texte brut.
    Retourne le texte extrait.
    """
    if fichier is not None:
        nom = fichier.name.lower()
        if nom.endswith(".pdf"):
            return extraire_texte_pdf(fichier)
        elif nom.endswith(".docx"):
            return extraire_texte_docx(fichier)
        else:
            raise ValueError("Format non supporté. Utilisez un fichier PDF ou DOCX.")
    elif texte_brut.strip():
        return texte_brut.strip()
    else:
        raise ValueError("Aucun contenu fourni. Uploadez un fichier ou saisissez du texte.")
