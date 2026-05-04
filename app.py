import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from modules.extractor import extraire_texte
from modules.generator import generer_questions
from modules.evaluator import sauvegarder_quiz, resume_feedbacks
from modules.utils import exporter_csv, exporter_json, tronquer_texte
from config import TYPES_QUESTIONS, NIVEAUX, NOMBRE_QUESTIONS_OPTIONS
from modules.performance import evaluer_qualite_questions
from modules.metrics import calculer_precision_recall_f1


# ─── Configuration de la page ───────────────────────────────────────────────
st.set_page_config(
    page_title="QuizGen IA",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS personnalisé ────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Sora', sans-serif;
    }

    .main { background-color: #0f1117; }

    .stApp {
        background: linear-gradient(135deg, #0f1117 0%, #1a1f2e 100%);
    }

    h1 { 
        font-size: 2.4rem !important; 
        font-weight: 700 !important;
        background: linear-gradient(90deg, #6ee7b7, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .question-card {
        background: linear-gradient(135deg, #1e2433, #252d3d);
        border: 1px solid #2e3750;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }

    .question-card:hover {
        transform: translateY(-2px);
        border-color: #3b82f6;
    }

    .question-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 0.8rem;
    }

    .option-item {
        background: #2a3347;
        border-radius: 8px;
        padding: 0.5rem 0.8rem;
        margin: 0.3rem 0;
        color: #94a3b8;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
    }

    .reponse-badge {
        display: inline-block;
        background: linear-gradient(90deg, #059669, #10b981);
        color: white;
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        font-size: 0.82rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }

    .score-card {
        background: linear-gradient(135deg, #1e3a5f, #1e4d3a);
        border: 1px solid #3b82f6;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        margin: 1rem 0;
    }

    .score-number {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #6ee7b7, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .badge-type {
        background: #1e3a5f;
        color: #60a5fa;
        border-radius: 8px;
        padding: 0.2rem 0.7rem;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .badge-niveau {
        background: #1e3d2a;
        color: #34d399;
        border-radius: 8px;
        padding: 0.2rem 0.7rem;
        font-size: 0.8rem;
        font-weight: 600;
        margin-left: 0.4rem;
    }

    .stButton > button {
        background: linear-gradient(90deg, #3b82f6, #6ee7b7);
        color: #0f1117;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 2rem;
        font-family: 'Sora', sans-serif;
        transition: opacity 0.2s;
    }

    .stButton > button:hover {
        opacity: 0.85;
    }

    .apercu-box {
        background: #1a2035;
        border-left: 3px solid #3b82f6;
        border-radius: 8px;
        padding: 1rem;
        color: #94a3b8;
        font-size: 0.88rem;
        font-family: 'JetBrains Mono', monospace;
        white-space: pre-wrap;
    }

    .sidebar-section {
        background: #1e2433;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ─── Initialisation session ──────────────────────────────────────────────────
if "questions" not in st.session_state:
    st.session_state.questions = []
if "feedbacks" not in st.session_state:
    st.session_state.feedbacks = {}
if "texte_extrait" not in st.session_state:
    st.session_state.texte_extrait = ""
if "generation_done" not in st.session_state:
    st.session_state.generation_done = False
if "type_question" not in st.session_state:
    st.session_state.type_question = TYPES_QUESTIONS[0]
if "niveau" not in st.session_state:
    st.session_state.niveau = NIVEAUX[1]


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 QuizGen IA")
    st.markdown("*Générateur de quiz pédagogiques*")
    st.divider()

    st.markdown("### ⚙️ Paramètres du quiz")

    type_question = st.selectbox(
        "Type de questions",
        TYPES_QUESTIONS,
        index=0,
        help="Choisissez le format des questions à générer"
    )
    st.session_state.type_question = type_question

    niveau = st.selectbox(
        "Niveau de difficulté",
        NIVEAUX,
        index=1,
        help="Adapte la complexité des questions"
    )
    st.session_state.niveau = niveau

    nombre = st.select_slider(
        "Nombre de questions",
        options=NOMBRE_QUESTIONS_OPTIONS,
        value=5
    )

    st.divider()
    st.markdown("### 📥 Source du contenu")

    source = st.radio(
        "Choisir la source",
        ["📄 Uploader un fichier", "✏️ Saisir du texte"],
        label_visibility="collapsed"
    )

    st.divider()
    st.caption("🤖 Architecture NLP: LLaMA 4 via Groq API")
    st.caption("Réalisé par HOUEHA Fanès, ISE | Data Scientist")


# ─── Contenu principal ────────────────────────────────────────────────────────
st.markdown("# 🎓 QuizGen IA")
st.markdown("##### Générez des évaluations pédagogiques de qualité en quelques secondes")
st.divider()

col1, col2 = st.columns([1.2, 1], gap="large")

# ── Colonne gauche : entrée ──
with col1:
    st.markdown("### 📝 Contenu source")

    fichier = None
    texte_saisi = ""

    if source == "📄 Uploader un fichier":
        fichier = st.file_uploader(
            "Déposez votre fichier ici",
            type=["pdf", "docx"],
            help="Formats acceptés : PDF, DOCX"
        )
        if fichier:
            st.success(f"✅ Fichier chargé : **{fichier.name}**")

    else:
        texte_saisi = st.text_area(
            "Collez votre texte ici",
            height=250,
            placeholder="Collez ici votre cours, syllabus ou tout autre contenu..."
        )

    # Bouton de génération
    st.markdown("")
    generer = st.button("⚡ Générer le quiz", use_container_width=True)

    if generer:
        try:
            with st.spinner("📖 Extraction du texte..."):
                texte = extraire_texte(fichier=fichier, texte_brut=texte_saisi)
                st.session_state.texte_extrait = texte

            with st.spinner(f"🤖 Llama 3 génère {nombre} questions de type {type_question}..."):
                questions = generer_questions(texte, type_question, niveau, nombre)
                st.session_state.questions = questions
                st.session_state.feedbacks = {}
                st.session_state.generation_done = True

            st.success(f"✅ {len(questions)} questions générées avec succès !")

        except ValueError as e:
            st.error(f"❌ {e}")
        except Exception as e:
            st.error(f"❌ Erreur inattendue : {e}")

    # Aperçu du texte extrait
    if st.session_state.texte_extrait:
        with st.expander("👁️ Aperçu du texte extrait"):
            st.markdown(
                f'<div class="apercu-box">{tronquer_texte(st.session_state.texte_extrait, 600)}</div>',
                unsafe_allow_html=True
            )

# ── Colonne droite : stats ──
with col2:
    if st.session_state.generation_done and st.session_state.questions:
        st.markdown("### 📊 Résumé")
        nb_q = len(st.session_state.questions)
        nb_fb = len(st.session_state.feedbacks)

        m1, m2, m3 = st.columns(3)
        m1.metric("Questions", nb_q)
        m2.metric("Évaluées", nb_fb)
        m3.metric("Restantes", nb_q - nb_fb)

        if st.session_state.feedbacks:
            resume = resume_feedbacks(st.session_state.feedbacks)
            st.markdown(f"""
            <div class="score-card">
                <div class="score-number">{resume['score']}%</div>
                <div style="color:#94a3b8; margin-top:0.3rem">Score de qualité</div>
                <div style="margin-top:0.8rem">
                    👍 {resume['positifs']} &nbsp;&nbsp; 👎 {resume['negatifs']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Export
        st.markdown("### 📤 Exporter")
        csv_data = exporter_csv(st.session_state.questions, st.session_state.type_question)
        json_data = exporter_json(st.session_state.questions)

        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                "⬇️ CSV",
                data=csv_data,
                file_name="quiz.csv",
                mime="text/csv",
                use_container_width=True
            )
        with c2:
            st.download_button(
                "⬇️ JSON",
                data=json_data,
                file_name="quiz.json",
                mime="application/json",
                use_container_width=True
            )

        # Sauvegarder avec feedbacks
        if st.session_state.feedbacks:
            if st.button("💾 Sauvegarder dans l'historique", use_container_width=True):
                sauvegarder_quiz(
                    st.session_state.questions,
                    st.session_state.feedbacks,
                    st.session_state.type_question,
                    st.session_state.niveau
                )
                st.success("✅ Quiz sauvegardé !")

        # === NOUVELLE SECTION PERFORMANCES ===
        st.divider()
        st.markdown("### 📊 Performances du modèle")
        
        if st.session_state.questions:
            # Évaluation de la qualité
            qualite = evaluer_qualite_questions(st.session_state.questions, st.session_state.type_question)
            
            # Afficher le score global
            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.metric("Score global", f"{qualite['score_global']}/100")
            
            if 'completude' in qualite['metriques']:
                col_s2.metric("Complétude", f"{qualite['metriques']['completude']['taux_validite']}%")
            if 'diversite' in qualite['metriques']:
                col_s3.metric("Diversité", f"{qualite['metriques']['diversite']['score_diversite']}%")
            
            # Métriques Précision/Rappel/F1 si feedbacks existent
            if st.session_state.feedbacks:
                st.markdown("---")
                st.markdown("#### 🎯 Métriques basées sur vos feedbacks")
                
                metriques = calculer_precision_recall_f1(st.session_state.questions, st.session_state.feedbacks)
                
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("📈 Précision", f"{metriques['precision']}%", 
                             help="% de questions que vous avez jugées bonnes")
                col_m2.metric("🎯 Rappel", f"{metriques['rappel']}%",
                             help="Couverture des concepts importants")
                col_m3.metric("⚖️ F1-Score", f"{metriques['f1_score']}%",
                             help="Équilibre précision/rappel")
                
                # Afficher la matrice
                st.caption(f"📊 Matrice: {metriques['matrice']['TP']} 👍 / {metriques['matrice']['FN']} 👎")
                
                # Interprétation
                if metriques['f1_score'] >= 80:
                    st.success("✅ Excellente qualité ! Les questions sont pertinentes.")
                elif metriques['f1_score'] >= 60:
                    st.info("📈 Bonne qualité, quelques améliorations possibles.")
                else:
                    st.warning("⚠️ Qualité à améliorer - Vérifiez le contenu source ou les paramètres.")
            
            # Barre de progression pour le score global
            st.progress(qualite['score_global'] / 100)


# ─── Affichage des questions ──────────────────────────────────────────────────
if st.session_state.generation_done and st.session_state.questions:
    st.divider()
    st.markdown("### 🗂️ Questions générées")

    # Toggle pour le mode examen
    show_answers = st.toggle("🔒 Mode examen (cacher les réponses)", value=False)

    if show_answers:
        st.info("🔒 Mode examen activé : les réponses sont cachées. Décochez pour voir les corrections.")
    else:
        st.success("📖 Mode révision activé : les réponses sont visibles.")

    type_q = st.session_state.type_question

    for i, q in enumerate(st.session_state.questions):
        with st.container():
            st.markdown(f"""
            <div class="question-card">
                <div style="margin-bottom:0.5rem">
                    <span class="badge-type">{type_q}</span>
                    <span class="badge-niveau">{st.session_state.niveau}</span>
                    <span style="color:#475569; font-size:0.8rem; margin-left:0.5rem">Q.{i+1}</span>
                </div>
                <div class="question-title">❓ {q.get('question', '')}</div>
            """, unsafe_allow_html=True)

            # ========== OPTIONS QCM (CORRIGÉES) ==========
            if type_q == "QCM" and "options" in q:
                for lettre, valeur in q["options"].items():
                    # SI mode examen DESACTIVE (show_answers = False) ALORS montrer la bonne réponse en vert
                    if not show_answers:
                        style = "color:#6ee7b7; font-weight:600;" if lettre == q.get("reponse_correcte") else ""
                    else:
                        style = ""  # Mode examen : tout est gris, pas de couleur
                    
                    st.markdown(
                        f'<div class="option-item" style="{style}"><b>{lettre}.</b> {valeur}</div>',
                        unsafe_allow_html=True
                    )
                
                # Afficher la réponse SEULEMENT si mode examen est DESACTIVE
                if not show_answers:
                    st.markdown(
                        f'<div class="reponse-badge">✓ Réponse : {q.get("reponse_correcte", "")}</div>',
                        unsafe_allow_html=True
                    )

            # ========== VRAI/FAUX (CORRIGÉ) ==========
            elif type_q == "Vrai/Faux":
                # Afficher la réponse SEULEMENT si mode examen est DESACTIVE
                if not show_answers:
                    st.markdown(
                        f'<div class="reponse-badge">✓ {q.get("reponse_correcte", "")}</div>',
                        unsafe_allow_html=True
                    )

            # ========== QUESTION OUVERTE ==========
            elif type_q == "Question ouverte":
                # Pour les questions ouvertes, on peut aussi cacher la réponse suggérée
                if not show_answers:
                    with st.expander("💡 Voir la réponse suggérée"):
                        st.markdown(f"**Réponse :** {q.get('reponse_suggeree', '')}")
                        pts = q.get("points_cles", [])
                        if pts:
                            st.markdown("**Points clés :**")
                            for pt in pts:
                                st.markdown(f"- {pt}")
                else:
                    # Mode examen : pas de réponse suggérée affichée
                    st.info("📝 Question ouverte - Réponse à rédiger par l'étudiant")

            # ========== EXPLICATION (cachée aussi en mode examen) ==========
            if "explication" in q and q["explication"]:
                if not show_answers:  # Cacher l'explication en mode examen
                    with st.expander("📚 Voir l'explication"):
                        st.markdown(q["explication"])

            st.markdown("</div>", unsafe_allow_html=True)

            # Feedback (toujours visible)
            fb_key = f"feedback_{i}"
            fb_col1, fb_col2, fb_col3 = st.columns([1, 1, 6])
            with fb_col1:
                if st.button("👍", key=f"up_{i}", help="Bonne question"):
                    st.session_state.feedbacks[fb_key] = "👍"
                    st.rerun()
            with fb_col2:
                if st.button("👎", key=f"down_{i}", help="Question à améliorer"):
                    st.session_state.feedbacks[fb_key] = "👎"
                    st.rerun()
            with fb_col3:
                if fb_key in st.session_state.feedbacks:
                    st.markdown(
                        f"<span style='color:#6ee7b7'>Évalué : {st.session_state.feedbacks[fb_key]}</span>",
                        unsafe_allow_html=True
                    )

            st.markdown("")
