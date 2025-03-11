import streamlit as st
import json
import faiss
import numpy as np
from together import Together
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