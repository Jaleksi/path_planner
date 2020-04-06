# 3rd party
from PyQt5 import QtWidgets


class ItemList(QtWidgets.QListWidget):
    def __init__(self):
        super().__init__()

    def new_target(self, target_obj):
        assert target_obj is not None, 'TARGET OBJECT NONE @ ITEM_LIST.py'
        self.addItem(target_obj)

    def del_target(self, target):
        target_index = self.row(target)
        self.takeItem(target_index)
