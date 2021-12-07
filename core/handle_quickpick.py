from LSP.plugin import Response
from LSP.plugin.core.sessions import Session
from LSP.plugin.core.types import Optional, Any

import sublime

def handle_quickpick(session: Session, params: Any, request_id: Any) -> None:
    """Handle the metals/quickPick request."""
    if not isinstance(params, dict):
        return

    items = []
    ids = []
    for item in params.get('items', []):
        details = []
        if 'description' in item:
            details.append(item.get('description'))
        if 'detail' in item:
            details.append(item.get('detail'))

        label = item.get('label')
        ids.append(item.get('id'))
        items.append(sublime.QuickPanelItem(label, details))

    placeHolder = params.get('placeHolder', '')

    def send_user_choice(index: int) -> None:
        # when noop; nothing was selected e.g. the user pressed escape
        result = {'cancelled': True}
        if index != -1:
            result = {'itemId': ids[index]}
        session.send_response(Response(request_id, result))

    if items:
        session.window.show_quick_panel(
            items,
            send_user_choice,
            sublime.KEEP_OPEN_ON_FOCUS_LOST,
            placeholder=placeHolder)
