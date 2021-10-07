from setuptools import setup


with open('requirements.txt') as fp:
    install_requires = fp.readlines()


setup(
    name='splight-lib',
    version='0.0.1',
    author='Splight',
    author_email='matias.silva@splight-ae.com',
    packages=['splight_lib', 'splight_lib.connector'],
    scripts=[],
    url=None,
    license='LICENSE.txt',
    description='Librar for Splight internal use',
    long_description=open('README.md').read(),
    install_requires=install_requires
)