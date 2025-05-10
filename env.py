import enum

from dataclasses import dataclass
from aiogram.types import User

from dialog_media_manager import DynamicMediaManager
from face_detector import FaceDetector
from resources_manager import ResourcesManager


@dataclass
class Env:
    class Type(enum.Enum):
        DEV = 'dev'
        PROD = 'prod'

    env_type: Type
    bot_info: User
    resources_manager: ResourcesManager
    face_detector: FaceDetector
    media_manager: DynamicMediaManager
