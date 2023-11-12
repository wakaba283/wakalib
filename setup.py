# pylint: disable=missing-module-docstring
import pathlib
from setuptools import find_namespace_packages, setup

install_requires = [
    'urllib3==1.26.17',
    'boxsdk==3.9.1',
    'boxsdk[jwt]',
    'docusign-esign==3.24.0',
    'Flask==3.0.0',
    'openpyxl==3.1.2',
    'pandas==2.1.1',
    'psycopg2-binary==2.9.9',
    'PyPDF2==3.0.1',
    'reportlab==3.6.13',
    'xhtml2pdf==0.2.11',
    'xlsx2html==0.4.4',
]

setup(
    name="wakalib",
    version="0.3.0a2",
    description=(
        "This is an experimental library thet extends the functionally of a "
        "group of Python libraries. Check the GitHub page for details."
    ),
    long_description=(pathlib.Path(__file__).parent / 'README.md').read_text(encoding='utf-8'),
    long_description_content_type='text/markdown',
    packages=find_namespace_packages(include=['wakalib.*']),
    include_package_data=True,
    install_requires=install_requires,
    author="Tsubasa Wakabayashi",
    url="https://github.com/wakaba283/wakalib",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Japanese",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.11",
    ],
)
