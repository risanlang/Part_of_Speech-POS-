#!/usr/bin/python

import sys
import nltk
import math
import time
import re
import numpy as np
from collections import defaultdict, deque
from pickle import dump

START_SYMBOL = '*'
STOP_SYMBOL = 'STOP'
RARE_SYMBOL = '_RARE_'
RARE_WORD_MAX_FREQ = 5
LOG_PROB_OF_ZERO = -1000


# Receives a list of tagged sentences and processes each sentence to generate a list of words and a list of tags.
# Each sentence is a string of space separated "WORD/TAG" tokens, with a newline character in the end.
def split_wordtags(brown_train):
    print(len(brown_train))
    print(brown_train)
    brown_tags = [[wordtag.rsplit('/', 1)[-1] for wordtag in sentence.strip().split()] for sentence in brown_train]
    brown_tags = [[START_SYMBOL] * 2 + sent_tags + [STOP_SYMBOL] for sent_tags in brown_tags]

    brown_words = [[wordtag.rsplit('/', 1)[0] for wordtag in sentence.strip().split()] for sentence in brown_train]
    brown_words = [[START_SYMBOL] * 2 + sent_words + [STOP_SYMBOL] for sent_words in brown_words]
    return brown_words, brown_tags


def calc_ngrams(sent_tags, n):
    ngrams = [tuple(sent_tags[i:(i + n)]) for i in range(len(sent_tags) - n + 1)]
    return ngrams


def deleted_interpolation(unigram_c, bigram_c, trigram_c):
    lambda1 = lambda2 = lambda3 = 0
    for a, b, c in trigram_c.keys():
        v = trigram_c[(a, b, c)]
        if v > 0:
            try:
                c1 = float(v-1)/(bigram_c[(a, b)]-1)
            except ZeroDivisionError:
                c1 = 0
            try:
                c2 = float(bigram_c[(a, b)]-1)/(unigram_c[(a,)]-1)
            except ZeroDivisionError:
                c2 = 0
            try:
                c3 = float(unigram_c[(a,)]-1)/(sum(unigram_c.values())-1)
            except ZeroDivisionError:
                c3 = 0

            k = np.argmax([c1, c2, c3])
            if k == 0:
                lambda3 += v
            if k == 1:
                lambda2 += v
            if k == 2:
                lambda1 += v

    weights = [lambda1, lambda2, lambda3]
    norm_w = [float(a)/sum(weights) for a in weights]
    return norm_w

# Receives tags from the training data and calculates tag trigram probabilities.
# It returns a python dictionary where the keys are tuples that represent the tag trigram, and the values are the log probability of that trigram.
def calc_ngram_counts(brown_tags):
    unigram_c = defaultdict(int)
    bigram_c = defaultdict(int)
    trigram_c = defaultdict(int)

    for sent_tags in brown_tags:
        unigram_tags = calc_ngrams(sent_tags, 1)
        bigram_tags = calc_ngrams(sent_tags, 2)
        trigram_tags = calc_ngrams(sent_tags, 3)

        for unigram in unigram_tags:
            unigram_c[unigram] += 1

        for bigram in bigram_tags:
            bigram_c[bigram] += 1

        for trigram in trigram_tags:
            trigram_c[trigram] += 1

    return unigram_c, bigram_c, trigram_c


def calc_ngram_probs(brown_tags, unigram_c, bigram_c, trigram_c):
    unigram_c[START_SYMBOL] = len(brown_tags)
    unigram_total = sum(unigram_c.values())
    unigram_p = {a: math.log(unigram_c[a], 2) - math.log(unigram_total, 2) for a in unigram_c}
    bigram_p = {(a, b): math.log(bigram_c[(a, b)], 2)  - math.log(unigram_c[(a,)], 2) for a, b in bigram_c}


    bigram_c[(START_SYMBOL, START_SYMBOL)] = len(brown_tags)
    trigram_p = {(a, b, c): math.log(trigram_c[(a, b, c)], 2) - math.log(bigram_c[(a, b)], 2) for a, b, c in trigram_c}

    weights = deleted_interpolation(unigram_c, bigram_c, trigram_c)
    trigram_d = {(a,b,c):math.log(weights[0] * (2 ** trigram_p[(a,b,c)]) + weights[1] * (2 **bigram_p[(a,b)]) + weights[2] * (2 ** unigram_p[(a,)]),2)for a, b,c in trigram_p}

    return unigram_p, bigram_p, trigram_p, trigram_d


