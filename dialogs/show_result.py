from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog import DialogManager
from aiogram.types import CallbackQuery

from i18n_dialog import I18nText
from states import States


async def on_back(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.back()


async def on_upload_more(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.start(States.upload_photo)


show_result_window = Window(
    Format(
        "Color type: {dialog_data[detection_result][color_type]}\n"
        "Eyes RGB: {dialog_data[detection_result][eye_rgb]}\n"
        "Skin RGB: {dialog_data[detection_result][skin_rgb]}\n"
        "Hair RGB: {dialog_data[detection_result][hair_rgb]}"
    ),
    Row(
        Button(I18nText("btn.back"), id="back", on_click=on_back),
        Button(I18nText("btn.upload_more"), id="upload_more", on_click=on_upload_more),
    ),
    state=States.show_result,
)
