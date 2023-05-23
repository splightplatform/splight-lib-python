from setuptools import find_packages, setup

with open("requirements.txt") as fp:
    install_requires = fp.readlines()

dependency_links = [
    # External repoitories different from pypi
]

test_requires = [
    "pytest==7.1.2",
    "mock==4.0.3",
]

setup(
    name="splight-lib",
    version="3.0.0.dev2",
    author="Splight",
    author_email="factory@splight-ae.com",
    packages=find_packages(),
    package_data={},
    include_package_data=True,
    scripts=[],
    url=None,
    zip_safe=False,
    license="LICENSE.txt",
    description="Library for public use. Splight",
    long_description=open("README.md").read(),
    install_requires=install_requires,
    dependency_links=dependency_links,
    extras_require={
        "test": test_requires,
        "dev": test_requires
        + [
            "flake8==6.0.0",
            "ipython==8.12.0",
            "ipdb==0.13.13",
            "pre-commit==3.2.2",
            "black==23.3.0",
            "isort==5.12.0",
        ],
    },
)
