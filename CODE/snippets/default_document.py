import armstrong
import buze

app = mainframe.get_application()
doc = mainframe.get_document()
doc.clear_song()
player = doc.get_player()

SEQUENCER = "@zzub.org/sequence/sequence"
PATTERN_PLAYER = "@zzub.org/sequence/pattern"

sequence_location = (0.2, -0.2)
pattern_location = (0.2, 0.2)

SEQ_PAT_LEN = 256

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
            format.add_column(plugin, group=2, track=1+i, 
			    column=n, idx=column_idx+n)
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

    printInfo(format_name, plugin)
    player.history_commit(0, 0, "Added Default %s Format" % format_name)
    return default_format


def add_subset_to_format_from_plugin(format, plugin, group, track, subset):
    '''
    format:     format to add to
    plugin:     plugin to add from
    group:      group to add from
    track:      track in group to add from
    subset:     list of 1 or more params to add.  f.ex [2,4,5,9] of lunar verb.
    '''
    column_idx = count_format_columns(format)
    for column in subset:
        format.add_column(plugin, group, track, column, column_idx)
        column_idx += 1


def create_new_pattern(pattern_format, pattern_name, pattern_length):
    new_pattern = player.create_pattern(pattern_format, pattern_name, pattern_length)
    player.history_commit(0, 0, "Added %s" % pattern_name)
    return new_pattern


# add_track_### and add_tracks_### would benefit from a rewrite.
def add_track_to_sequence_pattern(seq_plug, track, pattern_name):
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
        track = current_count + i
        # print("add_track_to_sequence_pattern(track -> track= %d" % track)
        add_track_to_sequence_pattern(seq_plug, track, pattern_name)

    print('Tracks added: %d' % num_tracks)
    player.history_commit(0, 0, "Added %d tracks to Sequence Pattern 00" % num_tracks)


# create plugs
seq_plug = create_machine(SEQUENCER, sequence_location, 1, "Sequence")
pattern_plug = create_machine(PATTERN_PLAYER, pattern_location, 1, "Pattern")



# seq_format needs a pattern
'''
zzub_event_type_insert_orderlist, zzub_event_type_delete_orderlist

the default with  GEN+FX Formats+Patterns: 
a pattern player machine is created
a sequene machine with a patternformat that includes 
only a pattern trigger column from the pattern player.

'''

def create_new_sequencer_format():
    s_format = player.create_pattern_format('Sequence')
    trigger_track = 0
    add_subset_to_format_from_plugin(s_format, pattern_plug, 2, 0, [trigger_track])
    return s_format

seq_format = create_new_sequencer_format()
sequence_pattern = create_new_pattern(seq_format, '00', SEQ_PAT_LEN)
sequence_pattern.set_row_count(512)
sequence_pattern.set_display_resolution(16)

# insert order

# select pattern
