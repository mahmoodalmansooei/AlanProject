import nengo
import numpy as np
import robot_control.action

robot_control.action = reload(robot_control.action)

model = nengo.Network(label="NetworkName")

testing_lip_position = np.asarray(np.linspace(1, 0, 3))
testing_hand_position = np.asarray(np.linspace(0, -1, 3))
with model:
    actions = nengo.Node(output=lambda t: [1, 0])
    lip_enable = nengo.Node(output=lambda t: [0])
    lip_position = nengo.Node(testing_lip_position.ravel())
    hand_position = nengo.Node(testing_hand_position.ravel())

    selection = robot_control.action.ActionSelectionExecution(2)

    nengo.Connection(actions, selection.actions.input)
    nengo.Connection(lip_enable, selection.lip_enable)
    nengo.Connection(lip_position, selection.lip_position)
    nengo.Connection(hand_position, selection.hand_position)
