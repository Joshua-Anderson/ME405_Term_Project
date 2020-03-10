# -*- coding: utf-8 -*-

##
# @file drive.py
# @author Josh Anderson
# @author Ethan Czuppa
#
# This file contains high level driving control functionality for the SUMO Bot.

import controller
import encoder
import motor_driver

DriveCommand = None

class ForwardDistance:
    def __init__(self, dist_inches, fix_overshoot=False):
        self._dist_ticks = encoder.in_to_ticks(dist_inches)
        self._fix_overshoot = fix_overshoot
        self._distance_remaining_ticks = self._dist_ticks
        self._cntrl = controller.PControl(0.1, self._dist_ticks)

    def step(self):
        """ Calculate motor speeds to execute movement """
        left_speed = right_speed = 0

        if self._fix_overshoot == True or encoder.LeftVal < self._dist_ticks:
            left_speed = self._cntrl.ploop(encoder.LeftVal)

        if self._fix_overshoot == True or encoder.RightVal < self._dist_ticks:
            right_speed = self._cntrl.ploop(encoder.RightVal)

        return left_speed, right_speed

    def dist_remaining_in(self):
        """ Get distance remaining of movement in inches """
        left_dist = encoder.ticks_to_in(self._dist_ticks - encoder.LeftVal)
        right_dist = encoder.ticks_to_in(self._dist_ticks - encoder.RightVal)
        return left_dist, right_dist

    def complete(self):
        """ Checks if movement is complete """
        return encoder.LeftVal >= self._dist_ticks and encoder.RightVal >= self._dist_ticks

class TurnAngle:
    """ Turn the SUMO bot a given angle clockwise.

    To spin in place, we run a p-controller on one wheel and mirror the speed on the other wheel """

    def __init__(self, degrees, fix_overshoot=False):
        self._dist_ticks = encoder.deg_to_ticks(degrees)
        self._fix_overshoot = fix_overshoot
        self._distance_remaining_ticks = self._dist_ticks
        self._cntrl = controller.PControl(0.1, self._dist_ticks)

    def step(self):
        """ Calculate motor speeds to execute movement """
        speed = 0

        if self._fix_overshoot == True or encoder.LeftVal < self._dist_ticks:
            speed = self._cntrl.ploop(encoder.LeftVal)

        return speed, -speed

    def dist_remaining_deg(self):
        """ Get distance remaining of movement in inches """
        return encoder.ticks_to_deg(self._dist_ticks - encoder.LeftVal)

    def complete(self):
        """ Checks if movement is complete """
        return encoder.LeftVal >= self._dist_ticks

def change_command(cmd):
    global DriveCommand

    motor_driver.Left.set_duty_cycle(0)
    motor_driver.Right.set_duty_cycle(0)

    encoder.Left.zero()
    encoder.LeftVal = 0
    encoder.Right.zero()
    encoder.RightVal = 0

    DriveCommand = cmd

def handler():
    global DriveCommand

    while True:
        yield(0)
        encoder.read()

        # Stop the motors if there is no currently active command
        if DriveCommand is None:
            print("[DRIVE] No command, stopping motors")
            motor_driver.Left.set_duty_cycle(0)
            motor_driver.Right.set_duty_cycle(0)
            continue

        left_speed, right_speed = DriveCommand.step()
        # print("[DRIVE]", DriveCommand.dist_remaining_in(), "inches remaining")
        # print("[DRIVE]", left_speed, " Left Motor", encoder.LeftVal, "Left Encoder")
        # print("[DRIVE]", right_speed, " Right Motor", encoder.RightVal, "Right Encoder")
        motor_driver.Left.set_duty_cycle(left_speed)
        motor_driver.Right.set_duty_cycle(right_speed)
