from app.services.document_processing.txt_processor import (
    TXTProcessor,
)

from app.services.document_processing.pdf_processor import (
    PDFProcessor,
)

from app.services.document_processing.docx_processor import (
    DOCXProcessor,
)


class ProcessorFactory:

    @staticmethod
    def get_processor(
        filename: str,
    ):

        filename = (
            filename.lower()
        )

        if filename.endswith(
            ".txt"
        ):
            return TXTProcessor()

        if filename.endswith(
            ".pdf"
        ):
            return PDFProcessor()

        if filename.endswith(
            ".docx"
        ):
            return DOCXProcessor()

        raise ValueError(
            "Unsupported file type"
        )