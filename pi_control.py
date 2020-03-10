# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 13:29:02 2020

@author: ethan
"""
DUTY_MAX = 100
CLAMP = 0.25

class PIcontrol:
    """
    This class implements a simple PI cruise control shceme for the ME 405 Nucleo dev board
    Contains methods to change Kp, Ki, and the target speed. 
    """

    def __init__(self,kp,ki,vel):
        """
        Sets up PI controller
        """
        
        self._kp = kp
        self._ki = ki
        self._vel = vel
        self.i_err = vel
        

    def pi_loop(self,v_act,dt):
        """
        Cruise Control Loop with duty cycle saturation. Returns the total saturated 
        actuator command
        """
        # Compute actual velocity and Error
        v_err = self._vel - v_act
        # Proportional Command
        p_cmd = self._kp * v_err
        # Integral Command
        self.i_err += v_err
        i_cmd = self._ki * self.i_err * dt
        if i_cmd > DUTY_MAX or i_cmd < -DUTY_MAX:
            i_cmd *= CLAMP
        # Total Actuator Command and Saturation
        act_cmd = p_cmd + i_cmd
        if act_cmd > DUTY_MAX:
            act_cmd = DUTY_MAX
        elif act_cmd < -DUTY_MAX:
            act_cmd = -DUTY_MAX
        return act_cmd

    def set_kp(self,proportional_gain):
        """ Allows the user to change the proportional gain."""
        if proportional_gain < 0:
            proportional_gain = 0

        self._kp = proportional_gain

    def set_ki(self,integral_gain):
        """ Allows the user to change the proportional gain."""
        if integral_gain < 0:
            integral_gain = 0

        self._ki = integral_gain

    def set_vel(self,crusing_speed):
        """ Allows the user to change the proportional gain."""
        self._kp = proportional_gain
