import streamlit as st
import json

from utils.helper_functions import ai_audit

st.markdown('<div style="display: flex; justify-content: center;"><h2>AI Audit Assist</h2></div>',unsafe_allow_html=True)


def get_agents():
    return [doc.id for doc in st.session_state['db'].collection("audio_transcriptions").stream()]

def get_entries(agent):
    return [doc.id for doc in st.session_state['db'].collection("audio_transcriptions").document(agent).collection("entries").stream()]

def get_data(agent, entry):
    return st.session_state['db'].collection("audio_transcriptions").document(agent).collection("entries").document(entry).get().to_dict() or {}

agent = st.selectbox("Select Agent", get_agents())
if agent:
    entry = st.selectbox("Select Entry", get_entries(agent))
    if entry:
        st.session_state['audited_data_firestore'] = get_data(agent, entry)

# st.write(st.session_state['audited_data_firestore'])

col1, col2 = st.columns([3,1])
with col1.container(height=150, border=True):
    st.markdown("<span style='color:red; font-weight:bold;'>Summary</span>", unsafe_allow_html=True)
    st.write(st.session_state['audited_data_firestore'].get("summary", "No summary found."))

with col2.container(height=150, border=True):
    st.markdown("<span style='color:red; font-weight:bold;'>Customer Sentiment</span>", unsafe_allow_html=True)
    st.write(st.session_state['audited_data_firestore'].get("audited_data", "No summary found.").get("customer_sentiment", "No summary found."))

with st.container(height=150, border=True):
    st.markdown("<span style='color:red; font-weight:bold;'>Agent Behaviour</span>", unsafe_allow_html=True)
    st.write(st.session_state['audited_data_firestore'].get("audited_data", "No summary found.").get("agent_behavior", "No summary found."))

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric(":red[Take Ownership]", str(st.session_state['audited_data_firestore'].get("audited_data", "No summary found.").get("agent_ratings", "No summary found.").get("take_ownership", "No summary found.")) + " %", border=True)
c2.metric(":red[Relate to Customer]", str(st.session_state['audited_data_firestore'].get("audited_data", "No summary found.").get("agent_ratings", "No summary found.").get("relate_to_customer", "No summary found.")) + " %", border=True)
c3.metric(":red[Understand the Issue]", str(st.session_state['audited_data_firestore'].get("audited_data", "No summary found.").get("agent_ratings", "No summary found.").get("understanding_issue", "No summary found.")) + " %", border=True)
c4.metric(":red[Set Expectations]", str(st.session_state['audited_data_firestore'].get("audited_data", "No summary found.").get("agent_ratings", "No summary found.").get("set_expectations", "No summary found.")) + " %", border=True)
c5.metric(":red[Think Forward]", str(st.session_state['audited_data_firestore'].get("audited_data", "No summary found.").get("agent_ratings", "No summary found.").get("think_forward", "No summary found.")) + " %", border=True)

with st.container(height=250, border=True):
    st.markdown("<span style='color:red; font-weight:bold;'>Suggestions</span>", unsafe_allow_html=True)
    # st.write(audited_data.get("suggestions", "No summary found."))
    for line in st.session_state['audited_data_firestore'].get("audited_data", "No summary found.").get("suggestions", "No summary found."):
        st.write(line)

