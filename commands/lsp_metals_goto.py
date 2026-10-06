from __future__ import annotations

from .utils import get_session
from .utils import handle_error
from LSP.plugin import Error
from LSP.protocol import ExecuteCommandParams
from typing import Any
import sublime_plugin


class LspMetalsGoto(sublime_plugin.WindowCommand):
    _command_name = 'goto'
    def run(self, parameters: list[Any]) -> None:
        session = get_session(self.window)
        if session:
            params: ExecuteCommandParams = {
                "command": self._command_name,
                "arguments": parameters
            }
            session.execute_command(params, progress=True).then(self._handle_response)

    def _handle_response(self, response: Any) -> None:
        if isinstance(response, Error):
            handle_error(self._command_name, response)

