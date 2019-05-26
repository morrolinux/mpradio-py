import sys
from fractions import Fraction
import av
import av.filter


def init_filter_graph(in_sample_rate=48000, in_fmt='s16', in_layout='stereo'):
    graph = av.filter.Graph()

    volume_val = 0.10

    # initialize filters
    filter_chain = [
        graph.add_abuffer(format=in_fmt,
                          sample_rate=in_sample_rate,
                          layout=in_layout,
                          time_base=Fraction(1, in_sample_rate)),

        # initialize filter with keyword parameters
        graph.add('volume', volume=str(volume_val)),

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
