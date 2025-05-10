import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog.setup import setup_dialogs
from dotenv import load_dotenv

from dialog_media_manager import DynamicMediaManager
from env import Env
from face_detector import FaceDetector
from handlers import register_all_routers
from log import setup_logging
from middlewares import EnvMiddleware, I18nMiddleware
from resources_manager import ResourcesManager


async def main():
    setup_logging()

    load_dotenv()

    bot = Bot(token=os.getenv('BOT_TOKEN'),
              default=DefaultBotProperties(parse_mode=ParseMode.HTML,
                                           link_preview_is_disabled=True))
    bot_info = await bot.me()

    env_type = Env.Type.DEV
    if os.getenv('ENV', 'dev').lower() == 'prod':
        env_type = Env.Type.PROD

    resources_manager = ResourcesManager(bot)
    await resources_manager.load()

    media_manager = DynamicMediaManager()

    env = Env(
        env_type=env_type,
        bot_info=bot_info,
        resources_manager=resources_manager,
        face_detector=FaceDetector(),
        media_manager=media_manager
    )

    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware.register(EnvMiddleware(env))
    dp.update.middleware.register(I18nMiddleware(env))

    setup_dialogs(dp, message_manager=media_manager)

    register_all_routers(dp)

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.exception('Interrupted')
