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
up till this point we have now added the various machines and connected them as desired.
- in create_machine we take care of the naming, location, machine type and track count 

this following section will show a way to create a custom pattern format, because we aren't using the
GUI we do manually have to add the default Pattern formats for each machine. no big deal, it will be part
of the API soon.
'''

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


def add_tracks_to_tparams(plugin, format, tracks_to_add):
    # configure format, currently default
    column_idx = count_format_columns(format)
    columns_per_tparams = plugin.get_parameter_count(2, 0)

    for i in range(tracks_to_add):
        for n in range(columns_per_tparams):
            format.add_column(plugin, group=2, track=1+i, column=n, idx=column_idx+n)
        column_idx+=columns_per_tparams
    return format


def create_simple_format_from_machine(plugin):
    plugin_name = plugin.get_name()
    format_name = "[default "+ plugin_name + "]"
    default_format = player.create_pattern_format(format_name)
    loader = plugin.get_pluginloader()
    
    #  global parameters
    num_gparams = plugin.get_parameter_count(1, 0)
    for i in range(num_gparams):
        param_type = plugin.get_parameter(1, 0, i)
        default_format.add_column(plugin, 1, 0, i, i)
    
    # track parameters
    num_tparams = plugin.get_parameter_count(2, 0)
    for i in range(num_tparams):
        param_type = plugin.get_parameter(2, 0,i)
        default_format.add_column(plugin, 2, 0, i, num_gparams + i)

    # add more tparams to the format if we specified more than 1 track.
    # this assumes the current format only has 1 track. in tparams.
    num_tracks = plugin.get_track_count(2)
    if num_tracks > 1:
        num_tracks_to_add = num_tracks - 1
        default_format = add_tracks_to_tparams(plugin, default_format, num_tracks_to_add)
    
    print("Created: " + format_name)
    print("g_params: %d" % num_gparams)
    print("t_params (params in note track) %d" % num_tparams)
    return default_format

matilde1_format = create_simple_format_from_machine(matilde1)
matilde2_format = create_simple_format_from_machine(matilde2)
fxVerb_format = create_simple_format_from_machine(verb_effect)
bassline_format = create_simple_format_from_machine(bassline_synth)

# now we have the formats and can create a mixed_format
mixed_format = player.create_pattern_format("MixFormat")

# decide the order in which you want to populate MixFormat with your machines
'''
there is room to craft a much more elegant function, but that is for lateron.
    |bassline(all)|
    |beats(all)
    !snare(all)
    |verb(wet)
'''
def add_columns_to_format_from_plugin(format, plugin):
    global column_idx

    num_gparams = plugin.get_parameter_count(1, 0)
    for i in range(num_gparams):
        format.add_column(plugin, 1, 0, i, column_idx)
        column_idx += 1

    num_tracks_in_tparams = plugin.get_track_count(2)
    for track in range(num_tracks_in_tparams):
        num_tparams = plugin.get_parameter_count(2,0)
        for i in range(num_tparams):
            format.add_column(plugin, 2, track, i, column_idx)
            column_idx += 1



#add the entire bassline synth to MixFormat
column_idx = 0

# bassline, beats, snare
add_columns_to_format_from_plugin(mixed_format, bassline_synth)
add_columns_to_format_from_plugin(mixed_format, matilde1)
add_columns_to_format_from_plugin(mixed_format, matilde2)

# verb, one parameter wet, param 10 (index 9) in verb_effect plugin
mixed_format.add_column(verb_effect, 1, 0, 9, column_idx)
column_idx += 1


