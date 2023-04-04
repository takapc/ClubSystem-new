from server.app import app
import multiprocessing
from felica.app import readLoop

if __name__ == ("__main__"):
    felica = multiprocessing.Process(name="felica_read", target=readLoop)
    felica.start()

    @app.route('/felica/start')
    def felica_start():
        felica = multiprocessing.Process(name="felica_read", target=readLoop)
        felica.start()
        return ""
    
    @app.route('/felica/stop')
    def felica_stop():
        felica.terminate()
        felica.join()
        return ""
    
    app.run(debug=True, host="0.0.0.0", port=5000)