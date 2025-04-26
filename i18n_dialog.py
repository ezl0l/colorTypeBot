import i18n

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.text import Text

from middlewares import I18nMiddleware


class I18nText(Text):
    def __init__(self, key: str):
        super().__init__()

        self.key = key

    async def _render_text(self, data, manager: DialogManager) -> str:
        return i18n.t(self.key, locale=I18nMiddleware.ctx_locale)
