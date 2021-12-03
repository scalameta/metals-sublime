from LSP.plugin.core.types import Any
from LSP.plugin.core.sessions import Session

def handle_status(session: Session, params: Any) -> None:
    """Handle the metals/status notification."""

    if not isinstance(params, dict):
        return
    key = "metals-status"
    hide = params.get("hide") if isinstance(params.get("hide"), bool) else False
    if not hide:
        session.set_window_status_async(key, params.get('text', ''))
    else:
        session.erase_window_status_async(key)
