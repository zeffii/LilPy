import armstrong

doc = mainframe.get_document()
player = doc.get_player()
plugin = player.get_plugin_by_name("Infector44")

dump = []
for group_n in range(3):
  groups = []
  for track_n in range(plugin.get_track_count(group_n)):
	tracks = []
	for param_n in range(plugin.get_parameter_count(group_n, track_n)):
	  value = plugin.get_parameter_value(group_n, track_n, param_n)
	  tracks.append(value)
	groups.append(tracks)
  dump.append(groups)      

for sublist in dump:
  print sublist
