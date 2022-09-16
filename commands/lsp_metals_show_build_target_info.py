from . lsp_metals_text_command import LspMetalsTextCommand
from . utils import handle_error
from LSP.plugin.core.protocol import Error
from LSP.plugin.core.types import List, Any

import sublime


class LspMetalsShowBuildTargetInfoCommand(LspMetalsTextCommand):
    _command_name = 'list-build-targets'

    def run(self, edit: sublime.Edit) -> None:
        session = self.session_by_name(self.session_name)
        if session:
            params = {
              "command": self._command_name
            }
            session.execute_command(params, progress=True).then(self._handle_response)

    def _handle_response(self, response: Any) -> None:
        if isinstance(response, Error):
            handle_error(self._command_name, response)
        elif isinstance(response, list) and response:
            self.view.window().show_quick_panel(
                response,
                lambda i: self._on_select(response, i),
                placeholder="Select the build target to display")

    def _on_select(self, items: List[str], index: int) -> None:
        if index >= 0:
            session = self.session_by_name(self.session_name)
            root = session._workspace_folders[0]
            target_name = items[index]
            path  = "file:///{}/{}".format(root, target_name)
            self.view.run_command("lsp_metals_file_decoder", {"decoding_type": "metals-buildtarget", "file_path": path})


