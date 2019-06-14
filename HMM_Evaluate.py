import nltk
from nltk.corpus.reader.plaintext import PlaintextCorpusReader
from pickle import load

DATA_PATH = 'E:/HMM/' # Directory of corpus.
DATA_PATH1= 'E:/HMM/POSoutput/'

infile = open(DATA_PATH + 'Brown_tagged_dev1.txt','r',encoding="UTF-8")
correct_sentences= infile.readlines()
infile.close()

infile = open(DATA_PATH1 + 'B5.txt','r',encoding="UTF-8")
user_sentences = infile.readlines()
infile.close()


num_correct = 0
total = 0
Hdictlist=[]
Pdictlist=[]
for user_sent, correct_sent in zip(user_sentences, correct_sentences):
    user_tok = user_sent.split()
    correct_tok = correct_sent.split()
    for i in user_tok:
        tagged = i.split()
        for t in tagged:
            temp1 = nltk.tag.str2tuple(t)
            Pdictlist.append(temp1)
    #print(Pdictlist)

    for i in correct_tok:
        tagged = i.split()
        for t in tagged:
            temp1 = nltk.tag.str2tuple(t)
            Hdictlist.append(temp1)
    #print(Hdictlist)

print(Pdictlist)
print(Hdictlist)
print(len(Hdictlist))
count=0
for i,j in zip(Pdictlist,Hdictlist):
    if i[1]==j[1]:
        count=count+1
print(count)
score=count/len(Pdictlist)
print(score)













'''newcorpus = PlaintextCorpusReader(corpusdir, '.*')
print(newcorpus.fileids())
dictlist=[]

for i in newcorpus.fileids():
    tagged_sent=newcorpus.raw(i)
    tagged=tagged_sent.split()
    for t in tagged:
        temp1=nltk.tag.str2tuple(t)
        dictlist.append(temp1)
print(dictlist)


#Loading the Saved Tagger
input = open('t2.pkl', 'rb')
tagger = load(input)
input.close()
#text = Ka por ïalap elekshon ha jylla Meghalaya na ka bynta ban jied ïa ki arngut ki MP sha Lok Sabha ka la kut noh
#print(tagger.tag(nltk.word_tokenize(text)))
print(tagger.evaluate([dictlist]))'''