from . lsp_metals_text_command import LspMetalsTextCommand
from . utils import handle_error
from LSP.plugin.core.protocol import Error
from LSP.plugin.core.typing import Any

import sublime

class LspMetalsAnalyzeStacktraceCommand(LspMetalsTextCommand):

    _command_name = 'analyze-stacktrace'

    def run(self, edit: sublime.Edit) -> None:
        sublime.get_clipboard_async(self._send_request)

    def _send_request(self, text: str) -> None:
        session = self.session_by_name(self.session_name)
        if session:
            params = {
                "command": self._command_name,
                "arguments": [text]
            }
            session.execute_command(params, progress=True).then(self._handle_response)

    def _handle_response(self, response: Any) -> None:
        if isinstance(response, Error):
            handle_error(self._command_name, response)
