from flask import request, url_for
from flask.ext.api import FlaskAPI, status, exceptions
from pymongo import MongoClient
import time

app = FlaskAPI(__name__)
client = MongoClient('mongodb://172.17.30.113:27017/')
db = client.revmine

def create_rev_natak(domain, pid):
    """
        add shubhus code here...
    """
    time.sleep(15)
    return [{'result': {'f': 1}, 'status':200}]

@app.route("/<domain>/<pid>", methods=['GET'])
def getRatings(domain,pid):
    """
    Retrieve, update or delete note instances.
    """
    foo = db.result.find({'_id' : pid, 'domain' :domain })
    print foo.count()
    if not foo.count() > 0:
        try:
            foo = create_rev_natak(domain,pid)
        except:
            return {'status':100, 'result':100}
    return {'result': foo[0], 'status': 200}

if __name__ == "__main__":
    app.run(debug=True)