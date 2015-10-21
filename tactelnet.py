#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  telnet.py
#
#  Copyright 2015 Neil Williams <codehelp@debian.org>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import time
from opentac import OpenTac
import socket
import logging

# pylint: disable=no-member,missing-docstring


class OpenTacTelnet(object):

    running = False
    delay = 1
    rpc_delay = 2
    blocksize = 4 * 1024
    all_groups = {}
    group_port = 4826  # 19 inches in mm * 10
    # All data handling for each connection happens on this local reference into the
    # all_groups dict with a new group looked up each time.
    group = None
    conn = None
    host = "localhost"
    
    def __init__(self):
        self.opentac = OpenTac()

    def run(self):
        sock = None
        while 1:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                logging.debug("binding to %s:%s", self.host, self.group_port)
                sock.bind(('0.0.0.0', self.group_port))
                break
            except socket.error as exc:
                logging.warn(
                    "Unable to bind, trying again with delay=%d msg=%s",
                    self.delay, exc.message)
                time.sleep(self.delay)
                self.delay *= 2
        sock.listen(1)
        self.running = True
        while self.running:
            logging.info("Ready to accept new connections")
            self.conn, _ = sock.accept()
            # read the header to get the size of the message to follow
            data = str(self.conn.recv(8))  # 32bit limit
            try:
                count = int(data, 16)
            except ValueError:
                logging.debug(
                    "Invalid message: %s from %s",
                    data, self.conn.getpeername()[0])
                self.conn.close()
                continue
            ccc = 0
            data = ''
            # get the message itself
            while ccc < count:
                data += self.conn.recv(self.blocksize)
                ccc += self.blocksize
            self.data_received(data)

    def _ack_response(self):
        msgdata = self._format_message("ack")
        if msgdata:
            self.conn.send(msgdata[0])
            self.conn.send(msgdata[1])
        self.conn.close()

    def _bad_request(self):
        msgdata = self._format_message("nack")
        if msgdata:
            self.conn.send(msgdata[0])
            self.conn.send(msgdata[1])
        self.conn.close()

    def _wait_response(self):
        msgdata = self._formatMessage("wait")
        if msgdata:
            self.conn.send(msgdata[0])
            self.conn.send(msgdata[1])
        self.conn.close()

    def _format_message(self, message):
        msglen = "%08X" % len(message)
        if int(msglen, 16) > 0xFFFFFFFF:
            logging.error("Message was too long to send! %d > %d" %
                          (int(msglen, 16), 0xFFFFFFFF))
            return None
        return msglen, msgstr

    def data_received(self, data):
        if not data:
            self._bad_request()
            return None
        if data == 'alarm':
            self.opentac.red_led_on()
            self._ack_response()
        elif data == 'clear_alarm':
            self.opentac.red_led_off()
            self._ack_response()


def main():
    OpenTacTelnet().run()
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
