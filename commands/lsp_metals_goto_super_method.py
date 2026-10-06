from __future__ import annotations

from .utils import handle_error
from LSP.plugin import Error
from LSP.plugin import first_selection_region
from LSP.plugin import LspTextCommand
from LSP.plugin import text_document_position_params
from LSP.protocol import ExecuteCommandParams
from typing import Any
import sublime


class LspMetalsSendPositionCommand(LspTextCommand):
    _commands = {'goto-super-method', 'super-method-hierarchy'}

    def run(self, edit: sublime.Edit, command_name: str) -> None:
        if not command_name in self._commands:
            return
        region = first_selection_region(self.view)
        if region is None:
            return
        session = self.session_by_name(self.session_name)
        if not session:
            return

        point = region.begin()
        document_position = text_document_position_params(self.view, point)
        params: ExecuteCommandParams = {
            "command": command_name,
            "arguments": [document_position]
        }

        def handle_response(response: Any) -> None:
            if isinstance(response, Error) or 'error' in response:
                handle_error(command_name, response)

        session.execute_command(params, progress=True).then(handle_response)
