import streamlit as st
import requests

st.set_page_config(page_title="Suncoast AI Agent", page_icon="🤖")

st.title("🤖 Suncoast Customer Support Agent")
st.markdown("---")

# Sidebar for Connection Status
with st.sidebar:
    st.header("System Status")
    st.success("Connected to Mac Mini (M4)")
    st.info("Model: Llama 3.2 (3B)")
    st.info("Engine: LangGraph Orchestrator")

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask about your order (e.g., 'Status of 123')"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call your Dockerized API
    with st.chat_message("assistant"):
        with st.spinner("Agent is thinking..."):
            try:
                # We use localhost:8001 because Streamlit is running on the Mac too
                response = requests.post(
                    "http://100.84.103.76:8001/webhook",
                    json={"message": prompt}
                )
                res_json = response.json()
                answer = res_json.get("ai_resolution", "Error: No response from agent.")
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Connection Error: {e}")
