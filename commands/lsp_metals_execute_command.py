from __future__ import annotations

from ..core.constants import SESSION_NAME
from LSP.plugin import LspExecuteCommand


class LspMetalsExecuteCommand(LspExecuteCommand):
    session_name = SESSION_NAME
