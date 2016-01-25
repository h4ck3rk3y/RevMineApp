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
    print "sleeping"
    return [{'result': {'f': 1}, 'status':200, 'reviews':['shit phone', 'very shitty phone'],'valid':0}]

@app.route("/<domain>/<pid>", methods=['GET'])
def getRatings(domain,pid):
    """
    Retrieve, update or delete note instances.
    """
    foo = db.result.find({'_id' : pid, 'domain' :domain })
    if not foo.count() > 0:
        try:
            foo = create_rev_natak(domain,pid)
        except:
            return {'status':69, 'result':100, 'reviews':['Not Applicable']}
    time.sleep(2)
    if foo[0]['valid']==1:
        return {'result': foo[0]['topics'], 'reviews':foo[0]['sentences'], 'status':200}
    else:
        return {'status': 100, 'reviews':['Not Applicable'], 'result': 100}

if __name__ == "__main__":
    app.run(debug=True)