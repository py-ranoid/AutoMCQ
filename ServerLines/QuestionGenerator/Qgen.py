# -*- coding: utf-8 -*-
import spacy
import random
import time
import re
from nltk import word_tokenize,sent_tokenize
# from nltk.util import ngrams
from gensim.models import Word2Vec
from spacy.symbols import ORTH, LEMMA
from nltk.stem.porter import PorterStemmer
from QuestionGenerator.Qgen_utils import ngrams, metric, date_eliminator, resolve_prons, w2v_model,get_w2v_options
from QuestionGenerator.Distract import datesDistract
from Constants import *
from QuestionGenerator import PDFManip as manip

try : nlp = spacy.load('en_core_web_sm')
except : nlp = spacy.load('en')
stemmer = PorterStemmer()
TEST_TEXT = """
The Battle of Plassey was a decisive victory of the British East India Company over the Nawab of Bengal and his French allies on 23 June 1757. The battle consolidated the Company's presence in Bengal, which later expanded to cover much of India over the next hundred years. The battle took place at Palashi (Anglicised version: Plassey) on the banks of the Hooghly River, about 150 kilometres (93 mi) north of Calcutta and south of Murshidabad, then capital of Bengal (now in Nadia district in West Bengal). The belligerents were the Nawab Sirajuddaulah, the last independent Nawab of Bengal, and the British East India Company. Siraj-ud-daulah had become the Nawab of Bengal the year before, and he ordered the English to stop the extension of their fortification. Robert Clive bribed Mir Jafar, the commander in chief of the Nawab's army, and also promised him to make him Nawab of Bengal. He defeated the Nawab at Plassey in 1757 and captured Calcutta. The battle was preceded by the attack on British-controlled Calcutta by Nawab Siraj-ud-daulah and the Black Hole massacre. The British sent reinforcements under Colonel Robert Clive and Admiral Charles Watson from Madras to Bengal and recaptured Calcutta. Clive then seized the initiative to capture the French fort of Chandernagar. Tensions and suspicions between Siraj-ud-daulah and the British culminated in the Battle of Plassey. The battle was waged during the Seven Years' War (1756–1763), and, in a mirror of their European rivalry, the French East India Company (La Compagnie des Indes Orientales) sent a small contingent to fight against the British. Siraj-ud-Daulah had a numerically superior force and made his stand at Plassey. The British, worried about being outnumbered, formed a conspiracy with Siraj-ud-Daulah's demoted army chief Mir Jafar, along with others such as Yar Lutuf Khan, Jagat Seths (Mahtab Chand and Swarup Chand), Omichund and Rai Durlabh. Mir Jafar, Rai Durlabh and Yar Lutuf Khan thus assembled their troops near the battlefield but made no move to actually join the battle. Siraj-ud-Daulah's army with 50,000 soldiers, 40 cannons and 10 war elephants was defeated by 3,000 soldiers of Col. Robert Clive, owing to the flight of Siraj-ud-daulah from the battlefield and the inactivity of the conspirators. The battle ended in 11 hours. This is judged to be one of the pivotal battles in the control of Indian subcontinent by the colonial powers. The British now wielded enormous influence over the Nawab and consequently acquired significant concessions for previous losses and revenue from trade. The British further used this revenue to increase their military might and push the other European colonial powers such as the Dutch and the French out of South Asia, thus expanding the British Empire.
#""".strip()

def timecop(tag,start):
    print (tag.upper()[:3]+"_TIME:",time.time()-start)

BLANQ = "__________"
ENTITY_PRIORITIES = {
    "PERSON": 20,
    "NORP": 10,
    "FAC": 9,
    "ORG": 19,
    "GPE": 15,
    "LOC": 9,
    "PRODUCT": 8,
    "EVENT": 18,
    "WORK_OF_ART": 17,
    "LAW": 16,
    "LANGUAGE": 0,
    "DATE": 14,
    "TIME": 1,
    "PERCENT": 5,
    "MONEY": 8,
    "QUANTITY": 7,
    "ORDINAL": 6,
    "CARDINAL": 2,
    "VERB":10,
    "NOUN": 8
}


def get_doc(content):
    return nlp(content)

def get_entities(doc):
    """
    Get all entities in given Spacy document object.
        :param doc: Spacy Doc object, Used to generate entities
    """
    return doc.ents


# def word_tokenize(word):
#     return word.split(' ')


def gen_word2vec(doc):
    """
    Trains word2vec model from Spacy document object
        :param doc: Spacy Document object
    """
    sents = [[y.orth_.lower() for y in x] for x in doc.sents]
    model = Word2Vec(sents, size=100, window=5, min_count=1, workers=4)
    return model


