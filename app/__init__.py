import json
from pathlib import Path

from flask import Flask


def create_app():
    app = Flask(__name__)
    config_path = Path(__file__).resolve().parent.parent / "config.json"
    app.config.update(json.loads(config_path.read_text(encoding="utf-8")))

    if __package__:
        from .routes import main
    else:
        from routes import main
    
    app.register_blueprint(main, url_prefix=app.config["routes"]["prefix"])
    return app

app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
    