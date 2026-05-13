from . utils import open_location
from typing import List, Any

import sublime_plugin

class LspMetalsMetalsGotoLocationCommand(sublime_plugin.WindowCommand):

    def run(self, parameters: List[Any]) -> None:
        if isinstance(parameters, list) and parameters:
            open_location(self.window, parameters[0])
