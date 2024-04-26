import os
from dotenv import load_dotenv, find_dotenv

# 加载env配置
_ = load_dotenv(find_dotenv(filename=f".env"))
print(f"Loading env... result: {_}")


#     GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
#     MOONSHOT_API_KEY = st.secrets["MOONSHOT_API_KEY"]
#     MOONSHOT_API_BASE_URL = st.secrets["MOONSHOT_API_BASE_URL"]

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
MOONSHOT_API_KEY = os.environ.get('MOONSHOT_API_KEY')
MOONSHOT_API_BASE_URL = os.environ.get('MOONSHOT_API_BASE_URL')
MOONSHOT_API_MODEL = os.environ.get('MOONSHOT_API_MODEL')

# os.environ["OPENAI_API_KEY"] = ''
# os.environ["SERPAPI_API_KEY"] = ''
# os.environ["OPENAI_API_BASE"] = 'https://gateway.ai.cloudflare.com/v1/92a11adae8e8640ee190fde50328431e/open-ai/openai'
# os.environ["GOOGLE_API_KEY"] = 'https://gateway.ai.cloudflare.com/v1/92a11adae8e8640ee190fde50328431e/google-gimini-pro/vertex-ai'


EMBEDDING_MODEL = ["text-embedding-3-small"]
# EMBEDDING_MODEL = ["text-embedding-3-small", "BAAI/bge-small-zh-v1.5"]

COLLECTION_NAME = "rabbitchat"

MILVUSCLIENT_URI = ""

MILVUSCLIENT_TOKEN = ""

OSS_ACCESS_KEY_ID = ""

OSS_ACCESS_KEY_SECRET = ""

ENDPOINT = 'http://oss-cn-shenzhen.aliyuncs.com' # 假设你的Bucket处于深圳区域

BUCKET_NAME = 'rabbitchat-bucket-shenzhen'

UPLOAD_OSS = False

# ONE_API_BASE_URL = "https://aiserver.club"
ONE_API_BASE_URL = "http://106.53.130.14:3000"


"""
在一个py文件下，不要使用任何同名的变量，尽管这些变量作用域不同，但是导致程序出错，目前没有找到原因

bug:
在翻译界面输入内容回车能正常翻译，但是这时候修改左侧的输入框内容，再次回车，就会出现错误，这是因为在翻译的时候，没有清除上一次的翻译结果，导致了错误
"""

















