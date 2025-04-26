from aiogram import types
from aiogram.enums import ContentType

from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Const

from states import States


async def on_upload_photo(message: types.Message, _, dialog_manager: DialogManager):
    if message.photo:
        photo = message.photo[-1]
        file_id = photo.file_id
        dialog_manager.dialog_data["photo_file_id"] = file_id
        await dialog_manager.next()
    else:
        await message.answer("Пожалуйста, отправьте именно фотографию.")


async def on_back(callback, button, dialog_manager):
    await dialog_manager.back()


upload_photo_window = Window(
    Const("Для определения цветотипа загрузите Ваше фото.\n"
          "Для более точного результата используйте естественное освещение "
          "и откажитесь от макияжа. Смотрите прямо в камеру."),
    MessageInput(
        on_upload_photo,
        content_types=[ContentType.PHOTO]
    ),
    Row(
        Button(Const("Вернуться"), id="go_back", on_click=on_back),
    ),
    state=States.upload_photo,
)
