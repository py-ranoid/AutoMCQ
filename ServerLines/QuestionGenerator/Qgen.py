# -*- coding: utf-8 -*-
import spacy
import random
from nltk import word_tokenize,sent_tokenize
# from nltk.util import ngrams
from gensim.models import Word2Vec
from Qgen_utils import ngrams, metric, date_eliminator, resolve_prons

nlp = spacy.load('en_core_web_sm')
MIN_SENT_LEN = 8
MAX_SENT_LEN = 25
TEST_TEXT = """
The Battle of Plassey was a decisive victory of the British East India Company over the Nawab of Bengal and his French allies on 23 June 1757. The battle consolidated the Company's presence in Bengal, which later expanded to cover much of India over the next hundred years. The battle took place at Palashi (Anglicised version: Plassey) on the banks of the Hooghly River, about 150 kilometres (93 mi) north of Calcutta and south of Murshidabad, then capital of Bengal (now in Nadia district in West Bengal). The belligerents were the Nawab Sirajuddaulah, the last independent Nawab of Bengal, and the British East India Company. Siraj-ud-daulah had become the Nawab of Bengal the year before, and he ordered the English to stop the extension of their fortification. Robert Clive bribed Mir Jafar, the commander in chief of the Nawab's army, and also promised him to make him Nawab of Bengal. He defeated the Nawab at Plassey in 1757 and captured Calcutta. The battle was preceded by the attack on British-controlled Calcutta by Nawab Siraj-ud-daulah and the Black Hole massacre. The British sent reinforcements under Colonel Robert Clive and Admiral Charles Watson from Madras to Bengal and recaptured Calcutta. Clive then seized the initiative to capture the French fort of Chandernagar. Tensions and suspicions between Siraj-ud-daulah and the British culminated in the Battle of Plassey. The battle was waged during the Seven Years' War (1756–1763), and, in a mirror of their European rivalry, the French East India Company (La Compagnie des Indes Orientales) sent a small contingent to fight against the British. Siraj-ud-Daulah had a numerically superior force and made his stand at Plassey. The British, worried about being outnumbered, formed a conspiracy with Siraj-ud-Daulah's demoted army chief Mir Jafar, along with others such as Yar Lutuf Khan, Jagat Seths (Mahtab Chand and Swarup Chand), Omichund and Rai Durlabh. Mir Jafar, Rai Durlabh and Yar Lutuf Khan thus assembled their troops near the battlefield but made no move to actually join the battle. Siraj-ud-Daulah's army with 50,000 soldiers, 40 cannons and 10 war elephants was defeated by 3,000 soldiers of Col. Robert Clive, owing to the flight of Siraj-ud-daulah from the battlefield and the inactivity of the conspirators. The battle ended in 11 hours. This is judged to be one of the pivotal battles in the control of Indian subcontinent by the colonial powers. The British now wielded enormous influence over the Nawab and consequently acquired significant concessions for previous losses and revenue from trade. The British further used this revenue to increase their military might and push the other European colonial powers such as the Dutch and the French out of South Asia, thus expanding the British Empire.
#""".strip()


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


def find_best_options(options, w2v_model, answer,ent_type):
    """
    Choose the best 3 (2+target) options from the given options.
        :param options: list, All options
        :param w2v_model: gensim Word2Vec model used to compare options with target
        :param answer: str, Target word
        :param ent_type: str, Entity type
    """
    # Convert answer to lowercase and create trigrams
    ans_low = answer.lower()
    source = word_tokenize(ans_low)
    source_grams = ngrams(ans_low, 3)

    distances = {}
    if ent_type == "DATE":
        options = date_eliminator(answer,options)
        # TODO If reduced options are too few, add synthetic date discriminators
    for opt in options:
        # Eliminate options that have too many common ngrams
        opt_low = opt.lower()
        if opt == answer:
            continue
        opt_grams = ngrams(opt_low, 3)
        if metric(source_grams, opt_grams) > 0.18:
            # Assign very high distance if metric is high
            distances[opt] = 40
        else:
            distances[opt] = w2v_model.wmdistance(word_tokenize(opt_low), source)
    # Assign distance to answer to 0 (closest to target)
    distances[answer] = 0
    options.sort(key=lambda x: distances[x])
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
        
        sent_start,sent_end = resolve_prons(all_starts.index(ent_sent.start),doc,nlp)
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


