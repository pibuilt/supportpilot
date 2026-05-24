import csv
import io
import json


class ExportService:

    @staticmethod
    def to_json(
        data,
    ) -> str:
        return json.dumps(
            data,
            indent=2,
            default=str,
        )

    @staticmethod
    def to_csv(
        rows,
    ) -> str:

        if not rows:
            return ""

        output = io.StringIO()

        writer = csv.DictWriter(
            output,
            fieldnames=rows[0].keys(),
        )

        writer.writeheader()

        writer.writerows(
            rows
        )

        return output.getvalue()