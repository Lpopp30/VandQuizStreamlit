from io import BytesIO
import json
import qrcode
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
    
    /* Gør hver radioknap til en fin boks/kort */
    .stRadio div[role="radiogroup"] label {
        background-color: #ffffff;
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        padding: 10px 15px;
        margin-bottom: 8px;
        width: 100%;
        transition: all 0.2s ease;
    }
    
    /* Effekt når musen holdes over en svarmulighed */
    .stRadio div[role="radiogroup"] label:hover {
        background-color: #f0f9ff;
        border-color: #0284c7;
    }

    /* Style formen pænt indeni */
    .stForm {
        border: none;
        background-color: transparent;
        padding: 0px;
    }
    </style>
""",
    unsafe_allow_html=True,
)



# 2. Indlæs quiz-data direkte fra din JSON-fil
# (Sørg for at stien passer til hvor din JSON-fil ligger i projektet)
try:
  with open("VandQuizStreamLit/quiz_data.json", "r", encoding="utf-8") as f:
    quiz_data = json.load(f)
except FileNotFoundError:
  st.error(
      "Kunne ikke finde 'quiz_data.json'. Tjek at filen ligger i mappen!"
  )
  quiz_data = []
if "selected_choices" not in st.session_state:
    st.session_state.selected_choices = {
        1 : ""
        }

# --- QUIZ FUNKTIONER ---
def show_question():
  question = quiz_data[st.session_state.current_question]
  st.subheader(
      f"Spørgsmål {st.session_state.current_question + 1} af"
      f" {len(quiz_data)}"
  )
  st.write(question["question"])

  svarende = question.get("choices", question.get("options", []))

  # Tjek om der allerede er gemt et svar for dette spørgsmål
  previous_answer = st.session_state.selected_choices.get(st.session_state.current_question)
  print(previous_answer)
  # Find indeks for det tidligere svar, ellers sæt den til None
  default_index = None
  if previous_answer in svarende:
    default_index = svarende.index(previous_answer)

  with st.form(key=f"question_form_{st.session_state.current_question}"):
    # Bemærk: Bruger 'options' eller 'choices' afhængigt af hvad din JSON-fil hedder
    # Her bruger vi 'choices' baseret på dit script
    selected_choice = st.radio("Vælg et svar:", svarende, index=default_index)

    col1, col2 = st.columns(2)
    with col1:
        back_button = st.form_submit_button("Tilbage")
        if st.session_state.current_question > 0:
            print(st.session_state.current_question)
    with col2:
      submit_button = st.form_submit_button("Næste")

    if back_button:
      st.session_state.current_question -= 1
      st.rerun()
    elif submit_button:
      if selected_choice is not None:
        st.session_state.selected_choices.update({st.session_state.current_question : selected_choice})
        print(st.session_state.selected_choices)
        check_answer(selected_choice)
        st.rerun()
      else:
        st.warning("Vælg venligst et svar, før du fortsætter!")


def check_answer(selected_choice):
  question = quiz_data[st.session_state.current_question]
  if selected_choice == question["answer"]:
    st.success("Rigtigt!")
    st.session_state.score += 1
  else:
    st.error(f"Forkert. Det rigtige svar var: {question['answer']}")

  st.session_state.current_question += 1


def main():
  if "current_question" not in st.session_state:
    st.session_state.current_question = 0
  if "score" not in st.session_state:
    st.session_state.score = 0

  st.title("💧 Quiz om vores vandforbrug")
  st.write(
      "Velkommen! Test hvor meget du ved om vandforbrug og bæredygtighed."
  )
  st.divider()

  if quiz_data:
    if st.session_state.current_question < len(quiz_data):
      show_question()
    else:
        if st.session_state.score == len(quiz_data):
            st.balloons()
            st.subheader(
                f"Fantastisk! Du fik alle spørgsmål rigtige! Din Score: {st.session_state.score}/{len(quiz_data)} 🎉"
            )
        else:
            st.subheader(
                f"Quiz Complete! Din Score: {st.session_state.score}/{len(quiz_data)} 🎉"
            )

        if st.button("Tag quizzen igen"):
            st.session_state.current_question = 0
            st.session_state.score = 0
            st.rerun()


if __name__ == "__main__":
  main()
