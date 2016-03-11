from flask import request, url_for
from flask.ext.api import FlaskAPI, status, exceptions
from pymongo import MongoClient
from integ import justDoIt
import time

app = FlaskAPI(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client.revmine_2

def create_rev(domain, pid, product_name):
    try:
    	print 'doesnt exist'
        justDoIt(domain,pid,product_name)
        print 'gained'
        foo = db.result.find_one({'_id' : pid, 'domain' :domain, 'valid':1 })
        if foo:
            return foo
        else:
            return {'status':69, 'result':110, 'reviews':['Not Applicable'],  'valid':0}
    except:
        return {'status':69, 'result':100, 'reviews':['Not Applicable'], 'valid':0}

@app.route("/<domain>/<pid>/<product_name>", methods=['GET'])
def getRatings(domain,pid,product_name=None):
    """
    Retrieve, update or delete note instances.
    """
    foo = db.result.find_one({'_id' : pid, 'domain' :domain, 'valid':1 })

    upvotes = 0

    if db.votes.count({'_id': pid, 'domain': domain}) == 0:
        db.votes.insert({'_id': pid, 'domain': domain, 'upvotes': 0})
    else:
        upvotes = db.votes.find_one({'_id': pid, 'domain': domain})['upvotes']

    if not foo:
        try:
            foo = create_rev(domain , pid, product_name)
        except:
            import traceback; traceback.print_exc();
            return {'status':69, 'result':100, 'reviews':['Not Applicable']}

    if foo and foo.has_key('topics') and len(foo['topics']) != 0:
    	item = db.reviews.find_one({'_id': pid, 'domain': domain})
    	ranked = -1
        if item.has_key('rank'):
            ranked = item['rank']
    	category = item['category']
    	low_price= item['low-price']
    	high_price= item['high-price']
    	if ranked  != -1:
    		message = "This product ranks %d in category `%s` in the range Rs %d - Rs %d. Following are the top products in the given range." %(ranked, category, low_price, high_price)
        else:
            message = "This product doesn't rank well in category `%s` and price range Rs %d - Rs %d, here are the top products" %(category, low_price, high_price)
        return {'result': foo['topics'], 'reviews':foo['sentences'], 'message': message, 'name': item['title'], 'related_products' : item['related_products'], 'status':200, 'upvotes': upvotes}
    else:
        return {'status': 100, 'reviews':['Not Applicable'], 'result': 100}


@app.route("/vote/<vote>/<domain>/<pid>/", methods=['GET'])
def vote(vote, domain,pid):
    """
    Retrieve, update or delete note instances.
    """
    try:
        if db.votes.count({'_id': pid, 'domain': domain}) == 0:
            db.votes.insert({'_id': pid, 'domain': domain, 'upvotes': 0})
        if vote =='up':
            db.votes.update({'_id': pid, 'domain': domain}, {'$inc': {'upvotes' : 1}})
        else:
            db.votes.update({'_id': pid, 'domain': domain}, {'$inc': {'upvotes' : -1}})

        return {'status': 200, 'message': 'received'}

    except:
        return {'status': 100}



if __name__ == "__main__":
    app.run(debug=True)