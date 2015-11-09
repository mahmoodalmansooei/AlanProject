import nengo
import numpy as np
import robot_control.action

robot_control.action = reload(robot_control.action)

model = nengo.Network(label="NetworkName")

testing_lip_position = np.asarray([.2, .2, 0])
testing_left_hand_position = np.asarray([-.3, .5, -.7])
testing_right_hand_position = np.asarray([.3, .5, -.7])
with model:
    actions = nengo.Node(output=lambda t: [1, 0, 1])
    lip_enable = nengo.Node(output=lambda t: [0, 0])
    lip_position = nengo.Node(testing_lip_position.ravel())
    left_hand_position = nengo.Node(testing_left_hand_position.ravel())
    right_hand_position = nengo.Node(testing_right_hand_position.ravel())
    killswitch = nengo.Node(output=0)

    selection = robot_control.action.ActionSelectionExecution()

    nengo.Connection(actions, selection.actions.input)
    nengo.Connection(lip_enable, selection.lip_enable)
    nengo.Connection(lip_position, selection.lip_position)
    nengo.Connection(left_hand_position, selection.left_arm_target_position)
    nengo.Connection(right_hand_position, selection.right_arm_target_position)
    nengo.Connection(killswitch, selection.killswitch)
