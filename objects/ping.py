from dataclasses import dataclass


@dataclass(frozen=True)
class Ping:
    status: str
    version: str
    type: str

    @property
    def ok(self) -> bool:
        return self.status == 'ok'
