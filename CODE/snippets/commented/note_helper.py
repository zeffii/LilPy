# this can be used to convert string representation of notes to the 
# integer representation used internally by buze.
# - to note: is for single notes
# - from_chord: uses multiple calls to to_note to return a list of ints.


def to_note(s):
    if s == "off":
        return 255
    if s == "cut":
        return 254

    notesList = [["C-"], ["C#"], ["D-"], ["D#", "Eb"], ["E-"], ["F-"],\
                 ["F#"], ["G-"], ["G#", "Ab"], ["A-"], ["A#", "Bb"], ["B-"]]
    
    notevalue = [index for index, notes in enumerate(notesList) if s[:2] in notes]
    if notevalue == [] or not s[2:].isdigit():
        print(s + " is not a valid note. ")
        return -1

    octave = int(s[2:])
    if octave not in range(0,10):
        print(s + " octave out of range")
        return -1
    
    return (notevalue[0] + octave * 16) + 1



def from_chord(notes):
    note_list = []
    for note in notes:
        note_list.append(to_note(note))
    return note_list

  
