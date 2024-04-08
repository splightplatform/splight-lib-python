import json
from typing import Dict, List, Optional

from pydantic import Field, field_serializer

from splight_lib.constants import DESCRIPTION_MAX_LENGTH
from splight_lib.models.base import FilePath, SplightDatabaseBaseModel


class HubSolution(SplightDatabaseBaseModel):
    id: Optional[str] = None
    name: str
    version: str
    description: Optional[str] = Field(
        default=None, max_length=DESCRIPTION_MAX_LENGTH
    )
    tags: Optional[List[str]] = Field(default=None)

    main_file: Optional[FilePath] = Field(default=None, exclude=True)
    variables_file: Optional[FilePath] = Field(default=None, exclude=True)
    values_file: Optional[FilePath] = Field(default=None, exclude=True)

    @field_serializer("tags", return_type="str", when_used="always")
    def tags_serializer(tags: List[str]) -> str:
        return json.dumps(tags)

    def save(self) -> None:
        if not all([self.main_file, self.variables_file, self.values_file]):
            raise ValueError("Missing one of the required files")
        return super().save()

    def _get_model_files_dict(self) -> Optional[Dict]:
        return {
            "main_file": self.main_file,
            "variables_file": self.variables_file,
            "values_file": self.values_file,
        }
