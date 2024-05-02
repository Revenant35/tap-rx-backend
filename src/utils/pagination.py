def create_next_token(fields: list[str], delimiter: str) -> str | None:
    if not fields or not delimiter:
        return None

    next_token = fields[0]
    for field in fields[1:]:
        next_token += delimiter + field
    return next_token


def parse_start_tkn(start_token: str | None, delimiter: str, expected_len: int = None) -> list[str | None] | None:
    if start_token is None:
        return [None] * expected_len if expected_len else None
    start_token_fields = start_token.split(delimiter)
    return start_token_fields
