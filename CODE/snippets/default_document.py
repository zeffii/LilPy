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


# take care of the machine loading and track count config
def create_machine(uri, position, tracks, name):
    loader = player.get_pluginloader_by_name(uri)
    newplug = player.create_plugin(None, 0, name, loader)
    newplug.set_position(*position)
    newplug.set_track_count(tracks)
    return newplug


def count_format_columns(format):
    format_iterator = format.get_iterator()
    column_counter = 0
    while format_iterator.valid():
        column_counter+=1
        format_iterator.next()
    format_iterator.destroy()
    return column_counter


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
player.set_order_length(1)
player.set_order_pattern(0, sequence_pattern)