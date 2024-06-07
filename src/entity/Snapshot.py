from typing import List, Any

from src.entity.Request import StaticRequest


class Snapshot:
    static_requests: list[StaticRequest]
    base_url: str

    def __init__(self, base_url: str):
        self.static_requests = []
        self.base_url = base_url

