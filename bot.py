from time import sleep
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from metaphone import doublemetaphone
from enchant.utils import levenshtein
from nltk import pos_tag
from os import path
import pickle

def safe_html_read(blocks: list):
    read = []
    for block in blocks:
        read.append(block.text)
    return read if len(read) > 0 else ['-']

class Bot:
    def __init__(self):
        pass

    def load_driver(self) -> None:
        options = webdriver.ChromeOptions()
        # options.add_argument('--start-maximized')
        options.add_argument('--headless')

        self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)

    def load_site(self) -> None:
        pass

    def scrape_data(self) -> list:
        pass

    def close_driver(self):
        self.driver.quit()

class HippoBot(Bot):
    def __init__(self):
        self.load_driver()
        self.load_site()

    def load_site(self) -> None:
        self.driver.get('https://www.wordhippo.com/')
        sleep(0.5)

        sentence_button = self.driver.find_element_by_xpath('//*[@class="menuoption" and @id="sentenceMenuOption"]')
        sentence_button.click()
        sleep(0.5)

    def scrape_data(self, query: str) -> list:
        if path.exists(query + '_sentences.pickle'):
            with open(query + '_sentences.pickle', 'rb') as f:
                sentences = pickle.load(f)
        else:
            search_box = self.driver.find_element_by_xpath('//*[@id="sentenceword"]')
            search_box.send_keys(query + '\n')
            sleep(0.5)

            one, two = [], []
            one = safe_html_read(self.driver.find_elements_by_xpath('//*[@class="exv2row1"]'))
            two = safe_html_read(self.driver.find_elements_by_xpath('//*[@class="exv2row2"]'))

            sentences = [sentence for sentence in one + two]
            sentences = [sentence for sentence in sentences if len(sentence) > len(query) and query in sentence]
            
            with open(query + '_sentences.pickle', 'wb') as f:
                pickle.dump(sentences, f)

        return sentences
    
    def sort_data(self, query:str, data: list) -> list:
        sentences = sorted([[sentence, sentence.index(query) / len(sentence)] for sentence in data], key=lambda x: x[1], reverse=True)[:10]
        return sorted([sentence[0] for sentence in sentences], key=lambda x: len(x.split(' ')))[:5]

    def close_driver(self):
        self.driver.quit()

class RhymeBot(Bot):
    def __init__(self):
        self.load_driver()
        self.load_site()

    def load_site(self) -> None:
        self.driver.get('https://www.rhymezone.com/')
        sleep(0.5)

    def scrape_data(self, query: str) -> list:
        if path.exists(query + '_homophones.pickle'):
            with open(query + '_homophones.pickle', 'rb') as f:
                homophones = pickle.load(f)
        else:
            search_box = self.driver.find_element_by_xpath('//*[@name="Word"]')
            search_box.send_keys(query + '\n')
            sleep(0.5)

            one, two = [], []
            one = [e.text for e in self.driver.find_elements_by_xpath('//*[@class="d r"]') if int(e.value_of_css_property('font-weight')) >= 700]
            two = [e.text for e in self.driver.find_elements_by_xpath('//*[@class="r"]') if int(e.value_of_css_property('font-weight')) >= 700]
            homophones = one + two

            with open(query + '_homophones.pickle', 'wb') as f:
                pickle.dump(homophones, f)

        return homophones
    
    def sort_data(self, query: str, data: list) -> list:
        query_pos, query_dm = pos_tag([query])[0][1], doublemetaphone(query)[0]
        homophones = sorted([[homophone, levenshtein(query_dm, doublemetaphone(homophone)[0])] for homophone in data if ' ' not in homophone], key=lambda x: x[1])
        homophones = [homophone[0] for homophone in homophones if homophone[0] not in query and query not in homophone[0]][:10]
        homophones = [homophone for homophone in homophones if pos_tag([homophone])[0][1] == query_pos] + [homophone for homophone in homophones if pos_tag([homophone])[0][1] != query_pos]
        homophones = [homophone for homophone in homophones if homophone[0] == query[0]] + [homophone for homophone in homophones if homophone[0] != query[0]]
        return homophones[:3]

    def close_driver(self):
        self.driver.quit()