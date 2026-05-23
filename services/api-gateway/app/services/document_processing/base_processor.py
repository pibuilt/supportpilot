from abc import ABC
from abc import abstractmethod


class BaseProcessor(
    ABC
):

    @abstractmethod
    def extract_text(
        self,
        file_bytes: bytes,
    ) -> str:
        pass