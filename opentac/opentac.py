"""
GPIO and I2C details for OpenTAC

Wrapper for accessing GPIO lines and
I2C devices on OpenTAC
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


class OpenTac(object):

    def __init__(self):
        self.exported = []
        self.gpio_path = '/sys/class/gpio/'
        self.gpio_data = {
            'red_led': 7,
            'green_led': 26
        }

    def _export_gpio(self, number):
        ex_path = os.path.join(self.gpio_path, 'export')
        with open(ex_path, 'w') as gpiof:
            gpiof.write(number)
        self.exported.append(number)

    def _write_value(self, number, filename, value):
        if number not in self.exported:
            return False
        wr_path = os.path.join(self.gpio_path, 'gpio%d' % number, filename)
        if not os.path.exists(wr_path):
            return False
        with open(wr_path, 'w') as gpiof:
            gpiof.write(value)
        return True

    def red_led_on(self):
        number = self.gpio_data['red_led']
        if number not in self.exported:
            self._export_gpio(number)
        self._write_value(number, 'direction', 'out')
        self._write_value(number, '1', 'active_low')
        self._write_value(number, '1', 'value')

    def red_led_off(self):
        number = self.gpio_data['red_led']
        if number not in self.exported:
            self._export_gpio(number)
        self._write_value(number, 'direction', 'out')
        self._write_value(number, '1', 'active_low')
        self._write_value(number, '0', 'value')


