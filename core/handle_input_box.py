from LSP.plugin import Response, Session
from LSP.plugin.core.types import Optional, Any


def handle_input_box(session: Session, params: Any, request_id: Any) -> None:
    """Handle the metals/inputBox request."""
    if not isinstance(params, dict):
        return

    def send_response(input: Optional[str]) -> None:
        p = {'value': input, 'cancelled': False} if input else {'cancelled': True}
        session.send_response(Response(request_id, p))

    session.window.show_input_panel(
        params.get('prompt', ''),
        params.get('value', ''),
        send_response,
        None,
        lambda: send_response(None)
    )
