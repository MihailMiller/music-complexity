# Analysis of the complexity of musical dimensions in European art music
This repository serves to summarize the artifacts that resulted from a student research project on the complexity of European art music (often summarized under the term classical music).

It contains the Python-script used to extract the necessary information from a given MIDI corpus.
The script was run on a constructed corpus from the "DisklavierTM World"-Archives, which is public at: http://www.kuhmann.com/Yamaha.htm .
The results of the feature extraction can be found in corpus/extracted_features.csv.

The methodology for determining the complexity of musical dimensions implements Schannon's entropy measure and is based on the work of **Madsen and Widmer (2015)**:

TY - JOUR
AU - Madsen, Søren
AU - Widmer, Gerhard
PY - 2015/07/15
SP - 
T1 - A complexity-based approach to melody track identification in MIDI files
JO - Proceedings of the International Workshop on Artificial Intelligence and Music
ER -  

The chosen categorization of musical dimensions is based on the work of **Conklin (2006)**:

TY - JOUR
AU - Conklin, Darrell
PY - 2006
DA - 2006/12/01
TI - Melodic analysis with segment classes
JO - Machine Learning
SP - 349
EP - 360
VL - 65
IS - 2
AB - This paper presents a representation for melodic segment classes and applies it to music data mining. Melody is modeled as a sequence of segments, each segment being a sequence of notes. These segments are assigned to classes through a knowledge representation scheme which allows the flexible construction of abstract views of the music surface. The representation is applied to sequential pattern discovery and to the statistical modeling of musical style.
SN - 1573-0565
UR - https://doi.org/10.1007/s10994-006-8712-x
DO - 10.1007/s10994-006-8712-x
ID - Conklin2006
ER - 
