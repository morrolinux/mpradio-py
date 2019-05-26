from abc import abstractmethod
from media import MediaInfo, MediaControl
import threading
import av
import av.filter
from fractions import Fraction


class Player(MediaControl, MediaInfo):

    CHUNK = 1024 * 8    # set to 8192 for it to perform well on the orignal Pi 1. For any newer model, 2048 will do.
    SLEEP_TIME = 0.035
    output_stream = None
    ready = None

    def __init__(self):
        self.ready = threading.Event()

    @abstractmethod
    def playback_position(self):
        pass

    def init_filter_graph(self, in_sample_rate=44100, in_fmt='fltp', in_layout='stereo'):
        graph = av.filter.Graph()

        volume_val = 10

        # initialize filters
        filter_chain = [
            graph.add_abuffer(format=in_fmt,
                              sample_rate=in_sample_rate,
                              layout=in_layout,
                              time_base=Fraction(1, in_sample_rate)),

            # initialize filter with keyword parameters
            # graph.add('volume', volume=str(volume_val)),
            graph.add('equalizer', 'f=5200:width_type=h:width=200:g=-20'),

            # there always must be a sink at the end of the filter chain
            graph.add('abuffersink')
        ]

        # link up the filters into a chain
        for c, n in zip(filter_chain, filter_chain[1:]):
            c.link_to(n)

        # initialize the filter graph
        graph.configure()

        return graph

    """
    legacy method for generating silence
    def silence(self, silence_time=1.2):
        tmp_stream = self.output_stream
        self.output_stream = subprocess.Popen(["sox", "-n", "-r", "48000", "-b", "16", "-c", "1", "-t", "wav", "-",
                                               "trim", "0", str(silence_time)],
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        time.sleep(silence_time)
        self.output_stream = tmp_stream
    """
