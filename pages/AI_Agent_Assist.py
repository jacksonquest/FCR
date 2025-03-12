import streamlit as st
from together import Together
import os
import json
from datetime import datetime

from utils.helper_functions import *

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

st.markdown('<div style="display: flex; justify-content: center;"><h2>AI Agent Assist</h2></div>',unsafe_allow_html=True)

TOGETHER_API_KEY = st.secrets["TOGETHER_API_KEY"]

if 'together_api_key' not in st.session_state:
    st.session_state['together_api_key'] = TOGETHER_API_KEY

st.session_state['client'] = Together(api_key=st.session_state['together_api_key'])
st.session_state['model_name'] = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"


# Structure
rec_col1, rec_col2 = st.columns(2)
uploaded_file = rec_col1.file_uploader("Upload an audio file", type=["mp3", "wav", "m4a"])
audio_value = rec_col2.audio_input("Get Live Conversation")

if uploaded_file is not None or audio_value is not None:
    try:
        file_path = os.path.join("temp_audio", uploaded_file.name)
        os.makedirs("temp_audio", exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    except:
        file_path = audio_value

    with st.expander("🎧 Listen to Audio File"):
        st.audio(file_path)

    if st.button("Analyze", use_container_width=True, type='primary'):
        col1,col2 = st.columns([1,2])
        with col1.expander("Raw Transcript"):
            st.session_state['transcript'] = transcribe_audio(file_path)
            # st.session_state['transcript'] ="""
            # hi I am Abhishek I am calling about my broadband connection I got the device installed like two days ago but the signal light on the router is still red I need to know when it will be activated good morning Abhishek thank you for calling let me just get your details ok I have your details now thank you account here I understand you are having trouble with your broadband connection and the signal light Steel red deeply apologize for the inconvenience let's first try some basic troubleshooting to see if we can resolve this quickly ok what do I need to do ok so first could you please confirm that all the cables are securely plucked into the modem and the wall socket sometimes you know a loose connection can cause this issue but I will check now ok they all seem to be plugged in tightly alright next please try restarting your modem unlock the power adaptor from the modem for about 30 seconds and then plug it back in ok just give me some time I will do that still red nothing has changed ok I understand sir thank you for trying the troubleshooting steps it appears that might be a more Complex issue with the connection to resolve this I need to calculate this to a technical team they have the tools and expertise to diagnose and fix the problem ok but how long will it take I need the internet for work I understand I will create a ticket for a technical team immediately and they will privatize it they will contact you within 24 hours to schedule a visit and guide you through the further steps ok thank you is there anything I can help you with know that is all thanks a lot for the quick response appreciate your patience have a good day
            # """
            st.write(st.session_state['transcript'])

        with col2.expander("Processed Transcript"):
            st.session_state['processed_transcript'] = ai_conversation(st.session_state['transcript'])
            st.write(st.session_state['processed_transcript'])

        st.session_state['summary'] = ai_summary(st.session_state['transcript'])
        cleaned_response = st.session_state['summary'].split("{", 1)[-1]  # Remove any extra text before `{`
        cleaned_response = "{" + cleaned_response  # Add `{` back
        summary_data = json.loads(cleaned_response)
        
        col1, col2 = st.columns(2)
        with col1.container(height=200, border=True):
            st.markdown("<span style='color:red; font-weight:bold;'>Summary</span>", unsafe_allow_html=True)
            st.write(summary_data.get("summary", "No summary found."))

        with col1.container(height=100, border=True):
            st.markdown("<span style='color:red; font-weight:bold;'>Customer Query</span>", unsafe_allow_html=True)
            st.write(summary_data.get("query", "No query found."))

        with col2.container(height=315, border=True):
            st.markdown("<span style='color:red; font-weight:bold;'>Key Information</span>", unsafe_allow_html=True)
            st.write(summary_data.get("key_information", {}))

        col1, col2 = st.columns([2,1])
        with col1.container(height=150, border=True):
            st.markdown("<span style='color:red; font-weight:bold;'>AI Recommended Solution</span>", unsafe_allow_html=True)
            knowledge_base = load_knowledge_base()
            model = initialize_model()
            index, _ = create_faiss_index(model, knowledge_base)
            context = retrieve_relevant_context(summary_data.get("query", "No query found."), model, index, knowledge_base)
            response = generate_response(summary_data.get("query", "No query found."), context, st.session_state['client'], st.session_state['model_name'])
            cleaned_response = response.split("{", 1)[-1]  # Remove any extra text before `{`
            cleaned_response = "{" + cleaned_response  # Add `{` back
            solution = json.loads(cleaned_response)
            st.write(solution.get("troubleshooting_steps", {}))


        with col2.container(height=150, border=True):
            st.markdown("<span style='color:red; font-weight:bold;'>Escalate To:</span>", unsafe_allow_html=True)
            st.write(solution.get("transfer_to", {}))

        st.session_state['audit_report'] = ai_audit(st.session_state['processed_transcript'])
        cleaned_response = st.session_state['audit_report'].split("{", 1)[-1]  # Remove any extra text before `{`
        cleaned_response = "{" + cleaned_response  # Add `{` back
        audited_data = json.loads(cleaned_response)
        st.session_state['audited_data'] = audited_data


        save_to_firestore(st.session_state['db'], st.session_state['agent_name'], datetime.now().isoformat(), st.session_state['processed_transcript'], 
                        summary_data.get("summary", "No summary found."), summary_data.get("query", "No query found."),
                        summary_data.get("key_information", {}), solution.get("troubleshooting_steps", {}), 
                        solution.get("transfer_to", {}), st.session_state['audited_data'])


