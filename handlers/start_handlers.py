from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram_dialog import DialogManager

from env import Env
from states import States

router = Router()


@router.message(CommandStart())
async def start_command(message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(States.start)
