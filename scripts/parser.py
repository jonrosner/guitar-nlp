import glob
import os
import json
import logging
import re

def get_tab(text):
    t = text.split("window.UGAPP.store.page")[-1]
    t = t.split("window.UGAPP.store.i18n")[0]
    t = t[:-6]
    t = t[2:]
    d = json.loads(t)
    raw_tab = ""
    try:
        raw_tab = d["data"]["tab_view"]["wiki_tab"]["content"]
    except:
        pass
    tab = raw_tab.split("\n")
    strings = {"E|", "A|", "D|", "G|", "B|", "e|"}

    def belongs_to_tab(x):
        try:
            if x[0:2] in strings:
                return True
            else:
                return False
        except: 
            return False
    
    tab = filter(lambda x: belongs_to_tab(x), tab)

    # cleaning process
    cleaned_tab = []
    for line in tab:
        if len(line) != 0 and line[-1] != "|":
            splits = line.split("|")[0:-1]
            if len(splits) >= 2:
                line = "|".join(line.split("|")[0:-1]) + "|"
            else:
                line = line[0:-1] + "|"
        cleaned_tab.append(line)
    cleaned_tab = "\n".join(cleaned_tab)
    return cleaned_tab




def parse(solo_pages_folder, tabs_folder, cwd):
    path = os.path.join(cwd, solo_pages_folder, '*.html')
    ps = glob.glob(path)
    for p in ps:
        with open(p, 'r') as f:
            tab_path = os.path.join(cwd, tabs_folder, p.split("/")[-1])
            tab = get_tab(f.read())
            if tab != "":
                with open(tab_path, 'w+') as tab_f:
                    tab_f.write(tab)
                logging.info("Saved tab into {0}".format(tab_path))
            else:
                logging.info("Tab is empty {0}".format(tab_path))