from typing import List

from langchain_community.document_loaders import PyPDFLoader, PyPDFium2Loader, OnlinePDFLoader
from langchain_core.documents import Document


class PdfLoader:
    """
    pdf文件加载器
    """
    def __init__(self, file_path: str):
        self.file_path = file_path

    def pypdf_loader(self) -> List[Document]:
        loader = PyPDFLoader(self.file_path)
        return loader.load()

    def pypdfium2_loader(self) -> List[Document]:
        loader = PyPDFium2Loader(self.file_path)
        return loader.load()

    def onlinepdf_loader(self) -> List[Document]:
        loader = OnlinePDFLoader(self.file_path)
        return loader.load()

if __name__ == '__main__':
    pages = PdfLoader("产业结构调整指导目录（2024 年本）.pdf").pypdfium2_loader()
    print(pages[6])
    print(len(pages))
