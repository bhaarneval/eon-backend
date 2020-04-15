"""
Providing exception detail for core app
"""


class CoreAppException(Exception):
    """
    Custom exception class for core app
    """
    def __init__(self, message=None, default_code=None, status_code=None):
        if message:
            self.default_detail = message
        if default_code:
            self.default_code = default_code
        if status_code:
            self.status_code = status_code
