import sys
import os
import subprocess

# 1. Force install Groq if Streamlit lost it
try:
    import groq
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "groq"])

import streamlit as st
import io
from contextlib import redirect_stdout

# 2. Fix the "Folder vs File" naming collision
root_dir = os.path.dirname(os.path.abspath(__file__))
agent_dir = os.path.join(root_dir, "agent")

# By putting the agent directory at the very front of the path, 
# Python will grab the script instead of the folder.
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if agent_dir not in sys.path:
    sys.path.insert(0, agent_dir)

import agent as agent_file

# 3. Hardcode the API Key so the terminal doesn't forget it
# ⚠️ REPLACE THE STRING BELOW WITH YOUR ACTUAL GROQ API KEY ⚠️
os.environ["GROQ_API_KEY"] = "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"

# --- UI Code ---
st.set_page_config(page_title="FinAgent AI", page_icon="📊")
st.title("📊 FinAgent: AI Financial Analyst")
st.markdown("Ask financial questions. The agent automatically routes to structured databases or unstructured document stores.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.text(msg["content"])

if prompt := st.chat_input("E.g., Compare Maybank's 2024 revenue with their credit risk strategy..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Agent is researching..."):
            f_out = io.StringIO()
            with redirect_stdout(f_out):
                # Call the function dynamically
                agent_file.run_financial_agent(prompt)
            raw_output = f_out.getvalue()
            
            # Clean up the output: isolate just the final answer
            if "🤖 FinAgent Response:" in raw_output:
                final_answer = raw_output.split("🤖 FinAgent Response:")[-1].strip()
            else:
                final_answer = raw_output.strip()
            
            # Now Streamlit will render pure Markdown without terminal junk!
            st.markdown(final_answer)
            st.session_state.messages.append({"role": "assistant", "content": final_answer})