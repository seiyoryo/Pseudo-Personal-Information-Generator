from __future__ import annotations

from flask import Flask

from .config import get_paths


def create_app() -> Flask:
    paths = get_paths()
    app = Flask(
        __name__,
        template_folder=str(paths.templates_dir),
        static_folder=str(paths.static_dir),
        static_url_path="/static",
    )
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

    from .routes import bp as routes_bp

    app.register_blueprint(routes_bp)
    return app

