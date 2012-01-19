'''
this script is modified from  create_song.py written by phed of 14 Jan 2012.
my changes are:
- the String constants for machine uri
- io_vals defaults
- added to_note ( which is a modified version of a snippet by calvin )
- other convenience functions like   from_chord and  app_wait
 '''
import armstrong
import buze
import random
import sys

PATTERN_LENGTH = 1024
seed = random.randint(0, PATTERN_LENGTH / 16 - 1)

# shuffle definitions and product
base = 125
width = 10
beat_s = (60./(base-width))+(60./(base+width))

# String constants.
LUNAR_SYNTH = "@trac.zeitherrschaft.org/aldrin/lunar/generator/synth;1"
ZZUB_NOTEGEN = "@zzub.org/notegen"
ZZUB_FSM_KICK = "@zzub.org/buzz2zzub/FSM+Kick+XP"
ZZUB_SEQ = "@zzub.org/sequence/sequence"
OSKARI_DELAY = "@oskari/ninja+delay;1"

# Parameter Defaults
io_vals = [[0, 0, 255, 255]]



def dump_errors(player):
  """This prints validation errors. But never seen it produce any """
  errs = player.get_validation_errors()
  n = 0
  while errs.valid():
    err = errs.current()
    print "error %i: %s" % (n, err)
    errs.next()
    n += 1


def find_master(player):
  '''Finds the first master'''
  master = None
  plugit = player.get_plugin_iterator()
  while plugit.valid():
    plugin = plugit.current()
    loader = plugin.get_pluginloader()
    if loader.get_uri() == "@zzub.org/master":
      print "Found master"
      master = plugin
    plugit.next()
    return master


def create_generator(player, uri=LUNAR_SYNTH, position=None, tracks=3, name=None):
  loader = player.get_pluginloader_by_name(uri)
  if not name:
    name = loader.get_name()
  newplug = player.create_plugin(None, 0, name, loader) # loader.get_name as default name
  if not position:
    position = random.random()*2-1.0, random.random()*2-1.0
  newplug.set_position(position[0], position[1])
  newplug.set_track_count(tracks) # We could use logic to test against max tracks
  return newplug 


def create_notegen(player, name, generator, uri=ZZUB_NOTEGEN, position=None):
  loader = player.get_pluginloader_by_name(uri)
  noteplug = player.create_plugin(None, 0, name, loader)
  if position:
    noteplug.set_position(position[0], position[1])
  noteplug.set_track_count(generator.get_track_count(2))
  generator.create_note_connection(noteplug)
  return noteplug


def set_parameters_from_dump_by_name(player, target_machine, dump):
  plugit = player.get_plugin_iterator()
  done = False
  while plugit.valid():
    plugin = plugit.current()
    if target_machine == plugin.get_name(): 
      set_parameters_from_dump(player, plugin, dump)
      done = True
    plugit.next()
  if done: 
    print "done setting params to %s" % target_machine
  else:
    print "did not find: %s" % target_machine
    print "did nothing."


def set_parameters_from_dump(player, plugin, dump):
  loader = plugin.get_pluginloader()
  for group_n in range(min(len(dump), 3)):
    group = dump[group_n]
    for track_n in range(min(len(group), plugin.get_track_count(group_n))):
      track = group[track_n]
      for param_n in range(min(len(track), plugin.get_parameter_count(group_n, track_n))):
        value = track[param_n]
        plugin.set_parameter_value(group_n, track_n, param_n, value, 0)
  print "done setting params to %s" % plugin.get_name()

  
def app_wait(n_points):
  app.set_wait_text("."*n_points)


def to_note(s):
	if s == "off":
		return 255
	if s == "cut":
		return 254

	try:
		octave = int(s[2:])
	except:
		return -1

	notepart = s[:2]
	notevalue = -1
		
	notes = [ "C-", "C#", "D-", "D#", "E-", "F-", "F#", "G-", "G#", "A-", "A#", "B-" ]
	notes2 = [ "C-", "C#", "D-", "Eb", "E-", "F-", "F#", "G-", "Ab", "A-", "Bb", "B-" ]
	
	if notepart in notes2:
		notes = notes2
		
	if notepart not in notes:
		return -1
	
	for index, item in enumerate(notes):
		if item == notepart:
			notevalue = index
			break

	if notevalue == -1 or octave == -1:
		return -1

	return (notevalue + octave * 16) + 1
  

def from_chord(notes):
	note_list = []
	for note in notes:
		note_list.append(to_note(note))
	return note_list
  
  
  
# Start!
# Clean up!
app = mainframe.get_application()
doc = mainframe.get_document()
player = doc.get_player()
app.show_wait_window()
app.set_wait_text("Going to generate %i rows: Clearing..." % PATTERN_LENGTH)
doc.clear_song()

# Policy for placement 
x_policy = lambda x_n: - 1.0 + 2*(1.+x_n) / (2+4) # 4 is hardcoded

# master is usually in the default document
master = find_master(player)
print "Master is %r" % master
assert master, "Master not found"


'''
Sequencer
'''

x = x_policy(0)
seq = create_generator(player, uri=ZZUB_SEQ, position=(x, 0), tracks=1)


'''
Bass Drum 
'''

