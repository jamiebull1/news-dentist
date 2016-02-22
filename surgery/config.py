import requests

def get_session():
    return requests.session()

current_session = get_session()