import os
from glob import glob
from tempfile import NamedTemporaryFile
from typing import Annotated, Self

import py7zr
from pydantic import BaseModel, Field

from splight_lib.constants import DESCRIPTION_MAX_LENGTH
from splight_lib.models.component import InputParameter
from splight_lib.models.database_base import (
    FilePath,
    PrivacyPolicy,
    SplightDatabaseBaseModel,
)
from splight_lib.utils.hub import (
    COMPRESSION_TYPE,
    README_FILE_1,
    RUN_FILE,
    SPEC_FILE,
    get_ignore_pathspec,
    get_spec,
)


class Port(BaseModel):
    name: str | None = None
    protocol: str = "tcp"
    internal_port: int
    exposed_port: int


class HubServer(SplightDatabaseBaseModel):
    id: str | None = None
    name: str
    version: str
    description: Annotated[
        str | None, Field(max_length=DESCRIPTION_MAX_LENGTH)
    ] = None
    tags: Annotated[list[str] | None, Field()] = []
    privacy_policy: PrivacyPolicy = PrivacyPolicy.PUBLIC

    config: list[InputParameter] = []
    ports: list[Port] = []
    environment: list[dict[str, str]] = []

    @classmethod
    def upload(cls, path: FilePath, image_file: str) -> Self:
        db_client = cls._SplightDatabaseBaseModel__get_database_client()
        image_path = os.path.join(path, image_file)
        spec = get_spec(path)
        name = spec.get("name")
        version = spec.get("version")

        raw_hub_server = db_client.get(
            resource_name=cls.__name__,
            name=name,
            version=version,
        )
        server = cls.model_validate(spec)
        if raw_hub_server:
            old_hub_server = cls.model_validate(raw_hub_server[0])
            server.id = old_hub_server.id

        server.save()

        file_name = f"{name}-{version}.{COMPRESSION_TYPE}"
        ignore_pathspec = get_ignore_pathspec(path)
        versioned_path = f"{name}-{version}"
        readme_path = os.path.join(path, README_FILE_1)
        for req_file in [SPEC_FILE, RUN_FILE, README_FILE_1]:
            if not os.path.exists(os.path.join(path, req_file)):
                raise FileNotFoundError(f"Required file not found: {req_file}")
        with py7zr.SevenZipFile(file_name, "w") as archive:
            all_files = glob(f"{path}/**", recursive=True)
            for filepath in all_files:
                if ignore_pathspec and ignore_pathspec.match_file(filepath):
                    continue
                if os.path.isdir(filepath):
                    continue
                if image_file in filepath:
                    continue
                rel_filename = os.path.relpath(filepath, path)
                new_filepath = os.path.join(versioned_path, rel_filename)
                archive.write(filepath, new_filepath)

        data = server.model_dump()
        try:
            db_client.upload(
                "hubserverversion",
                instance=data,
                file_path=file_name,
                type_="source",
            )
            db_client.upload(
                "hubserverversion",
                instance=data,
                file_path=readme_path,
                type_="readme",
            )
            db_client.upload(
                "hubserverversion",
                instance=data,
                file_path=image_path,
                type_="image",
            )
        except Exception as exc:
            raise exc
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)
        return server

    def download(self) -> NamedTemporaryFile:
        db_client = self._SplightDatabaseBaseModel__get_database_client()
        return db_client.download(
            resource_name="hubserverversion",
            instance=self.model_dump(),
            type_="source",
        )
