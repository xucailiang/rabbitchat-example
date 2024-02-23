from pymilvus import MilvusClient
import config
from server.loaders.pdf_loaders import PdfLoader
from server.splitter.pdf_splitter import recursive_character_splitter
from openai import OpenAI

openai_client = OpenAI()

zilliz_client = MilvusClient(
    uri=config.MILVUSCLIENT_URI,
    # Cluster endpoint obtained from the console
    token=config.MILVUSCLIENT_TOKEN
    # API key or a colon-separated cluster username and password
)


def get_embeddings(file_tmp_path: str, openai_key_id: str):
    pdf_loader = PdfLoader(file_tmp_path).pypdf_loader()
    embeddings_list = []
    for index, page in enumerate(pdf_loader):
        print(page)
        page_str_list = recursive_character_splitter(page.page_content)
        for page_str in page_str_list:
            response = openai_client.embeddings.create(
                input=page_str,
                model=config.EMBEDDING_MODEL[0]
            )
            embeddings_list.append({"openai_key_id": openai_key_id, "vector": response.data[0].embedding, "level": 1, "vip": False,
                                    "source": page.metadata['source'], "page": page.metadata['page'], "context": page_str})
    return embeddings_list


def get_query_embedding(query):
    response = openai_client.embeddings.create(
        input=query,
        model=config.EMBEDDING_MODEL[0]
    )
    return response.data[0].embedding


def save_to_vector(data_list):
    zilliz_client.insert(config.COLLECTION_NAME, data_list, progress_bar=True)


def query_vector():
    zilliz_client.query(config.COLLECTION_NAME, "id in [0]", output_fields=["title_vector"])


def search_vector(query_embed, upload_file_name):
    print("upload_file_name")
    print(upload_file_name)
    list_dict = zilliz_client.search(collection_name=config.COLLECTION_NAME, data=[query_embed],
                                     filter=f"source == '{upload_file_name}'",
                                     output_fields=["context", "page", "source"], limit=3)
    return list_dict

# if __name__ == '__main__':
#     query = "我国产业结构调整的关键是什么"
#     query_embed = get_query_embedding(query)
#     search_vector(query_embed)
