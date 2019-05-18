# https://github.com/mikeboers/PyAV/issues/260
# https://github.com/mikeboers/PyAV/issues/239
import argparse
import av
import av.filter
from av import AudioFormat


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("inputpath")
    args = parser.parse_args()

    icntnr = av.open(args.inputpath)
    ocntnr = av.open(args.inputpath + "-new.wav", "w")

    iastrm = next(s for s in icntnr.streams if s.type == "audio")  # add

    ostrms = {
        "audio": ocntnr.add_stream(codec_name="pcm_s16le", rate=48000),
        }

    # graph = av.filter.Graph()
    # you can enumerate available filters with av.filter.filters_available.
    # print(av.filter.filters_available)
    #

    in_args = "sample_rate=%d:sample_fmt=%s:channel_layout=%s:time_base=%d/%d" % (
        48000, 's16', 'stereo', 1, 48000,)
    eq_args = "f=1000:t=h:width=200:g=-10"

    fchain = []
    fchain.append(graph.add('abuffer', sample_fmt='s16', channel_layout="stereo", sample_rate="48000"))  # , in_args))
    # fchain.append(graph.add('equalizer', eq_args))
    fchain.append(graph.add('abuffersink'))
    fchain[-2].link_to(fchain[-1])

    for i, packet in enumerate(icntnr.demux()):
        print("packet", i)
        for ifr in packet.decode():
            print(ifr)
            typ = packet.stream.type
            if typ == "audio":
                ifr.pts = None
                fchain[0].push(ifr)
                ifr = fchain[1].pull()
                for p in ostrms[typ].encode(ifr):
                    ocntnr.mux(p)

    ocntnr.close()

