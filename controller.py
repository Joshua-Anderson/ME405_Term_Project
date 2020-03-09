"""
@file controller.py
@author Josh Anderson
@author Ethan Czuppa

This file implements various control algorithms used by the SUMO bot.
"""


class PControl:
    """ Simple proprtional only closed loop position control.
    Contains methods for the control loop, changing the setpoint, and
    changing the proportional gain Kp.
    """
    def __init__(self,Kp,setpoint):
        """Initializes control loop and sets up gains and constants."""
        self._Kp = Kp
        self._setpoint = setpoint

    def ploop(self,curr_pos):
        """Runs the proportional-only closed loop position control loop."""
        err = self._setpoint - curr_pos
        act_cmd = self._Kp*err
        return act_cmd

    def set_targetpos(self,setpoint):
        """Allows user to change the position setpoint of the motor."""
        self._setpoint = setpoint

    def set_kp(self,Kp):
        """Allows the user to change the Proportional gain of the controller.
            To prevent the system from going unstable negative values of Kp are
            set to zero.
        """
        if Kp < 0:
             Kp = 0
        self._Kp = Kp
