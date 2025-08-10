Folders
-------

- src/ ....... feudal simulator (python/tk application)
- tests/ ..... tests for feudal simulator (pytest)

- src2/ ...... libsdl 2.0 experimental application (C++)
  - Requires SDL2 development libraries.
  - Build with `make` inside `src2/`.
  - No C++ tests are available; none to run.

Style
-----

- Python code should follow PEP 8 (4-space indentation, descriptive naming, etc.).
- For C++ code, use a consistent brace style; `clang-format` may be used when available.

Notes
-----

- Always add tests when possible.
- Install dependencies with `pip install -r requirements.txt` before running tests.
- Run the test suite from the repository root with `pytest` (e.g., `pytest --cov`).

