from re import findall

def ngrams(text, n):    
    return set([text[i:i + n] for i in range(len(text) - n)])


def metric(x, y):
    """
    Returns Jaccard distance between sets x and y
        :param x: set 1
        :param y: set 2
    """
    try:
        return float(len(x.intersection(y))) / len(x.union(y))
    except ZeroDivisionError:
        return 0    


def date_eliminator(answer,options):
    """
    Eliminate date options that include the target
        :param answer: str, Target date
        :param options: list, Strings of date options
    """
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

def join_sents(doc):
    """
    Join sentences in a spacy document with commas & "and"
        :param doc: spacy doc object, Document
    """
    sents = list(doc.sents)
    fin_sent = sents[0].text
    for s in sents[1:-1]:
        fin_sent = fin_sent[:-1] + ', ' +sents[1].text[0].lower() + sents[1].text[1:]
    fin_sent = fin_sent[:-1] + ' and ' +sents[-1].text[0].lower() +  sents[-1].text[1:]
    return fin_sent

def get_source(doc,ind,verbose=False):
    """
    Trace pronoun backwards along doc to find source  (proper noun)
        :param doc: spacy doc object, Document
        :param ind: int, Index of pronoun in document
        :param verbose=False: bool, To print logs
    """
    if verbose:
        print "DOC",doc," :: ID",ind
    pro = doc[ind]
    root = pro.head
    temp = root
    while True:
        prev = temp
        if verbose:
            print 'temp:',temp
        if temp.left_edge == pro or temp.left_edge == temp and not temp.head.left_edge == temp:
            temp = temp.head
        else:
            temp_temp = None
            if verbose:
                print (list(temp.lefts))
            for i in list(temp.lefts)[::-1]:
                if i.pos_ == "PROPN":
                    temp_temp = i
            temp = temp_temp if temp_temp is not None else temp.left_edge
        if temp.pos_ == "PROPN":
            break
        if temp == prev:
            temp=None
            break
    return temp

def hanging_pron(sent):
    """
    Checks if sentence has a hanging pronoun, 
    ie. pronoun that refers to a noun that isn't present in the sentence
        :param sent: spacy doc object, Sentence to be checked.
    """
    init_id = 0
    for w in sent:
        init_id = w.i if init_id == 0 else init_id
        if w.pos_ == 'PRON' and (w == w.head.head.head.left_edge or w in list(w.head.head.head.lefts)):
            return w.i-init_id
    return None

def resolve_prons(sent_num,doc,nlp,sent=None):
    """
    Checks and resolves hanging pronouns by expanding scope.
        :param sent_num: int, Sentence number
        :param doc: spacy doc object, Document
        :param nlp: spacy NLP model
        :param sent=None: 
    """
    if sent is None:
        sent = list(doc.sents)[sent_num]
    pron_id = hanging_pron(sent)
    print ("Pron ID:",pron_id)
    if pron_id is not None:
        all_sent_starts = [x.start for x in doc.sents]
        sent_end = sent.end
        for i in all_sent_starts[:sent_num][::-1]:
            new_sent = nlp(doc[i:sent_end].orth_)
            source = get_source(nlp(join_sents(new_sent)),sent.start+pron_id-i,verbose=False)
            if source is not None:
                print (sent,'-->',source)