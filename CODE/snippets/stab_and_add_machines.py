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
# FUNKY_VERB = "@zzub.org/buzz2zzub/Larsha+Funkyverb"
# MATILDE_2 = "@zzub.org/buzz2zzub/Matilde+Tracker2"

PATTERN_LENGTH = 64;


'''big ugly function'''
def make_rhythm():

    # why not fill a list with the step_distances?
    tick_triggers = []
    tick = 0
    while tick < PATTERN_LENGTH:
        if tick == 0:
            # likely = 2,4,6, unlikely = 0,2,8
            skip = [0,0,0,2,2,2,2,2,2,2,4,4,4,4,4,6,6,6,8]
            step_distance = skip[randint(0, len(skip)-1)]

            if step_distance == 0:
                tick_triggers.append(0)
                skip = [2,4,4,4,4,4,4,6,6,6,6,6,8]
                step_distance = skip[randint(0, len(skip)-1)]
                tick += step_distance
                tick_triggers.append(tick)
                continue
        else:
            # likely = 4,6, unlikely 2,8
            skip = [2,4,4,4,4,4,4,4,6,6,6,6,6,6,6,8]
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
        
    return tick_triggers



def printInfo(format_name, num_gparams, num_tparams):
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
    # configure format, currently default
    column_idx = count_format_columns(format)
    columns_per_tparams = plugin.get_parameter_count(2, 0)

    for i in range(tracks_to_add):
        for n in range(columns_per_tparams):
            format.add_column(plugin, group=2, track=1+i, column=n, idx=column_idx+n)
        column_idx+=columns_per_tparams
    return format


def add_columns_to_format_from_plugin(format, plugin):
    
    def add_track_from_group(format, plugin, group, track):
        column_idx = count_format_columns(format)
        num_params = plugin.get_parameter_count(group, track)
        for i in range(num_params):
            format.add_column(plugin, group, track, i, column_idx)
            column_idx += 1

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
    #  global parametersm, track parameters
    num_gparams = plugin.get_parameter_count(1, 0)
    num_tparams = plugin.get_parameter_count(2, 0)
    printInfo(format_name, num_gparams, num_tparams)

    return default_format


def add_subset_to_format_from_plugin(format, plugin, group, track, subset):
    '''
    format:     format to add to
    plugin:     plugin to add from
    group:      group to add from
    track:      track in group to add from
    subset:     list of 1 or more parameters to add.  f.ex [2,4,5,9] of lunar verb.
    '''
    column_idx = count_format_columns(format)
    for column in subset:
        format.add_column(plugin, group, track, column, column_idx)
        column_idx += 1



synth_location = (-.25, -1)
synth = create_machine(LUNAR_SYNTH, synth_location, 6, "Synthline")
connect_machines("Synthline > Master")
synthline_format = create_simple_format_from_machine(synth)
player.history_commit(0, 0, "Added Default Format(s)")

# Create the pattern
pattern = player.create_pattern(synthline_format, "Stabs", PATTERN_LENGTH)
player.history_commit(0, 0, "Added Stabs Pattern")



# then iterate over it
tick = 0
for tick_event in range(PATTERN_LENGTH):
    if tick_event in make_rhythm():
        # print("trigger")
        notes = from_chord(["C-3", "E-3", "B-3", "G-2"])
        for track, note in enumerate(notes):
            pattern.insert_value(synth.get_id(), 2, track, 0, tick_event, note, 0)
            pattern.insert_value(synth.get_id(), 2, track, 0, tick_event+1, to_note("off"), 0) # note off
player.history_commit(0, 0, "Filled Stabs Pattern")