def gen_sents(doc,limit=20,largeDoc = None):
    """
    Get list of sentences and options from given spacy doc object.
        :param doc: Spacy Doc object, Used to create questions
        :param limit=20: Upper Limit on number of questions to be returned
    """
    ents = get_entities(doc)
    large_ents = get_entities(doc)
    if largeDoc is None:
        w2v_model = gen_word2vec(doc)
    else:
        w2v_model = gen_word2vec(largeDoc)
    ent2type, type2ent, counter, sent2ent = map_ents_to_types(ents, doc)
    large_type2ent= map_ents_to_types_only(large_ents, largeDoc)
    result = []
    for sentID in sent2ent:
        # Iterating over all sentences that contain entities
        ent1 = choose_ent(sent2ent[sentID], counter, ent2type)
        ent2 = choose_ent(sent2ent[sentID], counter, ent2type, True)
        sentence, sent_len = sentID2sent(sentID, doc)
        # Discarding sentences that are too long or too short
        if sent_len < MIN_SENT_LEN or sent_len > MAX_SENT_LEN:
            continue
        if ent1 == ent2:
            # Options : All entities of the same type as target but not present in question
            # Also add target to options
            options = [i for i in large_type2ent[ent2type[ent1]] if i not in sent2ent[sentID]] + [ent1]

            if len(options) > 3:
                options = find_best_options(list(options), w2v_model, ent1, ent2type[ent1])[:3]
            elif len(options) < 3:
                # TODO generate more options
                continue
            random.shuffle(options)
            sample = {"Question": sentence.replace(ent1, "_________"),
                      "Answer": ent1,
                      "Options": options,
                      "Type": ent2type[ent1]}
            result.append(sample)

        else:
            # For Entity 1
            options = [i for i in large_type2ent[ent2type[ent1]] if i not in sent2ent[sentID]] + [ent1]
            if len(options) > 3:
                options = find_best_options(list(options), w2v_model, ent1, ent2type[ent1])[:3]
            elif len(options) < 3:
                # TODO generate more options
                # TODO If entity type is date, add synthetic date discriminators
                continue
            random.shuffle(options)
            sample = {"Question": sentence.replace(ent1, "_________"),
                      "Answer": ent1,
                      "Options": options,
                      "Type": ent2type[ent1]}
            result.append(sample)

            # For Entity 2
            options = [i for i in large_type2ent[ent2type[ent2]] if i not in sent2ent[sentID]] + [ent2]
            if len(options) > 3:
                options = find_best_options(list(options), w2v_model, ent2,ent2type[ent2])[:3]
            elif len(options) < 3:
                # TODO generate more options
                continue
            random.shuffle(options)
            sample = {"Question": sentence.replace(ent2, "_________"),
                      "Answer": ent2,
                      "Options": options,
                      "Type": ent2type[ent2]}
            result.append(sample)
    
    # Sort by entity type, choose top 20 and then shuffle.
    result.sort(key=lambda x:ENTITY_PRIORITIES[x['Type']])
    result = result[:limit]
    random.shuffle(result)
    
    return result

def getWikiQuestions(allContent , quizContent):
    """

    :param allContent: Complete paragraph about the entire wikipedia article
    :param quizContent: Content of the subtopic to generate quiz on
    :return: All Questions
    """

    quizDoc = get_doc(quizContent)
    allDoc = get_doc(allContent)
    questionsArray = gen_sents(quizDoc, largeDoc=allDoc)
    return questionsArray


def getQuestions(content):
    """
    Get questions from given text content.
        :param content: str, Text to generate questions from
    """    
    doc = get_doc(content)
    questionArray = gen_sents(doc)
    return questionArray
