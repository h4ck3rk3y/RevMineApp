from __future__ import division
from pymongo import MongoClient
import nltk
from nltk.tag.perceptron import PerceptronTagger
import enchant
from pprint import pprint
eng_check = enchant.Dict("en_US")
tagger = PerceptronTagger()
tagset = None
import operator
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.corpus import wordnet as wn
from nltk.corpus import sentiwordnet as swn
import string
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
import inflect

#client = MongoClient('10.42.0.16')
client = MongoClient('mongodb://localhost:27017')
#client = MongoClient('172.17.30.135')
db = client.revmine
reviews = db.reviews
result_db = db.result
p = inflect.engine()

stop = stopwords.words('english')
stop.append('amazon')
stop.append('flipkart')
stop.append('snapdeal')
stop.append('book')
stop.append('phone')
stop.append('review')
stop.append('life')
stop.append('user')
stop.append('usage')
stop.append('product')
stop.append('quality')


def strip_proppers_POS(text):
	tokens = nltk.word_tokenize(text)
	tagged = nltk.tag._pos_tag(tokens,tagset, tagger)
	res = []
	words = [(word,pos) for word,pos in tagged if (pos[0]=="N" or pos[0]=="J") and len(word)>3 and word not in stop and not p.singular_noun(word) and eng_check.check(word) and not any(ccc.isdigit() for ccc in word)]
	word_serial = {}
	for w in range(0,len(words),1):
		word_serial[words[w][0]] = w
	for a in words:
		flag = 0
		if a[1][0] == "J":
			adj = a[0]
			minDist = 32768
			for w in words:
				if w[1][0] == "N":
					noun = w[0]
					dist = abs(word_serial[adj]-word_serial[noun])
					if dist < minDist:
						minDist = dist
						nearestNoun = noun
						flag = 1
			if flag==1:
				if minDist > 0.0:
					res.append((adj,noun,(1/pow(minDist,2))))
	return res

def doit(pid, domain):

	arr = []
	revs = []
	documents = []
	lefts = {}
	rights = {}

	print "In Doit"
	i = reviews.find_one({"_id":pid})
	title = nltk.word_tokenize(i['title'].lower())
	for y in title:
		stop.append(y)
	for j in range(1,min(len(i)-2,50)):
		sents = nltk.sent_tokenize(i[str(j)]['text'].lower())
		link = i[str(j)]['link']
		for sent in sents:
			arr.append(strip_proppers_POS(sent))
			revs.append((sent,link))
			documents.append(sent)
	noun_scores = {}
	neg_noun_scores = {}
	revsSelected = []
	tfidf_vectorizer = TfidfVectorizer(max_df=0.75, max_features=100,min_df=0.01,use_idf=True,stop_words="english", ngram_range=(1,2))
	try:
		tfidf_matrix = tfidf_vectorizer.fit_transform(documents)
		terms = tfidf_vectorizer.get_feature_names()
	except:
		err = 1
	bigrams = []
	for t in terms:
		if len(nltk.word_tokenize(t))==2:
			bigrams.append(i for i in t)
	
	for yolo in range(0,len(arr),1):
		for i in arr[yolo]:
			adj = i[0]
			noun = i[1]
			dist = i[2]
			if noun in terms or noun in bigrams:
				score = 0
				neg_score = 0
				adj_synset = swn.senti_synsets(adj,'a')
				if len(adj_synset) <= 0:
					adj_synset = swn.senti_synsets(adj,'v')
				if len(adj_synset) <= 0:
					synonyms = []
					for ss in wn.synsets(adj):
						for j in ss.lemma_names():
							synonyms.append(j)
					if len(synonyms)>1:
						w1 = synonyms[0]
						w2 = synonyms[1]
						adj_synset1 = swn.senti_synsets(w1,'a')
						adj_synset2 = swn.senti_synsets(w2,'a')
						if len(adj_synset1)>0:
							score += adj_synset1[0].pos_score()
							neg_score += adj_synset1[0].neg_score()
						if len(adj_synset2)>0:
							score += adj_synset2[0].pos_score()
							neg_score += adj_synset2[0].neg_score()
						score=score/2
				else:
					score += adj_synset[0].pos_score()
					neg_score += adj_synset[0].neg_score()
				if float(score) > 0.0:
					if noun not in noun_scores:
						noun_scores[noun] = [dist*score,1]
					else:
						noun_scores[noun][0] += dist*score
						noun_scores[noun][1] += 1
				if float(neg_score) > 0.0:
					if noun not in neg_noun_scores:
						neg_noun_scores[noun] = dist*neg_score
					else:
						neg_noun_scores[noun] += dist*neg_score
				if score+neg_score > 0.0:
					individualReview = revs[yolo][0]
					individualLink = revs[yolo][1]
					try:
						index = individualReview.index(noun)
						start = max(0,index-25)
						for st in range(start,0,-1):
							if individualReview[st]==" ":
								start = st+1
								break
						selectedPartOfReview = individualReview[start:min(len(individualReview),index+25)]
						if {'snippet':selectedPartOfReview,'link':individualLink,'topic':noun} not in revsSelected:
							revsSelected.append({'snippet':selectedPartOfReview,'link':individualLink,'topic':noun})
					except:
						revsSelected.append({'topic':adj+" "+noun,'link':"www.google.com"})
	noun_scores = sorted(noun_scores.items(),key=lambda x:x[1][1],reverse=True)
	ns = {}
	for n_s in noun_scores:
		ns[n_s[0]] = n_s[1][0]

	result = {}
	topics = {}
	valid_sents = {}
	result['domain'] = domain
	result['_id'] = pid
	result['valid'] = 0
	c=0
	for i in ns:
		if i in neg_noun_scores:
			if c<10:
				topics[i.rstrip('.').lstrip('$').replace('.','')] = round((ns[i])/(ns[i]+neg_noun_scores[i])*100,2)
				c+=1
			else:
				break

	result['valid'] = 1
	result['topics'] = topics

	final_sentences = []
	topics_selected = []
	for i in revsSelected:
		if i['topic'] in topics and i['topic'] not in topics_selected:
			final_sentences.append(i)
			topics_selected.append(i['topic'])

	result['sentences'] = {x['topic']:{'link': x['link'],'snippet': x['snippet']} for x in final_sentences}
	#pprint(result)
	result_db.insert(result)
	return True
#doit('B012II9E6C','www.amazon.in')
