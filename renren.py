#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    renren.py -- bridge between renren and twitter
    special thanks to:
    Yujing Zheng
    Daodao Zhang
"""

import sys
import json
import logging
import getpass
import datetime
from optparse import OptionParser
import time
import sleekxmpp
import json
import urllib


reload(sys)
sys.setdefaultencoding('utf8')

#TODO: use redis for twitter subscription
#import redis
#redis_cli = redis.StrictRedis(host='localhost', port=6379, db=0)

class SendMsgBot(sleekxmpp.ClientXMPP):
    def sendMessage(self, jid, msg):
        """
        overrided, convert multiple lines as multiple sends
        BECAUSE STUPID RENREN DOESN'T SUPPORT MUTIPLELINE CHAT!!!
        """
        msg = ' '.join(msg.splitlines())
        sleekxmpp.ClientXMPP.sendMessage(self, jid, msg)

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("failed_auth", self.failed)
        self.add_event_handler("message", self.onMessage)

    def _send_help_msg(self, jid):
        self.sendMessage(jid,u'\u5bf9\u6211\u4f7f\u7528'+
                         u'/twitter <keyword>\u8fdb\u884c'+
                         u'twitter\u641c\u7d22' +
                         u',\u6bd4\u5982/twitter \u9648' +
                         u'\u5149\u8bda, \u6216/twitter #freechen')

    def _fetch_twitter(self, query):
        query = "http://search.twitter.com/search.json?q="+\
            urllib.quote_plus(query.encode("utf-8"))
        json_str = urllib.urlopen(query).read()
        json_obj = json.loads(json_str)["results"]
        return [obj["text"] for obj in json_obj]


    def _handle_twitter_query(self, jid, query):
        print "User query:%s" % query
        try:
            replys = self._fetch_twitter(query)
        except:
            self.sendMessage(jid,
                             "Someting wrong," +
                             "please provide feedback to me,"+
                             "many thanks!")
            return

        if len(replys)==0:
            self.sendMessage(jid,
                             "Sorry, no search results")
            return

        for r in replys:
            self.sendMessage(jid, r)
            #sleep because xiaonei's stupid implementation
            #continuous packets get lost
            time.sleep(1.2)

        self.sendMessage(jid, u'\u641c\u7d22\u7ed3\u675f')

    def _handle_help(self, jid, _msg):
        self._send_help_msg(jid)

    def onMessage(self, message):
        msg = message['body'].strip()
        print "Get Msg:%s" % msg
        user = message['from'].user

        m_f_dict = {"/twitter":self._handle_twitter_query,
                    "/help":self._handle_help}

        def forward(prefix, func, msg, jid):
            if msg.startswith(prefix):
                msg = ' '.join(msg.split(' ')[1:])
                func(jid, msg)

        map(lambda x: forward(x, m_f_dict[x], msg, message['from']),
            m_f_dict)


    def failed(self, event):
        print "Failed Login"
        self.disconnect()

    def start(self, event):
        print "Logged in"
        self.send_presence()

if __name__ == '__main__':
    # Setup logging.
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)-8s %(message)s')

    #TODO: ADD MSG LOGGING TO FILE BEFORE PUBLIC TESTING!!

    #TODO: Add arguments support

    #Change the id to your renren id(the one in your homepage url)
    jid = "463212100@talk.renren.com"
    #jid = "240466769@talk.renren.com"
    password = "123456test"

    xmpp = SendMsgBot(jid, password)

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():
        xmpp.process(threaded=False)
        print("Done")
    else:
        print("Unable to connect.")
