import io
from typing import Union
import uuid

from aiogram import Bot
from aiogram.types import BufferedInputFile, InputFile
from aiogram_dialog.api.entities import MediaAttachment

from aiogram_dialog.manager.message_manager import MessageManager


class DynamicMediaManager(MessageManager):
    def __init__(self):
        self._medias = {}

    def register_media(self, filename: str, content: bytes):
        media_id = str(uuid.uuid4())

        self._medias[media_id] = {
            'filename': filename,
            'content': content
        }

        return f'bot://{media_id}'

    async def get_media_source(self, media: MediaAttachment, bot: Bot) -> Union[InputFile, str]:
        if media.url.startswith('bot://'):
            media_id = media.url.removeprefix('bot://')
            if media_id not in self._medias.keys():
                raise ValueError(f'No media with id={media_id} found')

            media = self._medias[media_id]

            return BufferedInputFile(media['content'], filename=media['filename'])

        raise ValueError(f'Unknown media URI: {media.url}')
