import logging
import sys

import requests
from pypi_cleanup import CsfrParser


def delete_developer_versions(
    package_name: str, release_version: str, username: str, password: str
):
    with requests.Session() as session:
        # generate csrf token
        with session.get("https://pypi.org/account/login/") as response:
            response.raise_for_status()
            form_action = "/account/login/"
            parser = CsfrParser(form_action)
            parser.feed(response.text)
            if not parser.csrf:
                raise ValueError(f"No CSFR found in {form_action}")
            csrf = parser.csrf

        # validate login
        with session.post(
            "https://pypi.org/account/login/",
            data={
                "csrf_token": csrf,
                "username": username,
                "password": password,
            },
            headers={"referer": "https://pypi.org/account/login/"},
        ) as response:
            response.raise_for_status()
            if response.url == "https://pypi.org/account/login/":
                logging.error(f"Login for user {username} failed")
                return 1

        # get developer versions to delete
        with session.get(
            f"https://pypi.org/pypi/{package_name}/json"
        ) as response:
            versions = list(response.json()["releases"].keys())
            to_delete = [
                version
                for version in versions
                if "dev" in version and release_version in version
            ]

        # delete versions
        for version in to_delete:
            logging.info(f"Deleting {package_name} version {version}")
            form_action = f"/manage/project/{package_name}/release/{version}/"
            form_url = f"https://pypi.org{form_action}"
            with session.get(form_url) as response:
                response.raise_for_status()
                parser = CsfrParser(form_action, "confirm_delete_version")
                parser.feed(response.text)
                if not parser.csrf:
                    raise ValueError(f"No CSFR found in {form_action}")
                csrf = parser.csrf
                referer = response.url

            with session.post(
                form_url,
                data={"csrf_token": csrf, "confirm_delete_version": version},
                headers={"referer": referer},
            ) as response:
                response.raise_for_status()


if __name__ == "__main__":
    """Remove all developer version from given release version

    Args:
        package_name (arg 1) (str): library package name (splight-lib)
        release_version (arg 2) (str): current release version (x.y.z)
        username (arg 3) (str): pypi account username
        password (arg 4) (str): pypi account password
    Raises:
        ValueError: When CSRF fails.
    """
    package_name = sys.argv[1]
    release_version = sys.argv[2]
    username = sys.argv[3]
    password = sys.argv[4]

    public_project_version = delete_developer_versions(
        package_name=package_name,
        release_version=release_version,
        username=username,
        password=password,
    )
