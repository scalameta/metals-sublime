from __future__ import annotations

from .utils import open_location
from typing import Any
from typing import List
import sublime_plugin


class LspMetalsMetalsGotoLocationCommand(sublime_plugin.WindowCommand):

    def run(self, parameters: List[Any]) -> None:
        if isinstance(parameters, list) and parameters:
            open_location(self.window, parameters[0])
