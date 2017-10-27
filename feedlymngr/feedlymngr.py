import configparser
from feedly.client import FeedlyClient

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

if __name__ == '__main__':

    fm = FeedlyMngr('../conf/feedly.conf')
    print "helo"

    for c in fm.feedly_categories():
        print c
