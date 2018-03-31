# -*- coding: utf-8 -*-
# Created: 3/27/2018
# Project : AnKindle

import os

from AnKindle.config import Config
from anki.db import DB
from anki.utils import isWin
from aqt import mw
# noinspection SqlResolve
from aqt.utils import getFile
from .const import DEBUG
from .lang import _trans


class KindleDB(DB):
    def __init__(self, db_path=None, force_select=False):

        if force_select:
            self.db = self.search_db(force_select)
        else:
            if db_path and os.path.isfile(db_path):
                self.db = db_path
            else:
                self.db = self.search_db()

        if self.db:
            Config.last_used_db_path = self.db
            super(KindleDB, self).__init__(self.db)

    @property
    def is_available(self):
        try:
            return os.path.isfile(self.db)
        except TypeError:
            return False

    def search_db(self, force_select_db=False):
        if isWin:
            allDisks = ['A:', 'B:', 'C:', 'D:', 'E:', 'F:', 'G:',
                        'H:', 'I:', 'J:', 'K:', 'L:', 'M:', 'N:', 'O:', 'P:', 'Q:',
                        'R:', 'S:',
                        'T:',
                        'U:', 'V:', 'W:', 'X:', 'Y:', 'Z:']

        else:
            allDisks = [os.path.join(os.path.sep, "Dev/Kindle"),
                        os.path.join(os.path.sep, "Volumes/Kindle"),
                        os.path.join(os.path.sep, "mnt/Kindle")]
        if DEBUG or force_select_db:
            allDisks = []
        for disk in allDisks:
            kindle_db = os.path.join(
                disk + os.path.sep + "system" + os.path.sep + "vocabulary" + os.path.sep + "vocab.db")
            if os.path.isfile(kindle_db):
                return kindle_db
        if force_select_db:
            kindle_db = getFile(mw, _trans("GET KINDLE DB"), lambda x: x, ("Kindle Vocab Db(*.db)"),
                                os.path.dirname(
                                    Config.last_used_db_path if
                                    os.path.isdir(os.path.dirname(Config.last_used_db_path)) else __file__
                                )
                                )
            return kindle_db

    def get_words(self, only_new):
        """

        :return: list of [id,word, ste, lang, added_tm,usage,title,authors]
        """
        return self.execute(
            """
            SELECT
              ws.id,
              ws.word,
              ws.stem,
              ws.lang,
              datetime(ws.timestamp * 0.001, 'unixepoch', 'localtime') added_tm,
              lus.usage,
              bi.title,
              bi.authors
            FROM words AS ws LEFT JOIN lookups AS lus ON ws.id = lus.word_key
              LEFT JOIN book_info AS bi ON lus.book_key = bi.id
            
            {}
            
            """.format("WHERE ws.CATEGORY = 0"  if only_new else "")
        )
