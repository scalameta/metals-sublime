from LSP.plugin.core.registry import LspTextCommand
from LSP.plugin.core.typing import Union
from LSP.plugin.core.protocol import Request, Range, TextDocumentIdentifier, Error, Hover
from LSP.plugin.core.views import first_selection_region, text_document_identifier, region_to_range, FORMAT_MARKED_STRING, FORMAT_MARKUP_CONTENT, minihtml, update_lsp_popup, show_lsp_popup
import sublime

HoverOrError = Union[Hover, Error]

class LspMetalsHoverRangeCommand(LspTextCommand):
    session_name = "metals"

    def run(self, edit: sublime.Edit) -> None:
        session = self.session_by_name()
        if not session:
            return
        view = self.view
        region = first_selection_region(view)
        begin = region.begin()
        document_range = {
            "textDocument": text_document_identifier(view),
            "range": region_to_range(view, region).to_lsp()
        }

        def on_response(response: HoverOrError):
            if isinstance(response, Error):
                sublime.status_message('Hover error: {}'.format(response))

            if response:
                content = (response.get('contents') or '') if isinstance(response, dict) else ''
                formated = minihtml(self.view, content, allowed_formats=FORMAT_MARKED_STRING | FORMAT_MARKUP_CONTENT)
                if self.view.is_popup_visible():
                    update_lsp_popup(self.view, formated)
                else:
                    show_lsp_popup(
                        self.view,
                        formated,
                        flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY,
                        location=begin
                    )

        def on_error(error: Error):
            sublime.status_message('Hover error: {}'.format(error))

        session.send_request(
            Request("textDocument/hover", document_range, self.view),
            on_response,
            on_error
        )
