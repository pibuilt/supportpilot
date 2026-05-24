from bs4 import BeautifulSoup

from app.services.document_processing.base_processor import (
    BaseProcessor,
)


class HTMLProcessor(
    BaseProcessor
):

    def extract_text(
        self,
        file_bytes: bytes,
    ) -> str:

        html = file_bytes.decode(
            "utf-8"
        )

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        return soup.get_text(
            separator="\n",
            strip=True,
        )