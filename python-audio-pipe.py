import sys
import subprocess

CHUNK = 1024

if len(sys.argv) < 2:
    print("Plays an audio file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

audio_input = subprocess.Popen(["sox", sys.argv[1], "-t", "wav", "-"],
                        stdout=subprocess.PIPE)
#audio_input = subprocess.Popen(["ffmpeg", "-i", sys.argv[1], "-loglevel", "panic", "-vn", "-f", "s16le", "pipe:1"],
#                        stdout=subprocess.PIPE, stdin=subprocess.PIPE)

audio_output = subprocess.Popen(["pi_fm_adv", "--audio", "-"], stdin=subprocess.PIPE)

# read data
data = audio_input.stdout.read(CHUNK)

# play stream (3)
while len(data) > 0:
    audio_output.stdin.write(data)
    audio_output.stdin.flush()
    data = audio_input.stdout.read(CHUNK)

