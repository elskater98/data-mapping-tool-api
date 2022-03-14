from datetime import date

from pydantic import BaseModel


class VersionModel(BaseModel):
    version: str
    num_classes: int
    num_relations: int
    date: date

    def generate_version(self):
        return f"{self.date.today().__str__().replace('-', '.')}.{self.num_classes}.{self.num_relations}"
