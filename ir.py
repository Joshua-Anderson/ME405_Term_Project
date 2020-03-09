"""
@file ir.py
@author Josh Anderson
@author Ethan Czuppa

This file contains the logic for handling the interrupts created by an IR remote sensor.
"""


import pyb
import utime
import task_share

IR_TMR_CH = None
IR_TMR_FREQ = 1000000
IR_QUEUE = task_share.Queue('I', 68, overwrite = False)
IR_QUEUE_EMPTY_TIME = 0
IR_START_CMD = 48
IR_STARTED = False

def init():
    global IR_TMR_CH

    ir_tmr = pyb.Timer(2, prescaler=79, period=65535)
    IR_TMR_CH = ir_tmr.channel(3, pyb.Timer.IC, pin=pyb.Pin.board.PA2, polarity = pyb.Timer.BOTH)
    IR_TMR_CH.callback(irq)

def irq(a):
    """Takes data from IR reciever and puts in queue"""
    IR_QUEUE.put(IR_TMR_CH.capture(), in_ISR = True)

def handler():
    """
    Decodes the data stored in queue from IR transmitter and prints out the data
    from the recieved the packet. The address, address complement, command, and
    command complement are all displayed along with the decimal representation of
    the command and address.
    """
    global IR_STARTED

    while True:
        yield(0)
        cur_time = utime.ticks_ms()
        if IR_QUEUE.empty():
            IR_QUEUE_EMPTY_TIME = cur_time
        elif IR_QUEUE.full():
            ir_evt_list = []
            while not IR_QUEUE.empty():
                ir_evt_list.append(IR_QUEUE.get())

            pulses = evt_time_to_pulse_len(ir_evt_list)
            pulses_ms = ticks_to_ms(pulses, IR_TMR_FREQ)
            packet = psls_to_logic_in_dct(pulses_ms)

            if packet is None:
                continue
            elif packet['cmd'] == IR_START_CMD:
                IR_STARTED = True
                print("[IR] Match Started")
            else:
                IR_STARTED = False
                print("[IR] Match Stopped")

        elif not IR_QUEUE.empty() and utime.ticks_diff(cur_time, IR_QUEUE_EMPTY_TIME) > 200:
            # if the queue has items but not a full ir message
            # assume we recived an incomplete message and drop the queue
            print("Incomplete message recieved, dropping ir packet")
            while not IR_QUEUE.empty():
                IR_QUEUE.get()

def evt_time_to_pulse_len(ir_evt_times):
    """Convert a list of absolute ir transition times to a list alternating between
    pulse time high and pulse time low. The first element will always a high pulse.
    Automatically handles wrapping of the initial list of time in absolute ticks at 2^16.

    Ex: [10, 40, 70, 75] -> [30, 30, 5] # one high pulse of 30 ticks, followed by 30 ticks of time low,
       then another pulse of 5 ticks.

    @param ir_evt_times list of ir irq evnts in 16-bit ticks
    @return list of pulse sizes in ticks, alternating between high and low. First pulse is always high.
    """
    tmr_max = 65535
    delta_ticks = []
    for i in range(1, len(ir_evt_times)):
        # Check if timer wrapped between ticks
        delta = ir_evt_times[i] - ir_evt_times[i-1]
        if(ir_evt_times[i] < ir_evt_times[i-1]):
            delta = tmr_max - ir_evt_times[i-1]
            delta += ir_evt_times[i]
        delta_ticks.append(delta)
    return delta_ticks

def ticks_to_ms(ir_pulses, tick_freq):
    """
    convert pulse times in clock ticks to pulse time in ms

    @param ir_pulses pulse sizes in ticks
    @param tick_freq ir irq timer freqency in hertz.
    @return ir pulses in ms
    """

    tick_to_ms = tick_freq/1000
    pulses_ms = []

    for pulse in ir_pulses:
        pulses_ms.append(pulse/tick_to_ms)

    return pulses_ms

def psls_to_logic_in_dct(ir_pulses_ms):
    """
    Decodes pulse times to logic ones and zeros and places the resulting
    Data into a 32 bit integer. This integer is then broken into bytes,
    checked for errors and if error free returned to be printed, else an
    error code is given for either the address or command given being invalid

    Adjust the ir_pw_err if the clock on the remote sends high pulses with greater
    variance than plus or minus 200 microseconds

    @param ir_pulses_ms ir pulse lengths in ms
    @return dictionary with address and command, or None if error was detected
    """
    # Pulse lengths and error margins in milliseconds
    ir_high_pw = 1.6875
    ir_pw_err = 0.2
    ir_lead_pw = 4.5

    ir_logic_int = 0
    packet = None
    # Evaluates logic 1's and 0's based on pulsewidth of transitions within a margin of error
    if not ir_pulses_ms[0] >= ir_lead_pw:
        print("start of packet not found")
        return None
    for pulse in ir_pulses_ms[3:-1:2]:
        ir_logic_int <<= 1
        if (pulse <= ir_high_pw + ir_pw_err and pulse >= ir_high_pw - ir_pw_err):
            ir_logic_int |= 1
    # Converts the int into bytes and stores the data packet in a dictionary
    packet = ir_logic_int.to_bytes(4, 'big')
    pkt_dict = {'raw' : ir_logic_int, 'addr': packet[0],'naddr':packet[1],
                   'cmd' : packet[2], 'ncmd' : packet[3]}
    # Checks for good/bad data. If data is bad, throws it away.
    # Tells the user which part of the transmission was corrupted
    if bin(pkt_dict['addr'] & 0xFF) != bin(~pkt_dict['naddr'] & 0xFF):
        print("invalid addr in data packet")
        return None
    elif bin(pkt_dict['cmd'] & 0xFF) != bin(~pkt_dict['ncmd'] & 0xFF):
        print("invalid cmd in data packet")
        return None
    return pkt_dict
