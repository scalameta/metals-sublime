from __future__ import annotations

from ..commands.utils import handle_error
from .handle_execute_client import handle_execute_client
from .handle_input_box import handle_input_box
from .status import handle_status
from LSP.plugin import ClientRequest
from LSP.plugin import Error
from LSP.plugin import first_selection_region
from LSP.plugin import LspPlugin
from LSP.plugin import notification_handler
from LSP.plugin import OnPreStartContext
from LSP.plugin import PluginStartError
from LSP.plugin import position_to_offset
from LSP.plugin import Promise
from LSP.plugin import region_to_range
from LSP.plugin import request_handler
from LSP.plugin import uri_handler
from LSP.protocol import DocumentUri
from LSP.protocol import ExecuteCommandParams
from pathlib import Path
from typing import Any
from typing import final
from typing_extensions import override
from urllib.request import Request
from urllib.request import urlopen
import json
import os
import re
import sublime

_COURSIER_PATH = str(Path(__file__).parent.parent / 'coursier')
_LATEST_STABLE = "latest-stable"
_LATEST_SNAPSHOT = "latest-snapshot"
_LATEST_STABLE_ARTIFACT = "latest.stable"
_SCALA_213_MINIMUM_VERSION = (0, 11, 2)


@final
class Metals(LspPlugin):

    @classmethod
    @override
    def on_pre_start_async(cls, context: OnPreStartContext) -> None:
        if not context.workspace_folders:
            raise PluginStartError("No workspace detected. Try opening your project at the workspace root.")

        plugin_settings = context.configuration.root_settings
        java_path = get_java_path(plugin_settings)
        if not java_path :
            raise PluginStartError("Please install java or set the 'java_home' setting")

        server_version = plugin_settings.get('server_version', _LATEST_STABLE)

        if server_version == _LATEST_SNAPSHOT:
            try:
                httprequest = Request(
                    "https://scalameta.org/metals/latests.json",
                    # The website rejects the default "Python-urllib" user agent with 403.
                    headers={"Accept": "application/json", "User-Agent": "LSP-metals"},
                    method="GET"
                )
                httpresponse = urlopen(httprequest)
                body = json.loads(httpresponse.read().decode())
                server_version = body.get("snapshot")
            except:
                raise PluginStartError(
                    "Couldn't get latest version number from scalameta website, please set the 'server_version'")
        elif not server_version or server_version == _LATEST_STABLE:
            server_version = _LATEST_STABLE_ARTIFACT

        properties = prepare_server_properties(plugin_settings.get("server_properties") or [])
        context.configuration.command = create_launch_command(java_path, server_version, properties)

    @override
    def on_pre_send_request_async(self, request: ClientRequest, view: sublime.View | None) -> None:
        if request['method'] == 'textDocument/hover' and view:
            session = self.weaksession()
            if not session:
                return
            if not session.get_capability('experimental.rangeHoverProvider'):
                return
            region = first_selection_region(view)
            if region is not None:
                params = request['params']
                point = position_to_offset(view, params['position'])
                if region.contains(point):
                    params['range'] = region_to_range(view, region)  # pyright: ignore[reportGeneralTypeIssues]

    @uri_handler('jar')
    def on_open_jar_uri(self, uri: DocumentUri, flags: sublime.NewFileFlags) -> Promise[sublime.Sheet | None]:
        session = self.weaksession()
        if not session:
            return Promise.resolve(None)

        params: ExecuteCommandParams = {"command": "file-decode", "arguments": [uri]}

        def handle_response(response: Any) -> Promise[sublime.Sheet | None]:
            if isinstance(response, Error) or 'error' in response:
                handle_error("file-decode", response)
                return Promise.resolve(None)

            if response and 'value' in response:
                session = self.weaksession()
                if not session:
                    return Promise.resolve(None)

                title = str(response['requestedUri'])
                uri_parts = title.split("!")
                if len(uri_parts) == 2:
                    jar_source, path_to_file = uri_parts
                    title = f"{Path(jar_source).name}!{path_to_file}"

                syntax = "Packages/Scala/Scala.sublime-syntax"
                if title.endswith('.java'):
                    syntax = "Packages/Java/Java.sublime-syntax"

                return session.open_scratch_buffer(title, response['value'], syntax, flags) \
                    .then(lambda view: view.sheet())
            return Promise.resolve(None)

        return session.execute_command(params, progress=True).then(handle_response)

    # notification and request handlers

    @notification_handler('metals/status')
    def on_metals_status(self, params: Any) -> None:
        session = self.weaksession()
        if not session:
            return
        handle_status(session, params)

    @notification_handler('metals/executeClientCommand')
    def on_metals_execute_client_command(self, params: Any) -> None:
        session = self.weaksession()
        if not session:
            return

        handle_execute_client(session, params)

    @request_handler('metals/inputBox')
    def on_metals_input_box(self, params: Any) -> Promise[Any]:
        session = self.weaksession()
        if not session:
            return Promise.resolve({'cancelled': True})
        return handle_input_box(session, params)


def get_java_path(settings: dict[str, Any]) -> str:
    java_home = settings.get("java_home")
    if isinstance(java_home, str) and java_home:
        return str(Path(java_home, "bin", "java"))
    java_home = os.environ.get('JAVA_HOME')
    if java_home:
        return str(Path(java_home, "bin", "java"))
    return "java"


def create_launch_command(java_path: str, artifact_version: str, server_properties: list[str]) -> list[str]:
    binary_version = "2.12"
    if artifact_version == _LATEST_STABLE_ARTIFACT or _uses_scala_213_artifact(artifact_version):
        binary_version = "2.13"

    return [java_path] + server_properties + [
        "-jar",
        _COURSIER_PATH,
        "launch",
        "--ttl",
        "Inf",
        "--repository",
        "bintray:scalacenter/releases",
        "--repository",
        "sonatype:snapshots",
        "--main-class",
        "scala.meta.metals.Main",
        "org.scalameta:metals_{}:{}".format(binary_version, artifact_version)
    ]


def prepare_server_properties(properties: list[str]) -> list[str]:
    stripped = map(lambda p: p.strip(), properties)
    none_empty = list(filter(None, stripped))
    return none_empty


def _uses_scala_213_artifact(artifact_version: str) -> bool:
    version = _numeric_version_prefix(artifact_version)
    if not version:
        return False

    padded_length = max(len(version), len(_SCALA_213_MINIMUM_VERSION))
    padded_version = version + (0,) * (padded_length - len(version))
    padded_minimum = _SCALA_213_MINIMUM_VERSION + (0,) * (padded_length - len(_SCALA_213_MINIMUM_VERSION))
    return padded_version > padded_minimum


def _numeric_version_prefix(artifact_version: str) -> tuple[int, ...]:
    # Metals versions can include tags or prerelease suffixes; only the leading
    # numeric release determines the Scala binary version.
    match = re.match(r"\d+(?:\.\d+)*", artifact_version.strip())
    if match is None:
        return ()
    return tuple(int(part) for part in match.group(0).split("."))
