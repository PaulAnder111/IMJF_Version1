import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','imjfpro2025.settings')
import django
django.setup()
from inscriptions.models import Inscription
from django.db import connection
print('model fields:', [f.name for f in Inscription._meta.fields])
with connection.cursor() as cur:
    try:
        cur.execute("SHOW COLUMNS FROM inscriptions_inscription")
        rows = cur.fetchall()
        print('db columns:')
        for r in rows:
            print(r)
    except Exception as e:
        print('Error querying DB columns:', e)
