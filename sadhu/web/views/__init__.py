import os
import datetime
import pathlib
import importlib
import logging

from flask import current_app

logger = logging.getLogger(__name__)


def add_date_url(url):
    """Append a cache-busting query string to a static asset URL.

    Uses the file's modification time so the browser refetches whenever the
    asset actually changes (e.g. a rebuilt ``css/tailwind.css``). Falls back to
    the current date for non-static URLs or if the file can't be found.
    """
    version = None
    try:
        static_url = current_app.static_url_path or ""
        prefix = static_url + "/"
        if static_url and url.startswith(prefix):
            file_path = os.path.join(current_app.static_folder, url[len(prefix):])
            version = int(os.path.getmtime(file_path))
    except Exception:
        version = None

    if version is None:
        version = datetime.datetime.now().strftime("%Y%m%d")

    separator = "&" if "?" in url else "?"
    return f"{url}{separator}date={version}"


def ymd(value):
    """Render a date/datetime as ``YYYY-MM-DD`` (empty string when missing)."""
    if value is None:
        return ""
    try:
        return value.strftime("%Y-%m-%d")
    except AttributeError:
        return value


def get_subblueprints(directory):
    blueprints = []

    package = directory.parts[len(pathlib.Path.cwd().parts) :]
    parent_module = None
    try:
        parrent_view = directory.with_name("__init__.py")
        pymod_file = f"{'.'.join(package)}"
        pymod = importlib.import_module(pymod_file)

        if "module" in dir(pymod):
            parent_module = pymod.module
            blueprints.append(parent_module)
    except Exception as e:
        logger.exception(e)
        return blueprints

    subblueprints = []
    for module in directory.iterdir():

        if "__" == module.name[:2]:
            continue

        if module.match("*.py"):
            try:
                pymod_file = f"{'.'.join(package)}.{module.stem}"
                pymod = importlib.import_module(pymod_file)

                if "module" in dir(pymod):
                    subblueprints.append(pymod.module)
            except Exception as e:
                logger.exception(e)

        elif module.is_dir():
            subblueprints.extend(get_subblueprints(module))

    for module in subblueprints:
        if parent_module:
            parent_module.register_blueprint(module)
        else:
            blueprints.append(module)

    return blueprints


def register_blueprint(app):
    app.add_template_filter(add_date_url)
    app.add_template_filter(ymd)
    parent = pathlib.Path(__file__).parent
    blueprints = get_subblueprints(parent)

    for blueprint in blueprints:
        app.register_blueprint(blueprint)
