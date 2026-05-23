from io import BytesIO

from docx import Document

from app.services.document_processing.base_processor import (
    BaseProcessor,
)


class DOCXProcessor(
    BaseProcessor
):

    def extract_text(
        self,
        file_bytes: bytes,
    ) -> str:

        doc = Document(
            BytesIO(
                file_bytes
            )
        )

        return "\n".join(
            p.text
            for p in doc.paragraphs
        )