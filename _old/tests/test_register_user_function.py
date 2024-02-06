import json
from unittest.mock import MagicMock, patch

import firebase_admin
import flask
import pytest

from _old.functions.register_user_function import main
from functions.register_user_function.localpackage import register_user

FIREBASE_KEY = "FIREBASE_DATABASE_KEY"
FIREBASE_DATABASE_URL = "FIREBASE_DATABASE_URL"


def test_register_user_handler_when_store_succeeds_returns_200():
    username = "test_user"
    first_name = "John"
    last_name = "Doe"
    email = "john.doe@example.com"
    phone = "123-456-7890"

    request_json = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone
    }

    request = flask.Request(request_json)

    fb_key_env = "{'key': 'value'}"
    fb_db_url_env = "test_url"
    mock_db_user_ref = MagicMock()

    with patch('flask.Request.get_json', return_value=request_json), \
            patch('functions.register_user_function.main.get_env_var', side_effect=[fb_key_env, fb_db_url_env]), \
            patch('json.loads', return_value={'key': 'value'}), \
            patch('functions.register_user_function.localpackage.register_user.initialize_firebase_app', return_value=None), \
            patch('firebase_admin.db.reference', return_value=mock_db_user_ref), \
            patch('functions.register_user_function.localpackage.register_user.store_user', return_value=None):
        response = main.register_user_handler(request)
        assert response == ("OK", 200)


def test_register_user_handler_when_invalid_request_json_return_400():
    username = "test_user"
    first_name = "John"
    last_name = "Doe"

    # missing email and phone
    request_json = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name
    }

    request = flask.Request(request_json)

    with patch('flask.Request.get_json', return_value=request_json):
        response = main.register_user_handler(request)
        assert response == ("Invalid request", 400)


def test_register_user_handler_firebase_key_invalid_return_500():
    username = "test_user"
    first_name = "John"
    last_name = "Doe"
    email = "john.doe@example.com"
    phone = "123-456-7890"

    request_json = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone
    }

    request = flask.Request(request_json)

    # invalid json
    fb_key_env = "{'key': }"
    fb_db_url_env = "test_url"

    with patch('flask.Request.get_json', return_value=request_json), \
            patch('functions.register_user_function.main.get_env_var', side_effect=[fb_key_env, fb_db_url_env]), \
            patch('json.loads', side_effect=json.JSONDecodeError("test", "test", 0)):
        response = main.register_user_handler(request)
        assert response == ("Internal server error", 500)


def test_register_user_handler_when_firebase_key_not_set_return_500():
    username = "test_user"
    first_name = "John"
    last_name = "Doe"
    email = "john.doe@example.com"
    phone = "123-456-7890"

    request_json = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone
    }

    request = flask.Request(request_json)

    with patch('flask.Request.get_json', return_value=request_json), \
            patch('functions.register_user_function.main.get_env_var', side_effect=ValueError()), \
            patch('json.loads', return_value={'key': 'value'}):
        response = main.register_user_handler(request)
        assert response == ("Internal server error", 500)


def test_register_user_handler_when_firebase_url_not_set_return_500():
    username = "test_user"
    first_name = "John"
    last_name = "Doe"
    email = "john.doe@example.com"
    phone = "123-456-7890"

    request_json = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone
    }

    request = flask.Request(request_json)

    fb_key_env = "{'key': 'value'}"

    with patch('flask.Request.get_json', return_value=request_json), \
            patch('functions.register_user_function.main.get_env_var', side_effect=[fb_key_env, ValueError()]), \
            patch('json.loads', return_value={'key': 'value'}):
        response = main.register_user_handler(request)
        assert response == ("Internal server error", 500)


def test_register_user_handler_when_initializing_app_fails_return_500():
    username = "test_user"
    first_name = "John"
    last_name = "Doe"
    email = "john.doe@example.com"
    phone = "123-456-7890"

    request_json = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone
    }

    request = flask.Request(request_json)

    fb_key_env = "{'key': 'value'}"
    fb_db_url_env = "test_url"

    with patch('flask.Request.get_json', return_value=request_json), \
            patch('functions.register_user_function.main.get_env_var', side_effect=[fb_key_env, fb_db_url_env]), \
            patch('json.loads', return_value={'key': 'value'}), \
            patch('functions.register_user_function.localpackage.register_user.initialize_firebase_app', side_effect=ValueError("test")):
        response = main.register_user_handler(request)
        assert response == ("Internal server error", 500)


