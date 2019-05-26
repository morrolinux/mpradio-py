"""
Simple audio filtering example ported from C code:
   https://github.com/FFmpeg/FFmpeg/blob/master/doc/examples/filter_audio.c
"""
from __future__ import division
from __future__ import print_function

import sys
from fractions import Fraction

import av
import av.filter


FRAME_SIZE = 1024

INPUT_SAMPLE_RATE = 48000
INPUT_FORMAT = 's16'
INPUT_CHANNEL_LAYOUT = 'stereo'

VOLUME_VAL = 0.10


def init_filter_graph():
    graph = av.filter.Graph()

    # initialize filters
    filter_chain = [
        graph.add_abuffer(format=INPUT_FORMAT,
                          sample_rate=INPUT_SAMPLE_RATE,
                          layout=INPUT_CHANNEL_LAYOUT,
                          time_base=Fraction(1, INPUT_SAMPLE_RATE)),

        # initialize filter with keyword parameters
        graph.add('volume', volume=str(VOLUME_VAL)),

        # there always must be a sink at the end of the filter chain
        graph.add('abuffersink')
    ]

    # link up the filters into a chain
    for c, n in zip(filter_chain, filter_chain[1:]):
        c.link_to(n)

    # initialize the filter graph
    graph.configure()

    return graph


def main(path):
    input_container = av.open(path)
    output_container = av.open(path+"-new.wav", "w")

    output_stream = output_container.add_stream(codec_name="pcm_s16le", rate=48000)

    graph = init_filter_graph()

    for i, packet in enumerate(input_container.demux()):
        print("packet", i)

        for f in packet.decode():
            # submit the frame for processing
            graph.push(f)

            # pull frames from graph until graph has done processing or is waiting for a new input
            while True:
                try:
                    out_frame = graph.pull()
                    out_frame.pts = None
                    for p in output_stream.encode(out_frame):
                        output_container.mux(p)

                except av.AVError as ex:
                    if ex.errno != 11:
                        raise ex
                    else:
                        break


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: {0} <audio file path>'.format(sys.argv[0]))
        exit(1)

    main(sys.argv[1])
