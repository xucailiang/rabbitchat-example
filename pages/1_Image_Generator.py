import requests
import streamlit as st
import config

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    openai_model = st.selectbox("请选择所需模型", ['dall-e-3'], 0, key="openai_model")
    image_size = st.selectbox("图像大小", ["1024x1024", '1024x1792', '1792x1024'], 0, key="image_size")

st.title("💬 Images Generation")
st.caption("🚀 使用dall-e-3模型尽情创作吧！\n\n ⚠️注意：图像地址会在一小时后过期噢😯")

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
        "prompt": prompt,
        "n": 1,
        "size": image_size
    }
    with st.spinner("图像创作中..."):
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
            st.error(msg)

