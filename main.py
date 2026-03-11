import streamlit as st
import numpy as np
from supabase import create_client

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Personality Assessment", layout="centered")

# ---------------- MOBILE CSS ----------------
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-size: 14px;
}
h1 {font-size:26px !important;}
h2 {font-size:20px !important;}
h3 {font-size:16px !important;}
p, label {font-size:14px !important;}
</style>
""", unsafe_allow_html=True)

st.markdown("## Personality Evaluation Survey")
st.caption("Answer the questions to understand your personality traits.")

# ---------------- SUPABASE ----------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- QUESTIONS ----------------
questions = [
"I enjoy being the center of attention at social events",
"I usually don't talk much",
"I feel comfortable when I am around people",
"I prefer to stay in the background",
"I often start conversations with others",
"I usually don't have much to say",
"I talk to many different people at gatherings",
"I don't like being noticed by others",
"I am okay with being the center of attention",
"I tend to stay quiet around people I don't know",

"I get stressed easily",
"I usually feel relaxed",
"I worry about many things",
"I rarely feel sad",
"I get upset easily",
"I lose my temper easily",
"My mood changes often",
"I experience mood swings",
"I get annoyed easily",
"I often feel sad",

"I don't care much about other people's problems",
"I like learning about other people",
"I sometimes say rude things to others",
"I understand how others feel",
"I don't show interest in other people's issues",
"I am kind and caring toward others",
"I don't pay much attention to others",
"I like helping other people",
"I can easily feel what others are feeling",
"I try to make people feel comfortable",

"I like to stay prepared",
"I often leave my things lying around",
"I pay close attention to small details",
"I tend to be messy",
"I complete tasks right away",
"I sometimes forget to put things back where they belong",
"I like things to be organized",
"I sometimes avoid my responsibilities",
"I like following a daily routine",
"I try to do my work very carefully",

"I know many words and express myself well",
"I find it hard to understand complex ideas",
"I have a strong imagination",
"I am not very interested in deep ideas",
"I often come up with good ideas",
"I don't think I have much imagination",
"I understand new things quickly",
"I sometimes use advanced words when speaking",
"I spend time thinking deeply about things",
"I often think of new and creative ideas"
]

# ---------------- SESSION STATE ----------------
if "answers" not in st.session_state:
    st.session_state.answers = {}

if "q_index" not in st.session_state:
    st.session_state.q_index = 0

# ---------------- PERSONAL INFO ----------------
st.subheader("Personal Information")

name = st.text_input("Full Name")
job_role = st.text_input("Current Job Role")
company = st.text_input("Current Company")

experience = st.number_input("Years of Experience", min_value=0.0, step=0.5)
age = st.number_input("Age", min_value=18, max_value=100)

st.divider()

# ---------------- QUESTION SECTION ----------------
st.subheader("Personality Questions")

progress = (st.session_state.q_index + 1) / len(questions)
st.progress(progress)

q = questions[st.session_state.q_index]

st.markdown(f"**Question {st.session_state.q_index + 1} of {len(questions)}**")
st.markdown(q)

answer = st.radio(
"",
[1,2,3,4,5],
format_func=lambda x:{
1:"Strongly Disagree",
2:"Disagree",
3:"Neutral",
4:"Agree",
5:"Strongly Agree"
}[x],
key=f"q_{st.session_state.q_index}"
)

# Save answer
st.session_state.answers[f"question_{st.session_state.q_index}"] = answer

# ---------------- NAVIGATION ----------------
col1, col2 = st.columns(2)

with col1:
    if st.button("Previous") and st.session_state.q_index > 0:
        st.session_state.q_index -= 1

with col2:
    if st.button("Next") and st.session_state.q_index < len(questions)-1:
        st.session_state.q_index += 1

st.divider()

# ---------------- PERSONALITY CALCULATION ----------------
def calculate_big_five(answers):

    scores=[answers.get(f"question_{i}") for i in range(50)]

    def safe_mean(values):
        valid=[v for v in values if v is not None]
        return np.mean(valid) if valid else 0

    return {
        "Extraversion": safe_mean(scores[0:10]),
        "Neuroticism": safe_mean(scores[10:20]),
        "Agreeableness": safe_mean(scores[20:30]),
        "Conscientiousness": safe_mean(scores[30:40]),
        "Openness": safe_mean(scores[40:50])
    }

# ---------------- INTERPRETATION ----------------
def interpret_personality(bigfive):

    dominant_trait=max(bigfive,key=bigfive.get)

    descriptions={

        "Openness":{
        "desc":"You enjoy exploring new ideas and experiences. You are creative and curious about the world.",
        "roles":"Product Designer, Researcher, Innovation Manager, Strategy Analyst"
        },

        "Conscientiousness":{
        "desc":"You are organized, disciplined and responsible. You like planning tasks and paying attention to details.",
        "roles":"Project Manager, Operations Manager, Financial Analyst, Engineer"
        },

        "Extraversion":{
        "desc":"You enjoy interacting with people and feel energized in social situations.",
        "roles":"Sales Manager, Marketing Executive, HR Manager, Public Relations Specialist"
        },

        "Agreeableness":{
        "desc":"You value cooperation and harmony. You are kind and considerate toward others.",
        "roles":"HR Specialist, Counselor, Customer Success Manager, Teacher"
        },

        "Neuroticism":{
        "desc":"You may experience emotions strongly and sometimes feel stressed or worried.",
        "roles":"Quality Assurance Analyst, Risk Analyst, Research Assistant, Data Analyst"
        }
    }

    return dominant_trait, descriptions

# ---------------- SAVE TO DATABASE ----------------
def save_to_database(name,job_role,company,experience,age,answers,personality,traits):

    data={
    "full_name":name,
    "job_role":job_role,
    "company":company,
    "years_experience":experience,
    "age":age,
    "answers":answers,
    "personality_type":personality,
    "extraversion":traits["Extraversion"],
    "neuroticism":traits["Neuroticism"],
    "agreeableness":traits["Agreeableness"],
    "conscientiousness":traits["Conscientiousness"],
    "openness":traits["Openness"]
    }

    supabase.table("personality_assessments").insert(data).execute()

# ---------------- SUBMIT ----------------
if st.button("Submit Assessment"):

    if len(st.session_state.answers) < 50:
        st.error("Please answer all questions before submitting.")
    else:

        bigfive = calculate_big_five(st.session_state.answers)

        trait, descriptions = interpret_personality(bigfive)

        personality_percentages={}

        for trait_name,score in bigfive.items():
            personality_percentages[trait_name]=round((score/5)*100,2)

        save_to_database(
        name,
        job_role,
        company,
        experience,
        age,
        st.session_state.answers,
        trait,
        personality_percentages
        )

        st.success("Assessment submitted successfully")

        st.subheader("Candidate Profile")

        st.write("Name:",name)
        st.write("Company:",company)
        st.write("Role:",job_role)
        st.write("Experience:",experience)
        st.write("Age:",age)

        st.divider()

        st.subheader("Personality Result")

        st.success(f"Dominant Personality Trait: {trait}")

        st.write(descriptions[trait]["desc"])

        st.info(f"Suitable Roles: {descriptions[trait]['roles']}")

        st.divider()

        st.subheader("Personality Trait Scores")

        for trait_name,percent in personality_percentages.items():
            st.write(f"{trait_name}: {percent}%")
            st.progress(percent/100)