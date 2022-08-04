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
)


class AlgorithmEndpoint(Consumer):
    @returns.json()
    @get("/algorithm/")
    def list(self):
        """Returns the algorithms"""

    @returns.json()
    @get("/algorithm/{id}/")
    def retrieve(self, resource_id: Path("id")):
        """Retrieves one algorithm"""

    @returns.json()
    @json
    @post("/algorithm/")
    def create(self, data: Body):
        """Creates a new algorithm"""

    @returns.json()
    @json
    @put("/algorithm/{resource_id}/")
    def update(self, resource_id: str, data: Body):
        """Updates an existing algorithm"""

    @returns.json()
    @json
    @patch("/algorithm/{resource_id}/")
    def modify(self, resource_id: str, data: Body):
        """Modifies an existing algorithm"""

    @delete("/algorithm/{id}/")
    def destroy(self, resource_id: Path("id")):
        """Deletes one algorithm"""
