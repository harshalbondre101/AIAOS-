from app.main import create_app

app, socket_io = create_app()

if __name__ == "__main__":
    socket_io.run(app, allow_unsafe_werkzeug=True,debug=True, use_reloader=True)
