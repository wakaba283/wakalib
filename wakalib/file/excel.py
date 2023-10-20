"""
This module is used for general excel operations.
"""

from xlsx2html import xlsx2html


def excel_to_html(file_path: str) -> str:
    """
    ## Summary
    Convert excel to html string.

    ## Args:
    - file_path (str) :
        Path of the target excel file path.

    ## Returns:
    - str : HTML text.
    """
    out_stream = xlsx2html(filepath=file_path)
    out_stream.seek(0)
    return out_stream.read()
