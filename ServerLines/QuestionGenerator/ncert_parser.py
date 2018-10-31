import re

with open('/home/b/Downloads/NCERT Class X Social Science Text Book - India and the Contemporary World II.txt') as f:
    book = f.read()

def get_pages(book):
    return re.split('\n[ ]+[0-9xiv]+[ ]*\n',book)
    
def get_lines(book):
    return [i for i in book.splitlines() if i]

def rm_title(content,title="India and the Contemporary World"):
    return '\n'.join(re.split('\n[ ]*'+title+'[ ]*\n',content))

def get_parts(line):
    lim = 14
    num_space = 3
    left,right = "",""
    split_parts = line.split(" "*num_space)
    for ind,i in enumerate(split_parts):
        if i:
            if ind < lim and not left:
                left = i
            else:
                right = i
    return (left.strip(),right.strip())

def rm_fig(fig_text):
    fig_parts = re.findall('^Fig. [0-9]+ — (.*)',fig_text)
    if fig_parts:
        return ' '.join(fig_parts)
    else:
        return fig_text

def title_prefix(line):
    return "::::"+line +"\n" if not re.findall(r"(^[0-9.]+ .*)",line) == [] else line

def get_page_parts(page):
    paras = rm_title(page).split("\n\n\n")
    para_parts = []
    title = None
    for para in paras:
        lines = get_lines(para)
        parts = {"l":[],"r":[]}
        for line in lines:
            l,r = get_parts(line)
            if l:
                parts['l'].append(title_prefix(l))
            if r:
                parts['r'].append(title_prefix(r))
            
        parts['l'] = rm_fig(' '.join(parts['l']))
        parts['r'] = rm_fig(' '.join(parts['r']))
        if len(parts['l'].split(" ")) <4:
            parts['l'] = None
        if len(parts['r'].split(" ")) <5:
            parts['r'] = None        
        if parts['r'] or parts['l']:
            para_parts.append(parts)
    return para_parts

def get_content(pages,start,stop,fname='Unit1.txt'):
    all_paras = []
    for i in range(start,stop):
        all_paras+=get_page_parts(pages[i])
    all_left = '\n'.join([p['l'] for p in all_paras if p['l']])
    all_right = '\n'.join([p['r'] for p in all_paras if p['r']])
    with open(fname,'w') as f:
        f.write(all_left+"\n\n\n"+all_right)

