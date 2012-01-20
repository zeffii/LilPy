
'''
g_params = 1 
param_track = 0 # this g_params has only one track, namely '0'
param_number = 7 # currently, resonance

param = plugin.get_parameter(g_params, param_track, param_number)
print(param.get_value_min())
print(param.get_value_max())

methods = [method for method in dir(param) if not method.startswith('_')]
pprint(methods)
'''

import armstrong

doc = mainframe.get_document()
player = doc.get_player()

# assuming Synth is present
plugin = player.get_plugin_by_name("Synth")
plugin.set_track_count(5)

# cofigure current format
format = player.get_pattern_format_by_name("Synth")

# print name of tracks for debug
format.set_track_name(plugin(1,0,"TestName"))
track_name = format.get_track_name(plugin, 1, 0)
print(track_name)