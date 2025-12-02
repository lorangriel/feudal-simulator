"""Global Combobox-policy som säkerställer säkra mushjulsval."""
from __future__ import annotations

import logging
from tkinter import ttk

from safe_combobox import apply_safe_combobox_patch

logger = logging.getLogger(__name__)


def apply_combobox_policy() -> None:
    """Aktivera global policy för ``ttk.Combobox``."""

    apply_safe_combobox_patch()
    logger.debug("Comboboxpolicy aktiverad")


def install_default_policy() -> None:
    """Bakåtkompatibel alias för att aktivera policyn."""

    apply_combobox_policy()


__all__ = ["apply_combobox_policy", "install_default_policy", "ttk"]
