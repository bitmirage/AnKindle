# -*- coding: utf-8 -*-
# Created: 3/27/2018
# Project : AnKindle
import os
import re
import sqlite3
from functools import partial
from threading import Thread
from urllib import urlretrieve

from PyQt4 import QtCore
from PyQt4.QtGui import QDialog, QVBoxLayout, QFrame, \
    QPushButton, QSpacerItem, QLabel, QHBoxLayout, QSizePolicy, QGroupBox, QComboBox, QCheckBox

import anki
from AnKindle import resource_rc
from anki import notes, lang
from anki.lang import currentLang
from aqt import mw
from aqt.importing import importFile
from aqt.progress import ProgressManager
from aqt.studydeck import StudyDeck
from aqt.utils import showInfo, getFile, showText, openLink, askUser
from .SharedControl import WeChatButton, MoreAddonButton, VoteButton, _ImageButton, UpgradeButton, AddonUpdater
from .config import Config
from .const import ADDON_CD, DEBUG, __version__, MDX_LIB_URL, DEFAULT_TEMPLATE
from .db import KindleDB
from .lang import _trans
from .libs.mdict import mdict_query
from .libs.mdict import readmdict

resource_rc.qInitResources()


class _HelpBtn(_ImageButton):
    def __init__(self, parent, help_text_or_file):
        super(_HelpBtn, self).__init__(parent, os.path.join(os.path.dirname(__file__), "resource", "help.png"))
        self.setToolTip(_trans("Help"))
        self.help_text_or_file = help_text_or_file
        self.clicked.connect(self.on_clicked)

    def on_clicked(self):
        if os.path.isfile(self.help_text_or_file):
            with open(self.help_text_or_file) as f:
                text = f.read().decode("utf-8")
        else:
            text = self.help_text_or_file
        dlg, box = showText(text
                            , self.parent(), "html", title=anki.lang._("Help"), run=False)
        btn_download_mdx = QPushButton(_trans("DOWNLOAD MDX"), dlg)
        btn_download_mdx.clicked.connect(partial(openLink, MDX_LIB_URL))
        dlg.layout().insertWidget(1, btn_download_mdx)
        dlg.exec_()


class _SharedFrame(QFrame):
    def __init__(self, parent, updater=None):
        super(_SharedFrame, self).__init__(parent)
        self.l_h_widgets = QHBoxLayout(self)
        wx = WeChatButton(self)
        wx.setObjectName("wx")
        self.l_h_widgets.addWidget(wx)
        vt = VoteButton(self, ADDON_CD)
        vt.setObjectName("vt")
        vt.setIcon(os.path.join(os.path.dirname(__file__), "resource", "upvote.png"))
        self.l_h_widgets.addWidget(vt)
        mr = MoreAddonButton(self)
        mr.setObjectName("mr")
        mr.setIcon(os.path.join(os.path.dirname(__file__), "resource", "more.png"))
        self.l_h_widgets.addWidget(mr)
        self.l_h_widgets.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum, ))
        self.l_h_widgets.addWidget(_HelpBtn(self, self.help_txt))
        self.l_h_widgets.setMargin(0)
        if updater:
            self.l_h_widgets.addWidget(UpgradeButton(self, updater))

    @property
    def help_txt(self):
        if currentLang == 'zh_CN':
            loc = os.path.join(os.path.dirname(__file__), "resource", "help_cn.html")
        else:
            loc = os.path.join(os.path.dirname(__file__), "resource", "help_en.html")
        return loc

def HLine():
    toto = QFrame()
    toto.setFrameShape(QFrame.HLine)
    toto.setFrameShadow(QFrame.Sunken)
    return toto


def VLine():
    toto = QFrame()
    toto.setFrameShape(QFrame.VLine)
    toto.setFrameShadow(QFrame.Sunken)
    return toto


