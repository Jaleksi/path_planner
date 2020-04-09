# 3rd party
from PyQt5 import QtWidgets


class ItemList(QtWidgets.QListWidget):
    def __init__(self):
        super().__init__()
        self.setSortingEnabled(True)

    def new_target(self, target_obj):
        assert target_obj is not None, 'TARGET OBJECT NONE @ ITEM_LIST.py'
        self.addItem(target_obj)

    def del_target(self, target):
        target_index = self.row(target)
        self.takeItem(target_index)

    def arrange_items(self, order):
        position = 1
        for item in order:
            target = self.item_by_parent_node(item)
            if target is None:
                continue
            target.num = position
            target.update_text()
            position += 1
        self.sortItems()

    def all_items(self):
        for i in range(self.count()):
            yield self.item(i)

    def item_by_parent_node(self, node):
        for item in self.all_items():
            if item.parent_node == node:
                return item
        return None
