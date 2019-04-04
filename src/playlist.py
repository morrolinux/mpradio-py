class Playlist:

    __queued = None
    __played = None
    __current = None

    def __init__(self):
        pass

    def __iter__(self):
        self.__queued = ["songs/1.mp3", "songs/3.mp3", "songs/song.m4a", "songs/2.mp3"]
        self.__queued.reverse()
        self.__played = []
        return self

    def __next__(self):
        try:
            self.__current = self.__queued.pop()
            self.__played.append(self.__current)
            return self.__current
        except IndexError:
            print("playlist ended")
            self.__iter__()     # maybe rescan media?
            raise StopIteration

    def back(self, n=0):
        for _ in range(n+1):
            self.__queued.append(self.__played.pop())

    def elements(self):
        return self.__queued

    def current(self):
        return self.__current
