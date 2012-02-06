import random
from random import randint


PATTERN_LENGTH = 32

random.seed(1)

tick = 0
while(tick < PATTERN_LENGTH):
    if tick % 2 is not 0:
        bass_drum_volume = randint(40, 53)
    else:
        bass_drum_volume = 50

    print("bass drum volume: ", bass_drum_volume)
    tick += 1

