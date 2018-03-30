# -*- coding: utf-8 -*-
# Created: 3/27/2018
# Project : AnKindle


# -*- coding:utf-8 -*-
#
# Copyright © 2016–2018 KuangKuang <upday7@163.com>
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version; http://www.gnu.org/copyleft/gpl.html.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from AnKindle import const, AnKindleAddon
from anki.hooks import addHook


def start():
    if const.HAS_SET_UP:
        return
    rr = AnKindleAddon()
    rr.perform_hooks(addHook)
    const.HAS_SET_UP = True


addHook("profileLoaded", start)