def test_register_user_handler_when_db_ref_is_invalid_return_500():
    username = "test_user"
    first_name = "John"
    last_name = "Doe"
    email = "john.doe@example.com"
    phone = "123-456-7890"

    request_json = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone
    }

    request = flask.Request(request_json)

    fb_key_env = "{'key': 'value'}"
    fb_db_url_env = "test_url"
    mock_db_user_ref = MagicMock()

    with patch('flask.Request.get_json', return_value=request_json), \
            patch('functions.register_user_function.main.get_env_var', side_effect=[fb_key_env, fb_db_url_env]), \
            patch('json.loads', return_value={'key': 'value'}), \
            patch('functions.register_user_function.localpackage.register_user.initialize_firebase_app', return_value=None), \
            patch('firebase_admin.db.reference', side_effect=ValueError("test")):
        response = main.register_user_handler(request)
        assert response == ("Internal server error", 500)


def test_register_user_handler_when_store_fails_return_500():
    username = "test_user"
    first_name = "John"
    last_name = "Doe"
    email = "john.doe@example.com"
    phone = "123-456-7890"

    request_json = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone
    }

    request = flask.Request(request_json)

    fb_key_env = "{'key': 'value'}"
    fb_db_url_env = "test_url"
    mock_db_user_ref = MagicMock()

    with patch('flask.Request.get_json', return_value=request_json), \
            patch('functions.register_user_function.main.get_env_var', side_effect=[fb_key_env, fb_db_url_env]), \
            patch('json.loads', return_value={'key': 'value'}), \
            patch('functions.register_user_function.localpackage.register_user.initialize_firebase_app', return_value=None), \
            patch('firebase_admin.db.reference', return_value=mock_db_user_ref), \
            patch('functions.register_user_function.localpackage.register_user.store_user', side_effect=ValueError("test")):
        response = main.register_user_handler(request)
        assert response == ("Internal server error", 500)


def test_register_user_handler_when_user_already_exists_return_409():
    username = "test_user"
    first_name = "John"
    last_name = "Doe"
    email = "john.doe@example.com"
    phone = "123-456-7890"

    request_json = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone
    }

    request = flask.Request(request_json)

    fb_key_env = "{'key': 'value'}"
    fb_db_url_env = "test_url"
    mock_db_user_ref = MagicMock()

    with patch('flask.Request.get_json', return_value=request_json), \
            patch('functions.register_user_function.main.get_env_var', side_effect=[fb_key_env, fb_db_url_env]), \
            patch('json.loads', return_value={'key': 'value'}), \
            patch('functions.register_user_function.localpackage.register_user.initialize_firebase_app', return_value=None), \
            patch('firebase_admin.db.reference', return_value=mock_db_user_ref), \
            patch('functions.register_user_function.localpackage.register_user.store_user', side_effect=register_user.UserAlreadyExistsError()):
        response = main.register_user_handler(request)
        assert response == ("User already exists", 409)


def test_store_user_when_store_succeeds_returns_none():
    username = "test_user"
    first_name = "John"
    last_name = "Doe"
    email = "john.doe@example.com"
    phone = "123-456-7890"

    mock_db_user_ref = MagicMock()
    mock_db_user_ref.child(username).set.return_value = None

    with patch('functions.register_user_function.localpackage.register_user.check_user_exists', return_value=False):
        register_user.store_user(mock_db_user_ref, username, first_name, last_name, email, phone)

    mock_db_user_ref.child(username).set.assert_called_once_with({
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        'medications': [],
        'dependents': [],
        'monitored_by': [],
        'monitoring': []
    })

    # Additional assertion to check that set() was not called with other arguments
    mock_db_user_ref.child(username).set.assert_called_once()


def test_store_user_when_user_already_exists_raises_user_already_exists_error():
    username = "test_user"
    first_name = "John"
    last_name = "Doe"
    email = "john.doe@example.com"
    phone = "123-456-7890"

    mock_db_user_ref = MagicMock()
    mock_db_user_ref.child(username).set.return_value = MagicMock()
    with patch('functions.register_user_function.localpackage.register_user.check_user_exists', return_value=True):
        with pytest.raises(register_user.UserAlreadyExistsError):
            register_user.store_user(mock_db_user_ref, username, first_name, last_name, email, phone)


def test_store_user_when_firebase_fails_raises_firebase_error():
    username = "test_user"
    first_name = "John"
    last_name = "Doe"
    email = "john.doe@example.com"
    phone = "123-456-7890"

    mock_db_user_ref = MagicMock()
    mock_db_user_ref.child(username).set.side_effect = firebase_admin.exceptions.FirebaseError(8, "test")

    with patch('functions.register_user_function.localpackage.register_user.check_user_exists', return_value=False):
        with pytest.raises(firebase_admin.exceptions.FirebaseError):
            register_user.store_user(mock_db_user_ref, username, first_name, last_name, email, phone)


