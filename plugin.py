import shutil
import os
import sublime
from LSP.plugin.core.handlers import LanguageHandler
from LSP.plugin.core.settings import ClientConfig, LanguageConfig
from LSP.plugin.core.url import uri_to_filename
from LSP.plugin.core.protocol import Location


server_name = 'metals-sublime'
settings_file = 'metals-sublime.sublime-settings'
coursierPath = os.path.join(os.path.dirname(__file__), './coursier')

def get_java_path(java_path: 'Optional[str]') -> 'Optional[str]':
    path = None
    java_home = os.environ.get('JAVA_HOME')

    if java_path:
        path = java_path + "/bin/java"
    elif java_home:
        path = java_home + "/bin/java"
    elif shutil.which("java") is not None:
        path = "java"

    return path

def create_launch_command(java_path: str, artifactVersion: str, serverProperties: 'List[str]') -> 'List[str]':
    command = [java_path] + serverProperties + [
        "-jar",
        coursierPath,
        "launch",
        "--ttl",
        "Inf",
        "--repository",
        "bintray:scalacenter/releases",
        "--repository",
        "sonatype:snapshots",
        "--main-class",
        "scala.meta.metals.Main",
        "org.scalameta:metals_2.12:{}".format(artifactVersion)
    ]
    return command

class LspMetalsPlugin(LanguageHandler):
    def __init__(self):
        missing_java_home = "Unable to find a Java 8 or Java 11 installation on this computer. Please set `java_home` in the settings."
        plugin_settings = sublime.load_settings(settings_file)
        server_version = plugin_settings.get('server_version')
        server_properties = prepare_server_properties(plugin_settings.get('server_properties', []))
        java_path = get_java_path(plugin_settings.get('java_home'))

        launch_command = []
        if java_path and server_version :
            launch_command = create_launch_command(java_path, server_version, server_properties)
        if java_path is None:
            sublime.error_message(missing_java_home)

        try:
            # ST4
            language = LanguageConfig("scala")
        except TypeError:
            # ST3
            language = LanguageConfig(
                language_id="scala",
                scopes=["source.scala"],
                syntaxes=["Packages/Scala/Scala.sublime-syntax"])

        metals_config = ClientConfig(
            name=server_name,
            binary_args=launch_command,
            tcp_port=None,
            languages=[language],
            enabled=True,
            init_options=dict(),
            settings=dict(),
            env=dict())
        self._name = server_name
        self._config = metals_config

    @property
    def name(self) -> str:
        return self._name

    @property
    def config(self) -> ClientConfig:
        return self._config

    def on_start(self, window) -> bool:
        plugin_settings = sublime.load_settings(settings_file)
        java_path = get_java_path(plugin_settings.get('java_home'))
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

def prepare_server_properties(properties: 'List[str]') -> 'List[str]':
    stripped = map(lambda p: p.strip(), properties)
    none_empty = list(filter(None, stripped))
    return none_empty
