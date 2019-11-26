
from . import site
from . import accounts
from . import dashboard
from . import courses
from . import classes
from . import assignments
from . import challenges
from . import solutions

from . import teaching_assistants

from . import admin
from . import administration


def get_subblueprints(views=[]):
    blueprints = []
    for view in views:
        blueprints.append(view.module)

        if 'subviews' in dir(view):
            for module in get_subblueprints(view.subviews):
                if view.module.url_prefix and module.url_prefix:
                    module.url_prefix = view.module.url_prefix + \
                            module.url_prefix
                blueprints.append(module)

    return blueprints


def register_blueprint(app):
    blueprints = get_subblueprints([site,
                                    accounts,
                                    dashboard,
                                    courses,
                                    classes,
                                    assignments,
                                    challenges,
                                    solutions,
                                    teaching_assistants,
                                    administration,
                                    admin
                                    ])

    for blueprint in blueprints:
        app.register_blueprint(blueprint)