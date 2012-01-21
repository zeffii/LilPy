import armstrong
# assumption : that a master plugin ("Master")  is present in the document.

doc = mainframe.get_document()
player = doc.get_player()

# machine uris 
LUNAR_SYNTH = "@trac.zeitherrschaft.org/aldrin/lunar/generator/synth;1"
FUNKY_VERB = "@zzub.org/buzz2zzub/Larsha+Funkyverb"
MATILDE_2 = "@zzub.org/buzz2zzub/Matilde+Tracker2"

# we wrote this function earlier to take care of the machine loading and track count config
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


matilde_1_location = (0, -1)
matilde_2_location = (.25, -1)
bassline_synth_location = (-.25, -1)
verb_send_location = (.25, -.75)

matilde1 = create_machine(MATILDE_2, matilde_1_location, 2, "Beats")
matilde2 = create_machine(MATILDE_2, matilde_2_location, 3, "Snares")
bassline_synth = create_machine(LUNAR_SYNTH, bassline_synth_location, 1, "Bassline")
verb_effect = create_machine(FUNKY_VERB, verb_send_location, 0, "SnareFX")

connect_machines("Beats > Master")
connect_machines("Snares > SnareFX > Master")
connect_machines("Bassline > Master")




'''
# assuming Synth is present
plugin = player.get_plugin_by_name("Synth")
plugin.set_track_count(5)
format = player.get_pattern_format_by_name("Synth")


def count_format_columns(format):
    format_iterator = format.get_iterator()
    column_counter = 0
    while format_iterator.valid():
      column_counter+=1
      format_iterator.next()

    # WARNING: it was iterating an sqlite recordset,
    # not closing it will cause leaks
    format_iterator.destroy()
    return column_counter


# configure format, currently default
tracks_to_add = 4
column_idx = count_format_columns(format)
for i in range(tracks_to_add):
    format.add_column(plugin, group=2, track=1+i, column=0, idx=column_idx)
    format.add_column(plugin, group=2, track=1+i, column=1, idx=column_idx+1)
    column_idx+=2
'''

