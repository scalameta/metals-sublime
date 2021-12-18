from .. commands.lsp_metals_text_command import LspMetalsTextCommand
from .. core.constants import SESSION_NAME
from LSP.plugin.execute_command import LspExecuteCommand  # TODO: bring to public API


class LspMetalsExecuteCommand(LspExecuteCommand):
    session_name = SESSION_NAME
