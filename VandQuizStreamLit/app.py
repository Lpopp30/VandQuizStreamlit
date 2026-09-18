from io import BytesIO
import qrcode
import json
import streamlit as st

# 1. Konfiguration af siden
st.set_page_config(
    page_title="Quiz om Vandforbrug", page_icon="💧", layout="centered"
)

# Lidt fed styling (CSS)
st.markdown(
    """
    <style>
    .main {
        background-color: #f8fafc;
    }
    .stTextInput > div > div > input {
        border-radius: 8px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 2. Hjemmesidens indhold: Vandforbrugs-quiz
st.title("💧 Quiz om vores vandforbrug")
st.write(
    "Velkommen til denne interaktive quiz! Test hvor meget du ved om vandforbrug"
    " og bæredygtighed."
)
st.divider()

# Quiz-spørgsmål
score = 0
total_questions = 3

# Åbn og indlæs JSON-filen
with open("VandQuizStreamLit/quiz_data.json", "r", encoding="utf-8") as f:
  quiz_data = json.load(f)

# Gå igennem spørgsmålene dynamisk
for i, q in enumerate(quiz_data):
  st.subheader(f"Spørgsmål {i + 1}: {q['question']}")
  user_answer = st.radio(
      "Vælg et svar:", q["options"], index=None, key=f"q_{i}"
  )

  if user_answer == q["answer"]:
    st.success("Rigtigt!")
  elif user_answer is not None:
    st.error(f"Forkert. Det rigtige svar er: {q['answer']}")
  st.divider()
st.divider()


# Resultat-knap
if st.button("Vis mit resultat"):
  current_score = 0
  if q1 == "Ca. 104 liter":
    current_score += 1
  if q2 == "Bad og personlig pleje":
    current_score += 1
  if q3 == "Ca. 71%":
    current_score += 1

  st.balloons()
  st.subheader(f"Du fik {current_score} ud af {total_questions} rigtige! 🎉")

  if current_score == total_questions:
    st.markdown("🏆 **Imponerende! Du har helt styr på vandforbruget.**")
  else:
    st.markdown("👍 Godt gået! Vand er en dyrebar ressource.")

