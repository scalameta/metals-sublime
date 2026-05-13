from __future__ import annotations

from ..core.constants import SESSION_NAME
from LSP.plugin import LspTextCommand


class LspMetalsTextCommand(LspTextCommand):
    session_name = SESSION_NAME
