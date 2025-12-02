"""Entry point for the feudal county simulator."""
import sys

try:
    from src.ui import app as ui_app_module
except ImportError:
    from ui import app as ui_app_module

ui_main = ui_app_module.main


_override = sys.modules.get("feodal_simulator")
if _override is not None and hasattr(_override, "main") and not hasattr(
    _override, "__file__"
):
    main = _override.main  # type: ignore[assignment]
else:
    main = ui_main


if __name__ == "__main__":
    main()
