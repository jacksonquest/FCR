import streamlit as st
import json
import faiss
import numpy as np
from together import Together
import speech_recognition as sr
from sentence_transformers import SentenceTransformer

def load_knowledge_base(file_path="data/knowledge_base.json"):
    with open(file_path, "r") as f:
        return json.load(f)["knowledge_base"]

def initialize_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

def create_faiss_index(model, knowledge_base):
    full_texts = [
        f"Conversation: {entry['conversation']}\n"
        f"Troubleshooting/Resolution: {entry['troubleshooting_resolution']}\n"
        f"Remarks: {entry['remarks']}\n"
        f"Transferred To: {entry['transferred_to']}" 
        for entry in knowledge_base
    ]
    embeddings = model.encode(full_texts, convert_to_numpy=True)
    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)
    return index, full_texts

def retrieve_relevant_context(query, model, index, knowledge_base):
    query_embedding = model.encode([query], convert_to_numpy=True)
    _, best_match_idx = index.search(query_embedding, 1)
    return knowledge_base[best_match_idx[0][0]]

def generate_response(query, context, client, model_name):
    prompt = f"""
    Based on the following customer service knowledge base entry, analyze the customer query and provide a structured response in a valid JSON format without any additional text or explanation.:

    Conversation: {context['conversation']}
    Troubleshooting/Resolution: {context['troubleshooting_resolution']}
    Remarks: {context['remarks']}
    Transferred To: {context['transferred_to']}

    Customer Query: {query}

    **Instructions:**

    1.  **Troubleshooting Steps:** Analyze the conversation and "Troubleshooting/Resolution" and "Remarks" sections to create a list of troubleshooting actions that can be suggested to the customer, with each line on a new line.
    2.  **Transfer Information:** Use the "Transferred To" section to identify the appropriate department for transfer, if necessary.
    3.  **JSON Output:** Format the response as a JSON object with the following structure:

        {{
          "troubleshooting_steps": "[List of troubleshooting steps, e.g., 1. blah blah, 2. blah blah blah]",
          "transfer_to": "[Department name, e.g., Technical Team]"
        }}

    **Example:**

    {{
      "troubleshooting_steps": "1. Restart your device. 2. Check your internet connection. 3. Reinstall the application.",
      "transfer_to": "Network Support"
    }}

    **Your Response (JSON):**
    """
    
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "system", "content": "You are a helpful customer service assistant."},
                  {"role": "user", "content": prompt}],
    )
    
    return response.choices[0].message.content


def ai_audit(text):
    response = st.session_state['client'].chat.completions.create(
            model=st.session_state['model_name'],
            messages=[
        {
            "role": "user",
            "content": f"""
            Based on the following conversation:
            {text}

            Provide the response as a valid JSON without any extra or additional text or explanation.
            Please provide the following analysis:

            1.  **Summary:** Create a summary of the conversation.
            2.  **Customer Sentiment:** Identify the overall sentiment of the customer (e.g., positive, negative, neutral) Also provide some details..
            3.  **Agent Behavior:** Describe the agent's behavior during the conversation in detail.
            4.  **Agent Ratings (Percentage):** Rate the agent's performance on the following metrics (0-100%):
                * Take ownership:
                * Relate to the customer:
                * Understanding the issue:
                * Set expectations:
                * Think forward:
            5.  **Suggestions/Recommendations:** Provide any suggestions or recommendations for improvement in the advisor's performance in bullets.

            **Output Format:**

            {{
              "summary": "[Summary]",
              "customer_sentiment": "[Sentiment]",
              "agent_behavior": "[Description]",
              "agent_ratings": {{
                "take_ownership": "[Percentage]",
                "relate_to_customer": "[Percentage]",
                "understanding_issue": "[Percentage]",
                "set_expectations": "[Percentage]",
                "think_forward": "[Percentage]"
              }},
              "suggestions": "[Suggestions]"
            }}
            """,
        }
    ],
        )
    
    bot_reply = response.choices[0].message.content
    return bot_reply


def ai_summary(text):
    response = st.session_state['client'].chat.completions.create(
            model=st.session_state['model_name'],
            messages=[
        {
            "role": "user",
            "content": f"""
            Based on the following conversation:
            {text}

            Provide the response as a valid JSON without any extra or additional text or explanation.

            1.  **Summary:** A concise summary of the conversation.
            2.  **Query:** The primary customer query or issue.
            3.  **Key Information:** Extract key information from the conversation and present it as key-value pairs.

            **Output Format:**

            {{
              "summary": "[Summary of the conversation]",
              "query": "[Customer's primary query or issue]",
              "key_information": {{
                "key1": "value1",
                "key2": "value2",
                // ... more key-value pairs as needed
              }}
            }}
            """,
        }
    ],
        )
    
    bot_reply = response.choices[0].message.content
    return bot_reply

def ai_conversation(text):
    response = st.session_state['client'].chat.completions.create(
            model=st.session_state['model_name'],
            messages = [
        {
            "role": "user",
            "content": f"""
            Based on the following conversation:
            {text}

            Please separate the lines spoken by the customer and the agent, and present them in a clear conversation format, with each line on a new line.

            **Output Format:**

            Customer:
            [Customer's line 1]
            Agent:
            [Agent's line 1]
            Customer:
            [Customer's line 2]
            Agent:
            [Agent's line 2]
            ... and so on.
            """,
        }
    ],
        )
    
    bot_reply = response.choices[0].message.content
    return bot_reply



def transcribe_audio(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
    try:
        transcript = recognizer.recognize_google(audio_data)
        return transcript
    except sr.UnknownValueError:
        return "Could not understand the audio."
    except sr.RequestError:
        return "Could not request results; check your internet connection."
    

def save_to_firestore(db, agent_name, timestamp, transcript, summary, customer_query,
                      key_info, ai_solution, escalated, audited_data):
    doc_ref = db.collection("audio_transcriptions").document(agent_name)
    doc_ref.set({}, merge=True)  # Ensure agent exists
    entry_data = {
        "timestamp": timestamp,
        "transcript": transcript,
        "summary": summary,
        "customer_query": customer_query,
        "key_information": key_info,
        "ai_recommended_solution": ai_solution,
        "escalated_to_team": escalated,
        "audited_data": audited_data
    }
    doc_ref.collection("entries").document(timestamp).set(entry_data)
    st.success("✅ Transcript saved to Firestore successfully!")