def gen_word2vec_from_content(content):
    """
    Trains word2vec model from string (paragraph)
        :param content: str, Text to train model on
    """
    sents = [word_tokenize(s) for s in sent_tokenize(content.lower())]
    model = Word2Vec(sents, size=100, window=5, min_count=1, workers=4)
    return model


def sentID2sent(sentID, doc):
    """
    Get sentence from document, given sentence ID.
    Returns sentence and sentence length.
        :param sentID: str, Sentence ID
        :param doc: Spacy document object, Document containing sentences
    """
    start, end = [int(x) for x in sentID.split("#")]
    return doc[start:end].orth_.strip(), end - start


def find_best_options(options, doc_w2v_model, answer,ent_type , sentence):
    """
    Choose the best 3 (2+target) options from the given options.
        :param options: list, All options
        :param doc_w2v_model: gensim Word2Vec model used to compare options with target
        :param answer: str, Target word
        :param ent_type: str, Entity type
    """
    # Convert answer to lowercase and create trigrams
    ans_low = answer.lower()
    ans_set = set(word_tokenize(ans_low))
    source = word_tokenize(ans_low)
    source_grams = ngrams(ans_low, 3)

    distances = {}
    temp = time.time()
    if ent_type == ENT_DATE:
        print ("TRYING DATE DISTRACT")
        try:
            return datesDistract(answer)
        except Exception as ex:
            print(str(ex))
            options = date_eliminator(answer,options)
        print ("DONE WITH DATE DISTRACT")
        # TODO If reduced options are too few, add synthetic date discriminators
    temp = time.time()
    for opt in options:
        # Eliminate options that have too many common ngrams
        opt_low = opt.lower()
        opt_set = set(word_tokenize(opt_low))
        if len(opt_set.union(ans_set)) ==len(ans_set):
            distances[opt] = 20
        if opt == answer:
            continue
        opt_grams = ngrams(opt_low, 3)
        if metric(source_grams, opt_grams) > 0.18:
            # Assign very high distance if metric is high
            distances[opt] = 40
        else:
            # print (answer,sentence,sentence.replace(answer , opt))
            distances[opt] = doc_w2v_model.wmdistance(word_tokenize(sentence.replace(answer , opt).lower()),word_tokenize(sentence.lower()))
            # distances[opt] = doc_w2v_model.wmdistance(word_tokenize(opt.lower()), word_tokenize(answer.lower()))
                
        if len(opt_set.union(ans_set)) == len(opt_set):
            # print(opt_set, ans_set)
            distances[opt] *= 2    
    # Assign distance to answer to 0 (closest to target)
    distances[answer] = 0
    options.sort(key=lambda x: distances[x])
    print ("Opt_sort_time:",time.time()-temp)
    # print (distances)
    return options


def map_ents_to_types(ent_list, doc):
    """
    Creates 4 dictionaries. 
    - ent2type : Maps entity text to entity type
    - type2ent : Maps entity type to list of all entities of that type
    - counter  : Maps entity text to its count
    - sent2ent : Maps sent_id ("start_index#end_index") to list of all entities in it.
        :param ent_list: Spacy entities generator object, Contains all entities in given document
        :param doc: Spacy Doc object
    """
    ent2type = {}
    type2ent = {}
    counter = {}
    sent2ent = {}
    all_starts = [s.start for s in doc.sents]
    for e in ent_list:
        init = e.start
        ent_sent = e.sent
        if doc[init].orth_ == '\n':
            continue

        try:
            sent_start,sent_end = resolve_prons(all_starts.index(ent_sent.start),doc,nlp)
        except Exception as ex:
            print('Hung over : ' + str(ex))
            sent_start, sent_end = ent_sent.start , ent_sent.end
        sent_id = str(sent_start) + "#" + str(sent_end)
        etype = doc[init].ent_type_

        ent2type[e.orth_] = etype
        temp = type2ent.get(etype, None)

        type2ent_new = set(
            [e.orth_]) if temp is None else temp.union(set([e.orth_]))
        type2ent[etype] = type2ent_new

        counter[e.orth_] = 1 + counter.get(e.orth_, 0)

        sent2ent[sent_id] = [e.orth_] + sent2ent.get(sent_id, [])

    return ent2type, type2ent, counter, sent2ent


