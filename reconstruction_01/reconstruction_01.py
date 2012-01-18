# assuming all machines in question will be stereo capable.

import armstrong
import buze

app = mainframe.get_application()
doc = mainframe.get_document()
player = doc.get_player()

LUNAR_SYNTH = "@trac.zeitherrschaft.org/aldrin/lunar/generator/synth;1"
FUNKY_VERB = "@zzub.org/buzz2zzub/Larsha+Funkyverb"


def create_machine(uri, position, tracks, name):
  loader = player.get_pluginloader_by_name(uri)
  newplug = player.create_plugin(None, 0, name, loader)
  newplug.set_position(*position)
  newplug.set_track_count(tracks)
  return newplug

  
def connect_machines(chain):
  chained_machines = chain.split(" > ")
  
  for machine in range(len(chained_machines)-1):
    first_machine = chained_machines[machine]
    second_machine = chained_machines[machine+1]

    from_machine = player.get_plugin_by_name(first_machine)
    to_machine = player.get_plugin_by_name(second_machine)
    
    to_machine.create_audio_connection(from_machine, 0, 2, 0, 2)

  
lunarSynth = create_machine(LUNAR_SYNTH, (-1,0), 6, "Synth")
funkyVerg = create_machine(FUNKY_VERB, (-0.5, 0), 0, "FunkyVerb")

connect_machines("Synth > FunkyVerb > Master")