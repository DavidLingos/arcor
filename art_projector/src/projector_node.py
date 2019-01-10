#!/usr/bin/env python

import sys
import signal
import rospy
from PyQt4 import QtGui, QtCore
from art_projector import Projector

proj = None


def sigint_handler(*args):

    global proj

    """Handler for the SIGINT signal."""
    sys.stderr.write('\r')
    proj.kill_now = True
    proj.close()
    QtGui.QApplication.quit()


def main(args):

    global proj

    rospy.init_node('projected_gui_projector', anonymous=True)
    rospy.sleep(1)

    signal.signal(signal.SIGINT, sigint_handler)

    app = QtGui.QApplication(sys.argv)

    proj = Projector()
    proj.connect()

    timer = QtCore.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)  # Let the interpreter run each 500 ms.

    if proj.kill_now:
        return

    sys.exit(app.exec_())


if __name__ == '__main__':
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        print("Shutting down")
