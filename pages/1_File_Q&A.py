import os
import streamlit as st
from langchain.chat_models import ChatOpenAI
import logging
from config import *
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

os.environ["OPENAI_API_BASE"] = 'https://gateway.ai.cloudflare.com/v1/92a11adae8e8640ee190fde50328431e/open-ai/openai'

import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
from config import EMBEDDING_MODEL

if UPLOAD_OSS:
    import oss2
    access_key_id = config.OSS_ACCESS_KEY_ID
    access_key_secret = config.OSS_ACCESS_KEY_SECRET
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, config.ENDPOINT, config.BUCKET_NAME)

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB


prompt = ChatPromptTemplate.from_template("""
                      请用中文回答。
                      我将会为你提供一些关于问题的已知信息，请完全根据我所提供的已知信息作为回答的依据，注意不能捏造虚假答案，并注意回答语句的流畅以及逻辑通顺，不能前后矛盾。如果无法回答，请说 "抱歉，暂时无法找到答案"。
                      若我提供的已知信息为空或者无效，可以根据自己的知识回答，但是必须在回答的句子前加上这段话:"知识库无法匹配到有效信息，以下为大模型自身能力回答\n\n"。
                       <已知信息>
                        {context}
                        </已知信息>
                        Question: {input}
                  """)


def on_submit():
    vector_store = st.session_state.get('vector_store', "")
    question = st.session_state.get('input_chat', "")
    do_query(vector_store, question)


def on_change():
    uploaded_file = st.session_state['uploaded_file']
    uploaded_files(uploaded_file)


def get_embeddings_model():
    logger.info(f"embedding模型: {embedding_model}")
    print(f"embedding模型: {embedding_model}")
    if embedding_model == "BAAI/bge-small-zh-v1.5":
        from langchain.embeddings import HuggingFaceBgeEmbeddings
        embeddings = HuggingFaceBgeEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'auto'},
            encode_kwargs={'normalize_embeddings': True},
            query_instruction="为这个句子生成表示以用于检索相关文章："
        )
    else:
        embeddings = OpenAIEmbeddings(model=embedding_model, openai_api_key=openai_api_key)
    return embeddings


def upload_to_aliyunoss(uploaded_file_name, file_tmp_path):
    result = bucket.put_object_from_file(uploaded_file_name, file_tmp_path,
                                         headers={"Content-Disposition": "attachment"})
    logger.info(f"文件{uploaded_file_name}上传成功!Etag:{result.etag},request_id:{result.request_id}")


with st.sidebar:
    openai_api_key = st.text_input("Openai API Key", key="openai_api_key", type="password")
    openai_model = st.selectbox("请选择所需llm模型", ["gpt-4"], 0, key="openai_model")
    embedding_model = st.selectbox("请选择所需embedding模型", EMBEDDING_MODEL, 0, key="embedding_model")
    "[![Open with GitHub](https://github.com/codespaces/badge.svg)](https://github.com/xucailiang/rabbitchat-example)"


st.title("📝 File Q&A with Anthropic")

uploaded_file = st.file_uploader("Upload an article", type=("pdf"), on_change=on_change, key="uploaded_file", disabled=not openai_api_key)

question = st.chat_input(
    "请输入对话内容，换行请使用Shift+Enter",
    on_submit=on_submit,
    key="input_chat"
)
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if "vector_store" not in st.session_state:
    st.error("请先上传文件才能提问噢")


if uploaded_file and question and not openai_api_key:
    st.info("Please add your Anthropic API key to continue.")


def do_query(vector_store, question):
    if not openai_api_key:
        st.error("Please add your Openai API key to continue.")
    elif vector_store:
        st.session_state.messages.append({"role": "user", "content": question})
        retriever = vector_store.as_retriever()
        llm = ChatOpenAI(model=openai_model, openai_api_key=openai_api_key)
        document_chain = create_stuff_documents_chain(llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        print(f"question: {question}")
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


def uploaded_files(uploaded_file):
    file_tmp_path = ""
    if openai_api_key and uploaded_file:
        try:
            # 检查文件大小是否超过限制
            if uploaded_file.size > MAX_FILE_SIZE_BYTES:
                st.error(f"上传的文件超过最大限制（{MAX_FILE_SIZE_BYTES / (1024 * 1024)} MB）")
                return
            else:
                uploaded_file_name = uploaded_file.name
                current_directory = os.getcwd()
                file_tmp_path = os.path.join(current_directory, uploaded_file_name)

                with open(file_tmp_path, "wb") as f:
                    f.write(uploaded_file.read())
                if UPLOAD_OSS:
                    upload_to_aliyunoss(uploaded_file_name, file_tmp_path)

                embeddings = get_embeddings_model()
                docs = PyMuPDFLoader(file_tmp_path).load()
                text_splitter = RecursiveCharacterTextSplitter()
                documents = text_splitter.split_documents(docs)
                vector_store = FAISS.from_documents(documents, embeddings)
                st.session_state['vector_store'] = vector_store
                st.session_state.pop("uploaded_file") # 如果不手动清理，第二次上传文件就会报错

                # docs = PyMuPDFLoader(file_tmp_path).load()
                # parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
                # child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)
                # # todo: 多用户可能会产生多数据库的问题，需要及时销毁。
                # vector_store = Chroma(collection_name="knowledge", embedding_function=embeddings)
                # # 创建内存存储对象
                # store = InMemoryStore()
                # retriever = ParentDocumentRetriever(
                #     vectorstore=vector_store,
                #     docstore=store,
                #     child_splitter=child_splitter,
                #     parent_splitter=parent_splitter,
                # )
                # retriever.add_documents(docs)

        finally:
            if file_tmp_path:
                os.remove(file_tmp_path)
                logger.info(f"文件删除完成")
    else:
        st.error("请确认openai是否输入正确")
