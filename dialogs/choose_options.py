from aiogram.enums import ContentType
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.media import DynamicMedia
import i18n

from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Group
from aiogram_dialog import DialogManager
from aiogram.types import BufferedInputFile, CallbackQuery

from i18n_dialog import I18nText
from states import States


async def on_choose(callback: CallbackQuery, button: Button, manager: DialogManager):
    # result_text = manager.dialog_data['detection_result']['color_type']
    # manager.dialog_data["result_text"] = result_text

    await manager.next()


async def get_data(dialog_manager: DialogManager, **kwargs):
    image = MediaAttachment(ContentType.PHOTO, url=dialog_manager.dialog_data['highlighted_photo_uri'])
    return {'highlighted_photo_uri': image}


choose_options_window = Window(
    I18nText('option_choosing_message'),
    DynamicMedia('highlighted_photo_uri'),
    Group(
        Button(I18nText("btn.only_color"), id="only_color", on_click=on_choose),
        # Button(I18nText("btn.makeup"), id="makeup", on_click=on_choose),
        # Button(I18nText("btn.hair_color"), id="hair_color", on_click=on_choose),
        # Button(I18nText("btn.clothes"), id="clothes", on_click=on_choose),
        # Button(I18nText("btn.all"), id="all", on_click=on_choose),
    ),
    state=States.choose_option,
    getter=get_data
)
