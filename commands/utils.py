from __future__ import annotations

from ..core.constants import SESSION_NAME
from LSP.plugin import parse_uri
from LSP.plugin import Session
from LSP.plugin.core.registry import windows
from LSP.plugin.core.views import to_encoded_filename
from LSP.protocol import Location
from typing import Any
from typing import Dict
from typing import Optional
import sublime


def handle_error(command: str, error: Dict[str, Any]) -> None:
    msg = "command '{}' failed. Reason: {}".format(command, str(error))
    sublime.error_message(msg)

def get_session(window: sublime.Window) -> Optional[Session]:
    wm = windows.lookup(window)
    metals_session = None
    if wm is not None:
        for session in wm._sessions:
            if session.config.name == SESSION_NAME:
                metals_session = session

    return metals_session

def open_location(window: sublime.Window, location: Location) -> None:
    uri = location['uri']
    r = location['range']
    (_, path) = parse_uri(uri)
    pos = r["start"] if r else {"line": 0, "character": 0}
    window.open_file(to_encoded_filename(path, pos), sublime.ENCODED_POSITION)
