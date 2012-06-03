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
                         u'twitter\u641c\u7d22')

    def _fetch_twitter(self, query):
        query = "http://search.twitter.com/search.json?q="+\
            urllib.quote_plus(query.encode("utf-8"))
        json_str = urllib.urlopen(query).read()
        json_obj = json.loads(json_str)["results"]
        return [obj["text"] for obj in json_obj]

    def onMessage(self, message):
        msg = message['body'].strip()
        print "Get Msg:%s" % msg
        user = message['from'].user

        if msg.startswith("/twitter"):
            if len(msg.split(' ')) == 1:
                _send_help_msg(self, message['from'])
                return

            query = ' '.join(msg.split(' ')[1:])
            try:
                replys = self._fetch_twitter(query)
            except:
                self.sendMessage(message['from'],
                                 "Someting wrong," +
                                 "please provide feedback to me,"+
                                 "many thanks!")
                return

            if len(replys)==0:
                self.sendMessage(message['from'],
                                 "Sorry, no search results")

            for r in replys:
                self.sendMessage(message['from'], r)
                #sleep because xiaonei's stupid implementation
                #continuous packets get lost
                time.sleep(1.2)


        if "/help" in msg:
            self._send_help_msg(message['from'])

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
