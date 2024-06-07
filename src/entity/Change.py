class Change:
    """
    Class representing a change.

    Attributes:
        show_score (bool): Flag indicating whether the score should be displayed or not.
        score (float): The score of the change.
        notice (str): Additional notice or comment about the change.

    Methods:
        __init__(self, score: float, notice: str = 'no comment'): Initializes a new instance of the Change class with the given score and notice.
        get_score(self): Retrieves the score of the change.
        get_notice(self): Retrieves the notice of the change.
    """
    show_score = False
    score: float
    notice: str

    def __init__(self, score: float, notice: str = 'no comment'):
        self.score = score
        self.notice = notice
        return

    def get_score(self):
        return round(self.score, 2)

    def get_notice(self):
        return self.notice



class MissingRequestChange(Change):

    def __init__(self, score: float = 0,  notice: str = 'no comment'):
        self.notice = 'Request was not present in snapshot 2'
        self.score = score
    def __str__(self):
        return f'MissingRequestChange'

class NewRequestChange(Change):

    def __init__(self, score: float = 0, notice: str = 'no comment'):
        self.notice = 'Request was not present in snapshot 1'
        self.score = score
    def __str__(self):
        return f'NewRequestChange'

class AsyncRequestsChange(Change):
    def __str__(self):
        return f'AsyncRequestsChange'


class JaccardStructureChange(Change):
    show_score = True
    def __str__(self):
        return f'JaccardStructureChange'


class ParamChange(Change):
    def __str__(self):
        return f'ParamChange'


class DHashStructureChange(Change):
    show_score = True
    def __str__(self):
        return f'DHashStructureChange'


class AsyncRequestParamChange(Change):
    def __str__(self):
        return f'AsyncRequestParamChange'


class AsyncResponseChange(Change):
    def __str__(self):
        return f'AsyncResponseChange'
class TreeDifferenceStructureChange(Change):
    show_score = True
    def __str__(self):
        return f'TreeDifferenceStructureChange'