def test_store_user_when_child_is_invalid_raises_value_error():
    username = None
    first_name = "John"
    last_name = "Doe"
    email = "john.doe@example.com"
    phone = "123-456-7890"

    mock_db_user_ref = MagicMock()
    mock_db_user_ref.child(username).set.side_effect = ValueError("test")
    with patch('functions.register_user_function.localpackage.register_user.check_user_exists', return_value=False):
        with pytest.raises(ValueError):
            register_user.store_user(mock_db_user_ref, username, first_name, last_name, email, phone)


def test_initialize_firebase_app_when_initialize_succeeds_returns_none():
    mock_fb_key_dict = {'key': 'value'}
    mock_fb_db_url = "test_url"
    mock_cred = MagicMock()

    with patch('firebase_admin._apps', new_callable=MagicMock) as mock_apps, \
            patch('firebase_admin.credentials.Certificate', return_value=mock_cred), \
            patch('firebase_admin.initialize_app', return_value=None) as mock_init_app:
        mock_apps.__bool__.return_value = False

        register_user.initialize_firebase_app(mock_fb_key_dict, mock_fb_db_url)
        mock_init_app.assert_called_once_with(mock_cred, {
            "databaseURL": mock_fb_db_url
        })


def test_initialize_firebase_app_when_app_already_exists_returns_none():
    mock_fb_key_dict = {'key': 'value'}
    mock_fb_db_url = "test_url"
    mock_cred = MagicMock()

    with patch('firebase_admin._apps', new_callable=MagicMock) as mock_apps, \
            patch('firebase_admin.credentials.Certificate', return_value=mock_cred), \
            patch('firebase_admin.initialize_app', return_value=None) as mock_init_app:
        mock_apps.__bool__.return_value = True

        register_user.initialize_firebase_app(mock_fb_key_dict, mock_fb_db_url)
        mock_init_app.assert_not_called()


def test_initialize_firebase_app_when_certificate_cant_be_read_raise_io_error():
    mock_fb_key_dict = {'key': 'value'}
    mock_fb_db_url = "test_url"

    with patch('firebase_admin._apps', new_callable=MagicMock) as mock_apps, \
            patch('firebase_admin.credentials.Certificate', side_effect=IOError("test")):
        mock_apps.__bool__.return_value = False
        with pytest.raises(IOError):
            register_user.initialize_firebase_app(mock_fb_key_dict, mock_fb_db_url)


def test_initialize_firebase_app_when_certificate_is_invalid_raise_value_error():
    mock_fb_key_dict = {'key': 'value'}
    mock_fb_db_url = "test_url"

    with patch('firebase_admin._apps', new_callable=MagicMock) as mock_apps, \
            patch('firebase_admin.credentials.Certificate', side_effect=ValueError("test")):
        mock_apps.__bool__.return_value = False
        with pytest.raises(ValueError):
            register_user.initialize_firebase_app(mock_fb_key_dict, mock_fb_db_url)


def test_initialize_firebase_app_when_app_is_invalid_or_already_exists_raise_value_error():
    mock_fb_key_dict = {'key': 'value'}
    mock_fb_db_url = "test_url"
    mock_cred = MagicMock()

    with patch('firebase_admin._apps', new_callable=MagicMock) as mock_apps, \
            patch('firebase_admin.credentials.Certificate', return_value=mock_cred), \
            patch('firebase_admin.initialize_app', side_effect=ValueError("test")):
        mock_apps.__bool__.return_value = False
        with pytest.raises(ValueError):
            register_user.initialize_firebase_app(mock_fb_key_dict, mock_fb_db_url)


def test_get_env_var_when_var_is_set_returns_var_value(monkeypatch):
    var = "test"
    expected = "test_value"

    monkeypatch.setenv(var, expected)
    actual = main.get_env_var(var)

    assert actual == expected


def test_get_env_var_when_var_is_not_set_raises_value_error(monkeypatch):
    var = "test"

    with pytest.raises(ValueError):
        main.get_env_var(var)


def test_get_env_var_when_var_is_empty_raises_value_error(monkeypatch):
    var = ""

    with pytest.raises(ValueError):
        main.get_env_var(var)


def test_get_env_var_when_var_is_none_raises_value_error(monkeypatch):
    var = None

    with pytest.raises(ValueError):
        main.get_env_var(var)
