import requests
import json
from re import findall

def get_transcript_from_id(vid_id):
    URL = 'https://www.khanacademy.org/api/internal/videos/%s/transcript'%vid_id
    return subtitles_to_text(requests.get(URL).json())

def get_transcript_from_URL(URL):
    r = requests.get(URL)
    cont = findall(r'children: ReactComponent[(](.*)[)]',r.content.decode())[0]
    sub_dict = json.loads(cont)['componentProps']['preloadedTranscript']['subtitles']
    return subtitles_to_text(sub_dict)

def subtitles_to_text(sub_dict):
    sub_sents = [t['text'] for t in sub_dict]
    return ' '.join(sub_sents).replace('\n',' ').replace('[Narrator]','')
