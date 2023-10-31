"""
This module is a collection of operations related to pdf.
It uses the following libraries
- xhtml2pdf

Typical usage example:
"""
import os
from collections.abc import Iterable
from io import BytesIO
from pathlib import Path
from typing import Literal, TypedDict, Union

from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from xhtml2pdf import pisa

from wakalib.exceptions.exception import (ArgsError, FailedToConvert,
                                          FilePathDoesNotExists,
                                          FilePathIsNotFile)
from wakalib.file.handler import get_file_type


class _InsertTextDict(TypedDict):
    text: str
    x: int
    y: int
    font_size: int
    color_rgb: tuple[int, int, int]


def insert_text_into_pdf(  # pylint: disable=too-many-arguments, too-many-locals, too-many-branches
        file_path: str,
        params: Iterable[_InsertTextDict],
        page_size: tuple[float, float] = A4,
        starting_point: Literal[
            'top-left',
            'bottom-left',
            'top-right',
            'bottom-right'
        ] = 'bottom-left',
        font: Union[str, Path] = 'Helvetica',
        target_pages: Union[int, Literal['all']] = 'all',
        output_suffix: Union[str, None] = None
    ) -> str:
    """
    ## Summary
    Appends any specified characters to the passed PDF file path
    and returns the path to the output PDF.
    The output PDF will be generated in the same directory
    as the specified path.

    ## Args:
    - file_path (str):
        Target PDF file path.
    - params (Iterable[_InsertTextDict]):
        Must be an Iterable object.
        The object must be described in the following format.
        {
            'text': (str) Strings to be inserted.
            'x': (int) X-coordinate.
            'y': (int) Y-coordinate.
            'font_size': (int) Font size.
            'color_rgb': (tuple[int, int, int]) Font color. RGB.
        }
    - page_size (tuple[float, float], optional):
        The size of the PDF to be read is described
        by a tuple containing two float types.
        This is used for the position of the text, etc.. Defaults to A4.
    - starting_point (Literal['top-left', 'bottom-left',
                              'top-right', 'bottom-right', optional):
        Select the corner that will be the starting point
        for the position of the text to be inserted.
        Defaults to 'bottom-left'.
    - font (Union[str, Path], optional):
        If the font is included in reportlab, it can be specified by letter.
        Fonts not included in reportlab can be specified
        by specifying the file path.
        Defaults to 'Helvetica'.
    - target_pages (Union[int, Literal['all']], optional):
        Page to insert text, starting with 0. Defaults to 'all'.
    - output_suffix (Union[str, None], optional):
        Suffix of the output file; if not specified,
        the first text of params is set.

    ## Returns:
    - str:
        Path of the output file. Generated in the same directory
        as the specified file.
    """
    if not get_file_type(filepath=file_path) == 'pdf':
        raise ArgsError(
            argument_name='file_path',
            add='This file is not PDF.'
        )
    if not output_suffix:
        output_suffix: str = f"({params[0]['text']})"
    _buffer = BytesIO()
    _pdf = canvas.Canvas(filename=_buffer, pagesize=A4)
    if os.path.isfile(path=font):
        pdfmetrics.registerFont(
            font=TTFont(name='User Font', filename=font)
        )
        font = 'User Font'
    for _param in params:
        _r, _g, _b = _param['color_rgb']
        _pdf.setFont(psfontname=font, size=_param['font_size'])
        _pdf.setFillColorRGB(r=_r, g=_g, b=_b)
        if starting_point == 'top-left':
            _, _y = page_size
            _pdf.drawString(
                x=_param['x'],
                y=_y-_param['y'],
                text=_param['text'],
            )
        elif starting_point == 'bottom-left':
            _pdf.drawString(
                x=_param['x'],
                y=_param['y'],
                text=_param['text'],
            )
        elif starting_point == 'top-right':
            _x, _y = page_size
            _pdf.drawString(
                x=_x-_param['x'],
                y=_y-_param['y'],
                text=_param['text'],
            )
        elif starting_point == 'bottom-right':
            _x, _ = page_size
            _pdf.drawString(
                x=_x-_param['x'],
                y=_param['y'],
                text=_param['text'],
            )
    _pdf.showPage()
    _pdf.save()
    _buffer.seek(0)
    _pdf = PdfReader(stream=_buffer)
    target_pdf = PdfReader(
        stream=file_path,
        strict=False
    )
    result_pdf = PdfWriter()
    if isinstance(target_pages, int):
        for num, _page in enumerate(target_pdf.pages):
            if num == target_pages:
                _page.merge_page(page2=_pdf.pages[0])
            result_pdf.add_page(page=_page)
    elif isinstance(target_pages, str) and target_pages == 'all':
        for _page in target_pdf.pages:
            _page.merge_page(page2=_pdf.pages[0])
            result_pdf.add_page(page=_page)
    output_directory, _file_name = os.path.split(p=file_path)
    output_filepath = os.path.join(
        output_directory,
        f'{output_suffix}{_file_name}'
    )
    result_pdf.write(stream=output_filepath)
    return output_filepath


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
