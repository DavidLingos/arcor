#!/usr/bin/env python

from PyQt4 import QtGui, QtCore
from item import Item
from button_item import ButtonItem
import rospkg
import rospy

translate = QtCore.QCoreApplication.translate

rospack = rospkg.RosPack()
icons_path = rospack.get_path('art_projected_gui') + '/icons/'


class ListItem(Item):

    def __init__(self, scene, x, y, w, data,
                 item_selected_cb=None, item_moved_cb=None,
                 parent=None, movable_items=False,
                 item_mouse_release_cb=None, item_mouse_move_cb=None):

        self.w = 100
        self.h = 100
        self.sp = 0

        self.item_selected_cb = item_selected_cb
        self.item_moved_cb = item_moved_cb

        super(ListItem, self).__init__(scene, x, y, parent=parent)

        self.w = self.m2pix(w)
        self.h = self.m2pix(0.2)
        self.sp = self.m2pix(0.005)

        self.items = []

        self.middle_item_idx = 0
        self.selected_item_idx = None

        for d in data:

            self.items.append(ButtonItem(self.scene(), 0, 0,
                                         d, self, self.item_clicked_cb,
                                         movable=movable_items,
                                         mouse_release_cb=item_mouse_release_cb,
                                         mouse_move_cb=item_mouse_move_cb,
                                         width=w, push_button=True))

        # TODO down_btn is not properly aligned
        self.up_btn = ButtonItem(self.scene(), 0, 0, "", self, self.up_btn_cb, width=w / 2 - 0.005 / 2,
                                 image_path=icons_path + "arrow-up.svg")
        self.down_btn = ButtonItem(self.scene(), 0, 0, "", self, self.down_btn_cb, width=w / 2 - 0.005 / 2,
                                   image_path=icons_path + "arrow-down.svg")

        self.up_btn.setPos(0, self.h - self.down_btn.boundingRect().height())
        self.down_btn.setPos(self.up_btn.boundingRect().width() + self.sp,
                             self.h - self.down_btn.boundingRect().height())

        self.set_current_idx(min(1, len(self.items) - 1))

        self.update()

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

            self.set_current_idx(self.selected_item_idx)

        if self.item_selected_cb is not None:

            self.item_selected_cb()

    def get_current_idx(self):

        return self.middle_item_idx

    def set_current_idx(self, idx, select=False, moving_item=None):

        if select:
            self.selected_item_idx = idx

        self.middle_item_idx = max(idx, min(1, len(self.items) - 1))

        for it in self.items:

            it.setVisible(False)

            if select:
                it.set_pressed(False)

        displayed = [self.middle_item_idx]

        if self.middle_item_idx != -1:

            # selected item is always vertically centered
            self.items[self.middle_item_idx].setPos(
                0, (self.h - self.items[self.middle_item_idx].boundingRect().height()) / 2)
            self.items[self.middle_item_idx].setVisible(True)

            if select:
                self.items[self.selected_item_idx].set_pressed(True)

            # how much vert. space is used
            vspace = self.items[self.middle_item_idx].boundingRect().height()

            # fill space above middle item
            for idx in range(self.middle_item_idx - 1, -1, -1):

                h = self.items[idx].boundingRect().height()
                y = self.items[idx + 1].y() - self.sp - h

                if y < 0:
                    break

                self.items[idx].setPos(0, y)
                self.items[idx].setVisible(True)
                displayed.append(idx)
                vspace += self.sp + h
                displayed.append(idx)

            # fill space below middle item
            for idx in range(self.middle_item_idx + 1, len(self.items)):

                h = self.items[idx].boundingRect().height()
                y = self.items[idx - 1].y() + self.items[idx
                                                         - 1].boundingRect().height() + self.sp

                if y + h > self.down_btn.y():
                    break

                self.items[idx].setPos(0, y)
                self.items[idx].setVisible(True)
                vspace += self.sp + h
                displayed.append(idx)

        if self.isEnabled():

            if None not in (self.item_moved_cb, self.selected_item_idx):

                self.up_btn.set_enabled(self.selected_item_idx > 0)
                self.down_btn.set_enabled(self.selected_item_idx < len(self.items) - 1)

            else:
                self.up_btn.set_enabled(min(displayed) > 0)
                self.down_btn.set_enabled(max(displayed) < len(self.items) - 1)

    """
        This function has been edited during work on bachelors thesis Visual Programming of Robotics Tasks
        Author: David Ling, xlingd00
        Year: 2019
    """

    def up_btn_cb(self, btn):

        if self.middle_item_idx > 0:
            self.set_current_idx(self.middle_item_idx - 1)

        if self.item_moved_cb is not None:
            self.item_moved_cb(up=True)

    """
        This function has been edited during work on bachelors thesis Visual Programming of Robotics Tasks
        Author: David Ling, xlingd00
        Year: 2019
    """

    def down_btn_cb(self, btn):

        if self.middle_item_idx < len(self.items) - 1:
            self.set_current_idx(self.middle_item_idx + 1)

        if self.item_moved_cb is not None:
            self.item_moved_cb(up=False)

    def boundingRect(self):

        return QtCore.QRectF(0, 0, self.w, self.h)

    def paint(self, painter, option, widget):

        pass
