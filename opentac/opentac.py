"""
GPIO and I2C details for OpenTAC

Wrapper for accessing GPIO lines and
I2C devices on OpenTAC

Status: experimental
logging is not useful yet, so print is used as well.

"""

#  opentac.py
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

import os
import smbus
import logging


class OpenTac(object):

    def __init__(self):
        self.exported = {}
        self.gpio_path = '/sys/class/gpio/'
        self.gpio_data = {
            'red_led': 7,
            'green_led': 26
        }

    def _export_gpio(self, number):
        ex_path = os.path.join(self.gpio_path, 'export')
        with open(ex_path, 'w') as gpiof:
            gpiof.write("%s\n" % number)
        self.exported.update({number: True})

    def _unexport_gpio(self, number):
        ex_path = os.path.join(self.gpio_path, 'unexport')
        with open(ex_path, 'w') as gpiof:
            gpiof.write("%s\n" % number)
        del self.exported[number]

    def teardown(self):
        for number, _ in self.exported.items():
            logging.info("clearing %s", number)
            print "clearing %s" % number
            self._unexport_gpio(number)

    def _write_value(self, number, filename, value):
        if not isinstance(number, int):
            logging.error("Invalid request: %s", number)
            print "Invalid request: %s" % number
            return False
        if number not in self.exported:
            logging.error("%d not exported", number)
            print "%d not exported" % number
            return False
        wr_path = os.path.join(self.gpio_path, 'gpio%d' % number, filename)
        if not os.path.exists(wr_path):
            logging.error("%s does not exist", wr_path)
            print "%s does not exist" % wr_path
            return False
        with open(wr_path, 'w') as gpiof:
            gpiof.write("%s\n" % value)
            gpiof.flush()
        return True

    def _output_active(self, number, value):
        self._write_value(number, 'direction', 'out')
        self._write_value(number, 'active_low', '1')
        self._write_value(number, 'value', '%s' % value)

    def red_led_on(self):
        number = self.gpio_data['red_led']
        if number not in self.exported:
            self._export_gpio(number)
        self._output_active(number, 1)

    def red_led_off(self):
        number = self.gpio_data['red_led']
        if number not in self.exported:
            self._export_gpio(number)
        self._output_active(number, 0)

    def green_led_on(self):
        number = self.gpio_data['green_led']
        if number not in self.exported:
            self._export_gpio(number)
        self._output_active(number, 1)

    def green_led_off(self):
        number = self.gpio_data['green_led']
        if number not in self.exported:
            self._export_gpio(number)
        self._output_active(number, 0)
