import types
from wsgiref.util import setup_testing_defaults

import src.http_server as http_server


def run_app(path):
    environ = {}
    setup_testing_defaults(environ)
    environ['PATH_INFO'] = path
    captured = {}

    def start_response(status, headers):
        captured['status'] = status
        captured['headers'] = headers
    body = b"".join(http_server.application(environ, start_response))
    captured['body'] = body.decode('utf-8')
    return captured


def test_index_page(monkeypatch):
    monkeypatch.setattr(http_server, 'ALL_WORLDS', {'A': {}, 'B': {}})
    res = run_app('/')
    assert res['status'].startswith('200')
    assert 'Feodal Simulator' in res['body']
    assert 'A' in res['body']
    assert 'B' in res['body']


def test_missing_world(monkeypatch):
    monkeypatch.setattr(http_server, 'ALL_WORLDS', {})
    res = run_app('/world/none')
    assert res['status'].startswith('404')

