#!/usr/bin/env python

import rospy
from PyQt4 import QtGui, QtCore
from item import Item
import rospkg


class LineItem(Item):

    def __init__(self, scene, x, y,
                 start_point, end_point,
                 color=QtCore.Qt.green,
                 parent=None):

        self.w = abs(end_point[0] - start_point[0])
        self.h = abs(end_point[1] - start_point[1])

        super(LineItem, self).__init__(scene, x, y, parent=parent)

        self.start_point = start_point
        self.end_point = end_point

        self.color = color

        self.setZValue(10000)

    def boundingRect(self):

        return QtCore.QRectF(0, 0, abs(self.w), abs(self.h))

    def paint(self, painter, option, widget):

        painter.setClipRect(option.exposedRect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        pen = QtGui.QPen()
        pen.setColor(self.color)
        pen.setStyle(QtCore.Qt.SolidLine)
        pen.setWidth(8)
        painter.setPen(pen)

        start = [0, 0]
        end = [self.w, self.h]
        if self.end_point[0] < self.start_point[0]:
            start = [0, self.h]
            end = [self.w, 0]
        painter.drawLine(
            QtCore.QPointF(start[0], start[1]),
            QtCore.QPointF(end[0], end[1])
        )
