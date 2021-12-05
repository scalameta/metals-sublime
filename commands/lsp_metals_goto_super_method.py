from . lsp_metals_text_command import LspMetalsTextCommand
from . utils import handle_error
from LSP.plugin.core.protocol import Error
from LSP.plugin.core.typing import Any
from LSP.plugin.core.views import first_selection_region
from LSP.plugin.core.views import text_document_position_params

import sublime

class LspMetalsSendPositionCommand(LspMetalsTextCommand):
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
        params = {
            "command": command_name,
            "arguments": [document_position]
        }

        def handle_response(response: Any) -> None:
            if isinstance(response, Error) or 'error' in response:
                handle_error(self._commands, response)

        session.execute_command(params, progress=True).then(handle_response)
