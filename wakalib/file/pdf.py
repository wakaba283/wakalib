"""
This module is a collection of operations related to pdf.
It uses the following libraries
- xhtml2pdf

Typical usage example:
"""
import os

from xhtml2pdf import pisa

from wakalib.exceptions.exception import (FailedToConvert,
                                          FilePathDoesNotExists,
                                          FilePathIsNotFile)


def html_to_pdf(
        source_html: str,
        output_filepath: str,
        css: str | None = None
    ) -> None:
    """
    ## Summary
    Converts HTML strings to PDF and outputs to a specified file path.

    ## Args:
    - source_html (str) :
        HTML string. Encoding must be UTF-8.
    - output_filepath (str) :
        The file path of the output destination.
        It is safer to specify an absolute path.
    - css (str, optional) :
        The default value is None.
        Use this to specify fonts, etc. in the output file.
    """
    if not os.path.exists(output_filepath):
        raise FilePathDoesNotExists(file_path=output_filepath)
    if not os.path.isfile(output_filepath):
        raise FilePathIsNotFile(file_path=output_filepath)
    with open(output_filepath, 'w+b') as file:
        pisa_status = pisa.CreatePDF(
            src=source_html.encode('utf-8'),
            dest=file,
            encoding='utf-8',
            default_css=css
        )
    if pisa_status.err:
        raise FailedToConvert(css=css)
