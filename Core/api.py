from flask import request, url_for
from flask.ext.api import FlaskAPI, status, exceptions
from pymongo import MongoClient
from integ import justDoIt
import time

app = FlaskAPI(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client.revmine

def createve_rev(domain,pid,product_name=None, upvotes, downvotes):
    try:
    	print 'doesnt exist'
        justDoIt(domain,pid,product_name)
        print 'gained'
        foo = db.result.find_one({'_id' : pid, 'domain' :domain, 'valid':1 })
        if foo:
            return foo
        else:
            return {'status':69, 'result':110, 'reviews':['Not Applicable'], 'valid':0, 'upvotes': upvotes, 'downvotes': downvotes}
    except:
        return {'status':69, 'result':100, 'reviews':['Not Applicable'], 'valid':0}

@app.route("/<domain>/<pid>/<product_name>", methods=['GET'])
def getRatings(domain,pid,product_name=None):
    """
    Retrieve, update or delete note instances.
    """
    foo = db.result.find_one({'_id' : pid, 'domain' :domain, 'valid':1 })

    upvotes = 0
    downvotes= 0

    if db.votes.count({'_id': pid, 'domain': domain}) == 0:
        db.votes.insert({'_id': pid, 'domain': domain, 'upvotes': 0, 'downvotes': 0})
        upvotes = 0
        downvotes = 0
    else:
        upvotes = db.votes.find_one({'_id': pid, 'domain': domain})['upvotes']
        downvotes = db.votes.find_one({'_id': pid, 'domain': domain})['downvotes']

    if not foo:
        try:
            foo = createve_rev(domain,pid,product_name, upvotes, downvotes)
        except:
            return {'status':69, 'result':100, 'reviews':['Not Applicable']}

    if foo and foo.has_key('topics'):
        return {'result': foo['topics'], 'reviews':foo['sentences'], 'status':200, 'upvotes': upvotes, 'downvotes': downvotes}
    else:
        return {'status': 100, 'reviews':['Not Applicable'], 'result': 100}


@app.route("/vote/<vote>/<domain>/<pid>/", methods=['GET'])
def getRatings(vote, domain,pid):
    """
    Retrieve, update or delete note instances.
    """
    try:
        if db.votes.count({'_id': pid, 'domain': domain}) == 0:
            db.votes.insert({'_id': pid, 'domain': domain, 'upvotes': 0, 'downvotes': 0})
        if vote =='up':
            db.votes.update({'_id': pid, 'domain': domain}, {'$inc': {'upvotes' : 1}})
        else:
            db.votes.update({'_id': pid, 'domain': domain}, {'$inc': {'downvotes' : 1}})

    except:
        return {'status': 100, 'reviews':['Not Applicable'], 'result': 100}



if __name__ == "__main__":
    app.run(debug=True)