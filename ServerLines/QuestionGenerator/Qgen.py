import spacy
import random
from nltk import word_tokenize,sent_tokenize
# from nltk.util import ngrams
from gensim.models import Word2Vec
from re import findall

nlp = spacy.load('en_core_web_sm')
MIN_SENT_LEN = 6
MAX_SENT_LEN = 25
TEST_TEXT = """
The Battle of Plassey was a decisive victory of the British East India Company over the Nawab of Bengal and his French allies on 23 June 1757. The battle consolidated the Company's presence in Bengal, which later expanded to cover much of India over the next hundred years.

The battle took place at Palashi (Anglicised version: Plassey) on the banks of the Hooghly River, about 150 kilometres (93 mi) north of Calcutta and south of Murshidabad, then capital of Bengal (now in Nadia district in West Bengal). The belligerents were the Nawab Sirajuddaulah, the last independent Nawab of Bengal, and the British East India Company. Siraj-ud-daulah had become the Nawab of Bengal the year before, and he ordered the English to stop the extension of their fortification. Robert Clive bribed Mir Jafar, the commander in chief of the Nawab's army, and also promised him to make him Nawab of Bengal. He defeated the Nawab at Plassey in 1757 and captured Calcutta.

The battle was preceded by the attack on British-controlled Calcutta by Nawab Siraj-ud-daulah and the Black Hole massacre. The British sent reinforcements under Colonel Robert Clive and Admiral Charles Watson from Madras to Bengal and recaptured Calcutta. Clive then seized the initiative to capture the French fort of Chandernagar. Tensions and suspicions between Siraj-ud-daulah and the British culminated in the Battle of Plassey. The battle was waged during the Seven Years' War (1756–1763), and, in a mirror of their European rivalry, the French East India Company (La Compagnie des Indes Orientales) sent a small contingent to fight against the British. Siraj-ud-Daulah had a numerically superior force and made his stand at Plassey. The British, worried about being outnumbered, formed a conspiracy with Siraj-ud-Daulah's demoted army chief Mir Jafar, along with others such as Yar Lutuf Khan, Jagat Seths (Mahtab Chand and Swarup Chand), Omichund and Rai Durlabh. Mir Jafar, Rai Durlabh and Yar Lutuf Khan thus assembled their troops near the battlefield but made no move to actually join the battle. Siraj-ud-Daulah's army with 50,000 soldiers, 40 cannons and 10 war elephants was defeated by 3,000 soldiers of Col. Robert Clive, owing to the flight of Siraj-ud-daulah from the battlefield and the inactivity of the conspirators. The battle ended in 11 hours.

This is judged to be one of the pivotal battles in the control of Indian subcontinent by the colonial powers. The British now wielded enormous influence over the Nawab and consequently acquired significant concessions for previous losses and revenue from trade. The British further used this revenue to increase their military might and push the other European colonial powers such as the Dutch and the French out of South Asia, thus expanding the British Empire.
""".strip()


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

def ngrams(text, n):
    return set([text[i:i + n] for i in range(len(text) - n)])

def get_doc(content):
    return nlp(content)

# def word_tokenize(word):
#     return word.split(' ')

def metric(x, y):
    try:
        return float(len(x.intersection(y))) / len(x.union(y))
    except ZeroDivisionError:
        return 0


def gen_word2vec(doc):
    sents = [[y.orth_.lower() for y in x] for x in doc.sents]
    model = Word2Vec(sents, size=100, window=5, min_count=1, workers=4)
    return model

def gen_word2vec_from_content(content):
    sents = [word_tokenize(s) for s in sent_tokenize(content.lower())]
    # sents = [[y.orth_.lower() for y in x] for x in doc.sents]
    model = Word2Vec(sents, size=100, window=5, min_count=1, workers=4)
    return model

def date_eliminator(answer,options):
    YEAR_REGEX = r'[12][0-9]{3}'
    month_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    short_months = [x[:3] for x in month_list]
    MONTH_REGEX = r'('+"|".join(month_list)+"|"+("|".join(month_list)).lower()+"|"+"|".join(short_months)+"|"+("|".join(short_months)).lower()+')'
    source_year = findall(YEAR_REGEX,answer)
    source_month = findall(MONTH_REGEX,answer)
    chosen_opts = []
    if source_year:
        if source_month:
            for opt in options:
                opt_year = findall(YEAR_REGEX,opt)
                if opt_year:
                    if source_year[0] == opt_year[0]:
                        opt_month = findall(MONTH_REGEX,opt)
                        if opt_month:
                            if source_month[0] == opt_month[0]:
                                continue
                            else:
                                chosen_opts.append(opt)
                        else:
                            continue
                    else:
                        chosen_opts.append(opt)
                else:
                    chosen_opts.append(opt)
        else:
            for opt in options:
                opt_year = findall(YEAR_REGEX,opt)
                if opt_year:
                    if source_year[0] == opt_year[0]:
                        continue
                    else:
                        chosen_opts.append(opt)
                else:
                    chosen_opts.append(opt)
        return (chosen_opts+[answer])
    else:
        return options

