from server.app import app

if __name__ == '__main__':
    host = 'localhost'
    port = 5000

    app.run(debug=False, host=host, port=port)

