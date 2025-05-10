from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from i18n_dialog import I18nText
from states import States


async def on_start(callback, button, manager):
    await manager.next()


start_window = Window(
    I18nText("welcome_message"),
    Button(I18nText("btn.continue"), id="start_continue", on_click=on_start),
    state=States.start,
)
