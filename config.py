
import os

OPENAI_API_KEY = ''

os.environ["OPENAI_API_KEY"] = ''
os.environ["OPENAI_API_BASE"] = 'https://gateway.ai.cloudflare.com/v1/92a11adae8e8640ee190fde50328431e/open-ai/openai'

EMBEDDING_MODEL = ["text-embedding-3-small"]

COLLECTION_NAME = "rabbitchat"

MILVUSCLIENT_URI = ""

MILVUSCLIENT_TOKEN = ""

OSS_ACCESS_KEY_ID = ""

OSS_ACCESS_KEY_SECRET = ""

ENDPOINT = 'http://oss-cn-shenzhen.aliyuncs.com' # 假设你的Bucket处于深圳区域

BUCKET_NAME = 'rabbitchat-bucket-shenzhen'

UPLOAD_OSS = False



















