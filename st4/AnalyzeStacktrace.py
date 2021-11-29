from LSP.plugin.core.protocol import Error
from LSP.plugin.core.registry import LspTextCommand
from LSP.plugin.core.typing import Any

import sublime
import sublime_plugin

from urllib.parse import urlparse,unquote
import re
import json

class AnalyzeStacktraceCommand(LspTextCommand):
    session_name = "metals"

    def run(self, edit: sublime.Edit) -> None:
        sublime.get_clipboard_async(self._send_request)

    def _send_request(self, text) -> None:
        session = self.session_by_name(self.session_name)
        if session:
            params = {
                "command": 'analyze-stacktrace',
                "arguments": [text]
            }
            session.execute_command(params, progress=True).then(self._handle_response)

    def _handle_response(self, response: Any) -> None:
        if isinstance(response, Error) or 'error' in response:
            error = response['error'] if 'error' in response else response
            sublime.message_dialog("command 'analyze-stacktrace' failed. Reason: {}".format(str(error)))
            return
