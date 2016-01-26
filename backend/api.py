from flask import request, url_for
from flask.ext.api import FlaskAPI, status, exceptions
from pymongo import MongoClient
from integ import justDoIt
import time

app = FlaskAPI(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client.revmine

def create_rev_natak(domain, pid):
    try:
    	print 'doesnt exist'
        justDoIt(pid)
        print 'gained'
        foo = db.result.find_one({'_id' : pid, 'domain' :domain, 'valid':1 })
        if foo:
            return foo
        else:
            return {'status':69, 'result':110, 'reviews':['Not Applicable'], 'valid':0}
    except:
        return {'status':69, 'result':100, 'reviews':['Not Applicable'], 'valid':0}

@app.route("/<domain>/<pid>", methods=['GET'])
def getRatings(domain,pid):
    """
    Retrieve, update or delete note instances.
    """
    foo = db.result.find_one({'_id' : pid, 'domain' :domain, 'valid':1 })
    if not foo:
        try:
            foo = create_rev_natak(domain,pid)
        except:
            return {'status':69, 'result':100, 'reviews':['Not Applicable']}

    if foo and foo.has_key('topics'):
        return {'result': foo['topics'], 'reviews':foo['sentences'], 'status':200}
    else:
        return {'status': 100, 'reviews':['Not Applicable'], 'result': 100}

if __name__ == "__main__":
    app.run(debug=True)