# Takes output from calc_trigrams() and outputs it in the proper format
def q2_output(q_values, filename):
    outfile = open(filename, 'w')
    trigrams = q_values.keys()
    trigrams=sorted(trigrams)
    for trigram in trigrams:
        output = ' '.join(['TRIGRAM', trigram[0], trigram[1], trigram[2], str(q_values[trigram])])
        outfile.write(output + '\n')
    outfile.close()


# Takes the words from the training data and returns a set of all of the words that occur more than 5 times.
# brown_words is a python list where every element is a python list of the words of a particular sentence.
def calc_known(brown_words):
    known_words = set()
    word_c = defaultdict(int)

    for sent_words in brown_words:
        for word in sent_words:
            word_c[word] += 1

    for word, count in word_c.items():
        if count > RARE_WORD_MAX_FREQ:
            known_words.add(word)
    return known_words


# Takes the words from the training data and a set of words that should not be replaced for '_RARE_'.
# Returns the equivalent to brown_words but replacing the unknown words by '_RARE_'.
def replace_rare(brown_words, known_words):
    for i, sent_words in enumerate(brown_words):
        for j, word in enumerate(sent_words):
            if word not in known_words:
                brown_words[i][j] = RARE_SYMBOL
    return brown_words


# Takes the output from replace_rare() and outputs it to a file.
def q3_output(rare, filename):
    outfile = open(filename, 'w')
    for sentence in rare:
        outfile.write(' '.join(sentence[2:-1]) + '\n')
    outfile.close()


# Calculates emission probabilities and creates a set of all possible tags.
# The first return value is a python dictionary where each key is a tuple where the first element is a word
# and the second is a tag, and the value is the log probability of the emission of the word given the tag.
# The second return value is a set of all possible tags for this dataset.
def calc_emission(brown_words_rare, brown_tags):
    e_values_c = defaultdict(int)
    tag_c = defaultdict(int)

    for sent_words, sent_tags in zip(brown_words_rare, brown_tags):
        for word, tag in zip(sent_words, sent_tags):
            e_values_c[(word, tag)] += 1
            tag_c[tag] += 1

    e_values = {(word, tag): math.log(e_values_c[(word, tag)], 2) - math.log(tag_c[tag], 2) for word, tag in e_values_c}
    taglist = set(tag_c)
    return e_values, taglist


# Takes the output from calc_emission() and outputs it to a file.
def q4_output(e_values, filename):
    outfile = open(filename, 'w')
    emissions = e_values.keys()
    emissions=sorted(emissions)
    for item in emissions:
        output = ' '.join([item[0], item[1], str(e_values[item])])
        outfile.write(output + '\n')
    outfile.close()

def subcategorize(word):
    if re.search(r'(sha|da|na|hapoh|halor|ha|naduh|shaduh|hapdeng|haduh)$', word):
        return 'IN'
    elif re.search(r'(.*ngut|.*tylli)$', word):
        return 'ADJ'
    elif re.search(r'^-?[0-9]+(.[0-9]+)?$', word):
        return 'CN'
    elif re.search(r'(bad|ruh|namar|hynrei|tangba|katba|katta)$',word):
        return 'COC'
    elif re.search(r'(dei|long|don)$', word):
        return 'CO'
    elif re.search(r'.*lade$',word):
        return 'RFP'
    elif re.search(r'^hi$',word):
        return 'EMP'
    elif re.search(r'(dang|nang)$',word):
        return 'VPP'
    elif re.search(r'([uU]n|[kK]an|[kK]in|[sS]a|[yY]n|[nN]gin|[pP]hin)$',word):
        return 'VFT'
    elif re.search(r'^[bB]a$',word):
        return 'COM'
    elif re.search(r'^\W+$',word):
        return 'SYM'
    elif re.search(r'[^a-z\W]a$',word):
        return 'IN'
    elif re.search(r'[Jj]ing',word):
        return 'ABN'
    else:
        return RARE_SYMBOL


