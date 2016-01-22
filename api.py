from flask import request, url_for
from flask.ext.api import FlaskAPI, status, exceptions

app = FlaskAPI(__name__)


@app.route("/<domain>/<pid>", methods=['GET'])
def getRatings(domain,pid):
    """
    Retrieve, update or delete note instances.
    """
    # request.method == 'GET'
    return {'result': {'camera':5,'battery':3,'screen':2,'speed':5,'calls':66}}

if __name__ == "__main__":
    app.run(debug=True)