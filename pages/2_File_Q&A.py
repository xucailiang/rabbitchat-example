import os
from pathlib import Path
import config
import streamlit as st
import logging
from openai import OpenAI
from langchain_core.prompts import ChatPromptTemplate

client = OpenAI(
    api_key=config.MOONSHOT_API_KEY,
    base_url=config.MOONSHOT_API_BASE_URL,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


if config.UPLOAD_OSS:
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

system_prompt = {
                "role": "system",
                "content": "你是 文档阅读机器人，提供上下文阅读总结概括功能，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。"
                           "同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。"
                           "完全基于给定的内容上下文做出回答，如果给定的内容中没有出现问题相关的线索，就根据自身能力回答，并标注是基于大模型自身能力回复。",
            }


def on_submit():
    question = st.session_state.get('input_chat', "")
    do_query(question)


def on_change():
    uploaded_file = st.session_state['uploaded_file']
    uploaded_files(uploaded_file)


def upload_to_aliyunoss(uploaded_file_name, file_tmp_path):
    result = bucket.put_object_from_file(uploaded_file_name, file_tmp_path,
                                         headers={"Content-Disposition": "attachment"})
    logger.info(f"文件{uploaded_file_name}上传成功!Etag:{result.etag},request_id:{result.request_id}")


# with st.sidebar:
#     openai_api_key = st.text_input("Openai API Key", key="openai_api_key", type="password")
#     openai_model = st.selectbox("请选择所需llm模型", ["gpt-4"], 0, key="openai_model")


st.title("📝 File Q&A Chatbot (免费！)")

# 清除旧的对话记录
st.button("清除对话记录", on_click=lambda: st.session_state.pop("messages", None))

uploaded_file = st.file_uploader("Upload an article", type=["pdf", "docx", "doc", "md"],
                                 on_change=on_change, key="uploaded_file")

question = st.chat_input(
    "请输入对话内容，换行请使用Shift+Enter",
    on_submit=on_submit,
    key="input_chat"
)
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if "file_object" not in st.session_state:
    st.error("请先上传文件才能提问噢")


def do_query(question):
    # if not openai_api_key:
    #     st.error("Please add your Openai API key to continue.")
    if 'file_object' not in st.session_state:
        st.error("请先上传文件")
    else:
        st.session_state.messages.append({"role": "user", "content": question})
        file_object = st.session_state['file_object']
        file_content = client.files.content(file_id=file_object.id).text
        # 把它放进请求中
        messages = [system_prompt,
                    {
                        "role": "system",
                        "content": file_content,
                    },
                    {"role": "user", "content": question}]
        print(f">>>messages：{messages}\n\n")

        # client.base_url = config.MOONSHOT_API_BASE_URL
        completion = client.chat.completions.create(
            model=config.MOONSHOT_API_MODEL,
            messages=messages,
            temperature=0.3,
        )
        msg = completion.choices[0].message
        print(f">>>msg: {msg.content}\n\n")
        st.session_state.messages.append({"role": "assistant", "content": msg.content})


def uploaded_files(uploaded_file):
    file_tmp_path = ""
    if uploaded_file:
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
                file_object = client.files.create(file=Path(file_tmp_path), purpose="file-extract")
                st.session_state["file_object"] = file_object

        finally:
            if file_tmp_path:
                os.remove(file_tmp_path)
                logger.info(f"文件删除完成")
    else:
        st.error("请确认openai是否输入正确以及文件是否上传成功")