def map_ents_to_types_only(ent_list, doc):
    """
    Creates 4 dictionaries. 
    - ent2type : Maps entity text to entity type
    - type2ent : Maps entity type to list of all entities of that type
    - counter  : Maps entity text to its count
    - sent2ent : Maps sent_id ("start_index#end_index") to list of all entities in it.
        :param ent_list: Spacy entities generator object, Contains all entities in given document
        :param doc: Spacy Doc object
    """
    type2ent = {}
    for e in ent_list:
        init = e.start
        if doc[init].orth_ == '\n':
            continue        
        etype = doc[init].ent_type_

        temp = type2ent.get(etype, None)
        type2ent_new = set([e.orth_]) if temp is None else temp.union(set([e.orth_]))
        type2ent[etype] = type2ent_new

    return type2ent

def get_all_verbs(doc):
    all_verbs = set([])
    all_nouns = set(doc.noun_chunks)
    for sent in doc.sents:
        for x in sent:
            if x.pos_=="VERB" and not x.is_stop:
                all_verbs.add(x.lower_)
    return all_verbs,all_nouns

def verb_picker(doc):
    """
    Function to pick verb target words from the document.
        :param doc: spacy soc object.
    """
    # Map sentence ID to potential verb blanks
    passive_sents2verbs = {}
    active_sents2verbs = {}
    all_verbs = set([])
    for sent in doc.sents:
        for x in sent:
            # Pick verbs that are not stopwords or roots of sentences shorter than MAX_SENT_LEN
            if x.pos_=="VERB" and not x.is_stop:
                all_verbs.add(x.lower_)
                if not x.head == x:
                    if x.n_lefts:
                        sent_id = str(x.sent.start)+"#"+str(x.sent.end)
                        passive_sents2verbs[sent_id] = passive_sents2verbs.get(sent_id,set()).union(set([x.orth_]))
                    elif x.n_rights:
                        sent_id = str(x.sent.start)+"#"+str(x.sent.end)
                        active_sents2verbs[sent_id] = active_sents2verbs.get(sent_id,set()).union(set([x.orth_]))
    print ("PASSIVE :",len(passive_sents2verbs),"ACTIVE :",len(active_sents2verbs))
    if len(passive_sents2verbs) >= len(active_sents2verbs):
        return passive_sents2verbs, all_verbs
    else:
        return active_sents2verbs, all_verbs

def get_w2v_sim(a,b):
    try:return w2v_model.similarity(a, b)
    except KeyError:return 999

def get_mul_optdoc(option,sent):
    if option in sent:
        return 0.1 
    else:
        return 1
    
def get_verb_qs(doc , skip_sent_ids = set()):
    sent_verbs, all_verbs = verb_picker(doc)
    questions = []
    for s in sent_verbs:

        if s in skip_sent_ids:
            continue

        sent = sentID2sent(s,doc)[0]
        sent_low = sent.lower()
        ans=sent_verbs[s].pop()

        """
        This currently only picks the best options from the document (~220 µs) which is fast and makes grammatical sense,
        but may not be very efficient. I see two alternatives
        - Get list of all verbs from the entire doc
        - Pick the best options from word2vec. 
            - Getting the most similar from word2vec's corpus is time-consuming. 
            - The best options may be too similar to the word and may need stem-based elimination.
                PorterStemmer takes around 20ms whereas spacy's lemmatization takes ~110ms.
        """
        options = sorted(all_verbs, key=lambda x:get_w2v_sim(ans.lower(),x) * get_mul_optdoc(x, sent_low),reverse=True)[:2]
        options += [ans.lower()]
        if len(options) <3:
            continue
        random.shuffle(options)
        sample = {
            QUESTION: blanq_sent(sent,ans),
            ANSWER: ans,
            OPTIONS: options,
            ANSWER_TYPE: "VERB",
            QUESTION_RANK: Q_TYPE_VERB + str(len(questions))
        }
        if "_________" not in sample[QUESTION]:continue
        questions.append(sample)
    return questions,set(sent_verbs.keys())


def noun_picker(doc):
    counts = doc.count_by(LEMMA)
    word_counter = {}
    for word_id, count in sorted(counts.items(), reverse=True, key=lambda item: item[1]):
        word = stemmer.stem(nlp.vocab.strings[word_id])
        word_counter[word] = word_counter.get(word,0)+count

    all_nouns = set()
    sent2nouns = {}
    noun_counts = {}
    sent_mins ={}
    for x in doc.noun_chunks:
        # Ignore chunk if longer than 3 words or shorted than 4 chars
        if len(x.orth_) < 4 or len(x)>3:continue

        # Truncating noun chunk by removing stop words and "the"
        start =x.start
        for y in x:
            if not y.is_stop and not y.lower_=='the':
                start = y.i
                break
        noun = doc[start:x.end]

        sent_id = str(x.sent.start)+"#"+str(x.sent.end)
        # Should nouns be converted to lowercase ?
        all_nouns.add(noun.lower_)

        if not noun.lower_ in noun_counts:
            noun_counts[noun.lower_] = sum([word_counter.get(stemmer.stem(x.lemma_),1) for x in noun])/len(noun)
        if noun_counts[noun.lower_] < sent_mins.get(sent_id,50):
            sent2nouns[sent_id] = set([noun.orth_])
            sent_mins[sent_id] = noun_counts[noun.lower_]
        elif noun_counts[noun.lower_] == sent_mins.get(sent_id,50):
            sent2nouns[sent_id] = sent2nouns[sent_id].union(set([noun.orth_]))
    return all_nouns, sent2nouns


