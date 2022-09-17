from . lsp_metals_execute_command import LspMetalsExecuteCommand
from LSP.plugin.core.types import List, Any

import os

class LspMetalsShowBuildTargetInfoCommand(LspMetalsExecuteCommand):

    def handle_success_async(self, result: Any, command_name: str) -> None:
        if isinstance(result, list) and result:
            self.view.window().show_quick_panel(
                result,
                lambda i: self._on_select(result, i),
                placeholder="Select the build target to display")

    def _on_select(self, items: List[str], index: int) -> None:
        if index >= 0:
            session = self.session_by_name(self.session_name)
            root = session.get_workspace_folders()[0]
            target_name = items[index]
            path  = os.path.join(root.uri(), target_name)
            self.view.run_command("lsp_metals_file_decoder", {"decoding_type": "metals-buildtarget", "file_path": path})
