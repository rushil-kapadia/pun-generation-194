import inflect
import pickle
from wordfreq import zipf_frequency

def get_similar(homophone):
    to_cap = homophone[0].isupper()
    if to_cap:
        homophone = homophone.lower()

    with open('updated-6B50d.pickle', 'rb') as f:
        model = pickle.load(f)

    similars = []
    try:
        similars = [i[0][0].upper() + i[0][1:] if to_cap else i[0] for i in model.most_similar(homophone, topn=20)]
        similars = [similar for similar in similars if '-' not in similar]
        similars = sorted([[similar, zipf_frequency(similar, 'en')] for similar in similars], key=lambda x: x[1], reverse=True)
    except KeyError:
        pass
    return [similar[0] for similar in similars]

def get_context(sentence, similar, homophone, tagger):
    contexts = []
    similar_pos = tagger(similar)[0].pos_

    seen_homophone = False
    if similar_pos != 'VERB':
        sentence_iter = tagger(sentence)
        for word in sentence_iter:
            if word.text == homophone:
                seen_homophone = True
            if word.pos_ == similar_pos and not seen_homophone:
                contexts.append(word.text)
    return contexts

plural_engine = inflect.engine()

def edit_plurality(similar, context):
    if not plural_engine.singular_noun(context):
        if not plural_engine.singular_noun(similar):
            return similar
        else:
            return plural_engine.singular_noun(similar)
    else:
        if not plural_engine.singular_noun(similar):
            return plural_engine.plural_noun(similar)
        else:
            return similar

def score_pun(pun, similar, tagger):
    def zipf(word):
        freq = zipf_frequency(word, 'en')
        return freq

    if pun[0].upper() != pun[0]:
        return -1

    pun_iter = tagger(pun)

    prev_noun, prev_similar = False, False
    for word in pun_iter:
        curr_noun, curr_similar = word.pos_ == 'NOUN' or tagger(word.text)[0].pos_ == 'NOUN', word.text == similar
        if prev_noun and curr_noun and (curr_similar or prev_similar):
            return -1
        prev_noun, prev_similar = curr_noun, curr_similar

    pun_words = pun.split(' ')
    return sum([zipf(word) for word in pun_words]) / len(pun_words)