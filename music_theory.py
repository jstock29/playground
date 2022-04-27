import midi

CIRCLE_OF_FIFTHS = [
    'C',
    'G',
    'D',
    'A',
    'E',
    'B',
    'F#',
    'C#',
    'G#',
    'D#',
    'A#',
    'F',
]

CIRCLE_OF_FIFTHS_MINORS = {
    'C': 'A',
    'G': 'E',
    'D': 'B',
    'A': 'F#',
    'E': 'C#',
    'B': 'G#',
    'F#': 'D#',
    'C#': 'A#',
    'G#': 'F',
    'D#': 'C',
    'A#': 'G',
}

MAJOR_SCALE_CHORDS = [
    'Major',
    'Minor',
    'Minor',
    'Major',
    'Major',
    'Minor',
    'Diminished',
]

MINOR_SCALE_CHORDS = [
    'Major 7',
    'Minor 7',
    'Minor 7',
    'Major 7',
    'Dominant 7',
    'Minor 7',
    'Half Diminished',
]

CHROMATIC = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

MIDI_RANGE = range(21, 108)


def beat_mapping(quarter_note: int) -> dict:
    return {
        "sixteenth": quarter_note / 4,
        "eigth": quarter_note / 2,
        "quarter": quarter_note,
        "half": quarter_note * 2,
        "whole": quarter_note * 4,
    }


def bpm_to_quarter_note(bpm: int) -> int:
    return int(60000 / bpm)


class Key:
    def __init__(self, root: str, key_type: str):
        self.root = root
        self.key_type = key_type
        self.major = self.major_scale()
        self.natural_minor = self.natural_minor_scale()
        self.harmonic_minor = self.harmonic_minor_scale()

    def major_scale(self):
        steps = ['whole', 'whole', 'half', 'whole', 'whole', 'whole', 'half']
        scale = [self.root]
        chromatic_idx = CHROMATIC.index(self.root)
        for step in steps:
            if step == 'whole':
                chromatic_idx += 2
            elif step == 'half':
                chromatic_idx += 1
            if chromatic_idx >= 12:
                chromatic_idx -= 12
            scale.append(CHROMATIC[chromatic_idx])
        return scale

    def natural_minor_scale(self):
        steps = ['whole', 'half', 'whole', 'whole', 'half', 'whole', 'whole']
        scale = [self.root]
        chromatic_idx = CHROMATIC.index(self.root)
        for step in steps:
            if step == 'whole':
                chromatic_idx += 2
            elif step == 'half':
                chromatic_idx += 1
            if chromatic_idx >= 12:
                chromatic_idx -= 12
            scale.append(CHROMATIC[chromatic_idx])
        return scale

    def harmonic_minor_scale(self):
        steps = ['whole', 'half', 'whole', 'whole', 'half', 'augmented', 'half']
        scale = [self.root]
        chromatic_idx = CHROMATIC.index(self.root)
        for step in steps:
            if step == 'whole':
                chromatic_idx += 2
            elif step == 'half':
                chromatic_idx += 1
            elif step == 'augmented':
                chromatic_idx += 3
            if chromatic_idx >= 12:
                chromatic_idx -= 12
            scale.append(CHROMATIC[chromatic_idx])
        return scale

    def major_third(self, midi_root: int) -> int:
        midi_note = midi_root + 4

        return midi_note

    def minor_third(self, midi_root: int) -> int:
        midi_note = midi_root + 3

        return midi_note

    def diminished_fifth(self, midi_root: int):
        midi_note = midi_root + 6

    def perfect_fifth(self, midi_root: int):
        midi_note = midi_root + 7

        return midi_note

    def major_seventh(self, midi_root: int):
        midi_note = midi_root + 11

        return midi_note

    def minor_seventh(self, midi_root: int):
        midi_note = midi_root + 10

        return midi_note

    def octave(self, midi_root: int, up: bool = True):
        if up:
            midi_note = midi_root + 12
        else:
            midi_note = midi_root - 12
        return midi_note

    def triad(self, note: str, octave: int, type: str = 'Major'):
        root_idx = self.major.index(note)
        if root_idx >= 7:
            root_idx -= 7
            octave += 1

        chord = []
        midi_root = midi.note_to_number(self.major[root_idx], octave)
        chord.append(midi_root)

        if 'Major' in type:
            if '7' in type:
                chord.append(self.major_seventh(midi_root))
            chord.append(self.major_third(midi_root))
        elif 'Minor' in type:
            if '7' in type:
                chord.append(self.minor_seventh(midi_root))
            chord.append(self.minor_third(midi_root))
        elif 'Diminished' in type:
            chord.append(self.minor_third(midi_root))
            if 'Half' in type:
                chord.append(self.minor_seventh(midi_root))
            else:
                chord.append(self.diminished_fifth(midi_root))

        else:
            chord.append(self.perfect_fifth(midi_root))

        return chord

    def chord(self, note: int, octave: int, has_seventh: bool = False, has_octave: bool = False):
        # idx in scale
        if self.key_type == 'Major':
            scale = self.major
        elif self.key_type == 'Minor':
            scale = self.harmonic_minor

        root = scale[note]
        chord = []
        chord.append(midi.note_to_number(root, octave))

        three_scale_num, three_octave = note + 2, octave
        if three_scale_num >= 7:
            three_scale_num -= 7
        third = scale[three_scale_num]

        if increased_octave(root, third):
            three_octave += 1

        chord.append(midi.note_to_number(third, three_octave))

        five_scale_num, five_octave = note + 4, octave
        if five_scale_num >= 7:
            five_scale_num -= 7
        fifth = scale[five_scale_num]

        if increased_octave(root, fifth):
            five_octave += 1
        chord.append(midi.note_to_number(fifth, five_octave))

        if has_seventh:
            seventh_scale_num, seventh_octave = note + 6, octave
            if seventh_scale_num >= 7:
                seventh_scale_num -= 7
            seventh = scale[seventh_scale_num]

            if increased_octave(root, seventh):
                seventh_octave += 1
            chord.append(midi.note_to_number(seventh, seventh_octave))

        if has_octave:
            chord.append(midi.note_to_number(root, octave + 1))

        return chord


def increased_octave(root, note):
    if CHROMATIC.index(root) > CHROMATIC.index(note):
        return True
    return False
