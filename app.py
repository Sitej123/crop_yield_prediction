from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
from routes.prediction import predict_bp
from routes.monitoring import monitor_bp
from models.crop_model import crop_model


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static", static_url_path="")
    app.config.from_object(Config)
    CORS(app)

    # ===============================
    # Load trained models on startup
    # ===============================
    print("=" * 55)
    print("🌾 Initializing Crop Yield Prediction System")
    print("=" * 55)

    if not crop_model.load():
        print("⚠️ Saved models not found.")

        # Uncomment the following if you want the app
        # to automatically train models when they don't exist.

        # try:
        #     metrics = crop_model.train()
        #     print("✅ Models trained successfully.")
        # except Exception as e:
        #     print(f"❌ Training failed: {e}")

    else:
        print("✅ Models loaded successfully.")

    # Register API routes
    app.register_blueprint(predict_bp)
    app.register_blueprint(monitor_bp)

    @app.route("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "model_trained": crop_model.is_trained,
            "version": "1.0.0"
        })

    @app.route("/")
    @app.route("/<path:path>")
    def frontend(path="index.html"):
        return send_from_directory(app.static_folder, "index.html")

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "status": "error",
            "message": "Route not found"
        }), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

    return app


# Create Flask app
app = create_app()


# Run locally only
if __name__ == "__main__":
    print("🚀 Starting Flask Server...")
    app.run(
        debug=Config.DEBUG,
        host="0.0.0.0",
        port=5000
    )
