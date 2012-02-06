import armstrong

doc = mainframe.get_document()
player = doc.get_player()

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