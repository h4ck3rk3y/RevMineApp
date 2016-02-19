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

client = MongoClient('192.168.1.106')
#client = MongoClient('172.17.30.135')
db = client.revmine
reviews = db.reviews
result_db = db.result


stop = stopwords.words('english')
stop.append('amazon')
stop.append('flipkart')
stop.append('snapdeal')
stop.append('book')
stop.append('phone')

def strip_proppers_POS(text):
	tokens = nltk.word_tokenize(text)
	tagged = nltk.tag._pos_tag(tokens,tagset, tagger)
	res = []
	words = [(word,pos) for word,pos in tagged if (pos[0]=="N" or pos[0]=="J") and len(word)>3 and word not in stop and eng_check.check(word) and not any(ccc.isdigit() for ccc in word)]
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

def findLefts(text):
	tokens = nltk.word_tokenize(text)
	tagged = nltk.tag._pos_tag(tokens,tagset, tagger)
	res = []
	words = [(word,pos) for word,pos in tagged if (pos[0]=="N") and len(word)>3 and word not in stop and eng_check.check(word) and not any(ccc.isdigit() for ccc in word)]
	leftsToBeReturned = {}
	for i in range(1,len(words)):
		leftsToBeReturned[words[i][0]] = []
		for j in range(0,i):
			leftsToBeReturned[words[i][0]].append(words[j][0])
	return leftsToBeReturned

def findRights(text):
	tokens = nltk.word_tokenize(text)
	tagged = nltk.tag._pos_tag(tokens,tagset, tagger)
	res = []
	words = [(word,pos) for word,pos in tagged if (pos[0]=="N") and len(word)>3 and word not in stop and eng_check.check(word) and not any(ccc.isdigit() for ccc in word)]
	
	rightsToBeReturned = {}
	for i in range(0,len(words)-1):
		rightsToBeReturned[words[i][0]] = []
		for j in range(i+1,len(words)):
			rightsToBeReturned[words[i][0]].append(words[j][0]) 
	return rightsToBeReturned

def jacard(lefts,rights, word1, word2):
	if word1 not in lefts or word2 not in lefts:
		left_jacard = 0
	else:
		left_jacard = len(set(lefts[word1]).intersection(lefts[word1]))/len(set(lefts[word1]).union(lefts[word2])) 
	if word1 not in rights or word2 not in rights:
		right_jacard = 0
	else:
		right_jacard = len(set(rights[word1]).intersection(rights[word1]))/len(set(rights[word1]).union(rights[word2]))

	return (left_jacard+right_jacard)/2


def doit(pid, domain):

	arr = []
	revs = []
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
			l = findLefts(sent)
			#l = {w1 :[w2,w3], w4:[w5]} 
			r = findRights(sent)
			for left in l:
				if left not in lefts:
					lefts[left] = list(set(l[left]))
				else:
					for left_val in l[left]:
						if left_val not in lefts[left]:
							lefts[left].append(left_val )
			
			for right in r:
				if right not in rights:
					rights[right] = list(set(r[right]))
				else:
					for right_val in r[right]:
						if right_val not in rights[right]:
							rights[right].append(right_val )
		

			revs.append((sent,link))
	jacard_scores = {}
	for i in lefts:
		for j in lefts:
			if j != i: 				
				score = jacard(lefts,rights,i,j)
				if i not in jacard_scores:
					jacard_scores[i] = score
				else:
					jacard_scores[i] += score
				if j not in jacard_scores:
					jacard_scores[j] = score
				else:
					jacard_scores[j] += score

	jacard_scores = (sorted(jacard_scores.iteritems(), key=operator.itemgetter(1), reverse=True))
	noun_scores = {}
	neg_noun_scores = {}
	revsSelected = []
		
	for yolo in range(0,len(arr),1):
		for i in arr[yolo]:
			adj = i[0]
			noun = i[1]
			dist = i[2]
			
			if noun in dict(jacard_scores[50:len(jacard_scores)]):
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

	result['sentences'] = final_sentences

	#pprint(result)
	result_db.insert(result)
	return True

#doit('itmedhx3uy3qsfks','www.amazon.in')
