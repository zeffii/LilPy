import random
from random import randint
PATTERN_LENGTH = 64;

# testing reproducable effects first
random.seed(1)


# we can avoid looking at the mechanics for a while
def get_step_distance(skip_list):
    return skip_list[randint(0, len(skip_list)-1)]


# returns lists like [0,0,0,2,2,2,2,2,2,2,4,4,4,4,4,6,6,6,6,6,8,8]
def make_list(dicted_list):
    # print(dicted_list)
    step_list = []
    for key, item in dicted_list.items():
        step_list += [key,]*item
    # print(step_list)
    return step_list


def get_skip_list(version):
    if version == 0:
        return make_list({0:3, 2:7, 4:5, 6:5, 8:2})
    if version == 1:
        return make_list({2:1, 4:6, 6:5, 8:2})
    if version == 2:
        return make_list({2:2, 4:5, 6:5, 8:2})
    if version == 3:
        return [2,4,6]


def get_tick_triggers():
    tick_triggers = []
    tick = 0

    while tick < PATTERN_LENGTH:
        if tick == 0:
            step = get_step_distance(get_skip_list(0))
            if step == 0:
                tick_triggers.append(tick)
                tick += step
                step = get_step_distance(get_skip_list(1))
            tick += step
            tick_triggers.append(tick)
        else:
            step = get_step_distance(get_skip_list(2))
            if tick+step < PATTERN_LENGTH:
                tick += step
                tick_triggers.append(tick)
            else:
                step = get_step_distance(get_skip_list(3))
                if tick+step < PATTERN_LENGTH:
                    tick += step
                    tick_triggers.append(tick)
                break

    return tick_triggers


# then iterate over it
tick = 0
tick_triggers = get_tick_triggers()
for i in range(PATTERN_LENGTH):
    if i in tick_triggers:
        print(i, "trigger")
    else:
        print(i, "...")
