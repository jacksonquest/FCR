import streamlit as st
import json

st.markdown('<div style="display: flex; justify-content: center;"><h2>Audit Assist</h2></div>',unsafe_allow_html=True)

def ai_audit(text):
    response = st.session_state['client'].chat.completions.create(
            model=st.session_state['model_name'],
            messages=[
        {
            "role": "user",
            "content": f"""
            Based on the following conversation:
            {text}

            Provide the response as a valid JSON without any additional text or explanation.
            Please provide the following analysis:

            1.  **Summary:** Create a concise summary of the conversation.
            2.  **Customer Sentiment:** Identify the overall sentiment of the customer (e.g., positive, negative, neutral).
            3.  **Agent Behavior:** Describe the agent's behavior during the conversation.
            4.  **Agent Ratings (Percentage):** Rate the agent's performance on the following metrics (0-100%):
                * Take ownership:
                * Relate to the customer:
                * Understanding the issue:
                * Set expectations:
                * Think forward:
            5.  **Suggestions/Recommendations:** Provide any suggestions or recommendations for improvement in the advisor's performance.

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


st.session_state['audit_report'] = ai_audit(st.session_state['processed_transcript'])
cleaned_response = st.session_state['audit_report'].split("{", 1)[-1]  # Remove any extra text before `{`
cleaned_response = "{" + cleaned_response  # Add `{` back
audited_data = json.loads(cleaned_response)

col1, col2 = st.columns([3,1])
with col1.container(height=150, border=True):
    st.markdown("<span style='color:red; font-weight:bold;'>Summary</span>", unsafe_allow_html=True)
    st.write(audited_data.get("summary", "No summary found."))

with col2.container(height=150, border=True):
    st.markdown("<span style='color:red; font-weight:bold;'>Customer Sentiment</span>", unsafe_allow_html=True)
    st.write(audited_data.get("customer_sentiment", "No summary found."))

with st.container(height=150, border=True):
    st.markdown("<span style='color:red; font-weight:bold;'>Agent Behaviour</span>", unsafe_allow_html=True)
    st.write(audited_data.get("agent_behavior", "No summary found."))

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric(":red[Take Ownership]", str(audited_data.get("agent_ratings", "No summary found.").get("take_ownership", "No summary found.")) + " %", border=True)
c2.metric(":red[Relate to Customer]", str(audited_data.get("agent_ratings", "No summary found.").get("relate_to_customer", "No summary found.")) + " %", border=True)
c3.metric(":red[Understand the Issue]", str(audited_data.get("agent_ratings", "No summary found.").get("understanding_issue", "No summary found.")) + " %", border=True)
c4.metric(":red[Set Expectations]", str(audited_data.get("agent_ratings", "No summary found.").get("set_expectations", "No summary found.")) + " %", border=True)
c5.metric(":red[Think Forward]", str(audited_data.get("agent_ratings", "No summary found.").get("think_forward", "No summary found.")) + " %", border=True)

with st.container(height=150, border=True):
    st.markdown("<span style='color:red; font-weight:bold;'>Suggestions</span>", unsafe_allow_html=True)
    st.write(audited_data.get("suggestions", "No summary found."))

