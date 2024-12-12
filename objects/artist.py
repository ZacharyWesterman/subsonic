from dataclasses import dataclass

@dataclass(frozen = True)
class Artist:
	id: str
	name: str
