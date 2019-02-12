from art_instructions.brain import BrainFSM, BrainInstruction
from transitions import State
import rospy
from art_brain import ArtBrainErrors, ArtBrainErrorSeverities, ArtBrainUtils
from geometry_msgs.msg import Pose


class PickFromPolygon(BrainInstruction):
    pass


class PickFromPolygonLearn(PickFromPolygon):
    pass


class PickFromPolygonRun(PickFromPolygon):
    pass


class PickFromPolygonFSM(BrainFSM):
    states = [
        State(name='pick_from_polygon', on_enter=[
            'state_update_program_item', 'check_robot_in', 'state_pick_from_polygon'],
            on_exit=['check_robot_out']),
        State(name='learning_pick_from_polygon', on_enter=[
            'learning_load_block_id', 'state_learning_pick_from_polygon'], on_exit=[]),
        State(name='learning_pick_from_polygon_run', on_enter=[
            'check_robot_in', 'learning_load_block_id', 'state_learning_pick_from_polygon_run'],
            on_exit=['check_robot_out']),
        State(name='learning_pick_from_polygon_activated', on_enter=[
            'check_robot_in', 'learning_load_block_id', 'state_learning_pick_from_polygon_activated'],
            on_exit=['check_robot_out']),
    ]

    transitions = [
        ('pick_from_polygon', 'program_run', 'pick_from_polygon'),
        ('done', 'pick_from_polygon', 'program_load_instruction'),
        ('error', 'pick_from_polygon', 'program_error'),
        ('pick_from_polygon', 'learning_run', 'learning_pick_from_polygon'),
        ('done', 'learning_pick_from_polygon', 'learning_step_done'),
        ('error', 'learning_pick_from_polygon', 'learning_step_error'),
        ('pick_from_polygon_run', 'learning_run', 'learning_pick_from_polygon_run'),
        ('done', 'learning_pick_from_polygon_run', 'learning_run'),
        ('error', 'learning_pick_from_polygon_run', 'learning_step_error'),
        ('pick_from_polygon_activated', 'learning_run', 'learning_pick_from_polygon_activated'),
        ('done', 'learning_pick_from_polygon_activated', 'learning_run'),
        ('error', 'learning_pick_from_polygon_activated', 'learning_step_error')
    ]

    state_functions = [
        'state_pick_from_polygon',
        'state_learning_pick_from_polygon',
        'state_learning_pick_from_polygon_run',
        'state_learning_pick_from_polygon_activated'
    ]

    def run(self, **kwargs):
        self.fsm.pick_from_polygon()

    def learning(self, **kwargs):
        self.fsm.pick_from_polygon()

    def learning_run(self, **kwargs):
        self.fsm.pick_from_polygon_run()

    def learning_activated(self, **kwargs):
        self.fsm.pick_from_polygon_activated()

    def state_pick_from_polygon(self, event):
        rospy.logdebug('Current state: state_pick_from_polygon')

        if not self.brain.check_robot():
            return
        self.pick_object_from_polygon(self.brain.instruction)

    def state_learning_pick_from_polygon(self, event):
        rospy.logdebug('Current state: state_learning_pick_from_polygon')
        # i have nothing to do yet

    def state_learning_pick_from_polygon_run(self, event):
        rospy.logdebug('Current state: state_learning_pick_from_polygon_run')
        instruction = self.brain.state_manager.state.program_current_item  # type: ProgramItem
        self.pick_object_from_polygon(instruction, update_state_manager=False)

    def state_learning_pick_from_polygon_activated(self, event):
        rospy.logdebug('Current state: state_learning_pick_from_polygon_activated')
        instruction = self.brain.state_manager.state.program_current_item
        if self.brain.robot.rh.look_at_enabled() and self.brain.ph.is_polygon_set(self.brain.block_id, instruction.id):

            polygon_centroid = self.brain.ph.get_polygon_centroid(self.brain.block_id, instruction.id)

            self.brain.robot.look_at_point(polygon_centroid.pose.position,
                                           polygon_centroid.header.frame_id if polygon_centroid.header.frame_id
                                           else "marker")

        self.fsm.done()

    def pick_object_from_polygon(self, instruction, update_state_manager=True):

        obj_type = self.brain.ph.get_object(self.brain.block_id, instruction.id)[0][0]
        polygon = self.brain.ph.get_polygon(self.brain.block_id, instruction.id)[0][0]

        obj = ArtBrainUtils.get_pick_obj_from_polygon(
            obj_type, polygon, self.brain.objects)
        if obj is None or obj.object_id is None or obj.object_id == "":
            self.fsm.error(severity=ArtBrainErrorSeverities.WARNING,
                           error=ArtBrainErrors.ERROR_OBJECT_MISSING_IN_POLYGON)
            if update_state_manager:
                self.brain.state_manager.update_program_item(
                    self.brain.ph.get_program_id(), self.brain.block_id, instruction)
            return
        if update_state_manager:
            self.brain.state_manager.update_program_item(
                self.brain.ph.get_program_id(), self.brain.block_id, instruction, {
                    "SELECTED_OBJECT_ID": obj.object_id})
        arm_id = self.brain.robot.select_arm_for_pick(
            obj, self.brain.objects.header.frame_id, self.brain.tf_listener)
        severity, error, arm_id = self.brain.robot.pick_object(
            obj, instruction.id, arm_id)
        if error is not None:
            if error is not ArtBrainErrors.ERROR_ROBOT_HALTED:
                self.brain.try_robot_arms_get_ready([arm_id])
            else:
                self.fsm.error(severity=severity, error=error, halted=True)
                return
            self.fsm.error(severity=severity, error=error)

        else:
            self.fsm.done(success=True)
