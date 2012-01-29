PATTERN_LENGTH = 64;
tick = 0
while tick < PATTERN_LENGTH:
    if tick % 8 == 0:
        print("bd")
    else:
        print("...")

    tick+=1
