#!/usr/bin/env python3

import curses
import time
import signal
import sys

#################################################
# This script can be used as a generic timer
#################################################


def main(stdscr):
    hr_elapsed = 0
    min_elapsed = 0
    sec_elapsed = 0

    stdscr.nodelay(True)
    start_time = time.time()
    while True:
        stdscr.clear()
        
        cur_time = time.time()
        delta_time = (time.time() - start_time)
        sec_elapsed = round(delta_time)
        min_elapsed = round(delta_time/60)
        hr_elapsed = round(delta_time/3600)

        stdscr.addstr(0, 1, "############## Time spent ##############")
        stdscr.addstr(1, 1, f"{hr_elapsed:02} : {min_elapsed%60:02} : {sec_elapsed%60:02}")
        stdscr.addstr(2, 1, "########################################")
        stdscr.addstr(3, 1, f"{min_elapsed} minutes elapsed")
        stdscr.addstr(4, 1, f"Press [q] to stop the timer")
        
        stdscr.refresh()
        key_pressed = stdscr.getch()
        if key_pressed == ord('q'):
            stdscr.nodelay(False)
            break
        time.sleep(1)
    stdscr.clear()
    stdscr.addstr(0, 1, f"{min_elapsed} minutes elapsed")
    stdscr.addstr(1, 1, f"Press any key to exit")
    stdscr.refresh()
    stdscr.getch()

def signal_handler(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

curses.wrapper(main)
