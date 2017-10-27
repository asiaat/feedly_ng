import configparser
from feedly.client import FeedlyClient
import datetime

class FeedlyMngr(object):

    def __init__(self, inp_conf):
        cnf = configparser.ConfigParser()
        cnf.read(inp_conf)

        self.__FEEDLY_REDIRECT_URI  = cnf.get('feedly', 'FEEDLY_REDIRECT_URI')
        self.__FEEDLY_CLIENT_ID     = cnf.get('feedly', 'FEEDLY_CLIENT_ID')
        self.__FEEDLY_CLIENT_SECRET = cnf.get('feedly', 'FEEDLY_CLIENT_SECRET')

        #print(self.__FEEDLY_REDIRECT_URI)

        self.__feedly = self.__get_feedly_client()


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

    #
    # Useful methods using Feedly API

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

        json_data = {
            'originid':         inp_feed['originId'],
            'type':             inp_feed['alternate'][0]['type'],
            'origin_url':       inp_feed['origin']['htmlUrl'],
            'origin_title':     inp_feed['origin']['title'],
            'title':            title,
            'author':           author,
            'fdl_category':     inp_feed['categories'][0]['label'],
            'timestamp': "%s" % time_stamp,
            'content':          content,
        }
        print(json_data)




if __name__ == '__main__':

    fm = FeedlyMngr('../conf/feedly.conf')
    print "helo"


    for category  in fm.feedly_categories()[1:6]:
        print fm.feeds_from_category(category)
        print  category
