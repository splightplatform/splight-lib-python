[![Lib upload](https://github.com/splightplatform/splight-lib/actions/workflows/libupload.yml/badge.svg)](https://github.com/splightplatform/splight-lib/actions/workflows/libupload.yml)

# Splight Library
Elements to build components. Language defined to sync BE and Worker tasks.

- **Asset**: Node to define a graph
- **Attribute**: Available property for node
- **ValueMapping**: Map an asset property to a static value
- **ReferenceMapping**: Map an asset property to another asset property
- **ClientMapping**: Map an asset property to a dynamic value read from a ClientConnector
- **ServerMapping**: Map an asset property to a dynamic value to be written in a ServerConnector

## How to install

For development
- `python setup.py develop`

For productive envs.
- `python setup.py install`

### M1 Mac
If you have an M1 Mac (not Intel) and get an error like this:

``` bash
/confluent_kafka.h:23:10: fatal error: 'librdkafka/rdkafka.h' file not found
      #include <librdkafka/rdkafka.h>
               ^~~~~~~~~~~~~~~~~~~~~~
      1 error generated.
      error: command '/usr/bin/clang' failed with exit code 1
      [end of output]
```
you should do the following steps:
1.  `brew install librdkafka`
2.  Check in your computer the version that you have installed: `brew info librdkafka`.
  
Example:
``` bash
$ brew info librdkafka
librdkafka: stable 1.9.1 (bottled), HEAD
Apache Kafka C/C++ library
https://github.com/edenhill/librdkafka
/opt/homebrew/Cellar/librdkafka/1.9.1 (38 files, 7.6MB) *
  Poured from bottle on 2022-07-26 at 15:08:28
From: https://github.com/Homebrew/homebrew-core/blob/HEAD/Formula/librdkafka.rb
License: BSD-2-Clause
==> Dependencies
Build: pkg-config ✘, python@3.10 ✔
Required: lz4 ✔, lzlib ✔, openssl@1.1 ✔, zstd ✔
==> Options
--HEAD
	Install HEAD version
==> Analytics
install: 15,967 (30 days), 31,614 (90 days), 102,982 (365 days)
install-on-request: 11,172 (30 days), 21,151 (90 days), 68,578 (365 days)
build-error: 1 (30 days)
```
in this case, the version is 1.9.1

3. Set these env variables:
``` bash
export C_INCLUDE_PATH=/opt/homebrew/Cellar/librdkafka/<VERSION_NUMBER>/include
export LIBRARY_PATH=/opt/homebrew/Cellar/librdkafka/<VERSION_NUMBER>/lib
```

Once you have done this, you can build the library.

## Tests
```
pytest splight_lib/tests
```
