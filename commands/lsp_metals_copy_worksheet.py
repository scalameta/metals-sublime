from . lsp_metals_text_command import LspMetalsTextCommand
from . utils import handle_error
from LSP.plugin.core.protocol import Error
from LSP.plugin.core.typing import Any
from LSP.plugin.core.url import filename_to_uri  # TODO: deprecated in a future version

import sublime

class LspMetalsCopyWorksheetCommand(LspMetalsTextCommand):

    _command_name = 'copy-worksheet-output'

    def is_enabled(self) -> bool:
        if super().is_enabled(None, None):
            return self.view.file_name().endswith('.worksheet.sc')
        else:
            return False

    def run(self, edit: sublime.Edit) -> None:
        file_name = self.view.file_name()
        session = self.session_by_name(self.session_name)
        if self.view.is_dirty():
            sublime.message_dialog('Please save your worksheet before using this command.')
        elif session:
            uri = filename_to_uri(file_name)
            params = {
                "command": self._command_name,
                "arguments": [uri]
            }
            session.execute_command(params, progress=True).then(self._handle_response)

    def _handle_response(self, response: Any) -> None:
        if isinstance(response, Error):
            handle_error(self._command_name, response)
        elif 'value' in response:
            sublime.set_clipboard(response['value'])
