import nltk
from nltk.corpus.reader.plaintext import PlaintextCorpusReader

#Loading the file you want to Train
corpusdir = 'E:\MTech' # Directory of corpus.

newcorpus = PlaintextCorpusReader(corpusdir, '.*')
print(newcorpus.fileids())
dictlist=[]

#Converting from word/tag pait to a list containing two tuple i.e,[(word1,tag),(word2,tag)]
for i in newcorpus.fileids():
    tagged_sent=newcorpus.raw(i)
    tagged=tagged_sent.split()
    for t in tagged:
        temp1=nltk.tag.str2tuple(t)
        dictlist.append(temp1)
print(dictlist)
print("This is the length of distinct words")
print(len(set(dictlist)))
fdist=nltk.FreqDist(dictlist)
print("fdist items")
print(fdist.items())
print(fdist.max())




rawtext = '''
 '''

def train_brill_tagger(train_data):
    # Modules for creating the templates.
    from nltk import UnigramTagger
    # The brill tagger module in NLTK.
    from nltk.tag.brill_trainer import BrillTaggerTrainer
    from nltk import BigramTagger,UnigramTagger,TrigramTagger
    import nltk
    from pickle import dump
    #unigram_tagger = UnigramTagger(train_data)
    templates=nltk.tag.brill.fntbl37()
    #Regular expression (Regex) Tagger as a default tagger
    default_tagger = nltk.RegexpTagger(
        [(r'^[Jj]ing', 'ABN'),
         (r'^[pP]yn', 'CAV'),
         (r'^[nN]ga$', '1PSG'),
         (r'^[pP]hi$', '2PG'),
         (r'^[pP]ha$', '2PF'),
         (r'^[mM]e$', '2PM'),
         (r'^[iI]$', '3PSG'),
         (r'^[bB]an$', 'INP'),
         (r'^[Kk]a$', '3PSF'),
         (r'^[uU]$', '3PSM'),
         (r'^[kK]i$', '3PPG'),
         (r'(sha|da|na|hapoh|halor|ha|naduh|shaduh|hapdeng|haduh)$', 'IN'),
         (r'(bad|ruh|namar|hynrei|tangba|katba|katta)$', 'COC'),
         (r'(lada|haba|khnang|ynda)$', 'SUC'),
         (r'(katkum|kat|pat|wat|tang|lang)$', 'AD'),
         (r'(bun|baroh)$', 'QNT'),
         (r'^-?[0-9]+(.[0-9]+)?$', 'CN'),
         (r'(dei|long|don)$', 'CO'),
         (r'^[jJ]ong$', 'POP'),
         (r'^[sS]hah$', 'PAV'),
         (r'^[lL]ah$', 'MOD'),
         (r'^[lL]a$', 'VST'),
         (r'(ym|em|khlem|nym|kam)$', 'NEG'),
         (r'^hi$', 'EM'),
         (r'.*lade$', 'RFP'),
         (r'(dang|nang)$', 'VPP'),
         (r'([uU]n|[kK]an|[kK]in|[sS]a|[yY]n|[nN]gin|[pP]hin)$', 'VFT'),
         (r'(.*ngut|.*tylli)$', 'ADJ'),
         (r'^[bB]a$', 'COM'),
         (r'^\W+$', 'SYM'),
         (r'[^a-z\W]a$', 'IN'),
         (r'([vV]ote|[bB]ye|[cC]onstituency|[sS]outh)$', 'FR'),
         (r'.*', 'CMN')

         ])
    t0 = default_tagger
    print(train_data)
    t1 = UnigramTagger(train_data,backoff=t0)
    t2 = BigramTagger(train_data,backoff=t1)
    t3 = TrigramTagger(train_data,backoff=t2)


    trainer = BrillTaggerTrainer(initial_tagger=t3,
                                   templates=templates, trace=3,
                                   deterministic=True)
    brill_tagger = trainer.train(train_data,max_rules=10)

    # Saving the Tagger for future use
    output = open('t2.pkl', 'wb')
    dump(t3, output, -1)
    output.close()
    return brill_tagger
#printing the number of distinct words
print(len(set(dictlist)))
#printing the number of words
length=len(dictlist)
print(length)
#Dividing the corpus into training and testing i.e, 90 for training and 10 percent for testing
trainsize=int((length*90)/float(100))
print(trainsize)

khasi_train = ([dictlist[:trainsize]])
print(khasi_train)

khasi_test = ([dictlist[trainsize+1:]])
print(khasi_test)

#Giving the training data to Brill's for training
mt = train_brill_tagger(khasi_train)

gold_tag=[]
test_tag=[]
#seperating the training corpus into individual words which is given to brill to tag which contain in test_tag
for i in khasi_test:
    for j in i:
        a=j[0]
        gold_tag.append(j)
        test_tag.append(a)
print(test_tag)
print(gold_tag)
output=mt.tag(test_tag)
print(output)
#Evaluating the accuracy of the brill's tagger
print(mt.evaluate(khasi_test))
#preparation of data to be given to the confusionmatrix
gold_tags = [tag for (word, tag) in gold_tag]
test_tags= [tag for (word,tag) in output]
print(gold_tags)
print(test_tags)
print(set(gold_tags+test_tags))
#printing the confusionmatrix of standard tags with the test tags
print(nltk.ConfusionMatrix(gold_tags,test_tags))
















#Loading the Saved Tagger
'''input = open('t2.pkl', 'rb')
tagger = load(input)
input.close()
text = """The board's action shows what free enterprise
...     is up against in our complex maze of regulatory laws ."""
tokens = text.split()
tagger.tag(tokens)'''