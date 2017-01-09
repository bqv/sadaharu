import requests

def sprunge(content):
    data = {'sprunge': content}
    response = requests.post('http://sprunge.us', data)
    return response.text.strip() if response.status_code == 200 else None

def ix(content):
    data = {'f:1': content}
    response = requests.post('http://ix.io', data)
    return response.text.strip() if response.status_code == 200 else None
