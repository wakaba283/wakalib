# wakalib
## 🌱About
### Project Name
wakalib

### Purpose
Extension of operatings taht are frequently used but not supported
by official SDKs or libraries.

### Document
https://wakalib.readthedocs.io/ja/latest/

### Support Language
- English
- Japanese

### Developed by
| Name | GitHub |
| ---- | ------ |
| Tsubasa Wakabayashi | https://github.com/wakabayashi283 |

### Collaborator
None

## 🤖Test Enviroment
### Python Version
Python3.11.6

## ⚡️Installation
```
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ wakalib
```
Note:
Some of the dependent libraries are not supported by test PyPI and must be installed with the above code.

## 🎓LICENSE
MIT License  
Check license file for details.

## 📚Used Libraries
#### Apache Software License (Apache License 2.0)
boxsdk (https://github.com/box/box-python-sdk)  
xhtml2pdf (https://github.com/xhtml2pdf/xhtml2pdf)
#### BSD-3-Clause
Flask (https://github.com/pallets/flask/)  
pandas (https://github.com/pandas-dev/pandas)  
reportlab (https://github.com/mattjmorrison/ReportLab)
#### LGPL
psycopg2 (https://github.com/psycopg/psycopg2)
#### MIT License
xlsx2html (https://github.com/Apkawa/xlsx2html)  
docusign-esign (https://developers.docusign.com/)
#### Other
PyPDF2 (https://github.com/py-pdf/pypdf)


## Change Log
This library follows semantic versioning.
#### Labels
- Added (New feature)
- Changed (Changes to existing feature.)
- Deprecated (Features to be removed in tha future.)
- Removed (Removed future.)
- Fixed (Bug fixes.)
- Security (Recommended updates for security issues.)

| Version | Label | Detail | Date |
| ------- | ----- | ------ | ---- |
| 0.0.0 | **Added** | Released Development version! | October 13, 2023 |
| 0.0.1 | Fixed | db.postgres: Fixed an error in argument type specification.<br>e.g. in upsert method<br>old: params=List[str, str]<br>new: params=List[str, Any] | October 19, 2023 |
| 0.0.2 | Fixed | mail.handler: Fixed a bug that caused an error when tha argument attachments was not specified. | October 19, 2023 |
| 0.0.3 | Fixed | The method of describing the return value has been corrected to solve the problem of being displaed as "Code is unreachable." by Pylance.<br>e.g.<br>old: def Function() -> NoReturn<br>new: def Function() -> None | October 20, 2023 |
| 0.1.0 | Added | A function has been added to pass a temporary folder as the first argument when used as a decorator. | October 20, 2023 |
| 0.1.0a4 | **Added** | I developed a module to generate random strings.<br>I have also optimized and tested parts of db/postgres.<br>I made it clear that this is a pre-alpha version of versioning. | October 22, 2023 |
| 0.2.0a1 | Added | The following functions have been added for PDF file operations.<br> - insert_text_into_pdf | October 31, 2023 |
| 0.3.0a1 | Added | Added function to convert string to date type. | November 9, 2023 |
| 0.3.0a2 | Changed | Changed str_to_datetime to be more powerful. | November 12, 2023 |
| 0.3.0a3 | Changed | db.postgres: minor fixes. | September 6, 2024 |
