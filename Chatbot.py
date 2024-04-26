import json
import requests
import streamlit as st
import config


def model_on_change():
    st.session_state.pop("messages", None)


with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    openai_model = st.selectbox("请选择所需模型", ["gpt-3.5-turbo-1106", "gpt-4"], 1, key="openai_model",
                                on_change=model_on_change)

st.title("💬 Chatbot")
st.caption("🚀 A streamlit chatbot powered by OpenAI LLM")


st.button("清除对话记录", on_click=lambda: st.session_state.pop("messages", None))

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    data = {
        "model": openai_model,
        "messages": st.session_state.messages,
        "max_tokens": 300,
        "temperature": 0.2,
        "stream": False
    }
    with st.spinner("生成AI回答中..."):
        response = requests.post(config.ONE_API_BASE_URL + '/v1/chat/completions',
                                 headers={"Content-Type": "application/json",
                                          "Authorization": f"Bearer {openai_api_key}"}, json=data)
        json_content = json.loads(response.content)
        print(json_content)
        try:
            msg = response.json()["choices"][0]["message"]["content"]
        except:
            msg = json_content["error"]
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
