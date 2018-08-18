import spacy
nlp = spacy.load('en_core_web_sm')

text = """
The Battle of Plassey was a decisive victory of the British East India Company over the Nawab of Bengal and his French allies on 23 June 1757. The battle consolidated the Company's presence in Bengal, which later expanded to cover much of India over the next hundred years.

The battle took place at Palashi (Anglicised version: Plassey) on the banks of the Hooghly River, about 150 kilometres (93 mi) north of Calcutta and south of Murshidabad, then capital of Bengal (now in Nadia district in West Bengal). The belligerents were the Nawab Sirajuddaulah, the last independent Nawab of Bengal, and the British East India Company. Siraj-ud-daulah had become the Nawab of Bengal the year before, and he ordered the English to stop the extension of their fortification. Robert Clive bribed Mir Jafar, the commander in chief of the Nawab's army, and also promised him to make him Nawab of Bengal. He defeated the Nawab at Plassey in 1757 and captured Calcutta.

The battle was preceded by the attack on British-controlled Calcutta by Nawab Siraj-ud-daulah and the Black Hole massacre. The British sent reinforcements under Colonel Robert Clive and Admiral Charles Watson from Madras to Bengal and recaptured Calcutta. Clive then seized the initiative to capture the French fort of Chandernagar. Tensions and suspicions between Siraj-ud-daulah and the British culminated in the Battle of Plassey. The battle was waged during the Seven Years' War (1756–1763), and, in a mirror of their European rivalry, the French East India Company (La Compagnie des Indes Orientales) sent a small contingent to fight against the British. Siraj-ud-Daulah had a numerically superior force and made his stand at Plassey. The British, worried about being outnumbered, formed a conspiracy with Siraj-ud-Daulah's demoted army chief Mir Jafar, along with others such as Yar Lutuf Khan, Jagat Seths (Mahtab Chand and Swarup Chand), Omichund and Rai Durlabh. Mir Jafar, Rai Durlabh and Yar Lutuf Khan thus assembled their troops near the battlefield but made no move to actually join the battle. Siraj-ud-Daulah's army with 50,000 soldiers, 40 cannons and 10 war elephants was defeated by 3,000 soldiers of Col. Robert Clive, owing to the flight of Siraj-ud-daulah from the battlefield and the inactivity of the conspirators. The battle ended in 11 hours.

This is judged to be one of the pivotal battles in the control of Indian subcontinent by the colonial powers. The British now wielded enormous influence over the Nawab and consequently acquired significant concessions for previous losses and revenue from trade. The British further used this revenue to increase their military might and push the other European colonial powers such as the Dutch and the French out of South Asia, thus expanding the British Empire.
""".strip()

doc = nlp(text)

def get_entities(doc):
    return doc.ents

def map_ents_to_types(ent_list,doc):
    ent2type = {}
    type2ent = {}
    counter = {}
    sent2ent = {}
    for e in ent_list:
        init = e.start
        sent_id = str(e.sent.start)+"#"+str(e.sent.end)
        etype = doc[init].ent_type_

        ent2type[e.orth_] = etype
        temp = type2ent.get(etype,None)

        type2ent_new = set([e.orth_]) if temp is None else temp.union(set([e.orth_]))
        type2ent[etype] = type2ent_new

        counter[e.orth_] = 1+counter.get(e.orth_,0)

        sent2ent[sent_id] = [e.orth_] + sent2ent.get(sent_id,[])

    return ent2type,type2ent,counter,sent2ent


def sentID2sent(sentID,doc):
    IDsplit = map(int,sentID.split("#"))
    return sentID[IDsplit[0]:IDsplit[1]]
