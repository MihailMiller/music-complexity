import lzma
import math
import os
import sys
import csv
import statistics
from fractions import Fraction
from music21 import midi, note, chord, pitch, abcFormat, stream, converter, key
from music21.exceptions21 import StreamException

#path to one of the archives
midi_path = sys.argv[1]


def open_midi(midi_path):
    mf = midi.MidiFile()
    mf.open(midi_path)
    mf.read()
    mf.close()

    return midi.translate.midiFileToStream(mf)


def extract_notes(midi_stream):
    result = []
    for current_note in midi_stream.flat.notes:
        if isinstance(current_note, note.Note):
            result.append(max(0.0, current_note.pitch.pitchClass))
        elif isinstance(current_note, chord.Chord):
            for pitch in current_note.pitches:
                result.append(max(0.0, pitch.pitchClass))
    return result


def extract_notes_melody(midi_stream):
    notes = midi_stream.flat.notes
    off_set = []
    m_notes = []
    highest_notes = []
    
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
            for y in range(1, 5):
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
        highest_notes.append(max(0, int(i)))

    return highest_notes


def extract_ioi(midi_stream):
    ioi_list = []
    off_set = []
    notes = midi_stream.flat.notes
    
    for i in range(0, len(notes)):
        if notes[i].offset not in off_set:
            m_note = notes[i]
            off_set.append(m_note.offset)

    for i in range(1, len(off_set)):
        ioi = Fraction(off_set[i] - off_set[i - 1]).limit_denominator(4)
        ioi_list.append(ioi)

    return ioi_list


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
        #ignore intervals > 12 notes
        if abs(interval) <= 12:
            if interval not in interval_list:
                interval_list.append(interval)
            interval_seq.append(interval)

    for i in interval_list:
        p = interval_seq.count(i)/len(interval_seq)
        entr = p*(math.log2(p))
        result.append(entr)

    return result


with open(os.path.join(midi_path, 'evaluation.csv'), newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';')
    with open(os.path.join(midi_path, 'analysis.csv'), 'a') as f:
        output = 'TITLE' + ";" + 'YEAR_FOR_ANALYSIS' + ";" + 'TONAL_CERTAINTY_PIECE' + ";" + 'MEAN_TONAL_CERTAINTY_MEASURES' + ";" + 'PITCH_CLASS_ENTROPY_PIECE' + ";" + 'MEAN_PITCH_CLASS_ENTROPY_MEASURES' + ";" + 'MELODIC_INTERVAL_ENTROPY_PIECE' + ";" + 'MAX_MEAN_MELODIC_INTERVAL_ENTROPY_MEASURES' + ";" + 'IOI_ENTROPY_MEASURES' + ";" + 'MAX_MEAN_IOI_ENTROPY_MEASURES' + ";" + 'LENGTH' + "\n"
        print(output)
        f.write(output)

    for row in reader:
        if row['YEAR_FOR_ANALYSIS'] != "":
            midi_file = os.path.join(midi_path, row['TITLE'])
            if os.path.exists(midi_file):
                try:
                    midi_stream = converter.parse(os.path.join(midi_path, row['TITLE'])).quantize()
                    measures_count = len(midi_stream.measures(0,None)[0])

                    #get the tonalCertainty for the whole piece
                    k_piece = midi_stream.analyze('key').tonalCertainty()

                    #get the mean tonalCertainty for every 16 measures
                    first_measure = 0
                    last_measure = 16
                    
                    k_list_measures = []

                    if last_measure > measures_count:
                        mean_k_measures = k_piece
                    else:
                        while last_measure <= measures_count:
                            k_list_measures.append(midi_stream.measures(first_measure,last_measure).analyze('key').tonalCertainty())
                            first_measure = last_measure
                            last_measure += last_measure
                        
                        mean_k_measures = statistics.mean(k_list_measures)

                    #get the pitchClassEntropy for the whole piece
                    Hpc_piece = 0 - sum(pitch_entropy(extract_notes(midi_stream)))
                    
                    #get the mean pitchClassEntropy for every 16 measures
                    first_measure = 0
                    last_measure = 16

                    Hpc_list_measures = []
                    
                    if last_measure > measures_count:
                        mean_Hpc_measures = Hpc_piece
                    else:
                        while last_measure <= measures_count:
                            Hpc_list_measures.append(0 - sum(pitch_entropy(extract_notes(midi_stream.measures(first_measure,last_measure)))))
                            first_measure = last_measure
                            last_measure += last_measure

                        mean_Hpc_measures = statistics.mean(Hpc_list_measures)


                    midi_parts = midi_stream.parts.stream()

                    Hpi_list_piece = []
                    Hioi_list_piece = []

                    for midi_part in midi_parts:
                        Hpi_list_piece.append(0 - sum(pitch_interval_entropy(extract_notes_melody(midi_part))))
                        Hioi_list_piece.append(0 - sum(ioi_entropy(extract_ioi(midi_part))))

                    max_Hpi_piece = max(Hpi_list_piece)
                    max_Hioi_piece = max(Hioi_list_piece)

                    for midi_part in midi_parts:
                        first_measure = 0
                        last_measure = 16

                        Hpi_list_measures = []
                        mean_Hpi_measures = []
                        if last_measure > measures_count:
                            mean_Hpi_measures = max_Hpi_piece
                        else:
                            while last_measure <= measures_count:
                                Hpi_list_measures.append(0 - sum(pitch_interval_entropy(extract_notes_melody(midi_part.measures(first_measure,last_measure)))))
                                first_measure = last_measure
                                last_measure += last_measure

                            mean_Hpi_measures.append(statistics.mean(Hpi_list_measures))

                        first_measure = 0
                        last_measure = 16

                        Hioi_list_measures = []
                        mean_Hioi_measures = []
                        if last_measure > measures_count:
                            mean_Hioi_measures = max_Hpi_piece
                        else:
                            while last_measure <= measures_count:
                                Hioi_list_measures.append(0 - sum(ioi_entropy(extract_ioi(midi_part.measures(first_measure,last_measure)))))
                                first_measure = last_measure
                                last_measure += last_measure
                            
                            mean_Hioi_measures.append(statistics.mean(Hioi_list_measures))

                    max_mean_Hpi_measures = max(mean_Hpi_measures)
                    max_mean_Hioi_measures = max(mean_Hioi_measures)


                    with open(os.path.join(midi_path, 'analysis.csv'), 'a') as f:
                        output = row['TITLE'] + ";" + row['YEAR_FOR_ANALYSIS'] + ";" + str(k_piece) + ";" + str(mean_k_measures) + ";" + str(Hpc_piece) + ";" + str(mean_Hpc_measures) + ";" + str(max_Hpi_piece) + ";" + str(max_mean_Hpi_measures) + ";" + str(max_Hioi_piece) + ";" + str(max_mean_Hioi_measures) + ";" + row['LENGTH'] + "\n"
                        print(output)
                        f.write(output)
                    
                except StreamException:
                    print("StreamException on " + row['TITLE'])
                    
                continue
