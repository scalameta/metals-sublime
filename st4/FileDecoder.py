from LSP.plugin.core.protocol import Error
from LSP.plugin.core.registry import LspTextCommand
from LSP.plugin.core.typing import Any
from LSP.plugin.core.url import filename_to_uri  # TODO: deprecated in a future version

import os
import sublime

class FileDecoderCommand(LspTextCommand):
    session_name = "metals"

    _jvm_extentions = {'java', 'scala', 'class'}
    _tasty_extentions = {'scala', 'tasty'}
    _sematicdb_extentions = {'scala', 'java', 'semanticdb'}
    _decoders = {
            'javap': _jvm_extentions,
            'javap-verbose': _jvm_extentions,
            'cfr': _jvm_extentions,
            'tasty-decoded': _tasty_extentions,
            'semanticdb-compact': _sematicdb_extentions,
            'semanticdb-detailed': _sematicdb_extentions,
            'semanticdb-proto': _sematicdb_extentions
        }

    def is_enabled(self, decoding_type: str) -> bool:
        if super().is_enabled(None, None):
            extension = os.path.splitext(self.view.file_name())[1][1:]
            accepted_extentions = self._decoders.get(decoding_type)
            return extension in accepted_extentions
        else:
            return False

    def run(self, edit: sublime.Edit, decoding_type: str) -> None:
        uri = 'metalsDecode:' + filename_to_uri(self.view.file_name()) + '.' + decoding_type
        session = self.session_by_name(self.session_name)
        if session:
            params = {
                "command": 'file-decode',
                "arguments": [uri]
            }

            def handle_response(response: Any) -> None:
                if isinstance(response, Error) or 'error' in response:
                    error = response['error'] if 'error' in response else response
                    sublime.message_dialog("command 'file-decode' failed. Reason: {}".format(str(error)))
                    return
                elif response and 'value' in response:
                    window = self.view.window()
                    view = window.new_file()
                    view.set_scratch(True)
                    view.set_name(os.path.basename(response['requestedUri']))
                    view.run_command("append", {"characters": response['value']})
                    view.set_read_only(True)

            session.execute_command(params, progress=True).then(handle_response)
