"""
display/shell/implem/main
"""

class FieldLen():
    """
    Length for display padding
    """

    LEN_DATE = 10
    LEN_NAME = LEN_DATE
    LEN_MODE = 8
    LEN_TIER = 18
    LEN_CAT = 10
    LEN_DESC = 34
    LEN_AMOUNT = 9

def formart_trunc_padd(str_in: str, len_in: int) -> str:
    """
    Format string : trunc and padd to length

    Args:
        str (str): String
        len (int): Length

    Returns:
        str: Formatted string
    """

    # Trunc to length
    str_out = str_in[:len_in]
    # Right padding w/ spaces
    str_out = str_out.ljust(len_in)

    return str_out

def format_amount(amount: float, str_len: int) -> str:
    """Format amount to specified length
    with 2 decimals and left justified"""
    return f"{amount:.2f}".rjust(str_len)
