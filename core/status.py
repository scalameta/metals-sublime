from LSP.plugin import Session
from LSP.plugin.core.types import Any

status_key = "metals-status"


def handle_status(session: Session, params: Any) -> None:
    """Handle the metals/status notification."""

    if not isinstance(params, dict):
        return
    hide = params.get("hide") if isinstance(params.get("hide"), bool) else False
    if not hide:
        session.set_window_status_async(status_key, params.get('text', ''))
    else:
        session.erase_window_status_async(status_key)
