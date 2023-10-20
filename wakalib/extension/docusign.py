"""
Help with Docusign certification.
"""

import datetime
import json
import os
from typing import Literal

import flask
import requests
from docusign_esign import ApiClient
from docusign_esign.client.api_exception import ApiException

from wakalib.exceptions.exception import (ArgsError, FilePathDoesNotExists,
                                          FilePathIsNotFile)


class Docusign:
    """
    ## Summary
    Help with Docusign certification.
    For example, prepare the following file.
        jwt_config_file
        {
            "app_url": "http://piyopiyo:5000",
            "authorization_server": "https://account-d.docusign.com",
            "target_account_id": None,
        }
        jwt_credential_file
        {
            "ds_client_id": "hogehoge",
            "ds_impersonated_user_id": "piyopiyo",
            "private_key_file": "hoge/fuga.key",
            "authorization_server": "https://account-d.docusign.com"
        }
    """
    def __init__(  # pylint: disable=dangerous-default-value
            self,
            grant_type: Literal['JWT'] = 'JWT',
            jwt_config_filepath: str | None = None,
            jwt_credential_filepath: str | None = None,
            scopes: list[str] = ['signature'],
        ):
        """
        ## Args:
        - grant_type (Literal['JWT'], optional) :
            Defaults to 'JWT'.
        - jwt_config_filepath (str | None, optional) :
            "jwt_config_filepath" is required
            when grant_type is set to "JWT"
        - jwt_credential_filepath (str | None, optional) :
            "jwt_credential_filepath" is required
            when grant_type is set to "JWT"
        - scopes (list[str], optional) :
            Defaults to ['signature'].
        """
        self.scopes = scopes
        self.grant_type = grant_type
        self.dict_connection: dict[str, str]
        if self.grant_type == 'JWT':
            if not (jwt_config_filepath and jwt_credential_filepath):
                raise ArgsError(
                    argument_name=(
                        'jwt_config_filepath, jwt_credential_filepath'
                    ),
                    add=(
                        '"jwt_config_filepath" and "jwt_credential_filepath" '
                        'is required when grant_type is set to "JWT"'
                    )
                )
            if not os.path.exists(jwt_config_filepath):
                raise FilePathDoesNotExists(file_path=jwt_config_filepath)
            if not os.path.exists(jwt_credential_filepath):
                raise FilePathDoesNotExists(file_path=jwt_credential_filepath)
            if not os.path.isfile(jwt_config_filepath):
                raise FilePathIsNotFile(file_path=jwt_config_filepath)
            if not os.path.isfile(jwt_credential_filepath):
                raise FilePathIsNotFile(file_path=jwt_credential_filepath)
            self.scopes.append('impersonation')
            self.__jwt(
                jwt_config_filepath=jwt_config_filepath,
                jwt_credential_filepath=jwt_credential_filepath
            )

    def _get_private_key(self) -> str:
        """
        ## Description

        Check that the private key present in the file and if it is,
        get it from the file.
        In the opposite way get it from config variable.

        ## Returns:
        - str: Private key.
        """
        private_key = self.dict_jwt_credential['private_key_file']
        if os.path.isfile(private_key):
            with open(os.path.abspath(private_key), encoding='utf-8') as _file:
                private_key = _file.read()
        return private_key

    def __jwt(
            self,
            jwt_config_filepath: str,
            jwt_credential_filepath: str
        ) -> None:
        with open(
                file=jwt_config_filepath, mode='rt', encoding='utf-8'
            ) as file_:
            self.dict_jwt_config = json.load(file_)
        with open(
                file=jwt_credential_filepath, mode='rt', encoding='utf-8'
            ) as file_:
            self.dict_jwt_credential = json.load(file_)
        api_client = ApiClient()
        api_client.set_base_path(
            self.dict_jwt_credential['authorization_server']
        )
        private_key = self._get_private_key()
        try:
            _response = api_client.request_jwt_user_token(
                client_id=\
                    self.dict_jwt_credential['ds_client_id'],
                user_id=\
                    self.dict_jwt_credential['ds_impersonated_user_id'],
                oauth_host_name=\
                    self.dict_jwt_credential['authorization_server'],
                private_key_bytes=\
                    private_key,
                expires_in=\
                    4000,
                scopes=\
                    self.scopes
            ).to_dict()
            self.dict_connection['ds_access_token'] = \
                _response['access_token']
            self.dict_connection['ds_refresh_token'] = \
                _response['refresh_token']
            self.dict_connection['ds_expiration'] = \
                datetime.datetime.utcnow() \
                + datetime.timedelta(seconds=int(_response['expires_in']))
            if not self.dict_connection.get('ds_account_id'):
                _response = requests.get(
                    url=(
                        f"{self.dict_jwt_config['authorization_server']}"
                        '/oauth/userinfo'
                    ),
                    headers={
                        'Authorization': (
                            'Bearer '
                            f"{self.dict_connection['ds_access_token']}"
                        )
                    },
                    timeout=(9, 30)
                ).json()
                self.dict_connection['ds_user_name'] = _response['name']
                self.dict_connection['ds_user_email'] = _response['email']
                accounts = _response['accounts']
                target_account_id = self.dict_jwt_config['target_account_id']
                if target_account_id:
                    account = next(
                        (
                            acc for acc in accounts if (
                                acc["account_id"] == target_account_id
                            )
                        ),
                        None
                    )
                    if not account:
                        raise ValueError('No access to target account')
                else:
                    account = next(
                        (acc for acc in accounts if acc['is_default']),
                        None
                    )
                    if not account:
                        raise ValueError('No default account')
                self.dict_connection['ds_account_id'] = \
                    account['account_id']
                self.dict_connection['ds_account_name'] = \
                    account['account_name']
                self.dict_connection['ds_base_path'] = \
                    f"{account['base_uri']}/restapi"
        except ApiException as err:
            body = err.body.decode('utf8')
            if 'consent_required' in body:
                consent_scopes = ' '.join(self.scopes)
                redirect_uri = \
                    (
                        f"{self.dict_jwt_config['app_url']}"
                        "{flask.url_for('ds.ds_callback')}"
                    )
                consent_url = \
                    (
                        f"{self.dict_jwt_config['authorization_server']}"
                        "/oauth/auth"
                        "?response_type=code"
                        f"&scope={consent_scopes}"
                        f"&client_id={self.dict_jwt_credential['ds_client_id']}"
                        f"&redirect_uri={redirect_uri}"
                    )
                return flask.redirect(consent_url)
            else:
                error_body_json = err and hasattr(err, 'body') and err.body
                try:
                    error_body = json.loads(error_body_json)
                except json.decoder.JSONDecodeError:
                    error_body = {}
                error_code = error_body \
                    and 'errorCode' in error_body \
                    and error_body['errorCode']
                error_message = error_body \
                    and 'message' in error_body \
                    and error_body['message']
                if error_code == 'WORKFLOW_UPDATE_RECIPIENTROUTING_NOT_ALLOWED':
                    return flask.render_template('error_eg34.html')
                return flask.render_template(
                    'error.html',
                    err=err,
                    error_code=error_code,
                    error_message=error_message
                )
