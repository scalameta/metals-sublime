import shutil
import sublime
from LSP.plugin.core.handlers import LanguageHandler
from LSP.plugin.core.settings import ClientConfig, LanguageConfig

config_name = 'metals-sublime'
server_name = 'metals-sublime'
service_name = "metals-sublime"
metals_config = ClientConfig(
    name=config_name,
    binary_args=[service_name],
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


def metals_is_running() -> bool:
    return shutil.which(service_name) is not None


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
        if not metals_is_running():
            window.status_message(
                "Metals must be installed run {}".format(server_name))
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
