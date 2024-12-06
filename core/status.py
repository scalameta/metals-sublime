from LSP.plugin import Session
from LSP.plugin.core.types import Any


def handle_status(session: Session, params: Any) -> None:
    """Handle the metals/status notification."""

    if not isinstance(params, dict):
        return
    hide = params.get("hide") if isinstance(params.get("hide"), bool) else False
    if not hide:
        session.set_config_status_async(params.get('text', ''))
    else:
        session.set_config_status_async('')
