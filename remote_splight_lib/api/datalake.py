from uplink import (
    Body,
    Consumer,
    Path,
    delete,
    get,
    json,
    patch,
    post,
    put,
    returns,
    Query
)


class DatalakeEndpoint(Consumer):
    @get("/datalake/data/")
    def data(self, source: Query):
        """Reads data from datalake"""

    @get("/datalake/dumpdata/")
    def dumpdata(self, source: Query):
        """Reads data from datalake"""
