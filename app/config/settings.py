import os


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
APP_DIR = os.path.join(BASE_DIR, "app")
VIEWS_DIR = os.path.join(APP_DIR, "views")
TEMPLATES_DIR = os.path.join(VIEWS_DIR, "templates")
