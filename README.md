# feudal-simulator

This project is a small prototype for a feudal county simulation. The code
is split across multiple modules under `src/`.

Run the original Tkinter GUI application with:

```
python src/simulator.py
```

A minimal HTTP server that renders the same data as HTML is also available.
Start it with:

```
python src/http_server.py
```

Then open `http://localhost:8000` in a browser.

## Testing
Run `pytest` in the repository root to execute the automated test suite.
