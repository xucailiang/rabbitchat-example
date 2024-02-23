import os
import streamlit as st
from langchain.chat_models import ChatOpenAI
import oss2
import logging
from config import *
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
from config import EMBEDDING_MODEL

if UPLOAD_OSS:
    access_key_id = config.OSS_ACCESS_KEY_ID
    access_key_secret = config.OSS_ACCESS_KEY_SECRET
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, config.ENDPOINT, config.BUCKET_NAME)

MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024  # 2MB

upload_file_status = st.session_state.get("uploaded_file", "")

vector = ""

prompt = ChatPromptTemplate.from_template("""
                      请用中文回答。
                      我将会为你提供一些关于问题的已知信息，请根据我所提供的已知信息作为回答的依据，注意不能捏造虚假答案，并注意回答语句的流畅以及逻辑通顺，不能前后矛盾。如果无法回答，请说 "抱歉，暂时无法找到答案"。
                      若我系统的已知信息为空或者无效，请在回答的句子前加上这段消息:"知识库无法匹配到有效信息以下为大模型自身能力回答\n\n
                       <已知信息>
                        {context}
                        </已知信息>
                        Question: {input}
                  """)


def on_submit():
    user_input = st.session_state['input_chat']
    vector = st.session_state.get('vector', "")
    openai_api_key = st.session_state.get('openai_api_key')
    do_query(user_input, vector, openai_api_key)


def on_change():
    uploaded_file = st.session_state['uploaded_file']
    openai_api_key = st.session_state['openai_api_key']
    embedding_model = st.session_state['embedding_model']
    uploaded_files(uploaded_file,openai_api_key,embedding_model)


with st.sidebar:
    openai_api_key = st.text_input("Openai API Key", key="openai_api_key", type="password")
    openai_model = st.selectbox("请选择所需llm模型", ["gpt-4"], 0, key="openai_model")
    embedding_model = st.selectbox("请选择所需embedding模型", EMBEDDING_MODEL, 0, key="embedding_model")
    "[![Open with GitHub](https://github.com/codespaces/badge.svg)](https://github.com/xucailiang/rabbitchat)"


st.title("📝 File Q&A with Anthropic")
uploaded_file = st.file_uploader("Upload an article", type=("pdf"), on_change=on_change, key="uploaded_file")
question = st.chat_input(
    "请输入对话内容，换行请使用Shift+Enter",
    on_submit=on_submit,
    key="input_chat"
)
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if "vector" not in st.session_state:
    st.error("请先上传文件才能提问噢")


if uploaded_file and question and not openai_api_key:
    st.info("Please add your Anthropic API key to continue.")


def do_query(question, vector, openai_api_key):
    if not openai_api_key:
        st.error("Please add your Openai API key to continue.")
    elif vector:
        st.session_state.messages.append({"role": "user", "content": question})
        retriever = vector.as_retriever()
        llm = ChatOpenAI(model=openai_model, openai_api_key=openai_api_key)
        document_chain = create_stuff_documents_chain(llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        response = retrieval_chain.invoke({"input": question})
        res_context = ""
        for document in response['context']:
            metadata = document.metadata
            source = metadata['source']
            page = metadata['page']
            res_context += f"> {source} 第{page}页 \n\n"
        st.session_state.messages.append({"role": "assistant", "content": f"{response['answer']}"
                                                                          f"\n\n答案出自 \n\n"
                                                                          f"{res_context}"})


def uploaded_files(uploaded_file, openai_api_key, embedding_model):
    uploaded_file_name = uploaded_file.name
    current_directory = os.getcwd()
    file_tmp_path = os.path.join(current_directory, uploaded_file_name)
    if openai_api_key:
        try:
            # 检查文件大小是否超过限制
            if uploaded_file.size > MAX_FILE_SIZE_BYTES:
                st.error(f"上传的文件超过最大限制（{MAX_FILE_SIZE_BYTES / (1024 * 1024)} MB）", timeout=3)
            else:
                with open(file_tmp_path, "wb") as f:
                    f.write(uploaded_file.read())
                if UPLOAD_OSS:
                    result = bucket.put_object_from_file(uploaded_file_name, file_tmp_path, headers={"Content-Disposition": "attachment"})
                    logger.info(f"文件{uploaded_file_name}上传成功!Etag:{result.etag},request_id:{result.request_id}")
                embeddings = OpenAIEmbeddings(model=embedding_model, openai_api_key=openai_api_key)
                docs = PyMuPDFLoader(file_tmp_path).load()
                text_splitter = RecursiveCharacterTextSplitter()
                documents = text_splitter.split_documents(docs)
                vector = FAISS.from_documents(documents, embeddings)
                st.session_state['vector'] = vector
        finally:
            os.remove(file_tmp_path)
            logger.info(f"文件删除完成")
    else:
        st.error("请确认openai是否输入正确")
