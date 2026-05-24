import csv
from io import StringIO

from app.services.document_processing.base_processor import (
    BaseProcessor,
)


class CSVProcessor(
    BaseProcessor
):

    def extract_text(
        self,
        file_bytes: bytes,
    ) -> str:

        content = file_bytes.decode(
            "utf-8"
        )

        reader = csv.reader(
            StringIO(content)
        )

        rows = []

        for row in reader:
            rows.append(
                " | ".join(row)
            )

        return "\n".join(
            rows
        )