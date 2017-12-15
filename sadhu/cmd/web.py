import sadhu

def main():
    options = sadhu.get_program_options()
    app = sadhu.create_app()

    app.run(
        debug=options.debug,
        host=options.host,
        port=int(options.port)
    )
