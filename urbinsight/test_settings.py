# File: ./backend/backend/test_settings.py

from .settings import *  # NOQA

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'