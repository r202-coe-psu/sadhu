from sadhu import web
from livereload import Server


def main():
    options = web.get_program_options()
    app = web.create_app()
    app.debug = options.debug

    server = Server(app.wsgi_app)
    server.watch("sadhu/web")
    server.serve(
        debug=options.debug,
        host=options.host,
        port=int(options.port),
        restart_delay=2,
    )

    # app.run(
    #     debug=options.debug,
    #     host=options.host,
    #     port=int(options.port)
    # )
