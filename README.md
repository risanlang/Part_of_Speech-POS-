# Part_of_Speech-POS-Tagger_in_Khasi_language
Part Of Speech Tagging in  Khasi Language
Transformation-Based-Learning (TBL) : 
The general framework of Brill’s corpus-based learning is called Transformation based Error-driven Learning (TBL). The name reflects the fact that the tagger is based on transformations or rules,and learns by detecting errors.  First, a general description of how TBL works in principle is given,then a more detailed explanation for the specific modules of the tagger will follow in subsequentsections.  Roughly, the TBL begins with an unannotated text as input which passes through the initial state annotator such as Regex, Unigram, Bigram and Trigram. It assigns tags to the input in some fashion. The output of the initial state annotator is a temporary corpus which is then compared to a goal corpus which has been manually tagged. For each time the temporary corpus is passed through the learner, the learner produces one new rule, the single rule that improves the annotation the most (compared with the goal corpus), and replaces the temporary corpus with the analysis that results when this rule is applied to it. By this process the learner produces an ordered list of rules. The tagger uses TBL twice: once in the lexical module deriving rules for tagging unknown words, and once in the contextual module for deriving rules that improve the accuracy.Both modules use two types of corpora:  the goal corpus,derived from a manually annotated corpus, and a temporary corpus whose tags are improved step bystep to resemble the goal corpus more and more.


Hidden Markov Model (HMM) : 
The HMM is widely used in natural language processing since language consists of sequences such as paragraph,  sentences,  phrases,  words and characters.  It is a probabilistic sequence model that assigns a label to each unit in a sequence of observations. This method calculates the probability distribution over the possible sequences of labels and chooses the best label sequence which maximizes the probability of generating the observed sequence.Here we use Trigram for POS in HMM.


Viterbi algirithm : The Viterbi algorithm,is a dynamic algorithm which makes the search computationally more efficient as compared to brute force because as the number of words to tag increase the time for computation also increase exponentially therefore Viterbi algorithm helps to find the most probable tags efficiently.We also provide the emmision and transition probability, testing text and the tagset as parameters to the algorithm.
The evaluate python file is used to calculate the accuracy of the HMM Tagger and use the formula :
      Accuracy= No. of words correctly tag/ No. of words in testing corpus
but, first we take the testing text and tag it manually and again give the testing text to the Viterbi algorithm and using the above formula to calculate the accuracy.
NOTE : The accuracy of HMM with viterbi algorithm is only approximately 60 percent
