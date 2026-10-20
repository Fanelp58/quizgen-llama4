# 🎓 QuizGen AI - Educational Quiz Generator

## Description

QuizGen AI is a web application that automatically generates educational quizzes from PDF documents or raw text.
The application uses **LLaMA 4** (via the Groq API) to generate high-quality questions tailored to a selected difficulty level.

### Features

-  **Text extraction** from PDF and DOCX files
-  **Question generation** (Multiple-choice, True/False, Open-ended)
-  **3 difficulty levels** (Easy, Medium, Hard)
-  **Exam mode** (hides answers)
-  **Performance metrics** (Precision, Recall, F1-Score)
-  **Local quiz history** storage
-  **Export options** (CSV/JSON)

### NLP Architecture

- **Model**: LLaMA 4 (17B parameters)
- **Architecture**: Auto-regressive Transformer
- **Fine-tuning**: Instruction-tuned
- **API**: Groq (optimized inference)

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- Groq API key ([Get one for free](https://console.groq.com))

### Local Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/quizgen-ia.git
cd quizgen-ia

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure the API key
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 5. Launch the application
streamlit run app.py