def get_noun_opts(all_nouns,target,sent):
    target_words = word_tokenize(target.lower())
    candidates = sorted(list(all_nouns),key=lambda x:w2v_model.wmdistance(target_words,word_tokenize(x))*(1/get_mul_optdoc(x.lower(),sent)))[:2]
    while target in candidates:
        candidates.remove(target)
    return candidates


def get_noun_sents(doc,skip_sent_ids=set()):
    all_nouns, sent2nouns = noun_picker(doc)
    all_sents = []
    for sent_id in sent2nouns:
        if sent_id in skip_sent_ids:
            continue
        sent = sentID2sent(sent_id,doc)[0]
        targets = sent2nouns[sent_id]
        if len(targets) == 1:
            target = targets.pop()
            try:
                options = get_w2v_options(target,nlp)
            except:
                options = get_noun_opts(all_nouns,target,sent.lower())
        else:
            target = random.sample(list(targets),1)[0]
            options = get_noun_opts(all_nouns,target,sent.lower())


        finalOptions = options
        for opt in finalOptions:
            if opt.lower() == target.lower():
                options.remove(opt)


        options = options[:2]
        options += [target]


        if len(options) < 3:
            continue

        random.shuffle(options)
        sample = {
            QUESTION: blanq_sent(sent,target),
            ANSWER: target,
            OPTIONS: options,
            ANSWER_TYPE: "NOUN",
            QUESTION_RANK: Q_TYPE_NOUN + str(len(all_sents))
        }
        if "_________" not in sample[QUESTION]:continue
        all_sents.append(sample)
    return all_sents,sent2nouns.keys()




def choose_ent(ents, counter, ent2type, mul_priority=False, weight=20):
    """
    Choose the best entity/target word from entites.
    - count_map : Maps counts to entities
        :param ents: list, All entities in sentence.
        :param counter: dict, Count of all entities in document
        :param ent2type: dict, Maps entity to entity type
        :param mul_priority=False: bool, to mutiple 
        :param weight=20: int, weightage given to
    """
    count_map = {}
    if mul_priority:
        # Assigns priority by mutiplying count and weightage
        # In case of multiple entities having the same value, picks the first entity
        for e in ents:
            pri = ENTITY_PRIORITIES[ent2type[e]]
            count_map[(weight / counter[e]) * pri] = [e] + count_map.get(e, [])
        return count_map[max(count_map.keys())][0]
    else:
        # Assigns priority based on count
        # In case of multiple entities having the same value, picks the entity with greates priority
        for e in ents:
            count_map[counter[e]] = [e] + count_map.get(e, [])
        temp = min(count_map.keys())
        if len(count_map[temp]) > 1:
            # Choose entity with greatest priority value 
            fin = max(count_map[temp],key=lambda x:ENTITY_PRIORITIES[ent2type[x]])
            # fin = None
            # max_pri = 0
            # for x in count_map[temp]:
            #     pri = ENTITY_PRIORITIES[ent2type[x]]
            #     if max_pri > pri:
            #         fin = x
            #         max_pri = pri
            return fin
        else:
            return count_map[temp][0]


def print_results(sents):
    """
    Display QA
        :param sents: list, Contains dictionary of samples, one for each question
    """
    for s in sents:
        print("Question", '\n', s["Question"])
        print("Answer", '\n', s["Answer"])
        print("Options", '\n', s["Options"])
        print("Type", '\n', s["Type"])
        print()
    print(len(sents))

def blanq_sent(sentence,target):
    blanked = re.sub(r"\b"+target+r"\b",BLANQ,sentence)
    if BLANQ in blanked:
        return blanked    
    else:
        return sentence.replace(target,BLANQ)

