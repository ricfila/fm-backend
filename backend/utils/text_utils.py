import re


def to_snake_case(text: str):
    return (
        re.sub(r"(?<=[a-z])(?=[A-Z])|[^a-zA-Z]", "_", text).strip("_").upper()
    )
