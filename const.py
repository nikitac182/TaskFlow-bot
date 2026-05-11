import os
import aiogram
import aiosqlite
from dotenv import load_dotenv
from aiogram.types import Message

load_dotenv()

TOKEN = os.getenv("TOKEN")

status_form = {
    'rejected': ('🔴', 'отклонена'),
    'accepted': ('🟢', 'принята'),
    'submitted': ('🔵', 'на расмотреннии'),
    'in_progress': ('🟠', 'в процессе'),
    'new': ('🆕', 'новая'),
}


def media_map(message: Message):
    return {
        "text": {
            "file_id": None,
            "text": message.text,
        },

        "photo": {
            "file_id": message.photo[-1].file_id,
            "text": "PHOTO",
        },

        "document": {
            "file_id": message.document.file_id,
            "text": "DOCUMENT",
        },

        "video": {
            "file_id": message.video.file_id,
            "text": "VIDEO",
        },

        "audio": {
            "file_id": message.audio.file_id,
            "text": "AUDIO",
        },

        "voice": {
            "file_id": message.voice.file_id,
            "text": "VOICE",
        },
    }