def gen_sents(doc,limit=15,largeDoc = None):
    """
    Get list of sentences and options from given spacy doc object.
        :param doc: Spacy Doc object, Used to create questions
        :param limit=20: Upper Limit on number of questions to be returned
    """

    start = time.time()
    ents = get_entities(doc)
    timecop("entities",start)
    if largeDoc is None:
        w2v_model = gen_word2vec(doc)
        large_type2ent = None
    else:
        large_ents = get_entities(largeDoc)
        w2v_model = gen_word2vec(largeDoc)
        large_type2ent = map_ents_to_types_only(large_ents, largeDoc)    
    timecop("Large",start)
    
    ent2type, type2ent, counter, sent2ent = map_ents_to_types(ents, doc)    
    timecop("doc",start)

    if largeDoc is None:
        large_type2ent = type2ent

    result = []
    ent_sents = set()
    for sentID in sent2ent:
        # Iterating over all sentences that contain entities
        ent1 = choose_ent(sent2ent[sentID], counter, ent2type)
        timecop("echoose",start)
        # ent2 = choose_ent(sent2ent[sentID], counter, ent2type, True)
        ent2 = ent1
        sentence, sent_len = sentID2sent(sentID, doc)
        # Discarding sentences that are too long or too short
        if sent_len < MIN_SENT_LEN or sent_len > MAX_SENT_LEN:
            continue

        for ent in [ent1]:
            # Options : All entities of the same type as target but not present in question
            # Also add target to options
            options = [i for i in large_type2ent[ent2type[ent1]] if i not in sent2ent[sentID]] + [ent]
            timecop("oALL",start)
            if len(options) > 3:
                print ("MORE",ent2type[ent1])
                options = find_best_options(list(options), w2v_model, ent, ent2type[ent] , sentence)[:3]
            elif len(options) < 3:
                print ("FEW")
                if (ent2type[ent] == ENT_DATE):
                    try:
                        options = datesDistract(ent)
                    except Exception  as ex:
                        continue
                else:
                    continue
            timecop("ochoose",start)
            random.shuffle(options)
            sample = {
                QUESTION: blanq_sent(sentence,ent),
                ANSWER: ent,
                OPTIONS: options,
                ANSWER_TYPE: ent2type[ent],
                QUESTION_RANK: Q_TYPE_ENT + str(len(result))
            }
            result.append(sample)
    timecop("generate ents",start)
    # Sort by entity type, choose top 20 and then shuffle.
    verb_sents = set()
    verb_qs = set()
    print ("---QUESTION COUNT---")
    print ("E   :",len(result))
    if len(result)<limit:
        verb_qs,verb_sents = get_verb_qs(doc , ent_sents)
        result += random.sample(verb_qs, min(limit - len(result), len(verb_qs)))
    timecop("VERB",start)
    print ("EV  :",len(result))
    if len(result) < limit:
        noun_qs,_ = get_noun_sents(doc,verb_sents.union(ent_sents))
        result += random.sample(noun_qs , min(limit - len(result) , len(noun_qs)))
    
    timecop("NOUN",start)    
    print ("ENV :",len(result))


    result.sort(key=lambda x:ENTITY_PRIORITIES[x[ANSWER_TYPE]] , reverse=True)

    result = result[:limit*3]
    result = random.sample(result , min(limit , len(result)))

    return result

def getWikiQuestions(allContent , quizContent):
    """

    :param allContent: Complete paragraph about the entire wikipedia article
    :param quizContent: Content of the subtopic to generate quiz on
    :return: All Questions
    """

    quizDoc = get_doc(quizContent)
    allDoc = get_doc(allContent)
    questionsArray = capitalizeEverything(gen_sents(quizDoc, largeDoc=allDoc))
    return questionsArray


def transformAnswerToIndex(questions):
    for i in range(len(questions)):
        questions[i][ANSWER] = questions[i][OPTIONS].index(questions[i][ANSWER])

    return questions

def capitalizeEverything(questionArray):
    questions = []
    try:
        for questionInfo in questionArray:
            questions.append({
                QUESTION: questionInfo[QUESTION],
                QUESTION_RANK: questionInfo[QUESTION_RANK],
                ANSWER: questionInfo[ANSWER].upper(),
                OPTIONS: [manip.removeTrailingContent(option.upper()) for option in questionInfo[OPTIONS]],
                ANSWER_TYPE: questionInfo[ANSWER_TYPE].upper()
            })

        return transformAnswerToIndex(questions)
    except:
        print(questions)
        raise Exception("Index problem")

def getQuestions(content):
    """
    Get questions from given text content.
        :param content: str, Text to generate questions from
    """    
    doc = get_doc(content)
    questionArray = capitalizeEverything(gen_sents(doc))

    return questionArray