# Create a bassdrum
x = x_policy(1)
bdplug = create_generator(player, uri=ZZUB_FSM_KICK, position=(x, -.5), tracks=1)
track_vals = [[255, 128, 115, 16, 5, 16, 50, 28, 41, 97, 13, 1, 240, 205, 255]]
parameter_dump = [	io_vals, [[]], track_vals	]
set_parameters_from_dump(player, bdplug, parameter_dump)
master.create_audio_connection(bdplug, 0, 2, 0, 1) # FSM Kick XP is mono


'''
Chord Synth
'''

# Create synth
x = x_policy(2)
chordplug = create_generator(player, uri=LUNAR_SYNTH, position=(x, -.5), tracks=6)
chordnoteplug = create_notegen(player, "Chord", chordplug, position=(x, -.9))
global_vals = [[0, 5810, 5634, 856, 6124, 59, 12, 735, 3923, 0, 617, 0]]
track_vals =  [[255, 255], [255, 255], [255, 255], [0, 255]]
parameter_dump = [	io_vals, global_vals, track_vals ]
set_parameters_from_dump(player, chordplug, parameter_dump)

# create echo
x = x_policy(3)
echo_val = int(beat_s*1000/4.*3)
echoplug = create_generator(player, uri=OSKARI_DELAY, position=(x, -.5), tracks=1)
echoplug.create_audio_connection(chordplug, 0, 2, 0, 2)
echoplug.set_parameter_value(2, 0, 0, echo_val, 0) # length
echoplug.set_parameter_value(2, 0, 1, 1, 0) # unit = ms (1)
master.create_audio_connection(chordplug, 0, 2, 0, 1)
master.create_audio_connection(echoplug, 0, 2, 0, 2)


''' Pattern Format '''


# Create a pattern format
format = player.create_pattern_format("Notes")
idx = 0
# BPM
format.add_column(seq, 1, 0, 0, idx) # Trigger Note
idx += 1


# Chords
generator = chordplug
notegen = chordnoteplug
for track_n in range(generator.get_track_count(2)):
  for n in [0, 2]:
    format.add_column(notegen, 2, track_n, n, idx)
    idx += 1
# Chords cut off
format.add_column(generator, 1, 0, 7, idx)
column = format.get_column(generator, 1, 0, 7)
column.set_mode(5) # slider 
idx += 1
# Chords decay
format.add_column(generator, 1, 0, 2, idx)
column = format.get_column(generator, 1, 0, 2)
column.set_mode(5) # slider 
idx += 1


# Create columns for kick: 
format.add_column(bdplug, 2, 0, 0, idx) # Trigger Note
idx += 1
format.add_column(bdplug, 2, 0, 1, idx) # Trigger
idx += 1
# Pattern format is done

# Create the pattern
pattern = player.create_pattern(format, "Riff", PATTERN_LENGTH)


# Shuffle BPM
for n in range(PATTERN_LENGTH):
  if n % 2:
    bpm = base + width
  else:
    bpm = base - width
  pattern.insert_value(seq.get_id(), 1, 0, 0, n, bpm, 0) 
app.set_wait_text("~shuffle~")
# calculate real delay - but you should use multiple timesources. but look at meeeeee......
app_wait(1)

# vestigial
# And insert a bass-line
for n in range(PATTERN_LENGTH/4):
  t = 2+n*4 # omPA

  
# Insert unz
pattern.insert_value(bdplug.get_id(), 2, 0, 0, 0, 17+0x10, 0)
for n in range(PATTERN_LENGTH/4):
  some_gibberish =  n*4+2+(((n>>3)^n)&3)
  more_gibberish = 00+(1<<(n&7))/3
  pattern.insert_value(bdplug.get_id(), 2, 0, 1, some_gibberish, more_gibberish, 0) # note "off"
  pattern.insert_value(bdplug.get_id(), 2, 0, 1, n*4, 0x60, 0) # note on
app_wait(4)


# Set base note for unz to C-2
for n in range(PATTERN_LENGTH/4):
  pattern.insert_value(bdplug.get_id(), 2, 0, 0, 0, 17+0x10, 0)
app_wait(5)


# Stabbed chords
steps = [0, 3, 7, 11, 14]
length = 16
n = 0 
while True:
  if t > PATTERN_LENGTH-1:
    break
  if n%48>36:
 	notes = from_chord(["C-3", "E-3", "B-3"])
  else: 
    notes = from_chord(["D-3", "F#3", "B-3"])

  t = int(n/len(steps))*length+steps[n % len(steps)]
  for track, note in enumerate(notes):
    pattern.insert_value(chordnoteplug.get_id(), 2, track, 0, t, note, 0)
    pattern.insert_value(chordnoteplug.get_id(), 2, track, 0, t+1, armstrong.zzub_note_value_off, 0) # note off
  n += 1
app_wait(6)


# Chords Cutoff & Decay 
for t in range(PATTERN_LENGTH):
  random_val1 = (((t*19)<<7) | ((t*7)*3)) % 0x4e16
  random_val2 = (((t*17)<<9) | ((t*3)*5)) % 0x2e16
  pattern.insert_value(chordplug.get_id(), 1, 0, 7, t, random_val1/2, 0) 
  pattern.insert_value(chordplug.get_id(), 1, 0, 2, t, random_val2/2+0x200+0x800*t/PATTERN_LENGTH, 0)
app_wait(7)


# Loop and tidy
pattern.set_loop_start(0)
pattern.set_loop_end(PATTERN_LENGTH)
pattern.set_loop_enabled(1)
player.set_order_length(1)
player.set_order_pattern(0, pattern)
player.history_commit(0, 0, "Commit the song")
app.hide_wait_window(0)
print "Done!"
