from ..common import get_java_path
from ..common import NewScalaFileCommand
from LSP.plugin import AbstractPlugin
from LSP.plugin import register_plugin
from LSP.plugin import Response
from LSP.plugin import unregister_plugin
from LSP.plugin.core.types import Optional, Dict, Any
import sublime

# TODO: Bring to public API
from LSP.plugin.core.views import location_to_encoded_filename


class Metals(AbstractPlugin):

    @classmethod
    def name(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def additional_variables(cls) -> Optional[Dict[str, str]]:
        settings = sublime.load_settings("LSP-metals.sublime-settings")
        return {
            "java_path": get_java_path(settings),
            "server_version": str(settings.get("server_version"))
        }

    # notification and request handlers

    def m_metals_status(self, params: Any) -> None:
        if not isinstance(params, dict):
            return
        session = self.weaksession()
        if not session:
            return
        key = "metals-status"
        if params.get("hide", False):
            session.set_window_status_async(key, params.get('text', ''))
        else:
            session.erase_window_status_async(key)

    def m_metals_executeClientCommand(self, params: Any) -> None:
        # handle https://scalameta.org/metals/docs/editors/new-editor.html#goto-location-1
        if not isinstance(params, dict):
            return
        if params.get('command') == "metals-goto-location":
            args = params.get('arguments')
            if isinstance(args, list) and args:
                session = self.weaksession()
                if session:
                    session.window.open_file(
                        location_to_encoded_filename(args[0]),
                        flags=sublime.ENCODED_POSITION
                    )

    def m_metals_inputBox(self, params: Any, request_id: Any) -> None:
        if not isinstance(params, dict):
            return
        session = self.weaksession()
        if not session:
            return

        def send_response(input: Optional[str]):
            p = { 'value': input, 'cancelled': False } if input else {'cancelled': True}
            session.send_response(Response(request_id, p))

        session.window.show_input_panel(
            params.get('prompt', ''),
            params.get('value', ''),
            send_response,
            None,
            lambda: send_response(None)
        )


def plugin_loaded() -> None:
    register_plugin(Metals)


def plugin_unloaded() -> None:
    unregister_plugin(Metals)
