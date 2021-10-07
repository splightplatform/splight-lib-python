from setuptools import setup
try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements

setup(
    name='splight-lib',
    version='0.0.1',
    author='Splight',
    author_email='matias.silva@splight-ae.com',
    packages=['splight_lib', 'splight_lib.tests'],
    scripts=[],
    url=None,
    license='LICENSE.txt',
    description='Librar for Splight internal use',
    long_description=open('README.md').read(),
    install_requires=parse_requirements('requirements.txt', session='hack')
)