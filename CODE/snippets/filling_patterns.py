from random import randint
import armstrong
import buze
import random
import sys
from pattern_helper import to_note
from pattern_helper import from_chord

# assumption : that a master plugin ("Master")  is present in the document.
doc = mainframe.get_document()
player = doc.get_player()

# machine uris 
LUNAR_SYNTH = "@trac.zeitherrschaft.org/aldrin/lunar/generator/synth;1"
LUNAR_KICK = "@trac.zeitherrschaft.org/aldrin/lunar/generator/kick;1"
# FUNKY_VERB = "@zzub.org/buzz2zzub/Larsha+Funkyverb"
# MATILDE_2 = "@zzub.org/buzz2zzub/Matilde+Tracker2"

PATTERN_LENGTH = 64

def get_step_distance(skip_list):
    return skip_list[randint(0, len(skip_list)-1)]


# returns lists like [0,0,0,2,2,2,2,2,2,2,4,4,4,4,4,6,6,6,6,6,8,8]
def make_list(dicted_list):
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



def printInfo(format_name, plugin):
    num_gparams = plugin.get_parameter_count(1, 0)
    num_tparams = plugin.get_parameter_count(2, 0)
    print("Created: " + format_name)
    print("g_params: %d" % num_gparams)
    print("t_params (params in note track) %d" % num_tparams)


# take care of the machine loading and track count config
def create_machine(uri, position, tracks, name):
    loader = player.get_pluginloader_by_name(uri)
    newplug = player.create_plugin(None, 0, name, loader)
    newplug.set_position(*position)
    newplug.set_track_count(tracks)
    return newplug

  
# this handles the short notation "machine1 > machine2 > machine3" for chaining machines.
def connect_machines(chain):
    machines = chain.split(" > ")
    for machine in range(len(machines)-1):
        from_machine = player.get_plugin_by_name(machines[machine])
        to_machine = player.get_plugin_by_name(machines[machine+1])
        to_machine.create_audio_connection(from_machine, 0, 2, 0, 2)


def count_format_columns(format):
    format_iterator = format.get_iterator()
    column_counter = 0
    while format_iterator.valid():
        column_counter+=1
        format_iterator.next()
    format_iterator.destroy()
    return column_counter


def add_tracks_to_tparams(plugin, format, tracks_to_add):
    column_idx = count_format_columns(format)
    columns_per_tparams = plugin.get_parameter_count(2, 0)

    for i in range(tracks_to_add):
        for n in range(columns_per_tparams):
            format.add_column(plugin, group=2, track=1+i, column=n, idx=column_idx+n)
        column_idx+=columns_per_tparams
    return format


def add_track_from_group(format, plugin, group, track):
        column_idx = count_format_columns(format)
        num_params = plugin.get_parameter_count(group, track)
        for i in range(num_params):
            format.add_column(plugin, group, track, i, column_idx)
            column_idx += 1


def add_columns_to_format_from_plugin(format, plugin):
    # g_params
    add_track_from_group(format, plugin, 1, 0)
    # t_params
    num_tracks_in_tparams = plugin.get_track_count(2)
    for track in range(num_tracks_in_tparams):
        add_track_from_group(format, plugin, 2, track)


def create_simple_format_from_machine(plugin):
    plugin_name = plugin.get_name()
    format_name = "[default "+ plugin_name + "]"
    default_format = player.create_pattern_format(format_name)
    add_columns_to_format_from_plugin(default_format, plugin)

    # for debug
    printInfo(format_name, plugin)
    return default_format


def add_subset_to_format_from_plugin(format, plugin, group, track, subset):
    '''
    format:    format to add to
    plugin:     plugin to add from
    group:     group to add from
    track:      track in group to add from
    subset:    list of 1 or more parameters to add.  f.ex [2,4,5,9] of lunar verb.
    '''
    column_idx = count_format_columns(format)
    for column in subset:
        format.add_column(plugin, group, track, column, column_idx)
        column_idx += 1


# machine locations
synth_location = (-.25, -1)
kick_location = (-.5, 0)


# machine creation
synth = create_machine(LUNAR_SYNTH, synth_location, 6, "Synthline")
kicksynth = create_machine(LUNAR_KICK, kick_location, 1, "Kick")


# machine connecting
connect_machines("Synthline > Master")
connect_machines("Kick > Master")


# format creation
synthline_format = create_simple_format_from_machine(synth)
kick_format = create_simple_format_from_machine(kicksynth)
player.history_commit(0, 0, "Added Default Format(s)")


# Create the pattern
stabs_pattern = player.create_pattern(synthline_format, "Stabs", PATTERN_LENGTH)
player.history_commit(0, 0, "Added Stabs Pattern")

kick_pattern = player.create_pattern(kick_format, "Kicks", PATTERN_LENGTH)
player.history_commit(0, 0, "Added Kicks Pattern")


# fill the stab pattern
tick_list = get_tick_triggers()
for tick_event in range(PATTERN_LENGTH):
    if tick_event in tick_list:
        notes = from_chord(["C-3", "E-3", "B-3", "G-2"])
        for track, note in enumerate(notes):
            stabs_pattern.insert_value(synth.get_id(), 2, track, 0, tick_event, note, 0)
            stabs_pattern.insert_value(synth.get_id(), 2, track, 0, tick_event+1, to_note("off"), 0) # note off
player.history_commit(0, 0, "Filled Stabs Pattern")


# fill the kick pattern
for tick_event in range(0, PATTERN_LENGTH, 8):
    kick_pattern.insert_value(kicksynth.get_id(), 2, 0, 0, tick_event, 1, 0)


# add stabs to the first track of the sequence_pattern, assumes presence of one track.
seq_plug = player.get_plugin_by_name("Pattern")
sequence_pattern = player.get_pattern_by_name("00")
sequence_pattern.insert_value(seq_plug.get_id(), 2, 0, 0, 0, stabs_pattern.get_id(), 0)
sequence_pattern.set_row_count(128)
sequence_pattern.set_display_resolution(16)
player.history_commit(0, 0, "Added Stabs Pattern to Sequence Pattern 00")


# REFACTOR FOLLOWING.
# I'm putting this here for convenience now.
def add_track_to_sequence_pattern(track, pattern_name):
    seq_plug = player.get_plugin_by_name("Pattern")
    current_count = seq_plug.get_track_count(2)
    seq_plug.set_track_count(current_count + 1)

    seq_pat = player.get_pattern_by_name(pattern_name)
    seq_pat_format = seq_pat.get_format()
    # add_column(plugin, group, track, i, column_idx)
    current_count = seq_plug.get_track_count(2)
    seq_pat_format.add_column(seq_plug, 2, track, 0, current_count-1)

def add_tracks_to_sequence_pattern(num_tracks, pattern_name):
    seq_plug = player.get_plugin_by_name("Pattern")
    current_count = seq_plug.get_track_count(2)
    
    for i in range(num_tracks):
        track = current_count + i - 1
        add_track_to_sequence_pattern(track, pattern_name)
    player.history_commit(0, 0, "Added %d tracks to Sequence Pattern 00" % num_tracks)

# add lunarkick track to Sequence, add pattern column first.
# insert_value(self, pluginid, group, track, column, time, value, meta):
# add_tracks_to_sequence_pattern(5, "00")
add_track_to_sequence_pattern(1, "00")
sequence_pattern.insert_value(seq_plug.get_id(), 2, 1, 0, 0, kick_pattern.get_id(), 0)
player.history_commit(0, 0, "Added Kick Pattern to Sequence Pattern 00")
# set tpb = 8
