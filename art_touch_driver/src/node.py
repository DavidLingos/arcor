#!/usr/bin/env python

import rospy
import numpy as np

import pycopia.OS.Linux.Input as input

from geometry_msgs.msg import PointStamped
from art_msgs.msg import Touch
from art_msgs.srv import TouchCalibrationPoints, TouchCalibrationPointsRequest
from std_srvs.srv import Empty as EmptySrv, EmptyResponse
from std_msgs.msg import Bool, Empty
from copy import deepcopy
import cv2
import ast


class Slot:

    def __init__(self, slot_id=None, track_id=None):
        if slot_id is None:
            self.slot_id = -1
        else:
            self.slot_id = slot_id

        if track_id is None:
            self.track_id = -1
        else:
            self.track_id = track_id

        self.x = 0
        self.y = 0

    def __eq__(self, other):
        return self.slot_id == other.slot_id


class ArtTouchDriver:

    def __init__(
            self, device_name="USBest Technology SiS HID Touch Controller"):
        self.device_name = device_name
        self.x = 0
        self.y = 0
        self.touch = False
        self.touch_id = -1
        self.device = input.EventDevice()
        self.device.find(name=self.device_name)
        self.target_frame = "marker"  # TODO parameter

        self.slots = []
        self.slot = None
        self.to_delete_id = -1

        # make sure that all messages will be sent
        self.touch_pub = rospy.Publisher("touch", Touch, queue_size=100, tcp_nodelay=True)
        self.calibrated_pub = rospy.Publisher('calibrated', Bool, queue_size=1, latch=True)
        self.calibrating_pub = rospy.Publisher('calibrating', Bool, queue_size=1, latch=True)
        self.touch_det_pub = rospy.Publisher('touch_detected', Empty, queue_size=10)
        self.calibrate_req_srv = rospy.Service("calibrate", EmptySrv, self.calibrate_req_srv_cb)

        self.calib_srv = rospy.ServiceProxy(
            '/art/interface/projected_gui/touch_calibration', TouchCalibrationPoints)

        self.ref_points = []
        self.set_calibrated(False)
        self.set_calibrating(False)

        self.h_matrix = rospy.get_param('calibration_matrix', None)

        if self.h_matrix is not None:
            rospy.loginfo("Loaded calibration from param server")
            self.h_matrix = np.matrix(ast.literal_eval(self.h_matrix))
            self.set_calibrated(True)

    def set_calibrated(self, state):

        self.calibrated = state
        self.calibrated_pub.publish(self.calibrated)

    def set_calibrating(self, state):

        self.calibrating = state
        self.calibrating_pub.publish(self.calibrating)

    def calibrate_req_srv_cb(self, req):

        # TODO wait in __init__??
        rospy.wait_for_service(
            '/art/interface/projected_gui/touch_calibration')

        req = TouchCalibrationPointsRequest()
        ps = PointStamped()
        ps.header.stamp = rospy.Time.now()
        ps.header.frame_id = self.target_frame
        ps.point.z = 0

        # x/y range (min, max)
        x = (rospy.get_param("~calib_x_min"), rospy.get_param("~calib_x_max"))
        y = (rospy.get_param("~calib_y_min"), rospy.get_param("~calib_y_max"))

        xm = (x[0] + x[1]) / 2.0
        ym = (y[0] + y[1]) / 2.0

        pts = [(x[0], y[0]), (xm, y[0]), (x[1], y[0]),
               (x[0], ym), (xm, ym), (x[1], ym),
               (x[0], y[1]), (xm, y[1]), (x[1], y[1])]

        self.ref_points = []

        for i in range(2):
            self.ref_points.extend(pts)

        for pt in self.ref_points:

            ps.point.x = pt[0]
            ps.point.y = pt[1]
            req.points.append(deepcopy(ps))

        try:
            resp = self.calib_srv(req)
        except rospy.ServiceException as e:
            print "Service call failed: %s" % e
            self.set_calibrating(False)
            return EmptyResponse()

        if resp.success:

            self.touch_cnt = 0
            self.calib_points = []
            self.set_calibrating(True)
            rospy.loginfo('Starting calibration')

        else:

            self.set_calibrating(False)
            rospy.logerr('Failed to start calibration')

        return EmptyResponse()

    def get_slot_by_id(self, slot_id):
        for slot in self.slots:
            if slot.slot_id == slot_id:
                return slot
        return None

    def process(self):

        try:
            event = self.device.read()
        except (OSError, TypeError):
            rospy.signal_shutdown("Failed to read data...")
            return

        if event.evtype == 3 and event.code == 47 and event.value >= 0:
            # MT_SLOT
            self.slot = self.get_slot_by_id(event.value)
            if self.slot is None:
                self.slot = Slot(slot_id=event.value, track_id=event.value)
                self.slots.append(self.slot)

        elif event.evtype == 3 and event.code == 57 and event.value >= 0:
            # MT_TRACK_ID start
            if self.slot is None:
                self.slot = Slot(track_id=event.value, slot_id=0)
                self.slots.append(self.slot)
            else:
                self.slot.track_id = event.value

        elif event.evtype == 3 and event.code == 57 and event.value < 0:
            # MT_TRACK_ID end
            if self.slot is not None:
                self.to_delete_id = self.slot.track_id
                self.slots.remove(self.slot)
                self.slot = None

        elif event.evtype == 3 and event.code == 53:
            # x position
            if self.slot:
                self.slot.x = event.value

        elif event.evtype == 3 and event.code == 54:
            # y position
            if self.slot:
                self.slot.y = event.value

        elif event.evtype == 0:

            touch = Touch()
            if self.slot is None:
                touch.id = self.to_delete_id
                touch.touch = False
            else:
                touch.touch = True
                touch.id = self.slot.track_id
                touch.point = PointStamped()
                touch.point.header.stamp = rospy.Time.now()
                touch.point.header.frame_id = self.target_frame

                if self.calibrated:

                    pt = [self.slot.x, self.slot.y, 1]

                    pt = self.h_matrix.dot(
                        np.array(pt, dtype='float64')).tolist()
                    # print pt
                    touch.point.point.x = pt[0][0]
                    touch.point.point.y = pt[0][1]

                if self.calibrating:

                    dist = None

                    if len(self.calib_points) > 0:

                        pp = np.array(self.calib_points[-1])
                        p = np.array((self.slot.x, self.slot.y))

                        # calculate distance from previous touch - in order
                        # to avoid unintended touches
                        dist = np.linalg.norm(pp - p)

                        rospy.logdebug(
                            "Distance from previous touch: " + str(dist))

                    if self.touch_cnt < len(self.ref_points) and (
                            dist is None or dist > 500):

                        self.calib_points.append(
                            (self.slot.x, self.slot.y))
                        self.touch_det_pub.publish()
                        self.touch_cnt += 1

                        if self.touch_cnt == len(self.ref_points):

                            self.calculate_calibration()
                            self.set_calibrating(False)

            if self.calibrated:
                self.touch_pub.publish(touch)

        # wtf?
        # if not self.device._eventq:
        #    break

    def calculate_calibration(self):

        # print self.calib_points
        # print self.ref_points

        h, status = cv2.findHomography(np.array(self.calib_points, dtype='float64'), np.array(
            self.ref_points, dtype='float64'), cv2.LMEDS)

        self.h_matrix = np.matrix(h)

        s = str(self.h_matrix.tolist())
        rospy.set_param("calibration_matrix", s)

        # print self.h_matrix

        self.set_calibrated(True)


if __name__ == '__main__':
    rospy.init_node('art_touch_driver')

    rospy.loginfo('Waiting for other nodes to come up...')

    rospy.loginfo('Ready!')

    try:
        node = ArtTouchDriver()

        while not rospy.is_shutdown():
            node.process()
    except rospy.ROSInterruptException:
        pass
