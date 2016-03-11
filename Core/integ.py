import amazon_rev
import flipkart
import snapdeal
import nlp_dep
from datetime import datetime
import sys
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')

db = client.revmine_2


def justDoIt(domain,pid,product_name=None):
    try:
        print datetime.now()
        if 'amazon.in' in domain:
            amazon_rev.main(pid, domain)
        elif 'snapdeal.com' in domain:
            snapdeal.main(pid, product_name, domain)
        elif 'flipkart' in domain:
            pid = pid.lower()
            flipkart.main(pid, product_name, domain)

        print datetime.now(),
        print ':reviews gained/exist'

        if db.result.find({'_id' : pid, 'domain' :domain, 'valid':1 }).count()==0:
            nlp_dep.doit(pid, domain)

        print datetime.now()
        print 'nltk done'
        return True
    except:
        import traceback; traceback.print_exc();
        print "Unexpected error:", sys.exc_info()[0]
        return False
