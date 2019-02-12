from art_instructions.brain import BrainFSM, BrainInstruction
from transitions import State
import rospy
from art_msgs.msg import UserActivity


class WaitUntilUserFinishes(BrainInstruction):
    pass


class WaitUntilUserFinishesLearn(WaitUntilUserFinishes):
    pass


class WaitUntilUserFinishesRun(WaitUntilUserFinishes):
    pass


class WaitUntilUserFinishesFSM(BrainFSM):
    states = [
        State(name='wait_until_user_finishes', on_enter=[
            'state_update_program_item', 'check_robot_in', 'state_wait_until_user_finishes'],
            on_exit=['check_robot_out']),
    ]

    transitions = [
        ('wait_until_user_finishes', 'program_run', 'wait_until_user_finishes'),
        ('done', 'wait_until_user_finishes', 'program_load_instruction'),
        ('error', 'wait_until_user_finishes', 'program_error'),
    ]

    state_functions = [
        'state_wait_until_user_finishes'
    ]

    def run(self, **kwargs):
        self.fsm.wait_until_user_finishes()

    def state_wait_until_user_finishes(self, event):
        rospy.logdebug('Current state: state_wait_until_user_finishes')

        self.brain.state_manager.update_program_item(
            self.brain.ph.get_program_id(), self.brain.block_id, self.brain.instruction)

        rate = rospy.Rate(10)

        while self.brain.user_activity != UserActivity.WORKING and self.brain.executing_program \
                and not rospy.is_shutdown():
            rate.sleep()

        self.fsm.done(success=True)
