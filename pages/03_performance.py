import streamlit as st
import json
import plotly.graph_objects as go
from modules.performance import evaluer_qualite_questions, comparer_modeles
from modules.metrics import calculer_precision_recall_f1
from modules.evaluator import charger_historique

st.set_page_config(page_title="Performances - QuizGen", page_icon="📊")
st.title("📊 Tableau de bord des performances")

# Charger l'historique
historique = charger_historique()

if not historique:
    st.info("Aucune donnée disponible. Générez d'abord des quiz.")
    st.stop()

# 1. Évolution des performances
st.subheader("📈 Évolution des scores")

scores = [quiz.get('score_qualite', 0) for quiz in historique]
dates = [quiz.get('date', '') for quiz in historique]

fig = go.Figure(data=go.Scatter(x=dates, y=scores, mode='lines+markers'))
fig.update_layout(title="Score de qualité dans le temps", xaxis_title="Date", yaxis_title="Score (%)")
st.plotly_chart(fig, use_container_width=True)

# 2. Distribution des types de questions
st.subheader("🎯 Performance par type de question")

types = list(set(quiz.get('type', '') for quiz in historique))
scores_par_type = {}

for t in types:
    scores_type = [quiz.get('score_qualite', 0) for quiz in historique if quiz.get('type') == t]
    if scores_type:
        scores_par_type[t] = sum(scores_type) / len(scores_type)

col1, col2 = st.columns(2)
with col1:
    st.bar_chart(scores_par_type)

# 3. Métriques globales
st.subheader("📊 Métriques globales")

all_feedbacks = {}
for quiz in historique:
    all_feedbacks.update(quiz.get('feedbacks', {}))

if all_feedbacks:
    metriques = calculer_precision_recall_f1([], all_feedbacks)
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Précision moyenne", f"{metriques['precision']}%", delta="👍 Qualité")
    col_b.metric("Rappel moyen", f"{metriques['rappel']}%")
    col_c.metric("F1-Score moyen", f"{metriques['f1_score']}%")