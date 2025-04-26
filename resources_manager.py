import json
import logging
import os.path
import aiofiles

from aiogram import Bot
from aiogram.types import FSInputFile


class ResourcesManager:
    def __init__(self, bot: Bot):
        self._bot = bot

        self._resources = {
            'photos': {}
        }

    async def load(self):
        if os.path.exists('resources/cached_resources.json'):
            async with aiofiles.open('resources/cached_resources.json', 'r') as f:
                try:
                    self._resources = json.loads(await f.read())
                except json.JSONDecodeError:
                    logging.exception('Failed to load resources/cached_resources.json')

    async def save(self):
        async with aiofiles.open('resources/cached_resources.json', 'w') as f:
            await f.write(json.dumps(self._resources, separators=(',', ':')))

    async def send_photo(self, chat_id, name: str, force: bool = False, **kwargs):
        if not force and (file_id := self._resources['photos'].get(name)):
            return await self._bot.send_photo(chat_id, file_id, **kwargs)

        message = await self._bot.send_photo(chat_id, FSInputFile(os.path.join('resources/photos', name)), **kwargs)

        if message.photo:
            self._resources['photos'][name] = message.photo[-1].file_id
            await self.save()

        return message
