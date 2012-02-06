import armstrong

'''
- makes default pattern format from machine
- connects machines

assumption : that a master plugin ("Master")  is present in the document.
- does not enter pattern values
= does not sequence

'''
doc = mainframe.get_document()
player = doc.get_player()

# machine uris 
LUNAR_SYNTH = "@trac.zeitherrschaft.org/aldrin/lunar/generator/synth;1"
FUNKY_VERB = "@zzub.org/buzz2zzub/Larsha+Funkyverb"
MATILDE_2 = "@zzub.org/buzz2zzub/Matilde+Tracker2"


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
    plugin:      plugin to add from
    group:      group to add from
    track:       track in group to add from
    subset:     list of 1 or more parameters to add.  f.ex [2,4,5,9] of lunar verb.
    '''
    column_idx = count_format_columns(format)
    for column in subset:
        format.add_column(plugin, group, track, column, column_idx)
        column_idx += 1


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

# MixFormat = bassline(all) + beats(all) + snare(all) + verb(wet=9)
mixed_format = player.create_pattern_format("MixFormat")
for machine in [bassline_synth, matilde1, matilde2]:
    add_columns_to_format_from_plugin(mixed_format, machine)
add_subset_to_format_from_plugin(mixed_format, verb_effect, 1, 0, [9])

player.history_commit(0, 0, "Added Mixed Format")

# add pattern formats for each machine, if you need to 
matilde1_format = create_simple_format_from_machine(matilde1)
matilde2_format = create_simple_format_from_machine(matilde2)
fxVerb_format = create_simple_format_from_machine(verb_effect)
bassline_format = create_simple_format_from_machine(bassline_synth)

player.history_commit(0, 0, "Added Default Formats")