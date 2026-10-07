from io import BytesIO
import json
import sqlite3
import pandas as pd
import streamlit as st
from email_validator import validate_email, EmailNotValidError

#py -m streamlit run VandQuizStreamLit/app.py

# Konfiguration af siden
st.set_page_config(
    page_title="Quiz om Vandforbrug", page_icon="💧", layout="centered"
)

# Lidt fed styling (CSS)
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            display: none !important;
            width: 0px !important;
        }
        
        /* Skjul knappen/pilen øverst til venstre */
        [data-testid="collapsedControl"], 
        button[aria-label="Close sidebar"],
        button[aria-label="Open sidebar"] {
            display: none !important;
        }

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

# Connection String til SQLite
conn = sqlite3.connect("quiz_entries.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS entries")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS entries (
        email TEXT PRIMARY KEY,
        name TEXT,
        score INTEGER
    )
""")
conn.commit()

# Indlæs quiz-data fra JSON-fil
try:
    with open("VandQuizStreamLit/quiz_data.json", "r", encoding="utf-8") as f:
        quiz_data = json.load(f)
except FileNotFoundError:
    try:
        with open("quiz_data.json", "r", encoding="utf-8") as f:
            quiz_data = json.load(f)
    except FileNotFoundError:
        st.error("Kunne ikke finde 'quiz_data.json'. Tjek at filen ligger i mappen!")
        quiz_data = []

# Initialisér Session State variabler
if "user_registered" not in st.session_state:
    st.session_state.user_registered = False
    st.session_state.user_name = ""
    st.session_state.user_email = ""

if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "selected_choices" not in st.session_state:
    st.session_state.selected_choices = {}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False


# --- QUIZ FUNKTIONER ---
def show_question():
    question = quiz_data[st.session_state.current_question]
    st.subheader(
        f"Spørgsmål {st.session_state.current_question + 1} af {len(quiz_data)}"
    )
    st.write(question["question"])

    svarende = question.get("choices", question.get("options", []))

    # Tjek om der allerede er gemt et svar for dette spørgsmål
    previous_answer = st.session_state.selected_choices.get(
        st.session_state.current_question
    )

    default_index = None
    if previous_answer in svarende:
        default_index = svarende.index(previous_answer)

    with st.form(key=f"question_form_{st.session_state.current_question}"):
        selected_choice = st.radio("Vælg et svar:", svarende, index=default_index)

        col1, col2 = st.columns(2)
        with col1:
            back_button = st.form_submit_button("Tilbage")
        with col2:
            submit_button = st.form_submit_button("Næste / Gem")

    if back_button:
        if st.session_state.current_question > 0:
            st.session_state.current_question -= 1
            st.rerun()

    elif submit_button:
        if selected_choice is not None:
            # Gem det valgte svar
            st.session_state.selected_choices[st.session_state.current_question] = selected_choice
            st.session_state.current_question += 1
            st.rerun()
        else:
            st.warning("Vælg venligst et svar, før du fortsætter!")


def calculate_score():
    score = 0
    for idx, q in enumerate(quiz_data):
        user_ans = st.session_state.selected_choices.get(idx)
        if user_ans == q.get("answer"):
            score += 1
    return score


def main():
    st.title("💧 Quiz om vores vandforbrug")
    st.write("Velkommen! Test hvor meget du ved om vandforbrug og bæredygtighed.")
    st.divider()

    # ---------------------------------------------------------
    # TRIN 1: Registrering (Start)
    # ---------------------------------------------------------
    if not st.session_state.user_registered:
        st.subheader("Indtast dit navn og din e-mail for at starte quizzen")

        with st.form("info_form"):
            name = st.text_input("Fulde Navn")
            email = st.text_input("E-mailadresse").strip().lower()

            submitted = st.form_submit_button("Start Quiz")

        if submitted:
            if not name or not email:
                st.error("Udfyld venligst både navn og e-mail.")
            else:
                # Tjek om e-mailen allerede er registreret i databasen
                cursor.execute("SELECT email FROM entries WHERE email = ?", (email,))
                existing_user = cursor.fetchone()



                if existing_user:
                    st.error("Denne e-mailadresse har allerede deltaget i quizzen!")
                
                try:
                    print(email)
                    # Tjekker format OG om domænet har en aktiv e-mail-server (check_deliverability=True)
                    valid = validate_email(email, check_deliverability=False)
                    print(valid)

                    normalized_email = valid.normalized  # Den 'rene' e-mail
                    print(normalized_email)
                    st.success(f"E-mailen er gyldig: {normalized_email}")

                    # Gem i session og lås quizzen op
                    st.session_state.user_registered = True
                    st.session_state.user_name = name
                    st.session_state.user_email = email
                    st.rerun()
        
                except EmailNotValidError as e:
                    # Vis fejlen hvis e-mailen er ugyldig eller domænet ikke findes
                    st.error("Ugyldig e-mail")
                    

    # ---------------------------------------------------------
    # TRIN 2: Quiz Spørgsmål & Afslutning
    # ---------------------------------------------------------
    else:
        st.info(f"Deltager: **{st.session_state.user_name}** ({st.session_state.user_email})")

        if quiz_data:
            # Viser spørgsmål indtil det sidste er nået
            if st.session_state.current_question < len(quiz_data):
                show_question()
            else:
                # Gem resultatet i databasen hvis det ikke er gemt endnu
                if not st.session_state.quiz_submitted:
                    final_score = calculate_score()
                    st.session_state.score = final_score
                    answers_str = json.dumps(st.session_state.selected_choices)

                    try:
                        cursor.execute(
                            "INSERT INTO entries (email, name, score) VALUES (?, ?, ?)",
                            (
                                st.session_state.user_email,
                                st.session_state.user_name,
                                final_score,
                            ),
                        )
                        conn.commit()
                        st.session_state.quiz_submitted = True
                    except sqlite3.IntegrityError:
                        st.error("Fejl ved gemning: Denne e-mail har allerede deltaget.")

                # Vis resultat til brugeren
                if st.session_state.score == len(quiz_data):
                    st.balloons()
                    st.subheader(
                        f"Fantastisk! Du fik alle spørgsmål rigtige! Din Score: {st.session_state.score}/{len(quiz_data)} 🎉"
                    )
                else:
                    st.subheader(
                        f"Quiz gennemført! Din Score: {st.session_state.score}/{len(quiz_data)} 🎉"
                    )

                st.success("Tak for din deltagelse! Dine svar er gemt i systemet.")

# ---------------------------------------------------------
# TRIN 3: Admin Zone (Hidden behind URL parameter)
# ---------------------------------------------------------
# Check if '?admin=true' is present in the browser URL
query_params = st.query_params

if query_params.get("admin") == "true":
    st.markdown("---")
    st.subheader("🔒 Admin Zone")
    admin_password = st.text_input("Indtast Admin Kodeord for at se svar", type="password")

    if admin_password == "admin123":
        df = pd.read_sql_query("SELECT * FROM entries", conn)
        st.write(f"Samlet antal deltagere: {len(df)}")
        st.dataframe(df)

        if not df.empty:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Submissions CSV",
                data=csv,
                file_name="quiz_winners.csv",
                mime="text/csv",
            )


if __name__ == "__main__":
    main()