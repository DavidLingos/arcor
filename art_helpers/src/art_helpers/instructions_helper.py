#!/usr/bin/env python

import rospy
import importlib
from art_utils.art_msgs_functions import obj_type, wait_item, feeder_item, grid_item, drill_item, place_item,\
    item, polygon_item, visual_inspection_item


class InstructionsHelperException(Exception):
    pass


class BaseInstruction(object):

    def __init__(self):

        self.params = {}


class GuiInstruction(BaseInstruction):

    def __init__(self):

        super(GuiInstruction, self).__init__()
        self.learn = None
        self.run = None
        self.vis = None

    @property
    def mandatory(self):

        return "learn", "run"


class BrainInstruction(BaseInstruction):

    def __init__(self):

        super(BrainInstruction, self).__init__()
        self.fsm = None

    @property
    def mandatory(self):

        return "fsm",


class Instruction(object):

    def __init__(self):

        self.gui = GuiInstruction()
        self.brain = BrainInstruction()


class InstructionsProperties(object):

    def __init__(self):

        self.using_object = frozenset()
        self.using_pose = frozenset()
        self.using_polygon = frozenset()
        self.pick = frozenset()
        self.place = frozenset()
        self.ref_to_pick = frozenset()
        self.runnable_during_learning = frozenset()


class InstructionsHelper(object):

    def __init__(self):

        self.packages = frozenset()
        self._instructions = {}
        self.properties = InstructionsProperties()

        self._load()

    def __getitem__(self, key):

        try:
            return self._instructions[key]
        except KeyError:
            raise InstructionsHelperException("Unknown instruction")

    def _load(self):

        while not rospy.is_shutdown():
            try:
                instructions = rospy.get_param("/art/instructions")
                break
            except KeyError:
                rospy.loginfo("Waiting for /art/instructions param...")
                rospy.sleep(1.0)

        if rospy.is_shutdown():
            raise InstructionsHelperException("Shutdown.")

        packages = set()

        try:

            for k, v in instructions["instructions"].iteritems():
                packages.add(v["gui"]["package"])

        except KeyError as e:

            rospy.logerr(str(e))
            raise InstructionsHelperException("Missing key - invalid configuration.")

        self.packages = frozenset(packages)

        for k, ins_conf in instructions["instructions"].iteritems():

            ins = Instruction()

            for art_module, value in ins.__dict__.iteritems():

                self._import_instruction(k, ins_conf, ins.__dict__[art_module], art_module)

            self._instructions[k] = ins

        for prop in self.properties.__dict__.keys():

            try:
                conf_prop = instructions[prop]
            except KeyError:
                rospy.logwarn("Property " + prop + " not defined.")
                continue

            ins_ok = []
            for ins in conf_prop:

                if ins not in self.known_instructions():
                    rospy.logwarn("Property " + prop + " contains unknown instruction: " + ins)
                    continue

                ins_ok.append(ins)

            self.properties.__dict__[prop] = frozenset(ins_ok)

    @staticmethod
    def _import_instruction(ins_name, ins_conf, ins_cls, art_module):

        try:
            pkg = ins_conf[art_module]["package"]
        except KeyError:
            raise InstructionsHelperException("Package not defined for: " + ins_name)

        try:
            mod = importlib.import_module(pkg + "." + art_module)
        except Exception as e:
            rospy.logerr(str(e))
            raise InstructionsHelperException("Could not import module: " + pkg + "." + art_module)

        for t, v in ins_cls.__dict__.iteritems():  # learn/run/vis/fsm

            if v is not None:
                continue

            try:
                cls = ins_conf[art_module][t]
            except KeyError as e:

                if t in ins_cls.mandatory:
                    rospy.logerr(str(e))
                    raise InstructionsHelperException("Invalid instruction, key " + t + " is mandatory!")

                continue

            try:
                ins_cls.__dict__[t] = getattr(mod, cls)
            except AttributeError as e:

                rospy.logerr(str(e))
                raise InstructionsHelperException("Invalid instruction, class " + cls + " does not exist.")

        try:
            ins_cls.params = ins_conf[art_module]["params"]
        except KeyError:
            pass

    def known_instructions(self):

        return self._instructions.keys()

    def requires_learning(self, ins):

        return ins in self.properties.using_object | self.properties.using_polygon | self.properties.using_pose

    @staticmethod
    def get_instruction_msgs(item_type, it_id,
                             on_success=0, on_failure=0, obj_type="", ref_id=[],
                             name="", objects=2, holes=2):

        if item_type == "PickFromPolygon":
            return polygon_item(it_id, on_success, on_failure, obj_type, ref_id)
        elif item_type == "PickFromFeeder":
            return feeder_item(it_id, on_success, on_failure, obj_type, ref_id)
        elif item_type == "VisualInspection":
            return visual_inspection_item(it_id, ref_id, on_success, on_failure)
        elif item_type == "PlaceToPose":
            return place_item(it_id, ref_id, on_success, on_failure, name)
        elif item_type == "PlaceToGrid":
            return grid_item(it_id, ref_id, on_success, on_failure, objects)
        elif item_type == "DrillPoints":
            return drill_item(it_id, ref_id, on_success, on_failure, holes, obj_type)
        elif item_type == "WaitUntilUserFinishes":
            return wait_item(it_id, ref_id, on_success, on_failure)
        else:
            return item(it_id, item_type, on_success, on_failure, ref_id)
