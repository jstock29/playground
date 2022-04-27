import io
import random

import pretty_midi
import streamlit as st
import magenta
import note_seq
import numpy as np
import fluidsynth

from note_seq.protobuf import music_pb2
from scipy.io import wavfile

import midi
import music_theory
from music_theory import Key

MIDI_RANGE = range(21, 108)


def main():
    print('----------------------------------------')
    seq = music_pb2.NoteSequence()
    col1, col2, col3 = st.columns(3)
    time = 0.0
    notes = []
    octave = 4
    with col1:
        key_selection = st.selectbox('Key', midi.NOTES)
        key_type = st.radio('Type', ['Major', 'Minor'], 0)
        key = Key(key_selection, key_type)
    with col2:
        duration = st.slider('Measures', 1, 32, value=4)
        n_notes = duration/4
    with col3:
        tempo = st.number_input('Tempo', 1, 300, 80)
        quarter_note = music_theory.bpm_to_quarter_note(tempo) / 1000

    col4, col5, col6 = st.columns(3)
    with col4:
        instrument = st.selectbox('Instrument', midi.INSTRUMENTS)
        midi_instrument = midi.instrument_to_program(instrument)

    root_idx = 0
    note_idx = root_idx
    chords = []
    for step in range(n_notes):

        if note_idx >= 7:
            note_idx -= 7
            octave += 1


        # Build chords here
        if step == n_notes - 1:
            # Resolve to root
            note_idx = 0
        chord = key.chord(note_idx, octave, has_seventh=False, has_octave=True)
        chords.append(chord)
        for note in chord:
            seq.notes.add(pitch=note, start_time=time, end_time=time + quarter_note, velocity=50, is_drum=False,
                          instrument=midi_instrument, program=midi_instrument)
        note_idx = next_chord(note_idx, key)
        time += quarter_note
    note_seq.sequence_proto_to_midi_file(seq, f'outputs/seq.mid')

    with st.spinner(f"Transcribing"):
        midi_data = pretty_midi.PrettyMIDI('outputs/seq.mid')
        audio_data = midi_data.fluidsynth()
        audio_data = np.int16(
            audio_data / np.max(np.abs(audio_data)) * 32767 * 0.9
        )  # -- Normalize for 16 bit audio https://github.com/jkanner/streamlit-audio/blob/main/helper.py

        virtualfile = io.BytesIO()
        wavfile.write(virtualfile, 44100, audio_data)

    st.audio(virtualfile)
    st.download_button('Download', virtualfile, file_name='song.wav', mime='audio/vnd.wav')
    st.line_chart(chords)
    return


def next_chord(prev_idx: int, key: Key) -> int:
    direction = int(round(np.random.normal(scale=5), 0))
    print(direction)

    if key.key_type == 'Major':

        next_idx = prev_idx + direction
        if next_idx >= 8:
            next_idx -= 8
        if next_idx <= -8:
            next_idx += 8

    elif key.key_type == 'Minor':
        prev_root = key.harmonic_minor[prev_idx]
        cof_idx = music_theory.CIRCLE_OF_FIFTHS.index(prev_root)
        print(prev_root, cof_idx)
        next_root = music_theory.CIRCLE_OF_FIFTHS[cof_idx + direction]
        print(next_root)
        next_idx = key.harmonic_minor.index(next_root)

    return next_idx


if __name__ == '__main__':
    main()
