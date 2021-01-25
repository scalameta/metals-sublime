from ..common import create_launch_command
from ..common import get_java_path
from ..common import NewScalaFileCommand
from ..common import LspMetalsExecuteCommand
from ..common import prepare_server_properties
from LSP.plugin import AbstractPlugin
from LSP.plugin import register_plugin
from LSP.plugin import Response
from LSP.plugin import unregister_plugin
from LSP.plugin import WorkspaceFolder
from LSP.plugin import ClientConfig
from LSP.plugin.core.types import Optional, Dict, Any, Tuple, List
import sublime

# TODO: Bring to public API
from LSP.plugin.core.views import location_to_encoded_filename


class Metals(AbstractPlugin):

    @classmethod
    def name(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def configuration(cls) -> Tuple[sublime.Settings, str]:
        settings, path = super().configuration()
        java_path = get_java_path(settings)
        version = settings.get("server_version")
        properties = prepare_server_properties(settings.get("server_properties"))
        command = create_launch_command(java_path, version, properties)
        settings.set("command", command)
        return settings, path

    @classmethod
    def can_start(
        cls,
        window: sublime.Window,
        initiating_view: sublime.View,
        workspace_folders: List[WorkspaceFolder],
        configuration: ClientConfig
    ) -> Optional[str]:
        if not workspace_folders :
            return "No workspace detected. Try opening your project at the workspace root."

        plugin_settings = sublime.load_settings("LSP-metals.sublime-settings")
        java_path = get_java_path(plugin_settings)
        if not java_path :
            return "Please install java or set the 'java_home' setting"
        server_version = plugin_settings.get('server_version')
        if not server_version :
            return "'server_version' setting should be set"

    # notification and request handlers

    def m_metals_status(self, params: Any) -> None:
        """Handle the metals/status notification."""
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
        """Handle the metals/executeClientCommand notification."""
        # https://scalameta.org/metals/docs/editors/new-editor.html#goto-location-1
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
        """Handle the metals/inputBox request."""
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
