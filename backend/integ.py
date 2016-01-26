import amazon_rev
import nlp_dep
from datetime import datetime
import sys
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')

db = client.revmine


def justDoIt(pid):
    try:
        print datetime.now()
        amazon_rev.main(pid)
        print datetime.now(),
        print ':reviews gained/exist'
        if db.result.find({'_id':pid,'valid':1}).count()==0:
            nlp_dep.doit(pid)
        print datetime.now()
        print 'nltk done'
        return True
    except:
        print "Unexpected error:", sys.exc_info()[0]
        return False
