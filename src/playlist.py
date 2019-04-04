from media_scanner import MediaScanner


class Playlist:

    __queued = None
    __played = None
    __current = None
    __ms = None

    def __init__(self):
        # TODO: read ini settings
        # TODO: load saved playlist from file
        if self.__queued is None:
            self.__ms = MediaScanner()
            self.__queued = self.__ms.scan()
        # self.__queued = ["../songs/1.mp3", "../songs/3.mp3", "../songs/song.m4a", "../songs/2.mp3"]
        self.__queued.reverse()
        self.__played = []

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.__queued) > 1:
            self.__current = self.__queued.pop()
            self.__played.append(self.__current)
        else:
            self.__queued = self.__ms.scan()
            self.__current = self.__queued.pop()
            self.__played.append(self.__current)

        return self.__current

        # TODO: save the playlist (__queued) to file

    def back(self, n=0):
        for _ in range(n+1):
            self.__queued.append(self.__played.pop())

    def elements(self):
        return self.__queued

    def current(self):
        return self.__current