class Window(QDialog):
    # noinspection PyStatementEffect
    def __init__(self, parent, mod_list_func, deck_list_func):
        """

        :param parent:
        :param mod_list:
        :param deck_list:
        """

        super(Window, self).__init__(parent)
        self.setMinimumWidth(300)
        self.setStyleSheet("font-family: 'Microsoft YaHei UI', Consolas, serif;")
        self.mod_list_func = mod_list_func
        self.deck_list_func = deck_list_func

        self.setWindowTitle("{} - {}".format(_trans("AnKindle"), __version__))

        # region init controls
        self.lb_db = QLabel(_trans("CANNOT FIND KINDLE VOLUME"), self)
        self.lb_db.setVisible(False)

        self.btn_select_db = _ImageButton(self, os.path.join(os.path.dirname(__file__), "resource", "kindle.png"))
        self.btn_select_db.clicked.connect(partial(self.on_select_kindle_db, True))
        self.btn_select_db.setToolTip(_trans("SELECT KINDLE DB"))
        self.btn_1select_model = QPushButton(_trans("SELECT MODEL"), self)
        self.btn_1select_model.clicked.connect(partial(self.on_select_model_clicked, None))
        self.btn_2select_deck = QPushButton(_trans("SELECT DECK"), self)
        self.btn_2select_deck.clicked.connect(partial(self.on_select_deck_clicked, None))

        self.btn_3select_mdx = QPushButton(_trans("SELECT MDX"), self)
        self.btn_3select_mdx.clicked.connect(partial(self.on_select_mdx, None))
        self.btn_3select_mdx.setEnabled(False)

        self.combo_lang = QComboBox(self)
        self.combo_lang.setMaximumWidth(100)
        self.combo_lang.setEnabled(False)

        self.updater = AddonUpdater(
            self, _trans("AnKindle"), ADDON_CD,
            "https://raw.githubusercontent.com/upday7/AnKindle/master/AnKindle/const.py",
            "",
            mw.pm.addonFolder(),
            __version__
        )

        # region layouts
        frm_widgets = _SharedFrame(self, self.updater)
        self.updater.start()

        frm_lists = QFrame(self)
        self.grp = QGroupBox(frm_lists)
        self.l_lists = QVBoxLayout(self.grp)

        l_grp_top = QHBoxLayout()
        self.l_lists.addWidget(self.lb_db, 0, QtCore.Qt.AlignCenter)
        l_grp_top.addWidget(QLabel(_trans("Mandatory"), self), 0, QtCore.Qt.AlignLeft)
        self.l_lists.addLayout(l_grp_top)

        l_language = QHBoxLayout()
        l_language.addWidget(self.btn_select_db)
        l_language.addWidget(VLine())
        l_language.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Minimum))
        l_language.addWidget(QLabel(_trans("language"), self), 0, QtCore.Qt.AlignLeft)
        l_language.addWidget(self.combo_lang)
        self.l_lists.addLayout(l_language)
        self.l_lists.addWidget(self.btn_1select_model)
        self.l_lists.addWidget(self.btn_2select_deck)

        l = QHBoxLayout()
        l.addWidget(self.btn_3select_mdx)

        self.l_lists.addWidget(HLine())
        self.l_lists.addWidget(QLabel(_trans("Optional"), self), 0, QtCore.Qt.AlignLeft)
        self.l_lists.addLayout(l)

        self.btn_import = QPushButton(_trans("ONE CLICK IMPORT"), self)
        self.btn_import.setEnabled(False)
        self.btn_import.clicked.connect(self.on_import)

        self.ck_import_new = QCheckBox(_trans("IMPORT NEW"), self, clicked=self.on_ck_import_new)

        self.l = QVBoxLayout(self)
        self.l.addWidget(frm_widgets)
        self.l.addWidget(self.grp)
        l_import = QHBoxLayout()
        self.ck_import_new.setFixedWidth(90)
        l_import.addWidget(self.ck_import_new)
        l_import.addWidget(self.btn_import)
        self.l.addLayout(l_import)
        self.l.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # endregion

        # endregion

        self.model = None
        self.deck = None
        self.mdx = None
        self.builder = None
        self._preload_data = None
        self._lang_config_dict = {}
        self.db = None
        self.on_select_kindle_db(False)

        self.missed_css = set()

        # init actions
        self.btn_import.setDefault(True)
        try:
            self._validate_langs()
        except MemoryError:
            pass
        except:
            showInfo(_trans("ENSURE USB"), mw, type="warning", title=_trans("ANKINDLE"))
        # self.load_lang_default_config()

    def set_model_deck_button(self, on_combo_changed=False):
        model_id = self.lang_config.get("model_id")
        deck_id = self.lang_config.get("deck_id")
        if model_id and model_id in [unicode(m['id']) for m in self.mod_list] or on_combo_changed:
            self.on_select_model_clicked(model_id, on_combo_changed)
        if deck_id and deck_id in [unicode(m['id']) for m in self.deck_list] or on_combo_changed:
            self.on_select_deck_clicked(deck_id, on_combo_changed)

    def _validate_clicks(self):
        self.btn_import.setEnabled(all([self.model, self.deck, self.current_mdx_lang]))

    def _validate_langs(self):
        if self.word_langs:
            try:
                self.combo_lang.currentIndexChanged.disconnect(self.on_combo_lang_index_changed)
            except:
                pass
            self.combo_lang.clear()
            self.combo_lang.addItems(self.word_langs)
            self.combo_lang.setEnabled(True)
            self.btn_3select_mdx.setEnabled(True)

            if Config.last_used_lang:
                last_used_lang_index = self.combo_lang.findText(Config.last_used_lang)
                if last_used_lang_index == -1:
                    last_used_lang_index = 0
            else:
                last_used_lang_index = 0

            self.combo_lang.setCurrentIndex(last_used_lang_index)
            self.on_combo_lang_index_changed(last_used_lang_index)

            # warning ensure this is connected at last
            self.combo_lang.currentIndexChanged.connect(self.on_combo_lang_index_changed)

        self._validate_clicks()

    @property
    def current_mdx_lang(self):
        return self.combo_lang.currentText()

    @property
    def mod_list(self):
        return self.mod_list_func()

    @property
    def deck_list(self):
        return self.deck_list_func()

    def on_ck_import_new(self, ):
        self.set_lang_config(import_new=self.ck_import_new.isChecked())

    def on_select_kindle_db(self, from_user_click):
        validated = False
        self.db = KindleDB(Config.last_used_db_path, from_user_click)
        if not self.db.is_available:
            self.lb_db.setVisible(True)
        else:
            self.lb_db.setVisible(False)
            if from_user_click:
                self._validate_langs()
            validated = True
        self.adjustSize()
        return validated

    def on_combo_lang_index_changed(self, index):
        Config.last_used_lang = self.combo_lang.currentText()
        self.mdx = self.lang_config.get("mdx_path")
        self.on_select_mdx(self.mdx, True)
        self.ck_import_new.setChecked(self.lang_config.get("import_new", True))
        self._validate_clicks()
        self.set_model_deck_button(True)

    def on_select_model_clicked(self, mid, ignore_selection=False):
        self.model = None
        if not mid:
            if not ignore_selection:
                study_deck_ret = self.select_model()
                self.model = mw.col.models.byName(study_deck_ret.name)
        else:
            self.model = mw.col.models.get(mid)

        if self.model:
            nm = self.model['name']
            self.btn_1select_model.setText(
                u'%s [%s]' % (_trans("NOTE TYPE"), nm))

            self.set_lang_config(model_id=unicode(self.model['id']) if self.model else u'')
        else:
            self.btn_1select_model.setText(_trans("SELECT MODEL"))
        self._validate_clicks()

    def select_model(self):
        if not self.mod_list:
            importFile(mw, DEFAULT_TEMPLATE)

        edit = QPushButton(_trans("USE LATEST TEMPLATE"),
                           clicked=lambda: importFile(mw, DEFAULT_TEMPLATE))
        ret = StudyDeck(mw, names=lambda: sorted([f['name'] for f in self.mod_list]),
                        accept=anki.lang._("Choose"), title=_trans("NOTE TYPE"), parent=self, buttons=[edit],
                        cancel=True)
        return ret

    def on_select_deck_clicked(self, did, ignore_selection=False):
        nm = None
        if did:
            nm = mw.col.decks.decks[did]["name"]
        else:
            ret = None
            if not ignore_selection:
                ret = StudyDeck(
                    mw, accept=anki.lang._("Choose"),
                    title=anki.lang._("Choose Deck"),
                    cancel=True, parent=self)
            if ret:
                nm = ret.name
        if nm:
            self.deck = mw.col.decks.byName(nm)
            self.btn_2select_deck.setText(
                u'%s [%s]' % (_trans("DECK TYPE"), nm))

            self.set_lang_config(deck_id=unicode(self.deck['id']) if self.deck else u'')
        else:
            self.btn_2select_deck.setText(_trans("SELECT DECK"))

        self._validate_clicks()

    def on_select_mdx(self, file_path, ignore_selection=False):
        self.mdx = None
        if file_path and os.path.isfile(file_path):
            self.mdx = file_path
        else:
            if not ignore_selection:
                self.mdx = getFile(self, _trans("MDX TYPE"), lambda x: x, ("MDict (*.MDX)"),
                                   os.path.join(os.path.dirname(__file__),
                                                u"resource") if not self.mdx else os.path.dirname(self.mdx)
                                   )

        if self.mdx and os.path.isfile(self.mdx):
            self.btn_3select_mdx.setText(
                u'%s [%s]' % (_trans("MDX TYPE"), os.path.splitext(os.path.basename(self.mdx))[0]))
            self.builder = mdict_query.IndexBuilder(self.mdx)
            self.set_lang_config(mdx_path=unicode(self.mdx) if self.mdx else u'')
        else:
            self.btn_3select_mdx.setText(_trans("SELECT MDX"))
            self.builder = None

    def get_html(self, word):
        html = ''

        if not self.builder:
            return html

        self.builder.check_build()
        result = self.builder.mdx_lookup(word)  # self.word: unicode
        if result:
            if result[0].upper().find(u"@@@LINK=") > -1:
                # redirect to a new word behind the equal symol.
                word = result[0][len(u"@@@LINK="):].strip()
                return self.get_html(word)
            else:
                html = self.adapt_to_anki(result[0])
        return html

    def save_file(self, filepath_in_mdx, savepath=None):
        basename = os.path.basename(filepath_in_mdx.replace('\\', os.path.sep))
        if savepath is None:
            savepath = '_' + basename
        try:
            bytes_list = self.builder.mdd_lookup(filepath_in_mdx)
            if bytes_list and not os.path.exists(savepath):
                with open(savepath, 'wb') as f:
                    f.write(bytes_list[0])
                    return savepath
        except sqlite3.OperationalError as e:
            showInfo(str(e))

    def save_media_files(self, data):
        """
        get the necessary static files from local mdx dictionary
        ** kwargs: data = list
        """
        # diff = data.difference(self.media_cache['files'])
        # self.media_cache['files'].update(diff)
        lst, errors = list(), list()
        wild = [
            '*' + os.path.basename(each.replace('\\', os.path.sep)) for each in data]
        try:
            for each in wild:
                keys = self.builder.get_mdd_keys(each)
                if not keys:
                    errors.append(each)
                lst.extend(keys)
            for each in lst:
                self.save_file(each)
        except AttributeError:
            pass

        return errors

    def adapt_to_anki(self, html):
        """
        1. convert the media path to actual path in anki's collection media folder.
        2. remove the js codes (js inside will expires.)
        """
        # convert media path, save media files
        media_files_set = set()
        mcss = re.findall(r'href="(\S+?\.css)"', html)
        media_files_set.update(set(mcss))
        mjs = re.findall(r'src="([\w\./]\S+?\.js)"', html)
        media_files_set.update(set(mjs))
        msrc = re.findall(r'<img.*?src="([\w\./]\S+?)".*?>', html)
        media_files_set.update(set(msrc))
        msound = re.findall(r'href="sound:(.*?\.(?:mp3|wav))"', html)
        if 1:  # config.export_media
            media_files_set.update(set(msound))
        for each in media_files_set:
            html = html.replace(each, u'_' + each.split('/')[-1])
        # find sounds
        p = re.compile(
            r'<a[^>]+?href=\"(sound:_.*?\.(?:mp3|wav))\"[^>]*?>(.*?)</a>')
        html = p.sub(u"[\\1]\\2", html)
        self.save_media_files(media_files_set)
        for cssfile in mcss:
            cssfile = '_' + \
                      os.path.basename(cssfile.replace('\\', os.path.sep))
            # if not exists the css file, the user can place the file to media
            # folder first, and it will also execute the wrap process to generate
            # the desired file.
            if not os.path.exists(cssfile):
                self.missed_css.add(cssfile[1:])

        return html

    @property
    def lang_config(self):
        return Config.lang_config.get(self.current_mdx_lang, {"model_id": u"",
                                                              "deck_id": u"",
                                                              "import_new": True,
                                                              "mdx_path": u"", })

    def set_lang_config(self, **kwargs):
        orig_dict = self.lang_config
        args = kwargs.keys()
        if 'model_id' in args:
            orig_dict.update({'model_id': kwargs['model_id']})
        if 'deck_id' in args:
            orig_dict.update({'deck_id': kwargs['deck_id']})
        if 'mdx_path' in args:
            orig_dict.update({'mdx_path': kwargs['mdx_path']})
        if 'import_new' in args:
            orig_dict.update({'import_new': kwargs['import_new']})
        all_dicts = Config.lang_config
        all_dicts.update({self.current_mdx_lang: orig_dict})
        Config.lang_config = all_dicts

    @property
    def word_data(self):
        if not self._preload_data:
            self._preload_data = list(self.db.get_words(self.ck_import_new.isChecked()))
        return self._preload_data

    @property
    def word_langs(self):
        langs = set()
        for i, _ in enumerate(self.word_data):
            (id, word, stem, lang, added_tm, usage, title, authors) = _
            if lang:
                langs.add(lang.upper())
        return list(langs)

    def on_import(self):
        self._preload_data = None
        # validate db still online
        if not self.on_select_kindle_db(False):
            showInfo(_trans("ENSURE USB"), mw, type="warning", title=_trans("ANKINDLE"))
            return

        dict_nm = ''
        if self.builder:
            try:
                mdx_dict = readmdict.MDX(self.mdx, only_header=True)
                self.builder._encoding = mdx_dict._encoding
            except MemoryError:
                showInfo(_trans("MDX MEMORY ERROR"), self, type="warning", title=_trans("ANKINDLE"))
                return
            except TypeError:
                showInfo(_trans("MDX TYPE ERROR"), self, type="warning", title=_trans("ANKINDLE"))
                return
            dict_nm = os.path.splitext(os.path.basename(mdx_dict._fname))[0]
        else:
            ret = askUser(
                _trans("ALERT FOR MISSING MDX"), self, defaultno=False, title=_trans("ANKINDLE")
            )
            if not ret:
                return

        progress = ProgressManager(self)
        total_new = 0
        total_dup = 0
        progress.start(immediate=True)
        words = self.word_data
        for i, _ in enumerate(words):
            progress.update(_trans("IMPORTING") + "\n{} / {}".format(i + 1, len(words)), i, True)
            (id, word, stem, lang, added_tm, usage, title, authors) = _
            if lang and lang.upper() != self.current_mdx_lang:
                continue
            try:
                note = notes.Note(mw.col, mw.col.models.models[unicode(self.model['id'])])
            except KeyError:
                continue
            note.model()['did'] = self.deck['id']

            def update_note(_note):
                _note.fields[_note._fieldOrd('id')] = id
                _note.fields[_note._fieldOrd('word')] = word
                _note.fields[_note._fieldOrd('stem')] = stem
                _note.fields[_note._fieldOrd('lang')] = lang
                _note.fields[_note._fieldOrd('creation_tm')] = added_tm
                _note.fields[_note._fieldOrd('usage')] = self.adapt_to_anki(usage.replace(word, u"<b>%s</b>" % word))
                _note.fields[_note._fieldOrd('title')] = title
                _note.fields[_note._fieldOrd('authors')] = authors
                _note.fields[_note._fieldOrd('mdx_dict')] = self.adapt_to_anki(self.get_html(stem))

                try:
                    _note.fields[_note._fieldOrd('mdx_name')] = dict_nm
                except KeyError:
                    pass

            update_note(note)
            if note.dupeOrEmpty() != 2:
                mw.col.addNote(note)
                total_new += 1
            else:
                total_dup += 1
            mw.col.autosave()
        progress.finish()

        mw.moveToState("deckBrowser")
        showInfo(_trans("CREATED AND DUPLICATES") % (total_new, total_dup))
