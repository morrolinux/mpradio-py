import threading
import time
import psutil


class Profiler:
    __termination = threading.Event()
    __l = None

    def __init__(self):
        self.__l = threading.Lock()
        self.__basetime = None
        self.__cpu_graph = None

    def add(self, event):
        d = self.__get_cpu_status()
        d["event"] = event
        print(">>", d["time"], ":", event)
        self.__add(d)

    def start(self):
        self.__basetime = time.time()
        self.__cpu_graph = []
        threading.Thread(target=self.__cpu_monitor).start()

    def stop(self):
        self.__termination.set()

    def __cpu_monitor(self):
        while not self.__termination.is_set():
            self.__add(self.__get_cpu_status())
            time.sleep(5)

    def __get_cpu_status(self):
        t = time.time() - self.__basetime
        """ 
        samples = 10
        cpu_percent = 0
        for _ in range(samples):
            cpu_percent += psutil.cpu_percent()
            time.sleep(0.05)
        cpu_percent /= samples
        return {"time": t, "cpu": cpu_percent}
        """
        # faster (less precise) sampling not to slow down the program
        return {"time": t, "cpu": psutil.cpu_percent}

    def __add(self, point):
        self.__l.acquire(blocking=True)
        self.__cpu_graph.append(point)
        self.__l.release()

    def print_stats(self):
        for i in self.__cpu_graph:
            print("t:", i["time"], "cpu:", i["cpu"], i["event"] if i.get("event") else "")

        self.export_csv()

    def export_csv(self):
        with open("prof.csv", "w") as f:
            f.write("time;cpu;event\n")
            for i in self.__cpu_graph:
                s = str(i["time"]) + ";" + str(i["cpu"]) + ";" + (i["event"] if i.get("event") else "")
                s += "\n"
                f.write(s)
