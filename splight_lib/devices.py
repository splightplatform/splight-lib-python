from splight_lib.status import STATUS_OK


class Device:
    _status = STATUS_OK


    @property
    def status(self):
        return self._status