from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from states import States


async def on_start(callback, button, dialog_manager):
    await dialog_manager.next()


start_window = Window(
    Const("Привет,\nЯ — ваш новый бот Твой цветотип 🌈!\n"
          "Моя цель — помочь Вам определить собственный цветотип по фотографии лица, "
          "а также подобрать подходящий макияж и соответствующий образ."),
    Button(Const("Продолжить"), id="start_continue", on_click=on_start),
    state=States.start,
)
