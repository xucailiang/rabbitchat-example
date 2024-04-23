import json
import requests
from openai import OpenAI
import streamlit as st

import config

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    openai_model = st.selectbox("请选择所需模型", ["gpt-3.5-turbo", "gpt-4", 'dall-e-3'], 1, key="openai_model")
    "[![Open with GitHub](https://github.com/codespaces/badge.svg)](https://github.com/xucailiang/rabbitchat-example)"

if openai_model == "dall-e-3":
    st.title("💬 Images Generation")
    st.caption("🚀 使用dall-e-3模型尽情创作吧！")
else:
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
    if openai_model == "dall-e-3":
        data = {
            "model": openai_model,
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024"
        }
        with st.spinner("生成AI回答中..."):
            response = requests.post(config.ONE_API_BASE_URL+'/v1/images/generations',
                                     headers={"Content-Type": "application/json", "Authorization": f"Bearer {openai_api_key}"},
                                     json=data)
            json_resp = response.json()
            print(json_resp)
            try:
                online_url = json_resp["data"][0]["url"]
                revised_prompt = json_resp["data"][0]["revised_prompt"]
                st.image(online_url, caption=revised_prompt)
            except:
                msg = json_resp["error"]
                if msg['code'] == 'content_policy_violation':
                    st.error("内容政策违规，请更换内容后重试！")
                else:
                    st.error(msg)
    else:
        data = {
            "model": openai_model,
            "messages": st.session_state.messages,
            "max_tokens": 300,
            "temperature": 0.2,
            "stream": False
        }
        with st.spinner("生成AI回答中..."):
            response = requests.post(config.ONE_API_BASE_URL+'/v1/chat/completions',
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

    # client = OpenAI(api_key=openai_api_key)
    # st.session_state.messages.append({"role": "user", "content": prompt})
    # st.chat_message("user").write(prompt)
    # with st.spinner("生成AI回答中..."):
    #     response = client.chat.completions.create(model=openai_model, messages=st.session_state.messages)
    #     msg = response.choices[0].message.content
    # st.session_state.messages.append({"role": "assistant", "content": msg})
    # st.chat_message("assistant").write(msg)
