import os

import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    SECRETS_KEY_LIST = st.secrets["SECRETS_KEY_LIST"]
except:
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    SECRETS_KEY_LIST = os.environ.get('SECRETS_KEY_LIST')

common_languages = [
    "中文", "英语", "西班牙语", "印地语", "阿拉伯语",
    "孟加拉语", "葡萄牙语", "俄语", "日语",
    "德语", "法语", "越南语", "韩语"
]

default_prompt = ChatPromptTemplate.from_template("""
    你是一个优秀的翻译官，请根据给定的内容进行翻译，在翻译过程中对于行业内的术语要翻译准确，对于数学标点符号无法翻译的应当适当保留，翻译后的内容应该符合语法规范，表达清晰，不要出现歧义。
    对于无法翻译的内容，可以使用括号标注原文,直接回答翻译结果即可。
    {human_input_prompt}
    一步一步完成翻译，翻译过程中要保持专注，不要分心。将目标内容翻译成{target_language}。
    现在开始翻译以下目标内容：{input}
""")


with st.sidebar:
    api_key = st.text_input("API Key", key="chatbot_api_key", type="password")
    # human_input_prompt
    human_input_prompt = st.text_area("自定义输入框", height=150, max_chars=200, key="human_input_prompt", placeholder="指定词语的翻译，例如：请将所有的normalization翻译成归一化。")
    # 定义一个下拉框
    target_language = st.selectbox("请选择要翻译的目标语言", common_languages, 0, key="target_language")

    "[![Open with GitHub](https://github.com/codespaces/badge.svg)](https://github.com/xucailiang/rabbitchat-example)"

st.title("💬 Translate")
st.caption("🚀 I am an AI translator")

# 清除旧的对话记录
st.button("清除对话记录", on_click=lambda: st.session_state.pop("messages", None))

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not api_key or api_key not in SECRETS_KEY_LIST:
        st.info("API KEY ERROR!!")
        st.stop()
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    model = ChatGoogleGenerativeAI(model="gemini-pro",
                                   temperature=0.2, google_api_key=GOOGLE_API_KEY, streaming=True)
    with st.spinner("生成AI回答中..."):
        chain = default_prompt | model | StrOutputParser()
        response = chain.invoke({"target_language": target_language, "input": prompt, "human_input_prompt": human_input_prompt})
    # st.success("完成！")
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)

    # client = OpenAI(api_key=openai_api_key)
    # st.session_state.messages.append({"role": "user", "content": prompt})
    # st.chat_message("user").write(prompt)
    # response = client.chat.completions.create(model=openai_model, messages=st.session_state.messages)
    # msg = response.choices[0].message.content
    # st.session_state.messages.append({"role": "assistant", "content": msg})
    # st.chat_message("assistant").write(msg)
