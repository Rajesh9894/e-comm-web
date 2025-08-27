import os
import sys

from django.core.wsgi import get_wsgi_application

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce_site.settings")

app = get_wsgi_application()
