#!/usr/bin/env python

from button_item import ButtonItem
from list_item import ListItem
import rospkg


rospack = rospkg.RosPack()
icons_path = rospack.get_path('art_projected_gui') + '/icons/'


class ItemsTreeListItem(ListItem):

    def __init__(self, scene, x, y, w, data, tree_data, item_selected_cb=None, item_moved_cb=None, parent=None):

        super(ItemsTreeListItem, self).__init__(
            scene,
            x,
            y,
            w,
            data,
            item_selected_cb=item_selected_cb,
            item_moved_cb=item_moved_cb,
            parent=parent)

        self.tree_data = tree_data
        self.hide_tree_btn = ButtonItem(self.scene(), 0, 0, "BTN", self, self.hide_tree_btn_cb,
                                        image_path=icons_path + "failure.svg")
        self.hide_tree_btn.setVisible(False)

    def show_items_tree(self):

        for it in self.items:

            it.setVisible(False)

        self.hide_tree_btn.setPos(0, 0)
        self.hide_tree_btn.setVisible(True)

    def hide_tree_btn_cb(self, btn):

        self.set_current_idx(0 if self.selected_item_idx is not None else self.selected_item_idx)
        self.hide_tree_btn.setVisible(False)
