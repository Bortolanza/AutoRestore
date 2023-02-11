from flask_session import Session


def checksessioninfo(info):
    if info is not None:
        return True
    return False
