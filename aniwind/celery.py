from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Устанавливаем модуль настроек Django по умолчанию для 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aniwind.settings')

app = Celery('aniwind')

# Используем строку для настройки, чтобы Celery не нужно было сериализовать
# конфигурационный объект для дочерних процессов.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживаем задачи в файлах tasks.py каждого приложения
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))