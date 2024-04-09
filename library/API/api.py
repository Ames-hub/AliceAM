import waitress
import datetime
import flask

app = flask.Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    return {
        # Allows users to calculate ping.
        'timenow': datetime.datetime.now().timestamp()
    }, 200

if __name__ == '__main__':
    waitress.serve(app, host='0.0.0.0', port=7000)
