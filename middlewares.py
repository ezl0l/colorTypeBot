import os
import i18n

from contextvars import ContextVar
from aiogram import BaseMiddleware

from env import Env


class EnvMiddleware(BaseMiddleware):
    def __init__(self, env: Env):
        self._env = env

    async def __call__(self, handler, event, data):
        data['env'] = self._env

        return await handler(event, data)


class I18nMiddleware(BaseMiddleware):
    ctx_locale = ContextVar('ctx_user_locale', default='ru')

    def __init__(self, env: Env, default_locale='ru'):
        self._env = env
        self._default_locale = default_locale

        i18n.set('filename_format', '{format}')
        i18n.set('skip_locale_root_data', True)
        i18n.set('fallback', default_locale)

        for strings_file in os.listdir('resources/strings'):
            i18n.resource_loader.load_translation_file(strings_file,
                                                       'resources/strings',
                                                       locale=strings_file.split('.')[0])

    @property
    def available_locales(self):
        return i18n.translations.container.keys()

    async def get_user_locale(self, data):
        user = data.get('event_from_user')

        locale = self._default_locale
        if user is None:
            return locale

        locale = user.language_code

        if not i18n.translations.container.get(user.language_code):
            return self._default_locale

        return locale

    def gettext(self, key: str, locale=None, **kwargs):
        if locale is None:
            locale = self.ctx_locale.get()

        return i18n.t(key, locale=locale, **kwargs)

    async def __call__(self, handler, event, data):
        locale = await self.get_user_locale(data)
        self.ctx_locale.set(locale)

        data['_'] = data['__'] = self.gettext
        data['locale'] = locale

        return await handler(event, data)
