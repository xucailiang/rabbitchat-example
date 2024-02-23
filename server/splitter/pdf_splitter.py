from typing import List

from langchain.text_splitter import NLTKTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter


def nltk_splitter(doc_page: str, chunk_size: str = "500", chunk_overlap: str = "10") -> List[str]:
    splitter = NLTKTextSplitter(chunk_size, chunk_overlap)
    texts = splitter.split_text(doc_page)
    return texts


def recursive_character_splitter(doc_page: str, chunk_size: int = 500, chunk_overlap: int = 10) -> List[str]:
    r_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,  # 块长度
        chunk_overlap=chunk_overlap  # 重叠字符串长度
    )
    page_str_list = r_splitter.split_text(doc_page)
    return page_str_list









