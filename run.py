from Football_Project import create_app
from flask_cors import CORS

app = create_app()
CORS(app)  # Enable Cross-Origin Resource Sharing if needed

if __name__ == "__main__":
    app.run(debug=True, threaded=True)