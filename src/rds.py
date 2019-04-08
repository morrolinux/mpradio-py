import threading
import time
import platform


class RdsUpdater:

    __interval = None
    __termination = None
    __song = None
    __step = None
    __output = None

    def __init__(self, interval=1):
        self.__interval = interval
        self.__termination = threading.Event()
        self.__step = 1
        if platform.machine() == "x86_64":
            self.__output = print
        else:
            self.__output = self.write_rds_to_pipe

    def set(self, song):
        self.__song = song

    def write_rds_to_pipe(self, text):
        with open("/home/pi/rds_ctl", "w") as f:
            f.write(text)

    def __run(self):
        while not self.__termination.is_set():
            # wait for the song to be set.
            if self.__song is None:
                time.sleep(0.2)
                continue

            for qg in self.q_gram(self.__song["title"]+" - "+self.__song["artist"]):
                self.__output(qg)
                time.sleep(self.__interval)
                if self.__termination.is_set():
                    return

    # print q-grams of the given title
    def q_gram(self, text):
        q = []

        if len(text) < 9:
            q.append(text)
            return q

        for i in range(0, len(text), self.__step):
            start = i
            end = i + 8
            if end > len(text):
                break
            s = text[start:end]
            q.append(s)
        return q

    def run(self):
        threading.Thread(target=self.__run).start()

    def stop(self):
        self.__termination.set()
