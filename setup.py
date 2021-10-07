from setuptools import setup


with open('requirements.txt') as fp:
    install_requires = fp.readlines()

dependency_links = [
    # External repositories different from pypi
]

setup(
    name='splight-lib',
    version='0.0.1',
    author='Splight',
    author_email='factory@splight-ae.com',
    packages=[
        'splight_lib',
        'splight_lib.connector',
        'splight_lib.connector.databases',
        'fake_splight_lib',
    ],
    scripts=[],
    url=None,
    license='LICENSE.txt',
    description='Library for internal use only. Splight®',
    long_description=open('README.md').read(),
    install_requires=install_requires,
    dependency_links=dependency_links
)