from . lsp_metals_text_command import LspMetalsTextCommand
from . utils import handle_error, create_readonly_dependency_file
from LSP.plugin.core.protocol import Error
from LSP.plugin.core.typing import Any
from LSP.plugin.core.url import filename_to_uri  # TODO: deprecated in a future version

import os
import re
import sublime

class LspMetalsFileDecoderCommand(LspMetalsTextCommand):

    _command = 'file-decode'
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
    _build_target = 'metals-buildtarget'

    def is_enabled(self, decoding_type: str, file_path: str = '') -> bool:
        if super().is_enabled(None, None):
            extension = os.path.splitext(self.view.file_name())[1][1:]
            accepted_extentions = self._decoders.get(decoding_type)
            return decoding_type == self._build_target or decoding_type == 'jar' or (accepted_extentions is not None and extension in accepted_extentions)
        else:
            return False

    def run(self, edit: sublime.Edit, decoding_type: str, file_path: str = '') -> None:
        path = file_path
        if not path:
            path = filename_to_uri(self.view.file_name())

        uri = 'metalsDecode:' + path + '.' + decoding_type
        if decoding_type == 'jar':
            uri = 'metalsDecode:' + path

        session = self.session_by_name(self.session_name)
        if session:
            params = {
                "command": self._command,
                "arguments": [uri]
            }

            def handle_response(response: Any) -> None:
                if isinstance(response, Error) or 'error' in response:
                    handle_error(self._command, response)
                elif response and 'value' in response:
                    window = self.view.window()
                    if decoding_type == 'jar':
                        # extract the jar from uri
                        regex = r"(?:\/(?:.*))+\/(.*\.jar)\!(.*)"
                        matches = re.search(regex, uri)
                        if matches:
                            file_path = matches.group(1) + matches.group(2)
                            folder = window.extract_variables()['folder']
                            full_path = create_readonly_dependency_file(folder, file_path, response['value'])
                            window.open_file(full_path)
                        else:
                            sublime.error_message(f"Unable to extract path from URI: {uri}")
                    else:
                        view = window.new_file()
                        view.set_scratch(True)
                        view.set_name(os.path.basename(response['requestedUri']))
                        view.run_command("append", {"characters": response['value']})
                        view.set_read_only(True)

            session.execute_command(params, progress=True).then(handle_response)
