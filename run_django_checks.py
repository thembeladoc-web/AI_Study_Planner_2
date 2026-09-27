import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ['DATABASE_ENGINE'] = 'sqlite3'
os.environ['DATABASE_NAME'] = '/home/ubuntu/timetable_work/backend/db.sqlite3'
os.environ['SECRET_KEY'] = 'test-secret-key'
os.environ['DEBUG'] = 'True'
import django
django.setup()
from django.core.management import call_command
call_command('check', verbosity=2)
call_command('makemigrations', '--check', verbosity=2)
