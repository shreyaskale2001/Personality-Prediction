import streamlit as st
import numpy as np
import pickle
from supabase import create_client
import xgboost as xgb






def convert_to_native(obj):
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native(v) for v in obj]
    else:
        return obj


# ---------------- SUPABASE CONNECTION ----------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- LOAD ML MODEL ----------------


with open("personality_model.pkl", "rb") as f:
    model = pickle.load(f)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Personality Assessment", layout="wide")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
h1 {font-size:30px !important;text-align:left !important;}
h2 {font-size:22px !important;}
h3 {font-size:18px !important;}
p, label {font-size:15px !important;}
</style>
""", unsafe_allow_html=True)

trait_mapping = {
    0: "Openness",
    1: "Conscientiousness",
    2: "Extraversion",
    3: "Agreeableness",
    4: "Neuroticism"
}

# ---------------- TITLE ----------------
st.title("Personality Evaluation Survey")
st.write("Answer all questions to discover your personality traits.")

# ---------------- PERSONAL INFO ----------------
st.header("Personal Information")

name = st.text_input("Full Name")
job_role = st.text_input("Current Job Role (Specify the role you are currently working in)")
company = st.text_input("Current Company")

col1, col2 = st.columns(2)

with col1:
    experience = st.number_input("Years of Experience", min_value=0.0, step=0.5)

with col2:
    age = st.number_input("Age", min_value=18, max_value=100)

st.divider()



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

st.header("Personality Questions")
st.write("1 = Strongly Disagree | 5 = Strongly Agree")

answers = {}

for i, q in enumerate(questions):
    st.markdown(f"### {i+1}. {q}")

    answers[i] = st.radio(
        "",
        [1,2,3,4,5],
        index=None,
        format_func=lambda x:{
            1:"Strongly Disagree",
            2:"Disagree",
            3:"Neutral",
            4:"Agree",
            5:"Strongly Agree"
        }[x],
        key=i
    )

    st.markdown("---")

# ---------------- CALCULATE BIG FIVE ----------------
def calculate_big_five(ans):

    scores = list(ans.values())

    return {
    "Extraversion": np.mean(scores[0:10]),
    "Neuroticism": np.mean(scores[10:20]),
    "Agreeableness": np.mean(scores[20:30]),
    "Conscientiousness": np.mean(scores[30:40]),
    "Openness": np.mean(scores[40:50])
    }

# ---------------- DESCRIPTIONS ----------------
descriptions = {

"Openness": {
"desc": "You enjoy new experiences and are curious about the world. You appreciate art, adventure, and different ideas. You have a strong imagination and can quickly understand new concepts.",
"roles": "Product Designer, Researcher, Innovation Manager, Strategy Analyst"
},

"Conscientiousness": {
"desc": "You are disciplined and organized. You like planning things in advance, paying attention to details, and following schedules. You prefer structured and well-organized work.",
"roles": "Project Manager, Operations Manager, Financial Analyst, Engineer"
},

"Extraversion": {
"desc": "You enjoy being around people and often take the lead in social situations. You are energetic, talkative, and comfortable being the center of attention.",
"roles": "Sales Manager, Marketing Executive, HR Manager, Public Relations Specialist"
},

"Agreeableness": {
"desc": "You value harmony and good relationships with others. You are kind, helpful, and considerate of people’s feelings, which makes others feel comfortable around you.",
"roles": "Human Resources Specialist, Counselor, Customer Success Manager, Teacher"
},

"Neuroticism": {
"desc": "You may experience emotions strongly and sometimes feel stressed or worried. You can be sensitive to pressure and may prefer calm environments.",
"roles": "Quality Assurance Analyst, Risk Analyst, Research Assistant, Data Analyst"
}

}



# ---------------- SUBMIT ----------------
if st.button("Submit Assessment"):

    if not name or not job_role or not company:
        st.error("Please fill all personal information fields.")

    elif None in answers.values():
        st.error("Please answer all questions before submitting.")

    else:

        features = list(answers.values())

        bigfive = calculate_big_five(answers)

        # ML MODEL PREDICTION
        prediction = model.predict([features])[0]
        dominant_trait = prediction

        # ---------------- STORE DATA ----------------
        data = {
            "name": name,
            "company": company,
            "job_role": job_role,
            "age": int(age),  # convert to native int
            "year_experience": float(experience),  # convert to native float
            "answers": {k: int(v) for k, v in answers.items()},  # convert all answers
            "dominant_trait": dominant_trait,
            "extraversion": float(round((bigfive["Extraversion"] / 5) * 100, 2)),
            "neuroticism": float(round((bigfive["Neuroticism"] / 5) * 100, 2)),
            "agreeableness": float(round((bigfive["Agreeableness"] / 5) * 100, 2)),
            "openness": float(round((bigfive["Openness"] / 5) * 100, 2))
        }

        try:
            data_serializable = convert_to_native(data)
            supabase.table("personality_assessments").insert(data_serializable).execute()

            # supabase.table("personality_assessments").insert(data).execute()

            st.success("Assessment submitted successfully!")

        except Exception as e:

            st.error("Database Error")
            st.write(e)

        st.divider()

        # ---------------- PROFILE ----------------
        st.header("Candidate Profile")

        st.write("Name:", name)
        st.write("Company:", company)
        st.write("Job Role:", job_role)
        st.write("Experience:", experience, "years")
        st.write("Age:", age)

        st.divider()

        # ---------------- RESULT ----------------
        st.header("Personality Result")

        st.success(f"Dominant Personality Trait: {dominant_trait}")

        st.divider()

        st.subheader("Personality Description & Suitable Organizational Roles")

        for personality, info in descriptions.items():

            st.markdown(f"### {personality}")
            st.write(info["desc"])
            st.info(f"Suitable Roles: {info['roles']}")
            st.markdown("---")

        # ---------------- TRAIT SCORES ----------------
        st.header("Personality Trait Scores")

        for trait, score in bigfive.items():

            percent = round((score/5)*100,2)

            st.write(f"{trait}: {percent}%")
            st.progress(percent/100)