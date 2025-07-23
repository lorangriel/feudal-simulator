from wsgiref.simple_server import make_server
import urllib.parse

from data_manager import load_worlds_from_file


def load_worlds():
    """Load worlds from disk."""
    try:
        return load_worlds_from_file()
    except Exception:
        return {}


def render_template(title: str, body: str) -> str:
    """Return a basic HTML page."""
    return f"""
    <html>
    <head>
        <meta charset='utf-8'>
        <title>{title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; }}
            th, td {{ border: 1px solid #ccc; padding: 4px 8px; }}
            a {{ text-decoration: none; color: #0645ad; }}
        </style>
    </head>
    <body>
        {body}
    </body>
    </html>
    """


ALL_WORLDS = load_worlds()


def application(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    if path in ('', '/'):  # index
        body = "<h1>Feodal Simulator</h1>\n<h2>Worlds</h2>\n<ul>"
        for name in sorted(ALL_WORLDS.keys()):
            link = urllib.parse.quote(name)
            body += f"<li><a href='/world/{link}'>{name}</a></li>"
        body += "</ul>"
        html = render_template("Feodal Simulator", body)
        start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
        return [html.encode('utf-8')]

    if path.startswith('/world/'):
        name = urllib.parse.unquote(path[len('/world/'):])
        data = ALL_WORLDS.get(name)
        if not data:
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return [b'World not found']
        body = [f"<h1>{name}</h1>"]
        body.append("<table><tr><th>ID</th><th>Name</th><th>Parent</th></tr>")
        for nid, node in data.get('nodes', {}).items():
            display_name = node.get('custom_name') or node.get('name')
            parent = node.get('parent_id')
            body.append(f"<tr><td>{nid}</td><td>{display_name}</td><td>{parent}</td></tr>")
        body.append("</table>")
        body.append("<p><a href='/'>Back</a></p>")
        html = render_template(name, "\n".join(body))
        start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
        return [html.encode('utf-8')]

    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return [b'Not found']


def main(port: int = 8000) -> None:
    """Run a simple web server on ``port``."""
    with make_server('', port, application) as server:
        print(f"Serving on http://localhost:{port}")
        server.serve_forever()


if __name__ == '__main__':
    main()
