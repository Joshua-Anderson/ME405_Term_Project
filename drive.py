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

class StraightDistance:
    def __init__(self, dist_inches, fix_overshoot=False):
        self._dist_ticks = encoder.in_to_ticks(dist_inches)
        self._fix_overshoot = fix_overshoot
        self._distance_remaining_ticks = self._dist_ticks
        self._cntrl = controller.PControl(0.1, self._dist_ticks)

    def step(self, left_enc, right_enc):
        """ Calculate motor speeds to execute movement """
        left_speed = right_speed = 0

        if self._fix_overshoot == True or left_enc.ticks < self._dist_ticks:
            left_speed = self._cntrl.ploop(left_enc.ticks)

        if self._fix_overshoot == True or right_enc.ticks < self._dist_ticks:
            right_speed = self._cntrl.ploop(right_enc.ticks)

        return left_speed, right_speed

    def dist_remaining_in(self, left_enc, right_enc):
        """ Get distance remaining of movement in inches """
        left_dist = encoder.ticks_to_in(self._dist_ticks - left_enc.ticks)
        right_dist = encoder.ticks_to_in(self._dist_ticks - right_enc.ticks)
        return left_dist, right_dist

    def complete(self):
        """ Checks if movement is complete """
        return encoder.LeftVal >= self._dist_ticks and encoder.RightVal >= self._dist_ticks

class StraightVelocity:
    def __init__(self, vel_in_ms):
        self._vel_ticks_ms = encoder.in_to_ticks(vel_in_ms)
        self._cntrl_left = controller.PIcontrol(12.0, 0.05, self._vel_ticks_ms)
        self._cntrl_right = controller.PIcontrol(12.0, 0.05, self._vel_ticks_ms)

    def step(self, left_enc, right_enc):
        """ Calculate motor speeds to execute movement """

        left_speed = self._cntrl_left.piloop(left_enc.vel_ticks_ms, left_enc.dt)
        right_speed = self._cntrl_right.piloop(right_enc.vel_ticks_ms, right_enc.dt)
        return left_speed, right_speed

class TurnAngle:
    """ Turn the SUMO bot a given angle clockwise.

    To spin in place, we run a p-controller on one wheel and mirror the speed on the other wheel """

    def __init__(self, degrees, fix_overshoot=False):
        self._dist_ticks = encoder.deg_to_ticks(degrees)
        self._fix_overshoot = fix_overshoot
        self._distance_remaining_ticks = self._dist_ticks
        self._cntrl = controller.PControl(0.25, self._dist_ticks)
        self.cw = degrees >= 0

    def step(self, left_enc, right_enc):
        """ Calculate motor speeds to execute movement """
        speed = 0

        if self._fix_overshoot == True or not self.complete(left_enc):
            speed = self._cntrl.ploop(left_enc.ticks)

        return speed, -speed

    def dist_remaining_deg(self, left_enc, right_enc):
        """ Get distance remaining of movement in inches """
        return encoder.ticks_to_deg(self._dist_ticks - left_enc.ticks)

    def complete(self, enc):
        """ Checks if movement is complete """
        if self.cw:
            print("[DRIVE]", enc.ticks, ">=", self._dist_ticks)
            return enc.ticks >= self._dist_ticks
        else:
            return enc.ticks <= self._dist_ticks

def change_command(cmd):
    global DriveCommand

    motor_driver.Left.set_duty_cycle(0)
    motor_driver.Right.set_duty_cycle(0)
    DriveCommand = cmd

def handler():
    global DriveCommand

    while True:
        yield(0)
        left_enc, right_enc = encoder.read()

        # Stop the motors if there is no currently active command
        if DriveCommand is None:
            # print("[DRIVE] No command, stopping motors")
            motor_driver.Left.set_duty_cycle(0)
            motor_driver.Right.set_duty_cycle(0)
            continue

        left_speed, right_speed = DriveCommand.step(left_enc, right_enc)
        # print("[DRIVE]", DriveCommand.dist_remaining_in(), "inches remaining")
        # print("[DRIVE]", left_speed, " Left Motor", left_enc.vel_ticks_ms, "Left Vel", DriveCommand._vel_ticks_ms, "Vel Target")
        # print("[DRIVE]", right_speed, " Right Motor", right_enc.vel_ticks_ms, "Right Vel", DriveCommand._vel_ticks_ms, "Vel Target")
        motor_driver.Left.set_duty_cycle(left_speed)
        motor_driver.Right.set_duty_cycle(right_speed)
