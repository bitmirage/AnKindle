# -*- coding:utf-8 -*-
#
# Copyright © 2016–2017 Liang Feng <finalion@gmail.com>
#
# Support: Report an issue at https://github.com/finalion/WordQuery/issues
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

from anki.lang import currentLang

_style = u"""
<style>

* {
    font-family: 'Microsoft YaHei UI', Consolas, serif;
}

</style>

"""

trans = {
    'ANKINDLE': {'zh_CN': u'AnKindle', 'en': u'AnKindle'},
    'NOTE TYPE': {'zh_CN': u'保存为笔记类型', 'en': u'Save as Note'},
    'DECK TYPE': {'zh_CN': u'保存到记忆库', 'en': u'Save to Deck'},
    'MDX TYPE': {'zh_CN': u'查询MDX字典', 'en': u'Query Dict'},
    'SELECT MODEL': {'zh_CN': u'保存为笔记类型', 'en': u'Save as Note'},
    'SELECT DECK': {'zh_CN': u'保存到记忆库', 'en': u'Save to deck'},
    'SELECT MDX': {'zh_CN': u'（可选） 选择MDX字典', 'en': u'(Optional) MDX Dict'},
    'CREATED AND DUPLICATES': {'zh_CN': u'新建：%s 张卡片。\n重复：%s 张卡片。',
                               'en': u'Created: %s cards.\nDuplicates: %s cards.'},
    'NONE': {'zh_CN': u'无', 'en': u'None'},
    'CANNOT FIND KINDLE VOLUME': {'zh_CN': u'** 无法找到 Kindle 数据库 **', 'en': u'** Cannot Find Kindle Db **'},
    'USING DB': {'zh_CN': u'读取%s', 'en': u'Reading %s'},
    'HELP': {'zh_CN': u'帮助', 'en': u'Help'},
    'IMPORT': {'zh_CN': u'导入设置', 'en': u'Import Config'},
    'SELECT KINDLE DB': {'zh_CN': u'重新选择Kindle数据库文件', 'en': u'Re-select Kindle Database File'},
    'IMPORT NEW': {'zh_CN': u'只导入新词', 'en': u'Import New'},
    'ONE CLICK IMPORT': {'zh_CN': u'一键导入', 'en': u'One-Click-Import'},
    'GET KINDLE DB': {'zh_CN': u'请手动选择Kindle数据库，。', 'en': u'Please select Kindle vocab database.'},
    'IMPORTING': {'zh_CN': u'正在导入生词', 'en': u'Importing'},
    # 'SELECT ORIG LANG': {'zh_CN': u'选择生词语言类型:', 'en': u'Language of words:'},
    'MANDATORY': {'zh_CN': u'<b>必选：</b>', 'en': u'<b>Mandatory:</b>'},
    'ALERT FOR MISSING MDX': {'zh_CN': u'您没有选择MDX文件，单词释义信息将不会被导入，确认继续吗？',
                              'en': u'None of MDX dictionaries are selected, '
                                    u'explanations will be lost in your imports. Confirm to continue?'},
    'OPTIONAL': {'zh_CN': u'<b>可选：</b>', 'en': u'<b>Optional:</b>'},
    'USE LATEST TEMPLATE': {'zh_CN': u'使用最新MDX-Kindle模板', 'en': u'Use latest MDX-Kindle Template'},
    'LANGUAGE': {'zh_CN': u'生词语言类型:', 'en': u'Word Language: '},
    'DOWNLOAD MDX': {'zh_CN': u'下载MDX词典', 'en': u'Download MDX Dictionaries'},
    'MDX MEMORY ERROR': {'zh_CN': u'无法读取MDX词典内容，请更换词典文件。', 'en': u'Memory error when loading MDX, please switch '
                                                                 u'another MDX file.'},
    'MDX TYPE ERROR': {'zh_CN': u'无法读取MDX词典内容，请更换词典文件。', 'en': u'Type error when loading MDX, please switch '
                                                               u'another MDX file.'},
    "ENSURE USB": {'zh_CN': u'请确保Kindle已经接入电脑。',
                   'en': u'Please ensure Kindle has been adtapted to your machine.'},
}


def _trans(key, lang=currentLang):
    key = key.upper().strip()
    if lang != 'zh_CN' and lang != 'en' and lang != 'fr':
        lang = 'en'  # fallback

    def disp(s):
        return s.capitalize()

    if key not in trans or lang not in trans[key]:
        return disp(key)
    return trans[key][lang]


def _sl(key):
    return trans[key].values()
