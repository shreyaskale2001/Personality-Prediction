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
"I am the life of the party","I don't talk a lot","I feel comfortable around people","I keep in the background","I start conversations","I have little to say","I talk to a lot of different people at parties","I don't like to draw attention to myself","I don't mind being the center of attention","I am quiet around strangers",
"I get stressed out easily","I am relaxed most of the time","I worry about things","I seldom feel blue","I am easily disturbed","I get upset easily","I change my mood a lot","I have frequent mood swings","I get irritated easily","I often feel blue",
"I feel little concern for others","I am interested in people","I insult people","I sympathize with others' feelings","I am not interested in other people's problems","I have a soft heart","I am not really interested in others","I take time out for others","I feel others' emotions","I make people feel at ease",
"I am always prepared","I leave my belongings around","I pay attention to details","I make a mess of things","I get chores done right away","I often forget to put things back in their proper place","I like order","I shirk my duties","I follow a schedule","I am exacting in my work",
"I have a rich vocabulary","I have difficulty understanding abstract ideas","I have a vivid imagination","I am not interested in abstract ideas","I have excellent ideas","I do not have a good imagination","I am quick to understand things","I use difficult words","I spend time reflecting on things","I am full of ideas"
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

st.title("🧠 Personality & Profile Assessment")

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

if st.button("Submit Assessment",type="primary"):

    errors=[]

    if not name.strip():
        errors.append("Name required")

    if not job_role.strip():
        errors.append("Job role required")

    if not company.strip():
        errors.append("Company required")

    if experience<=0:
        errors.append("Enter experience")

    if age<18:
        errors.append("Age must be 18+")

    if errors:

        st.error("Please complete required fields")

        for e in errors:
            st.warning(e)

    else:

        bigfive=calculate_big_five(all_scores)

        trait,description=interpret_personality(bigfive)

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

        st.subheader("🧠 Final Personality Result")

        st.success(f"Dominant Personality Trait: {trait}")

        st.write(description)

        st.divider()

        st.subheader("📊 Personality Trait Scores")

        for trait_name,percent in personality_percentages.items():
            st.write(f"{trait_name}: {percent}%")
            st.progress(percent/100)