from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog import DialogManager
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ContentType

from i18n_dialog import I18nText
from states import States

import i18n


async def on_upload_photo(message: Message, widget, manager: DialogManager):
    if message.photo:
        file_id = message.photo[-1].file_id
        manager.dialog_data["photo_file_id"] = file_id
        await manager.next()
    else:
        await message.answer(i18n.t("no_photo_error"))


async def on_back(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.back()


upload_photo_window = Window(
    I18nText("upload_photo_message"),
    MessageInput(on_upload_photo, content_types=[ContentType.PHOTO]),
    Row(
        Button(I18nText("btn.back"), id="go_back", on_click=on_back),
    ),
    state=States.upload_photo,
)