# This function implements the Viterbi algorithm by taking data to tag (brown_dev_words), a set of all possible tags (taglist), a set of all known words (known_words),
# trigram probabilities (q_values) and emission probabilities (e_values) and outputs a list where every element is a tagged sentence
# in the WORD/TAG format, separated by spaces and with a newline in the end, just like our input tagged data.
def viterbi(brown_dev_words, taglist, known_words, q_values, e_values):
    print(taglist)
    print(len(taglist))
    print(brown_dev_words)
    # pi[(k, u, v)]: max probability of a tag sequence ending in tags u, v
    # at position k
    # bp[(k, u, v)]: backpointers to recover the argmax of pi[(k, u, v)]
    tagged = []
    pi = defaultdict(float)
    bp = {}

    # Initialization
    pi[(0, START_SYMBOL, START_SYMBOL)] = 0.0

    # Define tagsets S(k)
    def S(k):
        if k in (-1, 0):
            return {START_SYMBOL}
        else:
            return taglist

    # The Viterbi algorithm
    for sent_words_actual in brown_dev_words:
        sent_words = [word if word in known_words else RARE_SYMBOL \
                      for word in sent_words_actual]
        n = len(sent_words)
        for k in range(1, n+1):
            for u in S(k-1):
                for v in S(k):
                    max_score = float('-Inf')
                    max_tag = None
                    for w in S(k - 2):
                        if e_values.get((sent_words[k-1], v), 0) != 0:
                            score = pi.get((k-1, w, u), LOG_PROB_OF_ZERO) + \
                                    q_values.get((w, u, v), LOG_PROB_OF_ZERO) + \
                                    e_values.get((sent_words[k-1], v))
                            if score > max_score:
                                max_score = score
                                max_tag = w
                    pi[(k, u, v)] = max_score
                    bp[(k, u, v)] = max_tag

        max_score = float('-Inf')
        u_max, v_max = None, None
        for u in S(n-1):
            for v in S(n):
                score = pi.get((n, u, v), LOG_PROB_OF_ZERO) + \
                        q_values.get((u, v, STOP_SYMBOL), LOG_PROB_OF_ZERO)
                if score > max_score:
                    max_score = score
                    u_max = u
                    v_max = v

        tags = deque()
        tags.append(v_max)
        tags.append(u_max)

        for i, k in enumerate(range(n-2, 0, -1)):
            tags.append(bp[(k+2, tags[i+1], tags[i])])
        tags.reverse()

        tagged_sentence = deque()
        for j in range(0, n):
            tagged_sentence.append(sent_words_actual[j] + '/' + tags[j])
        tagged_sentence.append('\n')
        tagged.append(' '.join(tagged_sentence))


    return tagged

# Takes the output of viterbi() and outputs it to file.
def q5_output(tagged, filename):
    outfile = open(filename, 'w',encoding='UTF-8')
    for sentence in tagged:
        outfile.write(sentence)
    outfile.close()





# Takes the output of nltk_tagger() and outputs it to file.
def q6_output(tagged, filename):
    outfile = open(filename, 'w',encoding="UTF-8")
    for sentence in tagged:
        outfile.write(sentence)
    outfile.close()


DATA_PATH = 'E:/HMM/'
OUTPUT_PATH = 'E:/HMM/POSoutput/'


def main():
    #t0=time.clock()

    infile = open(DATA_PATH + 'new1.txt', 'r',encoding="UTF-8")
    brown_train = infile.readlines()
    infile.close()

    brown_words, brown_tags = split_wordtags(brown_train)


    unigram_c, bigram_c, trigram_c = calc_ngram_counts(brown_tags)

    unigram_p, bigram_p, trigram_p, trigram_d = calc_ngram_probs(brown_tags, unigram_c, bigram_c, trigram_c)

    q_values = trigram_d

    q2_output(q_values, OUTPUT_PATH + 'B2.txt')

    known_words = calc_known(brown_words)

    brown_words_rare = replace_rare(brown_words, known_words)

    q3_output(brown_words_rare, OUTPUT_PATH + 'B3.txt')

    e_values, taglist = calc_emission(brown_words_rare, brown_tags)

    q4_output(e_values, OUTPUT_PATH + 'B4.txt')

    del brown_train
    del brown_words_rare

    infile = open(DATA_PATH + 'Brown_dev1.txt','r',encoding="UTF-8")
    brown_dev = infile.readlines()
    infile.close()

    brown_dev_words = []
    for sentence in brown_dev:
        brown_dev_words.append(sentence.split(' ')[:-1])
    print(brown_dev_words)

    viterbi_tagged = viterbi(brown_dev_words, taglist, known_words, q_values, e_values)
    print(viterbi_tagged)
    q5_output(viterbi_tagged, OUTPUT_PATH + 'B5.txt')




if __name__ == '__main__':
    main()