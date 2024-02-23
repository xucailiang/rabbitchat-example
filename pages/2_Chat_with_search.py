import streamlit as st

from langchain.agents import initialize_agent, AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.tools import DuckDuckGoSearchRun
from langchain.agents import load_tools

with st.sidebar:
    openai_api_key = st.text_input(
        "OpenAI API Key", key="langchain_search_api_key_openai", type="password"
    )
    serpapi_api_key = st.text_input("Serp API Key", key="serpapi_api_key", type="password")

    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[![Open with GitHub](https://github.com/codespaces/badge.svg)](https://github.com/xucailiang/rabbitchat-example)"

st.title("🔎 LangChain - Chat with search")

"""
需要使用在线搜索+大模型的检索对话？ 🤝here we are!🤝 

目前我们支持Google和DuckDuckGo的Search查询，并且支持了基于arxiv的论文查询！

赶快来试试吧，eg1:今天星期几？ eg2:给我推荐一篇研究卷积神经元的论文
"""

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi, I'm a chatbot who can search the web. How can I help you?"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="Who won the Women's U.S. Open in 2018?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
    if serpapi_api_key := st.session_state['serpapi_api_key']:
        st.info("正在使用Google Search")
        with st.chat_message("assistant"):
            llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", openai_api_key=openai_api_key, streaming=True)
            tools = load_tools(["serpapi", "llm-math", "arxiv"], llm=llm, serpapi_api_key=serpapi_api_key)
            agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True, handle_parsing_errors=True)
            response = agent.run(prompt, callbacks=[st_cb])
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.write(response)
    else:
        st.info("正在使用DuckDuckGoSearch")
        with st.chat_message("assistant"):
            llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", openai_api_key=openai_api_key, streaming=True)
            search = DuckDuckGoSearchRun(name="Search")
            search_agent = initialize_agent(
                [search], llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, handle_parsing_errors=True
            )
            response = search_agent.run(st.session_state.messages, callbacks=[st_cb])
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.write(response)
