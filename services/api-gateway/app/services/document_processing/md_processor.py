from app.services.document_processing.base_processor import (
    BaseProcessor,
)


class MDProcessor(
    BaseProcessor
):

    def extract_text(
        self,
        file_bytes: bytes,
    ) -> str:

        return file_bytes.decode(
            "utf-8"
        )