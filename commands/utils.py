from LSP.plugin.core.typing import Any, Dict
import sublime

def handle_error(command: str, error: Dict[str, Any]) -> None:
    msg = "command '{}' failed. Reason: {}".format(command, str(error))
    sublime.error_message(msg)
