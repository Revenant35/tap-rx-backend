from functools import wraps

from flask import request

from src.models.errors.invalid_request_error import InvalidRequestError


def validate_json(*expected_args):
    def decorator_validate_json(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            request_json = request.get_json()
            for arg in expected_args:
                if arg not in request_json:
                    raise InvalidRequestError(f"Missing required field: {arg}")
            return f(*args, **kwargs)
        return decorated_function
    return decorator_validate_json
