# -*- coding: utf-8 -*-
# Created: 3/27/2018
# Project : AnKindle

from PyQt4.QtGui import QAction

from AnKindle.util import MDXDownloader
from anki.collection import _Collection
from aqt import mw
from aqt.importing import importFile
from .const import MUST_IMPLEMENT_FIELDS, DEFAULT_TEMPLATE
from .gui import Window
from .lang import _trans


class ActionShow(QAction):
    def __init__(self, parent):
        super(ActionShow, self).__init__(parent)
        self.setText(_trans("AnKindle"))


class AnKindleAddon:

    def __init__(self):

        # variables
        self.main_menu = None
        self.action_visible = None
        # self.main_menu_action = None

        if not self.avl_col_model_names:
            importFile(mw, DEFAULT_TEMPLATE)

    def perform_hooks(self, func):
        # func('reviewCleanup', self.on_review_cleanup)
        func('profileLoaded', self.on_profile_loaded)
        # func('afterStateChange', self.after_anki_state_change)

    def on_profile_loaded(self):
        self.init_menu()

    def init_menu(self):
        # init actions
        if not self.action_visible:
            self.action_visible = ActionShow(mw.form.menuTools)
            self.action_visible.triggered.connect(self.on_show_dialog)
            mw.form.menuTools.addAction(self.action_visible)

    def on_show_dialog(self):
        self.dlg = Window(mw, self.avl_col_model_names, self.avl_decks, )
        self.dlg.exec_()

    def avl_col_model_names(self):
        _ = []
        for mid, m_values in self.collection.models.models.items():
            if not set([f.lower() for f in MUST_IMPLEMENT_FIELDS]).difference(
                    set([f[u'name'] for f in m_values[u'flds']])):
                _.append(mid)
        return [v for k, v in self.collection.models.models.items() if k in _]

    def avl_decks(self):
        _ = []
        for did, d_values in self.collection.decks.decks.items():
            _.append(did)
        return [v for k, v in self.collection.decks.decks.items() if k in _]

    @property
    def collection(self):
        """

        :rtype: _Collection
        """

        return mw.col
