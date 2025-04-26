from aiogram import Dispatcher

from . import (
    start_handlers,
    dialog_handlers
)


def register_all_routers(dp: Dispatcher):
    dp.include_routers(
        start_handlers.router,
        dialog_handlers.router,
    )
