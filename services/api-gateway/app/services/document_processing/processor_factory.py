from app.services.document_processing.txt_processor import (
    TXTProcessor,
)

from app.services.document_processing.pdf_processor import (
    PDFProcessor,
)

from app.services.document_processing.docx_processor import (
    DOCXProcessor,
)

from app.services.document_processing.md_processor import (
    MDProcessor,
)

from app.services.document_processing.html_processor import (
    HTMLProcessor,
)

from app.services.document_processing.csv_processor import (
    CSVProcessor,
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
            ".md"
        ):
            return MDProcessor()

        if filename.endswith(
            ".html"
        ) or filename.endswith(
            ".htm"
        ):
            return HTMLProcessor()

        if filename.endswith(
            ".csv"
        ):
            return CSVProcessor()

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