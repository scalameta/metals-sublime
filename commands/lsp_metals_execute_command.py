from __future__ import annotations

from ..core.constants import SESSION_NAME
from LSP.plugin.execute_command import LspExecuteCommand  # TODO: bring to public API


class LspMetalsExecuteCommand(LspExecuteCommand):
    session_name = SESSION_NAME
