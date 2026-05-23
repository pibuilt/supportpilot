from io import BytesIO

from pypdf import PdfReader

from app.services.document_processing.base_processor import (
    BaseProcessor,
)


class PDFProcessor(
    BaseProcessor
):

    def extract_text(
        self,
        file_bytes: bytes,
    ) -> str:

        reader = PdfReader(
            BytesIO(
                file_bytes
            )
        )

        pages = []

        for page in reader.pages:
            pages.append(
                page.extract_text()
                or ""
            )

        return "\n".join(
            pages
        )