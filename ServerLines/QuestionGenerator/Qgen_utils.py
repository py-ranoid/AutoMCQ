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
