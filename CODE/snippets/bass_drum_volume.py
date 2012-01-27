from random import randint

PATTERN_LENGTH = 64

tick = 0
while(tick < PATTERN_LENGTH):
    if tick in [4,12,28,32,46,60]:
        bass_drum_volume = randint(40, 53)
    else:
        bass_drum_volume = 50

    print("bass drum volume: ", bass_drum_volume)
    tick += 1

