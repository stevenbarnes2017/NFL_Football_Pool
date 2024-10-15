from Football_Project import create_app
from flask_cors import CORS
from Football_Project.utils import scheduler  # Import once at the top
import os
from Football_Project.utils import start_scheduler  # Use start_scheduler instead of scheduler directly

app = create_app()
CORS(app)  # Enable Cross-Origin Resource Sharing if needed



if __name__ == "__main__":
    app.run(debug=True, threaded=True)