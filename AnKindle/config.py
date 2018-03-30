# -*- coding: utf-8 -*-
# Created: 3/27/2018
# Project : AnKindle
import json

import aqt
from anki.sync import os
from aqt import mw

path_join = os.path.join


class _MetaConfigObj(type):
    """
    Meta class for reading/saving config.json for anki addon
    """
    metas = {}

    class StoreLocation:
        Profile = 0
        AddonFolder = 1
        MediaFolder = 3

    # noinspection PyArgumentList
    def __new__(mcs, name, bases, attributes):

        config_dict = {k: attributes[k] for k in attributes.keys() if not k.startswith("_") and k != "Meta"}
        attributes['config_dict'] = config_dict

        for k in config_dict.keys():
            attributes.pop(k)
        c = super(_MetaConfigObj, mcs).__new__(mcs, name, bases, attributes)

        # region Meta properties
        # meta class
        meta = attributes.get('Meta', type("Meta", (), {}))
        # meta values
        setattr(meta, "config_dict", config_dict)
        setattr(meta, "__store_location__", getattr(meta, "__store_location__", 0))
        setattr(meta, "__config_file__", getattr(meta, "__config_file__", None))

        _MetaConfigObj.metas[c.__name__] = meta
        # endregion

        if not config_dict:
            return c

        mcs.attributes = attributes  # attributes that is the configuration items

        if _MetaConfigObj.metas[name].__store_location__ == _MetaConfigObj.StoreLocation.MediaFolder:
            if not _MetaConfigObj.metas[name].__config_file__:
                raise Exception("If StoreLocation is Media Folder, __config_file__ must be provided!")
            setattr(c, "media_json_file",
                    mcs.MediaConfigJsonFile("_{}".format(_MetaConfigObj.metas[name].__config_file__).lower()))

        return c

    def __getattr__(cls, item):
        if item == "meta":
            return _MetaConfigObj.metas[cls.__name__]
        else:
            load_config = lambda: cls.get_config(cls.metas[cls.__name__].__store_location__)
            config_obj = load_config()
            return config_obj.get(item)

    def __setattr__(cls, key, value):
        """
        when user set values to addon config obj class, will be passed to anki's addon manager and be saved.
        :param key:
        :param value:
        :return:
        """
        try:
            config_obj = cls.get_config(cls.metas[cls.__name__].__store_location__)
            config_obj[key] = value
            store_location = cls.metas[cls.__name__].__store_location__
            if store_location == cls.StoreLocation.AddonFolder:
                if cls.IsAnki21:
                    mw.addonManager.writeConfig(cls.AddonModelName, config_obj)
                else:
                    with open(cls.ConfigJsonFile(), "w") as f:
                        json.dump(config_obj, f)
            elif store_location == cls.StoreLocation.MediaFolder:
                with open(cls.media_json_file, "w") as f:
                    json.dump(config_obj, f)
            elif store_location == _MetaConfigObj.StoreLocation.Profile:
                if _MetaConfigObj.IsAnki21():
                    mw.pm.profile.update(config_obj)
                else:
                    mw.pm.meta.update(config_obj)
        except:
            super(_MetaConfigObj, cls).__setattr__(key, value)

    def get_config(cls, store_location):
        """

        :param store_location:
        :rtype: dict
        """

        def _get_json_dict(json_file):
            if not os.path.isfile(json_file):
                with open(json_file, "w") as f:
                    json.dump(cls.config_dict, f)
            with open(json_file, 'r') as ff:
                return json.load(ff)

        if store_location == _MetaConfigObj.StoreLocation.Profile:
            if _MetaConfigObj.IsAnki21():
                disk_config_obj = mw.pm.profile
            else:
                disk_config_obj = mw.pm.meta
            cls.config_dict.update(disk_config_obj)
        elif store_location == _MetaConfigObj.StoreLocation.AddonFolder:
            # ensure json file
            obj = _get_json_dict(_MetaConfigObj.ConfigJsonFile())

            if _MetaConfigObj.IsAnki21():
                disk_config_obj = mw.addonManager.getConfig(_MetaConfigObj.AddonModelName())
            else:
                disk_config_obj = obj
            cls.config_dict.update(disk_config_obj)
        elif store_location == _MetaConfigObj.StoreLocation.MediaFolder:
            disk_config_obj = _get_json_dict(cls.media_json_file)
            cls.config_dict.update(disk_config_obj)
            with open(cls.media_json_file, "w") as f:
                json.dump(cls.config_dict, f)
        return cls.config_dict

    @staticmethod
    def IsAnki21():
        from anki import version
        return eval(version[:3]) >= 2.1

    @staticmethod
    def ConfigJsonFile():
        return path_join(_MetaConfigObj.AddonsFolder(), "config.json")

    @staticmethod
    def MediaConfigJsonFile(file_nm):
        return path_join(_MetaConfigObj.MediaFolder(), file_nm)

    @staticmethod
    def AddonsFolder():
        if _MetaConfigObj.IsAnki21():
            _ = path_join(mw.addonManager.addonsFolder(), _MetaConfigObj.AddonModelName())
        else:
            _ = mw.pm.addonFolder()
        if aqt.isWin:
            _ = _.encode(aqt.sys.getfilesystemencoding()).decode("utf-8")
        return _.lower()

    @staticmethod
    def AddonModelName():
        return __name__.split(".")[0]

    @staticmethod
    def MediaFolder():
        try:
            return path_join(mw.pm.profileFolder(), "collection.media")
        except:
            return ""


class Config:
    __metaclass__ = _MetaConfigObj

    class Meta:
        __store_location__ = _MetaConfigObj.StoreLocation.Profile

    mdx_kindle_model_id = u''  # todo invalid
    mdx_kindle_deck_id = u''  # todo invalid
    mdx_kindle_mdx_path = u''  # todo invalid

    mdx_kindle_mdx_path_dict = {}  # todo lang_cd : mdx_path # invalid

    lang_config = {

    }  # lang_cd: {"mdx_kindle_model_id":u"","mdx_kindle_deck_id":u"","mdx_kindle_mdx_path":u"",}

    last_used_lang = u""
    last_used_db_path = u""

    mdx_kindle_first_run = False
