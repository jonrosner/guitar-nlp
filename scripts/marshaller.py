import re
import logging
import glob
import os
import numpy as np
from sklearn.utils import shuffle

NUM_FRETS = 24  # 0 to 23
symbols = ["/", "\\", "h", "p", "~", "x", "b", "r"]
nums = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}
default_strings = ["e|--", "B|--", "G|--", "D|--", "A|--", "E|--"]


def convert_tab_to_notes(cwd, tabs_folder):
    path = os.path.join(cwd, tabs_folder, '*.html')
    tab_files = glob.glob(path)
    result = []
    for tab_file in tab_files:
        tab_path = os.path.join(cwd, "tabs", tab_file.split("/")[-1])
        with open(tab_file, 'r') as f:
            tab = f.read()
            note_array = marshall(tab, tab_path)
            # in case sth went wrong do not use it
            if len(note_array) > 0:
                result.append(note_array)
    return result


# string tab -> int array
def marshall(tab, name):
    result = []
    if not len(tab.split("\n")) % 6 == 0:
        logging.info("Wrong format of {0}".format(name))

    # 1. go through each tab-line (6 pair) and search for note
    all_lines = tab.split("\n")
    tab_lines = []
    num_tab_lines = len(all_lines) // 6
    for i in range(num_tab_lines):
        tab_lines.append(all_lines[i*6:i*6+6])
    for tab_line in tab_lines:
        # go from left to right, from top to bottom
        char = 0
        while char < len(tab_line[0]):
            for current_string in range(6):
                # check if we found a note, if yes loop until note ends
                i = char
                note = ""
                while i < len(tab_line[current_string]) and tab_line[current_string][i] in nums and len(note) < 2:
                    note += tab_line[current_string][i]
                    i += 1
                if note == "" and i < len(tab_line[current_string]):
                    if tab_line[current_string][i] in symbols:
                        note = tab_line[current_string][i]
                        i += 1
                if note != "":
                    # right now voicings are forbidden
                    char = i - 1
                    # 2. convert this note to integer
                    out_of_range = False
                    try:
                        out_of_range = int(note) > NUM_FRETS
                    except:
                        pass
                    if out_of_range:
                        # some tabs are malformed and 97 should be eg. 9\7
                        result.append(note_to_int(note[0], current_string))
                        result.append(note_to_int(note[1], current_string))
                    else:
                        result.append(note_to_int(note, current_string))
                    break
            char += 1
    return result


# int array -> string tab
def unmarshall(notes_as_ints):
    tab = ""
    strings = default_strings.copy()
    for int_note in notes_as_ints:
        fret, string = int_to_note(int_note)
        if fret == 0 and string == 0:
            print("THIS IS A LOW E")
        for i in range(len(strings)):
            if string == i:
                strings[i] += (fret + "-")
            else:
                strings[i] += ("-" * (len(fret)+1))
    strings = [s + "-|" for s in strings]
    tab = "\n".join(strings)
    return tab


def note_to_int(note, string):
    int_note = 0
    try:
        int_note = int(note)
    except:
        int_note = NUM_FRETS + symbols.index(note) - 1
    result = int_note + int(string)*(NUM_FRETS + len(symbols) - 1) + 1
    return result


def int_to_note(i):
    if i == 0:
        return (-1, -1)
    fret = (i - 1) % (NUM_FRETS + len(symbols) - 1)
    if fret >= NUM_FRETS:
        fret = symbols[fret - NUM_FRETS + 1]
    return (str(fret), i // (NUM_FRETS + len(symbols) - 1))


def int_to_one_hot(x, num_features):
    v = [0] * num_features
    v[x] = 1
    return np.array(v)


def one_hot_to_int(x):
    x_re = np.reshape(x, (-1,))
    return np.asscalar(np.where(x_re == 1)[0])


def ints_to_onehots(arr, num_features):
    return np.array(list(map(lambda x: int_to_one_hot(x, num_features), arr)))


def onehots_to_ints(arr):
    return list(map(one_hot_to_int, arr))


def onehots_to_notes(arr):
    intermediate = onehots_to_ints(arr)
    result = list(map(int_to_note, intermediate))
    return result


def count_n_grams(X, input_size):
    n_grams = {}
    for x in X:
        i = ".".join(map(str, onehots_to_ints(x)))
        try:
            n_grams[i] += 1
        except:
            n_grams[i] = 1
    print("N-grams", len(n_grams.keys()))
    print("Avg num of occurences", sum(
        list(n_grams.values())) / len(n_grams.values()))


def convert_to_dataset(songs, input_size, num_features, step):
    X = []
    Y = []
    for song in songs[0:200]:
        add_start = [0] * (input_size) + song
        one_hots = list(
            map(lambda x: int_to_one_hot(x, num_features), add_start))
        for i in range(0, len(add_start) - input_size, step):
            X.append(one_hots[i:i+input_size])
            Y.append(one_hots[i+input_size])
    count_n_grams(X, input_size)
    X, Y = shuffle(X, Y, random_state=0)
    return {
        "X": np.array(X),
        "Y": np.array(Y)
    }
