import streamlit as st
import requests

st.set_page_config(page_title="Suncoast AI Agent", page_icon="☀️")
st.title("☀️ Suncoast Voice-Enabled Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about orders, inventory, or policies..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call Backend (Tailscale IP)
    response = requests.post("http://100.84.103.76:8001/webhook", json={"message": prompt})
    answer = response.json()["ai_resolution"]

    with st.chat_message("assistant"):
        st.markdown(answer)
        # BROWSER VOICE TRIGGER
        st.components.v1.html(f"""
            <script>
                var msg = new SpeechSynthesisUtterance("{answer.replace('"', "'")}");
                window.speechSynthesis.speak(msg);
            </script>
        """, height=0)
    
    st.session_state.messages.append({"role": "assistant", "content": answer})
