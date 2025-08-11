# Football_Project/admin/__init__.py
from flask import Blueprint

# Define the admin blueprint with a single prefix
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Import routes so they register with the blueprint
from . import routes
