import math
import os
from fractions import Fraction
from music21 import midi, note, chord, pitch, abcFormat, stream, converter, key
from music21.exceptions21 import StreamException

midi_path = "./corpus"


def open_midi(midi_path):
    mf = midi.MidiFile()
    mf.open(midi_path)
    mf.read()
    mf.close()

    return midi.translate.midiFileToStream(mf)


def extract_pitch_classes(midi_part):
    result = []
    for current_element in midi_part.flat.notes:
        if isinstance(current_element, note.Note):
            result.append(max(0.0, current_element.pitch.pitchClass))
        elif isinstance(current_element, chord.Chord):
            for pitch in current_element.pitches:
                result.append(max(0.0, pitch.pitchClass))
    return result


def extract_melody(midi_part):
    result = []
    notes = midi_part.flat.notes
    off_set = []
    m_notes = []
    
    for i in range(0, len(notes)):
        if notes[i].offset in off_set:
            continue

        if isinstance(notes[i], chord.Chord):
            chord_pitches = notes[i].pitches
            p = []
            for x in chord_pitches:
                p.append(x.ps)
            m_note = max(p)

        else:
            m_note = notes[i].pitch.ps

        try:
            #assumption: maximum of 12 notes with the same offset (can also be chords in music21)
            for y in range(1, 12):
                if notes[i + y].offset == notes[i].offset:
                    if isinstance(notes[i + y], chord.Chord):
                        chord_pitches = notes[i + y].pitches
                        p = []
                        for x in chord_pitches:
                            p.append(x.ps)
                        sec_max = max(p)
                    else:
                        sec_max = notes[i + y].pitch.ps
                    m_note = m_note if (m_note > sec_max) else sec_max
                    
        except IndexError:
            pass

        off_set.append(notes[i].offset)
        m_notes.append(m_note)

    for i in m_notes:
        result.append(max(0, int(i)))

    return result


def extract_ioi(midi_part):
    off_set = []
    notes = midi_part.flat.notes
    result = []
    for i in range(0, len(notes)):
        if notes[i].offset not in off_set:
            m_note = notes[i]
            off_set.append(m_note.offset)

    for i in range(1, len(off_set)):
        ioi = Fraction(off_set[i] - off_set[i - 1]).limit_denominator(4)
        result.append(ioi)

    return result


def ioi_entropy(eo):
    result = []
    duration_list = []

    for i in eo:
        if i not in duration_list:
            duration_list.append(i)

    for i in duration_list:
        p = eo.count(i)/len(eo)
        entr = p*(math.log2(p))
        result.append(entr)

    return result


def pitch_entropy(en):
    result = []
    note_list = []
    for cn in en:
        if cn not in note_list:
            note_list.append(cn)

    for cn in note_list:
        p = en.count(cn)/len(en)
        entr = p*(math.log2(p))
        result.append(entr)

    return result


def pitch_interval_entropy(en):
    interval_list = []
    interval_seq = []
    result = []
    for i in range(1, len(en)):
        interval = en[i] - en[i-1]
        #from a heuristic perspective intervals > 12 notes are mostly due to rests in the melody (the algorithm calculates the interval to a lower voice)
        if abs(interval) <= 12:
            if interval not in interval_list:
                interval_list.append(interval)
            interval_seq.append(interval)

    for i in interval_list:
        p = interval_seq.count(i)/len(interval_seq)
        entr = p*(math.log2(p))
        result.append(entr)

    return result


with open("output_raw.txt", 'w') as f:
    for file in os.listdir(midi_path):
        try:
            midi_complete = converter.parse(os.path.join(midi_path, file))
            midi_16 = midi_complete.measures(0,16)
            
            extracted_pitches_complete = extract_pitch_classes(midi_complete)
            extracted_melody_complete = extract_melody(midi_complete)
            extracted_ioi_complete = extract_ioi(midi_complete)
            
            extracted_pitches_16 = extract_pitch_classes(midi_16)
            extracted_melody_16 = extract_melody(midi_16)
            extracted_ioi_16 = extract_ioi(midi_16)
            
            pc_complete = 0 - sum(pitch_entropy(extracted_pitches_complete))
            pi_complete = 0 - sum(pitch_interval_entropy(extracted_melody_complete))
            ioi_complete = 0 - sum(ioi_entropy(extracted_ioi_complete))
            
            pc_16 = 0 - sum(pitch_entropy(extracted_pitches_16))
            pi_16 = 0 - sum(pitch_interval_entropy(extracted_melody_16))
            ioi_16 = 0 - sum(ioi_entropy(extracted_ioi_16))
            
            tc_complete = midi_complete.analyze('key').tonalCertainty()
            tc_16 = midi_16.analyze('key').tonalCertainty()
            
            year = os.path.basename(os.path.join(midi_path, file))[:4]
            
            output_complete = str(year) + "," + str(pc_complete) + "," + str(pi_complete) + "," + str(ioi_complete) + "," + str(tc_complete)
            output_16 = str(year) + "," + str(pc_16) + "," + str(pi_16) + "," + str(ioi_16) + "," + str(tc_16)

            print(output_complete)
            print(output_16)

            output_complete = output_complete + "\n"
            output_16 = output_16 + "\n"
            
            f.write(output_complete)
            f.write(output_16)

        except StreamException:
            print("StreamException on " + file)
            continue
