import shutil
import os
import sublime
from LSP.plugin.core.handlers import LanguageHandler
from LSP.plugin.core.settings import ClientConfig, LanguageConfig

config_name = 'metals-sublime'
server_name = 'metals-sublime'
service_name = "metals-sublime"
coursierPath = os.path.join(os.path.dirname(__file__), './coursier')
service_path = []

def metals_is_running() -> bool:
    return shutil.which(service_name) is not None

def get_java_path(java_path: 'Optional[str]') -> 'Optional[str]':
    if java_path:
        return java_path + "/bin/java"
    elif shutil.which("java") is not None:
        return "java"
    else:
        return None

def plugin_loaded():
    global service_path
    plugin_settings = sublime.load_settings("metals-sublime.sublime-settings")

    java_path = get_java_path(plugin_settings.get('java_home'))
    if not java_path :
        window.status_message("Please install java or set the 'java_home' setting")

    server_version = plugin_settings.get('server_version')
    if not server_version :
        window.status_message("'server_version' should be set")

    server_properties = prepare_server_properties(plugin_settings.get('server_properties', []))

    service_path = [
        java_path,
        "-jar",
        coursierPath,
        "fetch",
        "-p",
        "--ttl",
        "Inf",
        "org.scalameta:metals_2.12:{}".format(server_version),
        "-r",
        "bintray:scalacenter/releases",
        "-r",
        "sonatype:public",
        "-r",
        "sonatype:snapshots",
        "-p"
    ]

metals_config = ClientConfig(
    name=config_name,
    binary_args=service_path,
    tcp_port=None,
    languages=[
        LanguageConfig(
            "scala",
            ["source.scala"],
            ["Packages/Scala/Scala.sublime-syntax"]
        )
    ],
    enabled=False,
    init_options=dict(),
    settings=dict(),
    env=dict())

class LspMetalsPlugin(LanguageHandler):
    def __init__(self):
        self._name = config_name
        self._config = metals_config

    @property
    def name(self) -> str:
        return self._name

    @property
    def config(self) -> ClientConfig:
        return self._config

    def on_start(self, window) -> bool:
        plugin_settings = sublime.load_settings("metals-sublime.sublime-settings")

        # if not metals_is_running():
        #     window.status_message(
        #         "Metals must be installed to run {}".format(server_name))
        #     return False

        print("#### {}".format(service_path))
        if not service_path:
            return False

        return True

    def on_initialized(self, client) -> None:
        register_client(client)


def register_client(client):
    client.on_notification(
        "metals/status",
        lambda params: on_metals_status(params))


def on_metals_status(params):
    view = sublime.active_window().active_view()
    hide = params.get('hide', False)
    if(hide):
        view.erase_status(server_name)
    else:
        view.set_status(server_name, params.get('text', ''))

def prepare_server_properties(properties: 'List[str]') -> str:
    stripped = map(lambda p: p.strip(), properties)
    none_empty = list(filter(None, stripped))
    result = ''
    if none_empty:
        result = ' '.join(none_empty)

    return result