def find_best_options(options, w2v_model, answer,ent_type):
    ans_low = answer.lower()
    source = word_tokenize(ans_low)
    source_grams = ngrams(ans_low, 3)
    distances = {}
    if ent_type == "DATE":
        options = date_eliminator(answer,options)
    for opt in options:
        opt_low = opt.lower()
        if opt == answer:
            continue
        opt_grams = ngrams(opt_low, 3)
        if metric(source_grams, opt_grams) > 0.18:
            distances[opt] = 40
            continue
        distance = w2v_model.wmdistance(word_tokenize(opt_low), source)
        # print (opt,distance,metric(source_grams,opt_grams))
        distances[opt] = distance
    distances[answer] = 0
    # print (distances)
    options.sort(key=lambda x: distances[x])
    return options

def get_entities(doc):
    return doc.ents

def map_ents_to_types(ent_list, doc):
    ent2type = {}
    type2ent = {}
    counter = {}
    sent2ent = {}
    for e in ent_list:
        init = e.start
        if doc[init].orth_ == '\n':
            continue
        sent_id = str(e.sent.start) + "#" + str(e.sent.end)
        etype = doc[init].ent_type_

        ent2type[e.orth_] = etype
        temp = type2ent.get(etype, None)

        type2ent_new = set(
            [e.orth_]) if temp is None else temp.union(set([e.orth_]))
        type2ent[etype] = type2ent_new

        counter[e.orth_] = 1 + counter.get(e.orth_, 0)

        sent2ent[sent_id] = [e.orth_] + sent2ent.get(sent_id, [])

    return ent2type, type2ent, counter, sent2ent


def sentID2sent(sentID, doc):
    start, end = [int(x) for x in sentID.split("#")]
    return doc[start:end].orth_.strip(), end - start


def choose_ent(ents, counter, ent2type, mul_priority=False, weight=20):
    count_map = {}
    if mul_priority:
        for e in ents:
            pri = ENTITY_PRIORITIES[ent2type[e]]
            count_map[(weight / counter[e]) * pri] = [e] + count_map.get(e, [])
        return count_map[max(count_map.keys())][0]
    else:
        for e in ents:
            count_map[counter[e]] = [e] + count_map.get(e, [])
        temp = min(count_map.keys())
        if len(count_map[temp]) > 1:
            fin = None
            max_pri = 0
            for x in count_map[temp]:
                pri = ENTITY_PRIORITIES[ent2type[x]]
                if max_pri > pri:
                    fin = x
                    max_pri = pri
            return fin
        else:
            return count_map[temp][0]


def print_results(sents):
    for s in sents:
        print("Question", '\n', s["Question"])
        print("Answer", '\n', s["Answer"])
        print("Options", '\n', s["Options"])
        print("Type", '\n', s["Type"])
        print()
    print(len(sents))


def gen_sents(doc,limit=20):
    ents = get_entities(doc)
    w2v_model = gen_word2vec(doc)
    ent2type, type2ent, counter, sent2ent = map_ents_to_types(ents, doc)
    result = []
    for sentID in sent2ent:
        ent1 = choose_ent(sent2ent[sentID], counter, ent2type)
        ent2 = choose_ent(sent2ent[sentID], counter, ent2type, True)
        sentence, sent_len = sentID2sent(sentID, doc)
        if sent_len < MIN_SENT_LEN or sent_len > MAX_SENT_LEN:
            continue
        if ent1 == ent2:
            options = [i for i in type2ent[ent2type[ent1]]
                       if i not in sent2ent[sentID]] + [ent1]

            if len(options) > 3:
                options = find_best_options(list(options), w2v_model, ent1, ent2type[ent1])[:3]
            elif len(options) < 3:
                continue
            sample = {"Question": sentence.replace(ent1, "_________"),
                      "Answer": ent1,
                      "Options": options,
                      "Type": ent2type[ent1]}
            result.append(sample)

        else:
            # For Entity 1
            options = [i for i in type2ent[ent2type[ent1]]
                       if i not in sent2ent[sentID]] + [ent1]
            if len(options) > 3:
                options = find_best_options(list(options), w2v_model, ent1, ent2type[ent1])[:3]
            elif len(options) < 3:
                continue
            sample = {"Question": sentence.replace(ent1, "_________"),
                      "Answer": ent1,
                      "Options": options,
                      "Type": ent2type[ent1]}
            result.append(sample)

            # For Entity 2
            options = [i for i in type2ent[ent2type[ent2]]
                       if i not in sent2ent[sentID]] + [ent2]
            if len(options) > 3:
                options = find_best_options(list(options), w2v_model, ent2,ent2type[ent2])[:3]
            elif len(options) < 3:
                continue
            sample = {"Question": sentence.replace(ent2, "_________"),
                      "Answer": ent2,
                      "Options": options,
                      "Type": ent2type[ent2]}
            result.append(sample)
    result.sort(key=lambda x:ENTITY_PRIORITIES[x['Type']])
    result = result[:limit]
    random.shuffle(result)
    return result

def getQuestions(content):
    doc = get_doc(content)
    questionArray = gen_sents(doc)
    return questionArray
