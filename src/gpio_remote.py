import threading
import RPi.GPIO as GPIO
import time


class GpioRemote:

    __event = None
    __msg = None
    __s = None

    def __init__(self, event, msg):
        self.__event = event
        self.__msg = msg
        self.reset_s()

    def __run(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        down = 0
        up = 0
        fired = False

        while True:
            input_state = GPIO.input(18)

            if not input_state:  # button down
                up = 0
                down += 1
                if self.__s[len(self.__s) - 1] == 0:
                    self.__s.append(1)
            else:               # button up
                up += 1
                down = 0
                if self.__s[len(self.__s) - 1] == 1:
                    self.__s.append(0)

            # long press
            if down > 20:
                fired = True
                self.poweroff()

            # single and double click
            if up in range(3, 8) and len(self.__s) > 2 and not fired:
                action = "".join([str(b) for b in self.__s])
                if action == "010":  # single click
                    fired = True
                    self.next()             # TODO: read what to do from ini settings
                elif action == "01010":  # double click
                    fired = True
                    self.pause()
                self.reset_s()
            elif up > 8:  # reset status and prepare for next click
                self.reset_s()
                fired = False

            # cleanup after long time unused
            if up > 9000:
                self.reset_s()
                up = 0

            time.sleep(0.1)

    def run(self):
        threading.Thread(target=self.__run).start()

    def resume(self):
        pass

    def pause(self):
        pass

    def next(self):
        print("push button pressed: next")
        self.__msg["command"] = ["next"]
        self.__msg["source"] = "gpio"
        self.__event.set()

    def previous(self):
        pass

    def poweroff(self):
        self.__msg["command"] = ["system", "poweroff"]
        self.__msg["source"] = "gpio"
        self.__event.set()

    def reset_s(self):
        self.__s.clear()
        self.__s.append(0)
