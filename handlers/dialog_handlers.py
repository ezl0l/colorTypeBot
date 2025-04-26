from aiogram import Router
from aiogram_dialog import Dialog

from dialogs.choose_options import choose_options_window
from dialogs.show_result import show_result_window
from dialogs.start import start_window
from dialogs.upload_photo import upload_photo_window

router = Router()

dialog = Dialog(
    start_window,
    upload_photo_window,
    choose_options_window,
    show_result_window,
)

router.include_router(dialog)
