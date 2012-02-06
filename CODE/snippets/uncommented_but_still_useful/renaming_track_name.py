import armstrong

doc = mainframe.get_document()
player = doc.get_player()

# assuming Synth is present
plugin = player.get_plugin_by_name("Synth")
plugin.set_track_count(5)

# cofigure current format
format = player.get_pattern_format_by_name("Synth")

# print name of tracks for debug
format.set_track_name(plugin, 1,0,"TestName")
track_name = format.get_track_name(plugin, 1, 0)
print(track_name)