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


def test_world_page(monkeypatch):
    world = {
        'nodes': {
            1: {'name': 'Root', 'parent_id': 0},
            2: {'custom_name': 'Child', 'parent_id': 1}
        }
    }
    monkeypatch.setattr(http_server, 'ALL_WORLDS', {'World': world})
    res = run_app('/world/World')
    assert res['status'].startswith('200')
    assert '<td>1</td>' in res['body']
    assert '<td>Child</td>' in res['body']
    assert "Back" in res['body']


def test_unknown_path():
    res = run_app('/unknown')
    assert res['status'].startswith('404')
    assert res['body'] == 'Not found'


def test_load_worlds_error(monkeypatch):
    def boom():
        raise RuntimeError('fail')
    monkeypatch.setattr(http_server, 'load_worlds_from_file', boom)
    assert http_server.load_worlds() == {}


def test_main_starts_server(monkeypatch, capsys):
    called = {}

    class DummyServer:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            called['closed'] = True
        def serve_forever(self):
            called['served'] = True

    def fake_make_server(host, port, app):
        called['args'] = (host, port, app)
        return DummyServer()

    monkeypatch.setattr(http_server, 'make_server', fake_make_server)
    http_server.main(1234)
    assert called['args'] == ('', 1234, http_server.application)
    assert called.get('served')
    assert called.get('closed')
    out = capsys.readouterr().out
    assert 'http://localhost:1234' in out
