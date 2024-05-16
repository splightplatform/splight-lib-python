from typing import Dict, List, Optional

from pydantic import Field

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
    readme_file: Optional[FilePath] = Field(default=None, exclude=True)

    def save(self) -> None:
        if not all(
            [
                self.main_file,
                self.variables_file,
                self.values_file,
                self.readme_file,
            ]
        ):
            raise ValueError("Missing one of the required files")
        return super().save()

    def _get_model_files_dict(self) -> Optional[Dict]:
        return {
            "main_file": self.main_file,
            "variables_file": self.variables_file,
            "values_file": self.values_file,
            "readme_file": self.readme_file,
        }
