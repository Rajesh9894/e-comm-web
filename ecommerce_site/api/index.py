import os
import sys

from django.core.wsgi import get_wsgi_application

# Add your Django project path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Set the settings module (replace 'your_project_name' with your actual project folder name)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce_site.settings")

app = get_wsgi_application()


