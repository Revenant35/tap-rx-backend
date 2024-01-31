import flask
import functions_framework


@functions_framework.http
def register_user_handler(request: flask.request) -> flask.Response:
    try:
        request_json = request.get_json(silent=True)
        username = request_json["username"]
        first_name = request_json["first_name"]
        last_name = request_json["last_name"]
        email = request_json["email"]
        phone = request_json["phone"]
    except:
        return flask.make_response("Invalid request", 400)

    return flask.make_response("That worked!")


