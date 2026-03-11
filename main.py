import streamlit as st
import numpy as np
from supabase import create_client

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Personality Assessment", layout="centered")

st.title("Personality Evaluation Survey")
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

# ---------------- PERSONALITY CALCULATION ----------------
def calculate_big_five(answers):

    scores = [answers.get(f"question_{i}") for i in range(50)]

    def safe_mean(values):
        valid = [v for v in values if v is not None]
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

    dominant_trait = max(bigfive, key=bigfive.get)

st.subheader("Personality Description & Suitable Organizational Roles")
st.write("Below is the description of your dominant personality trait and some organizational roles that may suit your strengths.")

descriptions = {

"Openness": {
"desc": "You enjoy new experiences and are curious about the world. You appreciate art, adventure, and different ideas. You have a strong imagination and can quickly understand new concepts.",
"Suitable roles": "Product Designer, Researcher, Innovation Manager, Strategy Analyst"
},

"Conscientiousness": {
"desc": "You are disciplined and organized. You like planning things in advance, paying attention to details, and following schedules. You prefer structured and well-organized work.",
"Suitable roles": "Project Manager, Operations Manager, Financial Analyst, Engineer"
},

"Extraversion": {
"desc": "You enjoy being around people and often take the lead in social situations. You are energetic, talkative, and comfortable being the center of attention.",
"Suitable roles": "Sales Manager, Marketing Executive, HR Manager, Public Relations Specialist"
},

"Agreeableness": {
"desc": "You value harmony and good relationships with others. You are kind, helpful, and considerate of people’s feelings, which makes others feel comfortable around you.",
"Suitable roles": "Human Resources Specialist, Counselor, Customer Success Manager, Teacher"
},

"Neuroticism": {
"desc": "You may experience emotions strongly and sometimes feel stressed or worried. You can be sensitive to pressure and may prefer calm environments.",
"Suitable roles": "Quality Assurance Analyst, Risk Analyst, Research Assistant, Data Analyst"
}

}

trait, _ = interpret_personality(bigfive)

st.success(f"Dominant Personality Trait: {trait}")

st.write(descriptions[trait]["desc"])

st.info(descriptions[trait]["roles"])

# ---------------- SAVE TO DATABASE ----------------
def save_to_database(name, job_role, company, experience, age, answers, personality, traits):

    data = {
        "full_name": name,
        "job_role": job_role,
        "company": company,
        "years_experience": experience,
        "age": age,
        "answers": answers,
        "personality_type": personality,
        "extraversion": traits["Extraversion"],
        "neuroticism": traits["Neuroticism"],
        "agreeableness": traits["Agreeableness"],
        "conscientiousness": traits["Conscientiousness"],
        "openness": traits["Openness"]
    }

    supabase.table("personality_assessments").insert(data).execute()

# ---------------- PERSONAL INFO ----------------
st.header("👤 Personal Information")

name = st.text_input("Full Name")
job_role = st.text_input("Current Job Role")
company = st.text_input("Current Company")

experience = st.number_input("Years of Experience", min_value=0.0, step=0.5)
age = st.number_input("Age", min_value=18, max_value=100)

st.divider()

# ---------------- QUESTIONS ----------------
st.header("📝 Personality Questions")

st.write("1 = Strongly Disagree | 5 = Strongly Agree")

all_scores = {}

progress = st.progress(0)

for i, q in enumerate(questions):

    progress.progress((i + 1) / len(questions))

    st.markdown(f"### {i+1}. {q}")

    key = f"question_{i}"

    all_scores[key] = st.radio(
        "",
        [1,2,3,4,5],
        format_func=lambda x: {
            1:"Strongly Disagree",
            2:"Disagree",
            3:"Neutral",
            4:"Agree",
            5:"Strongly Agree"
        }[x],
        key=key,
        index=None
    )

    st.markdown("---")

# ---------------- SUBMIT ----------------
if st.button("Submit Assessment", type="primary"):

    errors = []

    if not name.strip():
        errors.append("Full Name is required")

    if not job_role.strip():
        errors.append("Job Role is required")

    if not company.strip():
        errors.append("Company name is required")

    if experience <= 0:
        errors.append("Experience must be greater than 0")

    if age < 18:
        errors.append("Age must be 18+")

    unanswered = []

    for i in range(50):
        if all_scores.get(f"question_{i}") is None:
            unanswered.append(i+1)

    if unanswered:
        errors.append("All questions must be answered")

    if errors:

        st.error("Please complete required fields")

        for e in errors:
            st.warning(e)

    else:

        bigfive = calculate_big_five(all_scores)

        trait, description = interpret_personality(bigfive)

        personality_percentages = {}

        for trait_name, score in bigfive.items():
            personality_percentages[trait_name] = round((score/5)*100,2)

        save_to_database(
            name,
            job_role,
            company,
            experience,
            age,
            all_scores,
            trait,
            personality_percentages
        )

        st.success("Assessment submitted successfully")

        st.header("👤 Candidate Profile")

        st.write("Name:", name)
        st.write("Company:", company)
        st.write("Role:", job_role)
        st.write("Experience:", experience)
        st.write("Age:", age)

        st.divider()

        st.subheader("Final Personality Result")

        st.success(f"Dominant Personality Trait: {trait}")

        st.write(description)

        st.divider()

        st.subheader("📊 Personality Trait Scores")

        for trait_name, percent in personality_percentages.items():

            st.markdown(f"**{trait_name}: {percent}%**")

            st.progress(percent/100)