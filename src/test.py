# ffmpeg

for i, packet in enumerate(input_container.demux(audio_stream)):
    for frame in packet.decode():
        out_pack = out_stream.encode(frame)
        if out_pack:
            out_container.mux(out_pack)

# portAudio

# How many frames to read each time. for 44100Hz 44,1 is 1ms equivalent
frame_chunk = int((sample_rate/1000) * buffer_time)

while not self.__terminating:
    data = audio_stream.read(frame_chunk)
    container.writeframesraw(data)
