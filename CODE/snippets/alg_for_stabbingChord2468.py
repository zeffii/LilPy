from random import randint
PATTERN_LENGTH = 64;

# why not fill a list with the step_distances?
tick_triggers = []
tick = 0
while tick < PATTERN_LENGTH:
    if tick == 0:
        # likely = 2,4,6, unlikely = 0,2,8
        skip = [0,0,0,2,2,2,2,2,2,2,4,4,4,4,4,6,6,6,6,6,8,8]
        step_distance = skip[randint(0, len(skip)-1)]

        if step_distance == 0:
            tick_triggers.append(0)
            skip = [2,2,4,4,4,4,4,6,6,6,6,6,8,8]
            step_distance = skip[randint(0, len(skip)-1)]
            tick += step_distance
            tick_triggers.append(tick)
            continue
    else:
        # likely = 4,6, unlikely 2,8
        skip = [2,2,4,4,4,4,4,6,6,6,6,6,8,8]
        step_distance = skip[randint(0, len(skip)-1)]

    if (step_distance + tick) < PATTERN_LENGTH:
        tick_triggers.append(tick)
        tick += step_distance
    else:
        # one last change to fill a last trigger
        step_distance = [2,4,6][randint(0,2)]
        if (step_distance + tick) < PATTERN_LENGTH:
            tick_triggers.append(tick)
            tick += step_distance
        break
    
    

print(tick_triggers)


# then iterate over it
tick = 0
for i in range(PATTERN_LENGTH):
    if i in tick_triggers:
        print("trigger")
    else:
        print("...")
