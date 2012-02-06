def to_note(s):
    notes = [ "C-", "C#", "D-", "D#", "E-", "F-", "F#", "G-", "G#", "A-", "A#", "B-" ]
    notes2 = [ "C-", "C#", "D-", "Eb", "E-", "F-", "F#", "G-", "Ab", "A-", "Bb", "B-" ]
 
        if s == "off":
                return 255
        if s == "cut":
                return 254
 
        try:
                octave = int(s[2:])
                if s[:2] in notes2:
                    notes = notes2    
                notevalue = notes.index(s[:2])
        except:
                return -1
 
        return (notevalue + octave * 16) + 1



def from_chord(notes):
	note_list = []
	for note in notes:
		note_list.append(to_note(note))
	return note_list


print(from_chord(["C-3", "Eb3", "F#4", "Ab4"]))
print(from_chord(["C-3", "D#3", "F#4", "G#4"]))
