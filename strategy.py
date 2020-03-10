# -*- coding: utf-8 -*-

##
# @file strategy.py
# @author Josh Anderson
# @author Ethan Czuppa

import utime
import line_sensor
import drive
import encoder
import tof

Strategy = None

class SensorState:
    def __init__(self, line_sens, l_enc, r_enc, enemy_vec, time_ms, dt_ms):
        self.line_sens = line_sens
        self.time_ms = time_ms
        self.dt_ms = dt_ms
        self.l_enc = l_enc
        self.r_enc = r_enc
        self.enemy_vec = enemy_vec

def handler():
    last_state = SensorState([0,0,0,0], None, None, None, utime.ticks_ms, 0)
    last_lsens = [None, None, None, None]


    last_l_enc, last_r_enc = encoder.read()

    while True:
        yield(0)
        tof_ang = tof.read()
        now = utime.ticks_ms()

        l_enc, r_enc = encoder.read(last_l_state=last_l_enc, last_r_state=last_r_enc)
        last_l_enc = l_enc
        last_r_enc = r_enc

        state = SensorState([0,0,0,0], l_enc, r_enc, tof.ang_to_vec(tof_ang), 0, 0)

        if line_sensor.FrontLeft.read():
            if last_lsens[0] is None:
                last_lsens[0] = encoder.ticks_to_in(l_enc.ticks)
            state.line_sens[0] = abs(encoder.ticks_to_in(l_enc.ticks) - last_lsens[0])
        else:
            last_lsens[0] = None

        if line_sensor.FrontRight.read():
            if last_lsens[1] is None:
                last_lsens[1] = encoder.ticks_to_in(l_enc.ticks)
            state.line_sens[1] = abs(encoder.ticks_to_in(l_enc.ticks) - last_lsens[1])
        else:
            last_lsens[1] = None

        now = utime.ticks_ms()
        state.time_ms = now
        state.dt_ms = utime.ticks_diff(now, last_state.time_ms)

        # If the strategy state returns true, reset robot state
        if Strategy.step(state):
            encoder.reset()
            last_lsens = [None, None, None, None]



class BasicStrategy:
    def __init__(self):
        self.current_state = self.drive_forward_init

    def drive_forward_init(self, sens_state):
        drive.change_command(drive.StraightVelocity(0.018))
        self.current_state = self.drive_forward
        return True

    def drive_forward(self, sens_state):
        drive.DriveCommand.seek(sens_state.enemy_vec)
        if sens_state.line_sens[0] < 1.5 and sens_state.line_sens[1] < 1.5:
            return False
        drive.change_command(drive.StraightVelocity(-0.018))
        self.current_state = self.drive_backwards
        return True


    def drive_backwards(self, sens_state):
        #print("[BACK]", encoder.ticks_to_in(sens_state.l_enc.ticks))
        if encoder.ticks_to_in(sens_state.l_enc.ticks) > -6:
            return False
        drive.change_command(drive.TurnAngle(75))
        self.current_state = self.turn_around
        return True


    def turn_around(self, sens_state):
        if not drive.DriveCommand.complete(sens_state.l_enc):
            return False
        self.current_state = self.drive_forward_init
        return False

    def step(self, sens_state):
        return self.current_state(sens_state)




