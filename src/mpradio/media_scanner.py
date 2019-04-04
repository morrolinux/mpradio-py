import os


class MediaScanner:

    supported_formats = ("mp3", "mp4", "m4a", "wav")

    def __init__(self):
        # TODO: read configuration here
        path = os.getcwd()
        for root, d_names, f_names in os.walk(path):
            for f in f_names:
                if f.endswith(self.supported_formats):
                    print(root+"/"+f)
