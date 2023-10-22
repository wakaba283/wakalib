"""
This module performs mail operations.
"""

import mimetypes
import os
import smtplib
from email import message
from typing import Literal

from wakalib.exceptions.exception import ArgsError


class EMail:
    """
    E-mail handler
    """
    def __init__(
            self,
            server_type: Literal['SMTP'],
            host: str,
            port: int
        ) -> None:
        """
        ## Args:
        - server_type (Literal['SMTP']) :
            Mail server type.
        - host (str) :
            Server host.
        - port (int) :
            Server port.
        """
        self.__server_type = server_type
        self.__host = host
        self.__port = port

    @property
    def server_type(self):  # pylint: disable=missing-function-docstring
        return self.__server_type

    @property
    def host(self):  # pylint: disable=missing-function-docstring
        return self.__host

    @property
    def port(self):  # pylint: disable=missing-function-docstring
        return self.__port

    @staticmethod
    def create_message(
            sender: str,
            subject: str,
            body: str,
            body_subtype: Literal['text', 'html'] = 'text',
            to: list[str] | None = None,
            cc: list[str] | None = None,
            bcc: list[str] | None = None,
            attachments: list[str] | None = None,
        ) -> message.EmailMessage:
        """
        ## Args:
        - ender (str) : Email from.  ex. hogehoge@fuga.com
        - subject (str) : Message subject.
        - body (str) : Message body.
        - body_subtype (Literal['text';, 'html'], optional) :
                Select according to "body".
                Defaults to 'text'.
        - to (list[str] | None, optional) :
                Email to.
                e.g. ['hoge@hoge.com', 'fuga@hoge.com']
        - cc (list[str] | None, optional) :
                Email cc.
                e.g. ['piyo@fuga.com', 'nyao@fuga.com']
        - bcc (list[str] | None, optional) :
                Email bcc.
                e.g. ['wanwan@piyo.com', 'hihin@piyo.com']
        - attachments (list[str] | None, optional) :
                Attachment file path list.
                e.g. ['hoge/fuga/piyo.pdf']

        ## Returns:
        - message.EmailMessage : Created message object.
        """
        if not (to or cc or bcc):
            raise ArgsError(
                argument_name='to, cc, bcc',
                add='To, Cc, or Bcc must be entered.'
            )
        msg = message.EmailMessage()
        msg['Subject'] = subject
        msg.add_alternative(body, subtype=body_subtype)
        if to:
            msg['To'] = to
        if cc:
            msg['Cc'] = cc
        if bcc:
            msg['Bcc'] = bcc
        msg['From'] = sender
        if attachments:
            for attachment in attachments:
                guess_type = mimetypes.guess_type(attachment)[0]
                mime_type, mime_subtype = guess_type.split('/', 1)
                with open(attachment, 'rb') as file:
                    msg.add_attachment(
                        file.read(),
                        maintype=mime_type,
                        subtype=mime_subtype,
                        filename=os.path.basename(attachment)
                    )
        return msg

    def send(self, msg: message.EmailMessage) -> None:
        """
        ## Args:
        - msg (message.EmailMessage) :
            Message object
        """
        if self.server_type == 'SMTP':
            with smtplib.SMTP(host=self.host, port=self.port) as server:
                server.send_message(msg=msg)
