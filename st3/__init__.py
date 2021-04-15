from ..common import create_launch_command
from ..common import get_java_path
from ..common import LspMetalsExecuteCommand
from ..common import NewScalaFileCommand
from ..common import prepare_server_properties
from LSP.plugin.core.collections import DottedDict
from LSP.plugin.core.handlers import LanguageHandler
from LSP.plugin.core.protocol import Location, Response
from LSP.plugin.core.settings import ClientConfig, LanguageConfig, read_client_config
import os
import sublime

server_name = 'LSP-metals'
settings_file = 'LSP-metals.sublime-settings'
LspMetalsExecuteCommand.session_name = server_name


class LspMetalsPlugin(LanguageHandler):

    @property
    def name(self) -> str:
        return server_name

    @property
    def config(self) -> ClientConfig:
        settings = sublime.load_settings(settings_file)
        server_version = settings.get('server_version', '0.9.2')
        server_properties = prepare_server_properties(settings.get('server_properties', []))
        java_path = get_java_path(settings)
        init_options = settings.get("initializationOptions")
        # Disable features that aren't available in ST3
        init_options.update({"decorationProvider": False})
        init_options.update({"inlineDecorationProvider": False})
        return read_client_config(self.name, {
            "enabled": True,
            "command": create_launch_command(java_path, server_version, server_properties),
            "initializationOptions": init_options,
            "languages": [{
                "languageId": "scala",
                "scopes": ["source.scala"],
                "syntaxes": ["Packages/Scala/Scala.sublime-syntax"]
            }]
        })

    def on_start(self, window) -> bool:
        plugin_settings = sublime.load_settings(settings_file)
        java_path = get_java_path(plugin_settings)
        if not java_path :
            window.status_message("Please install java or set the 'java_home' setting")
            return False

        server_version = plugin_settings.get('server_version')
        if not server_version :
            window.status_message("'server_version' setting should be set")
            return False

        return True

    def on_initialized(self, client) -> None:
        register_client(client)


def register_client(client):
    client.on_notification(
        "metals/status",
        lambda params: on_metals_status(params))
    client.on_notification(
        "metals/executeClientCommand",
        lambda params: on_execute_client_command(params))
    client.on_request(
        "metals/inputBox",
        lambda params, request_id: on_metals_inputbox(client, params, request_id))

def on_metals_inputbox(client, params, request_id):
    def send_response(input: 'Optional[str]' = None):
        param = { 'value': input, 'cancelled': False } if input else {'cancelled': True}
        client.send_response(Response(request_id, param))

    sublime.active_window().show_input_panel(
        params.get('prompt', ''),
        params.get('value', ''),
        lambda value: send_response(value),
        None,
        lambda: send_response(None)
    )


def on_metals_status(params):
    view = sublime.active_window().active_view()
    hide = params.get('hide', False)
    if(hide):
        view.erase_status(server_name)
    else:
        view.set_status(server_name, params.get('text', ''))

def _open_file(location: Location):
    file_path = location.file_path
    row = location.range.start.row + 1
    col = location.range.start.col + 1
    encoded_file_name = "{}:{}:{}".format(file_path, row, col)
    window = sublime.active_window()
    window.open_file(encoded_file_name, sublime.ENCODED_POSITION)

def on_execute_client_command(params):
    # handle https://scalameta.org/metals/docs/editors/new-editor.html#goto-location-1
    if(params.get('command') == "metals-goto-location"):
        args = params.get('arguments', [])
        if(args):
            location = Location.from_lsp(args[0])
            _open_file(location)
