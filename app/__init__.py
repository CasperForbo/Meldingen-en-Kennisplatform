from flask import Flask


def create_app():
    app = Flask(__name__)
    if __package__:
        from .routes import main
    else:
        from routes import main
    
    app.register_blueprint(main)
    return app

app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
    