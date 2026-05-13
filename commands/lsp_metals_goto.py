from __future__ import annotations

from .utils import get_session
from .utils import handle_error
from LSP.plugin.core.protocol import Error
from typing import Any
from typing import List
import sublime_plugin


class LspMetalsGoto(sublime_plugin.WindowCommand):
    _command_name = 'goto'
    def run(self, parameters: List[Any]) -> None:
        session = get_session(self.window)
        if session:
            params = {
                "command": self._command_name,
                "arguments": parameters
            }
            session.execute_command(params, progress=True).then(self._handle_response)

    def _handle_response(self, response: Any) -> None:
        if isinstance(response, Error):
            handle_error(self._command_name, response)

