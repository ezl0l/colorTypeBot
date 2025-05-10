import cv2
import numpy as np
import i18n

from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog import DialogManager
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ContentType

from env import Env
from i18n_dialog import I18nText
from states import States


async def on_upload_photo(message: Message, widget, manager: DialogManager):
    if message.photo:
        file_id = message.photo[-1].file_id
        manager.dialog_data['photo_file_id'] = file_id

        file = await message.bot.get_file(file_id)

        file_path = file.file_path
        file_bytes = await message.bot.download_file(file_path)

        np_array = np.frombuffer(file_bytes.read(), np.uint8)
        img_cv2 = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        env: Env = manager.middleware_data['env']

        result = await env.face_detector.highlight_face(img_cv2)

        highlighted_photo = result['highlighted_photo']

        manager.dialog_data['highlighted_photo_uri'] = env.media_manager.register_media('photo.png',
                                                                                        highlighted_photo.read())
        manager.dialog_data['detection_result'] = result

        await manager.next()
    else:
        await message.answer(i18n.t('no_photo_error'))


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
