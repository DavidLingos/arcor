#!/usr/bin/env python

import rospkg
import rospy
from PyQt4 import QtGui, QtCore
from item import Item
from list_item import ListItem
from button_item import ButtonItem
from art_projected_gui.helpers.items import group_enable, group_visible

rospack = rospkg.RosPack()
icons_path = rospack.get_path('art_projected_gui') + '/icons/'
translate = QtCore.QCoreApplication.translate


class SelectInstructionItem(Item):

    def __init__(self,
                 scene,
                 x,
                 y,
                 program_helper,
                 block_id=None,
                 item_id=None,
                 obj=None,
                 instruction_selected_cb=None):

        self.obj = obj
        self.ph = program_helper
        self.selected_instruction_id = None
        self.instruction_selected_cb = instruction_selected_cb

        super(SelectInstructionItem, self).__init__(
            scene,
            x,
            y,
            parent=obj if isinstance(obj, Item) else None)

        self.w = self.m2pix(0.2)
        self.h = self.m2pix(0.25)
        self.sp = self.m2pix(0.005)

        self.instruction_list = None
        self.new_item_map = None
        self.instruction_confirm_btn = ButtonItem(self.scene(), 0, 0, "BTN", self, self.selection_done_cb,
                                                  image_path=icons_path + "plus.svg")

        self.instruction_back_btn = ButtonItem(self.scene(), 0, 0, "BTN", self, self.selection_done_cb,
                                               image_path=icons_path + "back.svg")

        self.instruction_confirm_btn.set_enabled(False)
        group_visible((self.instruction_confirm_btn, self.instruction_back_btn), False)
        self.setVisible(False)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setZValue(1000)
        self.update()

        if obj is not None:
            self.instruction_btns = []
            for i in self.ph.get_object_instructions(
                block_id,
                object_type=None if isinstance(obj, QtGui.QGraphicsView) else obj.object_type,
                    previous_item_id=item_id):

                btn = ButtonItem(self.scene(), 0, 0, "BTN", self, self.btn_instruction_cb,
                                 id=i,
                                 image_path=icons_path + i.lower() + ".svg")
                self.instruction_btns.append(btn)

            total_width = 0

            for it in self.instruction_btns:
                total_width += it._width() + self.sp

            self.w = total_width

            self._place_childs_horizontally(
                0,
                self.sp, self.instruction_btns)

            group_enable(self.instruction_btns, True)
            self.setVisible(True)

        else:
            idata = []

            self.new_item_map = self.ph.get_allowed_new_items(block_id, item_id)

            for i in range(len(self.new_item_map)):
                idata.append(translate("ProgramItem", "Instruction %1\n").arg(self.new_item_map[i]))

            self.instruction_list = ListItem(self.scene(), 0, 0, 0.2 - 2 * 0.005, idata,
                                             self.item_selected_cb, parent=self)
            self.instruction_list.setPos(self.sp, y)
            y += self.instruction_list._height() + self.sp

            self._place_childs_horizontally(y, self.sp, [
                self.instruction_back_btn, self.instruction_confirm_btn
            ])

            group_visible((self.instruction_confirm_btn, self.instruction_back_btn), True)
            self.instruction_back_btn.set_enabled(True)
            self.setVisible(True)

    def item_selected_cb(self):

        if self.instruction_list.selected_item_idx is not None:

            self.selected_instruction_id = self.new_item_map[self.instruction_list.selected_item_idx]
            self.instruction_confirm_btn.set_enabled(True)

        else:
            self.instruction_confirm_btn.set_enabled(False)
            self.selected_instruction_id = None

        return

    def btn_instruction_cb(self, btn):

        self.selected_instruction_id = btn.id

        self.selection_done_cb(btn)

    def selection_done_cb(self, btn):

        if btn == self.instruction_back_btn:
            self.selected_instruction_id = None

        if self.instruction_selected_cb is not None:
            self.instruction_selected_cb()

    def boundingRect(self):

        return QtCore.QRectF(0, 0, self.w, self.h)

    def paint(self, painter, option, widget):

        if not self.scene() or self.obj is not None:
            return

        painter.setClipRect(option.exposedRect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        pen = QtGui.QPen()
        pen.setStyle(QtCore.Qt.NoPen)
        painter.setPen(pen)

        painter.setBrush(QtCore.Qt.gray)
        painter.setOpacity(0.5)
        painter.drawRoundedRect(QtCore.QRect(0, 0, self.w, self.h), 5.0, 5.0)
