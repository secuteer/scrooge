from typing import List, Any, Self


class Request:
    url: str
    identifier: str
    id: int
    changes: [Any]
    id_count = 0

    def __init__(self):
        self.id = Request.id_count
        Request.id_count += 1

        self.identifier = ''
        self.url = ''
        self.paramSchema = ''
        self.responseSchema = ''
        self.method = ''
        self.requestHeaders = ''
        self.response = ''
        self.responseHeaders = ''
        self.har = None
        self.merge_counter = 0
        self.changes = []
        self.content = ''


class AsyncRequest(Request):
    def __init__(self):
        super().__init__()
        self.caller = None


class StaticRequest(Request):
    previous_requests: List[Self]
    async_requests: List[AsyncRequest]

    def __init__(self):
        super().__init__()
        self.previous_requests = []
        self.async_requests = []


