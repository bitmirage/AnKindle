import os
from urllib import urlretrieve

from PyQt4.QtCore import QThread


class MDXDownloader(QThread):
    def __init__(self, parent):
        super(MDXDownloader, self).__init__(parent)
        self.remote_mdx, self.local_mdx = None, None
        self.success = False

    def run(self):
        try:
            urlretrieve(self.remote_mdx, self.local_mdx)
            self.success = True
        except:
            if os.path.isfile(self.local_mdx):
                try:
                    os.remove(self.local_mdx)
                except:
                    pass
            self.success = False

    def start(self, remote_mdx, local_mdx):
        super(MDXDownloader, self).start()
        self.remote_mdx, self.local_mdx = remote_mdx, local_mdx
