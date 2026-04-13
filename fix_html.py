import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()
from webapp.models import Video
from pathlib import Path

updated = 0
for v in Video.objects.all():
    vid_path = v.file_path
    if '/VOD/' in vid_path:
        html_path = vid_path.replace('/VOD/', '/HTML/').rsplit('.', 1)[0] + '.html'
        if Path(html_path).exists():
            v.html_path = html_path
            v.save()
            updated += 1

print(f"Successfully linked {updated} HTML files!")
