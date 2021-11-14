"""
bank/error
"""

class NoOverrideError(Exception):
    """
    Exception raised for not overriden method
    """

    def __init__(self, base_class: str = "", derived_class: str = "", method: str = "") -> None:
        msg = f"{base_class}.{method} not overriden in {derived_class}"
        super().__init__(msg)
