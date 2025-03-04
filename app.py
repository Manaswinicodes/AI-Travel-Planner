import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
import time
import random
import re

# Set up API key
GEMINI_API_KEY = "AIzaSyDPqddRi-U9PM2p2ZIPappjnwVtjNSZDoM"

st.set_page_config(page_title="AI Travel Planner", page_icon="✈️", layout="wide")
st.title("🌍 AI Travel Planner ✈️")
st.write("Plan your trip with cost estimates, travel details, and food recommendations!")


col1, col2 = st.columns(2)
with col1:
    source = st.text_input("📍 Enter Source Location:", help="Start typing and select a location")
with col2:
    destination = st.text_input("📍 Enter Destination:", help="Start typing and select a location")

budget = st.number_input("💰 Budget (in your currency):", min_value=0, step=100)
travel_time = st.selectbox("⏰ Preferred Travel Time:", ["🌅 Morning", "🌞 Afternoon", "🌆 Evening", "🌙 Night", "Anytime"])
num_travelers = st.number_input("👥 Number of Travelers:", min_value=1, step=1)
preferred_mode = st.multiselect("🚗 Preferred Mode of Transport:", ["🏍️ Bike", "🚖 Cab", "🚌 Bus", "🚆 Train", "✈️ Flight", "Any"])

def clean_markdown(text):
    """Remove markdown formatting like ** for bold"""
    # Remove bold formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # Remove other markdown if needed
    text = re.sub(r'\*(.*?)\*', r'\1', text)  # Remove italics
    return text

def format_travel_option(option_text):
    """Clean and format a travel option for display"""
    cleaned_text = clean_markdown(option_text)
    # Make sure there's content in the cleaned text
    if cleaned_text.strip():
        parts = cleaned_text.split(':')
        if len(parts) > 1:
            return parts[0], ': '.join(parts[1:])
        return cleaned_text, ""
    return "Travel Option", "Details not available"

if st.button("🛫 Plan My Trip"):
    if source and destination:
        with st.spinner("🔄 Fetching travel options and food recommendations...."):
            time.sleep(2)  # Simulating loading time

            chat_template = ChatPromptTemplate(messages=[
                ("system", """You are an AI-Powered Travel Planner. Provide travel options (bike, cab, bus, train, flight)
                including estimated cost, travel time, distance, and food recommendations along the way.
                Format each option with a clear title followed by details. Do not use markdown formatting like bold (**) 
                in your response."""),
                ("human", """
                Find travel options from {source} to {destination}.
                Budget: {budget}, Travel Time: {travel_time},
                Number of Travelers: {num_travelers}, Preferred Modes: {preferred_mode}.
                """)
            ])

            chat_model = ChatGoogleGenerativeAI(api_key=GEMINI_API_KEY, model="gemini-2.0-flash-exp")
            parser = StrOutputParser()
            chain = chat_template | chat_model | parser

            raw_input = {
                "source": source,
                "destination": destination,
                "budget": budget,
                "travel_time": travel_time,
                "num_travelers": num_travelers,
                "preferred_mode": ", ".join(preferred_mode) if preferred_mode else "Any"
            }
            response = chain.invoke(raw_input)
            
            # Clean the response
            response = clean_markdown(response)

            st.success("✅ Travel Options:")
            
            # Split the response by newlines, but filter out empty lines
            travel_modes = [line for line in response.split("\n") if line.strip()]
            
            for mode in travel_modes:
                # Skip lines that don't have enough content
                if len(mode.strip()) < 5:
                    continue
                    
                title, details = format_travel_option(mode)
                
                with st.expander(f"📌 {title}"):
                    if details:
                        st.markdown(details)
                    else:
                        st.markdown(title)  # If no details, just show the title
                    st.progress(random.uniform(0.5, 1)) 

            # Food recommendations section
            st.subheader("🍔 Recommended Food on the Route")
            sample_foods = ["🍕 Pizza", "🍛 Biryani", "🌮 Tacos", "🍜 Noodles", "🥗 Salad"]
            st.write("Try these delicacies during your trip:")
            st.markdown(" - " + "\n - ".join(random.sample(sample_foods, 3)))
    else:
        st.warning("⚠️ Please enter both source and destination locations.")