import json

import requests
import streamlit as st
from langchain_core.prompts import PromptTemplate

import config

common_languages = [
    "中文", "英语", "西班牙语", "印地语", "阿拉伯语",
    "孟加拉语", "葡萄牙语", "俄语", "日语",
    "德语", "法语", "越南语", "韩语"
]

default_prompt = PromptTemplate.from_template("""
    你是一个专业的翻译官，请根据给定的内容进行翻译，在翻译过程中对于行业内的术语要翻译准确，对于数学标点符号无法翻译的应当适当保留，翻译后的内容应该符合语法规范，表达清晰，不要出现歧义。
    对于无法翻译的内容，可以使用括号标注,直接回答翻译结果。
    {human_input_prompt}
    一步一步完成翻译，翻译过程中要保持专注，不要分心。将目标内容翻译成{target_language}。
    请直接回答翻译结果，不要复述我的提示。目标内容:{input}
""")

with st.sidebar:
    api_key = st.text_input("API Key", key="api_key", type="password")
    openai_model = st.selectbox("请选择所需模型", ["gpt-4"], 0, key="openai_model")
    # human_input_prompt
    human_input_prompt = st.text_area("自定义输入框", height=150, max_chars=200, key="human_input_prompt", placeholder="指定词语的翻译，例如：请将所有的normalization翻译成归一化。")
    # 定义一个下拉框
    target_language = st.selectbox("请选择要翻译的目标语言", common_languages, 0, key="target_language")


st.title("💬 Translate")
st.caption("🚀 I am an AI translator")

st.button("清除对话记录", on_click=lambda: st.session_state.pop("messages", None))

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not api_key or not prompt:
        st.info("API KEY AND PROMPT ARE REQUIRED!")
        st.stop()
    messages_list = list(st.session_state.messages)
    target_prompt = default_prompt.format(human_input_prompt=st.session_state.human_input_prompt,
                                          target_language=target_language, input=prompt)
    messages_list.append({"role": "user", "content": target_prompt})
    print(f"target_prompt: {target_prompt}")
    print(f"messages_list: {messages_list}")
    data = {
        "model": openai_model,
        "messages": messages_list,
        "max_tokens": 300,
        "temperature": 0.2,
        "stream": False
    }
    with st.spinner("生成AI回答中..."):
        response = requests.post(config.ONE_API_BASE_URL + '/v1/chat/completions',
                                 headers={"Content-Type": "application/json",
                                          "Authorization": f"Bearer {api_key}"}, json=data)
        json_content = json.loads(response.content)
        print(f"ai output:{json_content}")
        try:
            ai_output = response.json()["choices"][0]["message"]["content"]
        except:
            ai_output = json_content["error"]
    st.session_state.messages.append({"role": "assistant", "content": ai_output})
    st.chat_message("assistant").write(ai_output)
