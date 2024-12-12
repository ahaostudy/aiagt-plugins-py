import requests
from io import BytesIO
import PyPDF2
import pandas as pd
from docx import Document

from utils import http


class FileReaderService:
    def read_file(self, url: str, typ: str) -> str:
        response = http.client().get(url)
        response.raise_for_status()  # 确保请求成功
        file_content = BytesIO(response.content)

        if typ == '.txt':
            return self.read_txt_file(file_content)
        elif typ == '.docx':
            return self.read_docx_file(file_content)
        elif typ == '.pdf':
            return self.read_pdf_file(file_content)
        elif typ in ('.xls', '.xlsx'):
            return self.read_excel_file(file_content)

        raise ValueError("Unsupported file type")

    @staticmethod
    def read_txt_file(file_content: BytesIO) -> str:
        return file_content.getvalue().decode('utf-8')

    @staticmethod
    def read_docx_file(file_content: BytesIO) -> str:
        document = Document(file_content)
        return '\n'.join(paragraph.text for paragraph in document.paragraphs)

    @staticmethod
    def read_pdf_file(file_content: BytesIO) -> str:
        reader = PyPDF2.PdfReader(file_content)
        text = ''
        for page in reader.pages:
            text += page.extract_text() + '\n'
        return text.strip()

    @staticmethod
    def read_excel_file(file_content: BytesIO) -> str:
        df = pd.read_excel(file_content)
        return df.to_string(index=False)
