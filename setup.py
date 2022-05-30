from setuptools import setup, find_packages


with open('requirements.txt') as fp:
    install_requires = fp.readlines()

dependency_links = [
    # External repositories different from pypi
]

setup(
    name='splight-lib',
    version='0.3.25',
    author='Splight',
    author_email='factory@splight-ae.com',
    packages=find_packages(),
    package_data={'splight_deployment': ['kubernetes/templates/*.yaml']},
    include_package_data=True,
    scripts=[],
    url=None,
    zip_safe=False,
    license='LICENSE.txt',
    description='Library for internal use only. Splight',
    long_description=open('README.md').read(),
    install_requires=install_requires,
    dependency_links=dependency_links
)
