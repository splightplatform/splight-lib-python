#!/bin/bash -e
 cat << EOF >> ~/.pypirc
 [distutils]
 index-servers=splightlib
 [splightlib]
 repository:https://splight.jfrog.io/artifactory/api/pypi/testjfrog-pypi
 username=thomas.vadora@splight-ae.com
 password=4bhy35L@Tha!!fRpV2N3_oL1
 EOF
 python setup.py bdist_wheel upload -r splightlib
 rm ~/.pypirc;