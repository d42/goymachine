#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from core.pluginface import(PluginBase, triggered_by,
                            trigger_every, triggers as t)

import base64


class SASL(PluginBase):

    def setup(self):
        if self.settings['authenticate'] == 'plain':
            self.auth = self._plain_auth
        pass

    @triggered_by(t.init)
    def say_hello(self, conn, event):
        conn.cap_req('sasl')
        self.bot.eventd.subscribe(
            self.resp_ack,
            t.cap_ack,
            single=True)

    def resp_ack(self, conn, event):
        if event.data.strip() == 'ACK sasl':
            self.auth(conn)

    def _plain_auth(self, conn):
        token = '\0'.join([
            self.settings['login'],
            self.settings['login'],
            self.settings['password']
        ])
        pass_base64 = base64.b64encode(token.encode('utf-8')).decode('utf-8')
        conn.data_send("AUTHENTICATE PLAIN")
        self.bot.eventd.subscribe(self.cap_end, 903, single=True)

        def response(conn, event):
            conn.data_send("AUTHENTICATE {password}".format(
                password=pass_base64))
        self.bot.eventd.subscribe(response, 'AUTHENTICATE', single=True)

    def cap_end(self, conn, event):
        conn.data_send("CAP END")

    @triggered_by(451)
    def end_cert(self, conn, event):
        pass
