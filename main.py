from numpy.core.fromnumeric import var
from bot import HippoBot, RhymeBot
from model import get_similar, get_context, edit_plurality, score_pun

import spacy

def pun_from_word(query):
    hippo = HippoBot()
    sentences = hippo.scrape_data(query)
    sentences = hippo.sort_data(query, sentences)
    hippo.close_driver()

    homophone = RhymeBot()
    homophones = homophone.scrape_data(query)
    homophones = homophone.sort_data(query, homophones)
    homophone.close_driver()

    puns = []

    tagger = spacy.load('en_core_web_sm')

    for sentence in sentences:
        for homophone in homophones:
            sentence_homophone = sentence.replace(query, homophone)
            similars = get_similar(homophone)[:3]
            for similar in similars:
                contexts = get_context(sentence_homophone, similar, homophone, tagger)
                for context in contexts[:1]:
                    edited_similar = edit_plurality(similar, context)
                    sentence_word = sentence_homophone.replace(context, edited_similar)
                    puns.append([sentence_word, score_pun(sentence_word, edited_similar, tagger), sentence, homophone, similar])

    puns = sorted(puns, key=lambda x: x[1], reverse=True)

    def get_variety(puns, index, topn):
        variety, indices = [], set()
        for pun in puns:
            if pun[index] not in indices and pun[1] >= 0:
                indices.add(pun[index])
                variety.append(pun[:2])
        variety = variety[:topn]
        return variety, sum([v[1] for v in variety]) / topn

    variety = max([[get_variety(puns, i, 3), i] for i in [2, 3, 4]], key=lambda x: len(x[0][0]) + x[0][1] + 2 / x[1])
    return [pun[0] for pun in variety[0][0]]