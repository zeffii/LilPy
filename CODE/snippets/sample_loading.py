import armstrong
import buze
import sys
import os


doc = mainframe.get_document()
player = doc.get_player()

# Load a sample
cur_path = os.getcwd()
file_and_path = os.path.join(cur_path, "Samples", "HHCD4.WAV")
print(file_and_path)
target = player.get_wave(0)
doc.import_wave(file_and_path, target)

