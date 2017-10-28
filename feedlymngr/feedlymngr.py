# -*- coding: utf-8 -*-

import configparser
from feedly.client import FeedlyClient
import datetime
from elasticsearch import Elasticsearch
import time
import textblob
from textblob import TextBlob


class FeedlyMngr(object):

    def __init__(self, inp_conf):
        cnf = configparser.ConfigParser()
        cnf.read(inp_conf)

        self.__FEEDLY_REDIRECT_URI  = cnf.get('feedly', 'FEEDLY_REDIRECT_URI')
        self.__FEEDLY_CLIENT_ID     = cnf.get('feedly', 'FEEDLY_CLIENT_ID')
        self.__FEEDLY_CLIENT_SECRET = cnf.get('feedly', 'FEEDLY_CLIENT_SECRET')

        #print(self.__FEEDLY_REDIRECT_URI)

        self.__feedly = self.__get_feedly_client()

        self.__elastic      = Elasticsearch(cnf.get('elastic','url'))
        self.__elastic_indx = cnf.get('elastic','index')
        #print(elastic_url)



    def __feedly_auth(self):
        fdl = FeedlyClient(client_id=self.__FEEDLY_CLIENT_ID, client_secret=self.__FEEDLY_CLIENT_SECRET)

        subs = fdl.get_user_subscriptions()
        #print(subs)

        return fdl.get_code_url(self.__FEEDLY_REDIRECT_URI)

    def __get_feedly_client(self,token=None):
        if token:
            return FeedlyClient(token=token, sandbox=False)
        else:
            return FeedlyClient(client_id       = self.__FEEDLY_CLIENT_ID,
                                client_secret   = self.__FEEDLY_CLIENT_SECRET,
                                sandbox         = False )

    def detect_lang(self, inp_origin_title, inp_content):

        lang = ''

        try:
            b = TextBlob(inp_content)
            lang = b.detect_language()
        except:
            try:
                c = TextBlob(inp_origin_title)
                lang = c.detect_language()
            except:
                lang = ''

        return lang


    def translate(self, inp_orig_lang,inp_lang, inp_txt):
        txt_translated = ''

        try:
            b = TextBlob(inp_txt)
            txt_translated = "%s" % b.translate(from_lang=inp_orig_lang,to=inp_lang)

        except:
            txt_translated = ''

        return txt_translated

    def sentiment(self,inp_text):

        sentim = {}

        try:
            b = TextBlob(inp_text)
            s = b.sentiment
            sentim['pol'] = b.sentiment.polarity
            sentim['sub'] = b.sentiment.subjectivity
        except:
            sentim['pol'] = 0.0
            sentim['sub'] = 0.0

        return sentim



    #
    # Useful methods using Feedly API
    #

    def feedly_categories(self):
        categories = self.__feedly.get_info_type(self.__FEEDLY_CLIENT_SECRET, 'categories')

        return categories

    def feeds_from_category(self,inp_cat):

        result = self.__feedly.get_feed_content(self.__FEEDLY_CLIENT_SECRET,
                                                inp_cat.get('id'), False)

        for i in result.get('items', []):
            #print i
            self.__parse_feed(i)

    def __parse_feed(self,inp_feed):

        try:    title = inp_feed['title']
        except: title = ""

        try:    author = inp_feed['author']
        except: author = ""

        try:    content = inp_feed['summary']['content']
        except: content = ""

        time_stamp = datetime.datetime.fromtimestamp(int(str(inp_feed['published'])[:10])).strftime("%Y-%m-%dT%H:%M:%SZ")
        #print("timestamp:\t", time_stamp)

        detect_lang = self.detect_lang(title,content)
        content_en  = self.translate(detect_lang, 'en', content)

        sentiment       = self.sentiment(content_en)
        feedly_category = str(inp_feed['categories'][0]['label']).replace(' ','')

        el_id = inp_feed['fingerprint']
        #print el_id

        json_data = {
            #'originid':         inp_feed['originid'],
            'type':             inp_feed['alternate'][0]['type'],
            'origin_url':       inp_feed['origin']['htmlUrl'],
            'origin_title':     inp_feed['origin']['title'],
            'title':            title,
            'title_en':         self.translate(detect_lang,'en',title),
            'author':           author,
            'fdl_category':     feedly_category,
            'timestamp':        "%s" % time_stamp,
            'content':          content,
            'content_en':       content_en,
            'lang':             detect_lang,
            'sentiment_pol':    sentiment.get('pol'),
            'sentiment_sub':    sentiment.get('sub'),
        }
        print(json_data)


        try:
            elastic_res = self.__elastic.index( index       = self.__elastic_indx,
                                                doc_type    = feedly_category,
                                                id          = inp_feed['fingerprint'],
                                                body        = json_data)

            print(elastic_res)
        except:
            print "Cant save into elastic"




if __name__ == '__main__':

    fm = FeedlyMngr('../conf/feedly.conf')
    print "helo"


    categories = fm.feedly_categories()
    for cat in categories:
        print cat.get('label')


    for category  in categories:
        if category.get('label') == 'Kataloonia':
            print fm.feeds_from_category(category)
            #print  category.get('label')



    #fm.feeds_from_category('Kataloonia')
