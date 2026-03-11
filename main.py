import streamlit as st
import json
import numpy as np
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

st.set_page_config(page_title="Personality Assessment", layout="wide")

# ---------------- SUPABASE ----------------

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

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

    scores=[answers.get(f"question_{i}") for i in range(50)]

    def safe_mean(values):
        valid=[v for v in values if v is not None]
        return np.mean(valid) if valid else 0

    extraversion=safe_mean(scores[0:10])
    neuroticism=safe_mean(scores[10:20])
    agreeableness=safe_mean(scores[20:30])
    conscientiousness=safe_mean(scores[30:40])
    openness=safe_mean(scores[40:50])

    return {
        "Extraversion":extraversion,
        "Neuroticism":neuroticism,
        "Agreeableness":agreeableness,
        "Conscientiousness":conscientiousness,
        "Openness":openness
    }

# ---------------- PERSONALITY INTERPRETATION ----------------

def interpret_personality(bigfive):

    dominant_trait=max(bigfive,key=bigfive.get)

    descriptions={
        "Extraversion":"You are an **Extraverted Personality**. You enjoy social interaction and being around people.",
        "Neuroticism":"You show **High Emotional Sensitivity** and may experience emotions strongly.",
        "Agreeableness":"You are an **Agreeable Personality**. You are cooperative and compassionate.",
        "Conscientiousness":"You are a **Highly Conscientious Personality**. You are organized and responsible.",
        "Openness":"You are an **Open and Creative Personality**. You enjoy exploring new ideas and experiences."
    }

    return dominant_trait,descriptions[dominant_trait]

# ---------------- SAVE TO SUPABASE ----------------

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

# ---------------- UI ----------------

st.title("Personality Evaluation Survey")

st.header("👤 Personal Information")

name=st.text_input("Full Name")
job_role=st.text_input("Current Job Role")
company=st.text_input("Current Company")

col1,col2=st.columns(2)

with col1:
    experience=st.number_input("Years of Experience",min_value=0.0,step=0.5)

with col2:
    age=st.number_input("Age",min_value=18,max_value=100)

st.divider()

# ---------------- QUESTIONS ----------------

st.header("📝 Personality Questions")
st.write("Questions are optional. 1 = Strongly Disagree | 5 = Strongly Agree")

all_scores={}

for i,q in enumerate(questions):

    st.markdown(f"**{i+1}. {q}**")

    key=f"question_{i}"

    all_scores[key]=st.radio(
        "",
        [1,2,3,4,5],
        format_func=lambda x:{
            1:"Strongly Disagree",
            2:"Disagree",
            3:"Neutral",
            4:"Agree",
            5:"Strongly Agree"
        }[x],
        key=key,
        horizontal=True,
        index=None,
        label_visibility="collapsed"
    )

    st.markdown("---")

# ---------------- SUBMIT ----------------
if st.button("Submit Assessment", type="primary"):

    errors = []

    # Personal info validation
    if not name.strip():
        errors.append("Full Name is required")

    if not job_role.strip():
        errors.append("Job Role is required")

    if not company.strip():
        errors.append("Company name is required")

    if experience <= 0:
        errors.append("Years of Experience must be greater than 0")

    if age < 18:
        errors.append("Age must be 18 or above")

    # Question validation
    unanswered = []
    for i in range(50):
        if all_scores.get(f"question_{i}") is None:
            unanswered.append(i + 1)

    if unanswered:
        errors.append(f"You must answer all questions. Missing: {unanswered}")

    # Show errors
    if errors:
        st.error("Please complete all required fields")
        for e in errors:
            st.warning(e)

    else:
        bigfive = calculate_big_five(all_scores)

        trait, description = interpret_personality(bigfive)

        save_to_database(
            name,
            job_role,
            company,
            experience,
            age,
            all_scores,
            trait
        )

        st.success("Assessment submitted successfully")

        st.header("👤 Candidate Profile")

        col1, col2 = st.columns(2)

        with col1:
            st.write("Name:", name)
            st.write("Company:", company)
            st.write("Role:", job_role)

        with col2:
            st.write("Experience:", experience)
            st.write("Age:", age)

        st.divider()

        st.subheader("Final Personality Result")

        st.success(f"Dominant Personality Trait: {trait}")

        st.write(description)

        # -------- Convert to percentage --------

        personality_percentages={}

        for trait_name,score in bigfive.items():
            personality_percentages[trait_name]=round((score/5)*100,2)

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

        col1,col2=st.columns(2)

        with col1:
            st.write("Name:",name)
            st.write("Company:",company)
            st.write("Role:",job_role)

        with col2:
            st.write("Experience:",experience)
            st.write("Age:",age)

        st.divider()

        st.subheader("Final Personality Result")

        st.success(f"Dominant Personality Trait: {trait}")

        st.write(description)

        st.divider()

        st.subheader("📊 Personality Trait Scores")

        for trait_name,percent in personality_percentages.items():
            st.write(f"{trait_name}: {percent}%")
            st.progress(percent/100)