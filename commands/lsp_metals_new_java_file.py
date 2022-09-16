from . lsp_metals_text_command import LspMetalsTextCommand
from LSP.plugin.core.types import List
from LSP.plugin.core.url import filename_to_uri  # TODO: deprecated in a future version
from LSP.plugin.execute_command import LspExecuteCommand

import sublime
import sublime_plugin

class LspMetalsNewJavaFileCommand(LspMetalsTextCommand):

    def run(self, edit: sublime.Edit, paths: List[str]) -> None:
        path = paths[0] if paths else self.view.file_name()
        args = {
            "command_name": "new-java-file",
            "command_args": [filename_to_uri(path)]
        }
        self.view.run_command("lsp_metals_execute", args)
