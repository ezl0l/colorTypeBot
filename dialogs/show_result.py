from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog import DialogManager
from aiogram.types import CallbackQuery
from states import States


async def on_back(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.back()


async def on_upload_more(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.start(States.upload_photo)


show_result_window = Window(
    Format("{dialog_data[result_text]}"),
    Row(
        Button(Const("Назад"), id="back", on_click=on_back),
        Button(Const("Загрузить другое фото"), id="upload_more", on_click=on_upload_more),
    ),
    state=States.show_result,
)
