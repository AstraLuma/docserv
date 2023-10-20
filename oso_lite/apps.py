
import functools
from pathlib import Path

from django.apps import AppConfig
from django.utils.autoreload import autoreload_started

from .oso import init_oso
from django.conf import settings


def watch_files(files, sender, **kwargs):
    for file in files:
        sender.extra_files.add(Path(file))


class OsoLiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'oso_lite'

    def ready(self):
        loaded_files = init_oso()
        if getattr(settings, 'OSO_RELOAD_SERVER', True):
            autoreload_started.connect(
                functools.partial(watch_files, files=loaded_files), weak=False
            )
