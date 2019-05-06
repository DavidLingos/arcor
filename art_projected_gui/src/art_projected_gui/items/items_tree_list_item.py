#!/usr/bin/env python

import rospy
from PyQt4 import QtGui, QtCore
from button_item import ButtonItem
from list_item import ListItem
from line_item import LineItem
import rospkg


rospack = rospkg.RosPack()
icons_path = rospack.get_path('art_projected_gui') + '/icons/'


class ItemsTreeListItem(ListItem):

    def __init__(self, scene, x, y, w, data,
                 tree_data,
                 program_helper,
                 visualization_finished_cb=None,
                 item_selected_cb=None,
                 item_moved_cb=None, parent=None):

        self.w = 100
        self.h = 100

        super(ItemsTreeListItem, self).__init__(
            scene,
            x,
            y,
            w,
            data,
            movable_items=True,
            item_selected_cb=item_selected_cb,
            item_moved_cb=item_moved_cb,
            item_mouse_release_cb=self.item_mouse_release,
            item_mouse_move_cb=self.item_mouse_move,
            parent=parent)

        # Array of arrays with indexes:
        # 0 - index of button item
        # 1 - item_id
        # 2 - item_on_success
        # 3 - item_on_failure
        self.tree_data = tree_data
        self.visualize = False
        self.selected_item_idx = None
        self.lines = []
        self.ph = program_helper
        self.sp_x = 50
        self.sp_y = 3 * self.sp

        self.visualization_finished_cb = visualization_finished_cb

        self.hide_tree_btn = ButtonItem(self.scene(), 0, 0, "BTN", self, self.hide_tree_btn_cb,
                                        image_path=icons_path + "failure.svg")
        self.hide_tree_btn.setVisible(False)

    def item_clicked_cb(self, btn):

        if not self.isEnabled():

            return

        if not btn.pressed:

            self.selected_item_idx = None

        else:

            self.selected_item_idx = self.items.index(btn)

            for i in range(0, len(self.items)):

                if i != self.selected_item_idx:

                    self.items[i].set_pressed(False)

            if not self.visualize:
                self.set_current_idx(self.selected_item_idx, select=True)

        if self.item_selected_cb is not None:

            self.item_selected_cb(self.visualize)

    def item_mouse_release(self, button, point):

        previous_item = None
        for it in self.items:
            if not it.isVisible() or it == button:
                continue
            rospy.logdebug(it.pos().y())
            rospy.logdebug(point.y())
            if it.pos().y() <= point.y():
                previous_item = it
            else:
                break
        if previous_item is not None:
            idx = self.items.index(previous_item)

        return

    def item_mouse_move(self, button, point):

        if point.y() == 0:
            self.set_current_idx(self.get_current_idx() - 1, moving_item=button)
        elif point.y() == self.pos().y() + self.h - 3 * button.h:
            self.set_current_idx(self.get_current_idx() + 1, moving_item=button)
        return

    def show_items_tree(self):
        if len(self.tree_data) == 0:

            return

        processed_items = []
        current_item = self.tree_data[0]
        item_width = self.items[0].w
        y = self.hide_tree_btn.h + self.sp

        self.place_tree_item(
            current_item,
            (self.w - item_width) / 2,
            y,
            processed_items)

        self.fit_to_tree()

        self.up_btn.setVisible(False)
        self.down_btn.setVisible(False)

        self.hide_tree_btn.setPos(self.w - self.hide_tree_btn.w, 0)
        self.hide_tree_btn.setVisible(True)
        self.visualize = True

    def place_tree_item(self, tree_item, x, y, processed_items):
        item = self.items[tree_item[0]]
        item.setVisible(True)
        item.setPos(x, y)
        processed_items.append(tree_item[1])
        if tree_item[2] not in processed_items:
            new_x = x + self.sp_x
            if tree_item[3] not in processed_items and \
                    tree_item[3] != 0 and \
                    len(list(filter(lambda i:
                                    tree_item[3] == i[2], self.tree_data))) == 0:
                new_x += item.w + self.sp

            new_item = list(filter(lambda i:
                                   i[1] == tree_item[2], self.tree_data))[0]
            self.place_tree_item(
                new_item,
                new_x,
                y + item.h + self.sp_y,
                processed_items)
            self.place_line_item(
                [x + 0.5 * item.w, y + item.h],
                [self.items[new_item[0]].x() + 0.5 * item.w, self.items[new_item[0]].y()],
                True
            )
        if tree_item[3] not in processed_items and tree_item[3] != 0:
            new_item = list(filter(lambda i:
                                   i[1] == tree_item[3], self.tree_data))[0]
            self.place_tree_item(
                new_item,
                x - item.w - self.sp,
                y + item.h + self.sp_y,
                processed_items)
            self.place_line_item(
                [x + 0.5 * item.w, y + item.h],
                [self.items[new_item[0]].x() + 0.5 * item.w, self.items[new_item[0]].y()],
                False
            )

    def place_line_item(self, start_point, end_point, success):

        line = LineItem(self.scene(), 0, 0, start_point, end_point,
                        color=QtCore.Qt.green if success else QtCore.Qt.red, parent=self)
        self.lines.append(line)
        line.setVisible(True)
        if start_point[0] < end_point[0]:
            line.setPos(start_point[0], start_point[1])
        else:
            line.setPos(end_point[0], start_point[1])

    def hide_tree_btn_cb(self, btn):

        self.hide_tree_btn.setVisible(False)
        self.visualize = False

        for i in range(0, len(self.lines)):
            self.scene().removeItem(self.lines[i])

        if self.visualization_finished_cb is not None:
            self.visualization_finished_cb()

    def fit_to_tree(self):

        y = self.hide_tree_btn.h + self.sp
        min_x = min(self.items, key=lambda i: i.x()).x()
        max_item = max(self.items, key=lambda i: i.x())
        max_x = max_item.x() + max_item.w
        if min_x < 0:
            for i in range(0, len(self.items)):
                self.items[i].setPos(self.items[i].x() + abs(min_x), self.items[i].y())
            for i in range(0, len(self.lines)):
                self.lines[i].setPos(self.lines[i].x() + abs(min_x), self.lines[i].y())
        else:
            for i in range(0, len(self.items)):
                self.items[i].setPos(self.items[i].x() + self.sp, self.items[i].y())
            for i in range(0, len(self.lines)):
                self.lines[i].setPos(self.lines[i].x() + self.sp, self.lines[i].y())
        self.w = max_x - min_x + 2 * self.sp
        min_y = min(self.items, key=lambda i: i.y()).y()
        max_item = max(self.items, key=lambda i: i.y())
        max_y = max_item.y() + max_item.h
        self.h = max_y - min_y + y + 2 * self.sp

    def paint(self, painter, option, widget):

        if not self.scene() or not self.visualize:
            return

        painter.setClipRect(option.exposedRect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        pen = QtGui.QPen()
        pen.setStyle(QtCore.Qt.NoPen)
        painter.setPen(pen)

        painter.setBrush(QtCore.Qt.gray)
        painter.setOpacity(0.5)
        painter.drawRoundedRect(QtCore.QRect(0, 0, self.w, self.h), 5.0, 5.0)

        pen.setStyle(QtCore.Qt.SolidLine)
        painter.setOpacity(1)
