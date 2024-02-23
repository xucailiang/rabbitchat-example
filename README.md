![RabbitChatv2.png](https://cdn.nlark.com/yuque/0/2024/png/33530968/1708586265466-792e6e49-76bd-48fe-a353-56151cb56158.png#averageHue=%23fefefe&clientId=ubdd0a957-4a4a-4&from=paste&height=236&id=ubcda15e2&originHeight=236&originWidth=890&originalType=binary&ratio=1&rotation=0&showTitle=false&size=38444&status=done&style=shadow&taskId=u34dc6ee6-5be0-4669-8cd0-5091f530369&title=&width=890)

在线体验地址：https://dcct2v5ghezpqttymwbps8.streamlit.app/

文件问答由于需要先初始化数据库连接，在线体验处于不可用状态。


欢迎来到最最最最简洁版的大模型对话/文件问答项目，以下是启动方式：
> 注意，使用启动本项目前需要把数据库、openai key 阿里云oss内容准备好。

```python
# 初始化之前请先修改config，换成你自己的内容

pip install -r requirements.txt

python init_vector_db.py # 初始化数据库

streamlit run Chatbot.py # 启动
```

什么？你电脑没得GPU？

没事，本项目的嵌入、向量数据库和模型问答均来自online api，无需本地跑模型.

什么？你连CPU都是i3的老古董？？

没事，本项目的嵌入、向量数据库和模型问答均来自online api，CPU和大内存统统不需要。

什么？你是个赶时髦学习大模型的小白？？？

没事，本项目集成llm+oss+Langchain+streamlit+向量数据库，用最简单的方式打通学习的大门。

前端框架：[https://streamlit.io/](https://streamlit.io/)

阿里云oss：[https://cn.aliyun.com/](https://cn.aliyun.com/)

llm应用框架：[https://github.com/langchain-ai/langchain](https://github.com/langchain-ai/langchain)

在线向量数据库：[https://cloud.zilliz.com/orgs](https://cloud.zilliz.com/orgs)

llm大模型：[https://openai.com/](https://openai.com/)

embedding：[https://openai.com/](https://openai.com/)

本项目借鉴开源前端项目有：
[https://github.com/streamlit/llm-examples](https://github.com/streamlit/llm-examples)















