from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Group
from aiogram_dialog.widgets.text import Const
from aiogram_dialog import DialogManager
from aiogram.types import CallbackQuery
import i18n

from i18n_dialog import I18nText
from states import States


async def on_choose(callback: CallbackQuery, button: Button, manager: DialogManager):
    result_text = i18n.t(f"result_texts.{button.widget_id}", default=i18n.t("result_texts.unknown"))
    manager.dialog_data["result_text"] = result_text
    await manager.next()

choose_options_window = Window(
    I18nText("option_choosing_message"),
    Group(
        Button(I18nText("btn.only_color"), id="only_color", on_click=on_choose),
        Button(I18nText("btn.makeup"), id="makeup", on_click=on_choose),
        Button(I18nText("btn.hair_color"), id="hair_color", on_click=on_choose),
        Button(I18nText("btn.clothes"), id="clothes", on_click=on_choose),
        Button(I18nText("btn.all"), id="all", on_click=on_choose),
    ),
    state=States.choose_option,
)
