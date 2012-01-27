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

	for index, item in enumerate(notes):
		if item == notepart:
			notevalue = index
			break

	if notevalue == -1 or octave == -1:
		return -1

	return (notevalue + octave * 16) + 1


print(to_note("C-2"))
print(to_note("E-3"))
print(to_note("A-3"))
