from __future__ import annotations

from LSP.plugin import Promise
from LSP.plugin import Session
from typing import Any


def handle_input_box(session: Session, params: Any) -> Promise[Any]:
    """Handle the metals/inputBox request."""
    if not isinstance(params, dict):
        return Promise.resolve({'cancelled': True})

    promise, resolve = Promise.packaged_task()

    def send_response(input: str | None) -> None:
        resolve({'value': input, 'cancelled': False} if input else {'cancelled': True})

    session.window.show_input_panel(
        params.get('prompt', ''),
        params.get('value', ''),
        send_response,
        None,
        lambda: send_response(None)
    )
    return promise
