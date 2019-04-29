import os
import logging

from scripts.scraper import scrape
from scripts.parser import parse
from scripts.marshaller import convert_tab_to_notes
from scripts.marshaller import convert_to_dataset, marshall, unmarshall, int_to_one_hot, one_hot_to_int
from scripts.lstm import Model


def init():
    cwd = os.getcwd()
    logging.basicConfig(format="%(asctime)s %(message)s",
                        filename='logs.log', level=logging.DEBUG)
    logging.info("Saving logs to {0}".format(cwd))
    list_pages_folder = os.path.join(cwd, "list_pages")
    if not os.path.exists(list_pages_folder):
        os.mkdir(list_pages_folder)
        logging.info(
            "Created list pages folder at {0}".format(list_pages_folder))
    solo_pages_folder = os.path.join(cwd, "solo_pages")
    if not os.path.exists(solo_pages_folder):
        os.mkdir(solo_pages_folder)
        logging.info(
            "Created solo pages folder at {0}".format(solo_pages_folder))
    tabs_folder = os.path.join(cwd, "tabs")
    if not os.path.exists(tabs_folder):
        os.mkdir(tabs_folder)
        logging.info("Created solo pages folder at {0}".format(tabs_folder))
    model_folder = os.path.join(cwd, "model")
    if not os.path.exists(model_folder):
        os.mkdir(model_folder)
        logging.info("Created model folder at {0}".format(model_folder))
    tabs_folder = "tabs"
    run(list_pages_folder, solo_pages_folder, tabs_folder, model_folder, cwd)


def run(list_pages_folder, solo_pages_folder, tabs_folder, model_folder, cwd):
    scrape(list_pages_folder, solo_pages_folder)
    parse(solo_pages_folder, "tabs", cwd)
    songs = convert_tab_to_notes(cwd, tabs_folder)
    logging.info("Number of solos: {0}\nNumber of notes: {1}".format(
        len(songs), sum(map(len, songs))))

    input_size = 32
    num_features = 187  # 31 (frets + symbols) * 6 (strings) + 1 (start symbol)
    step = 1
    epochs = 300
    units = 512
    batch_size = 128
    learning_rate = .005
    train = True

    model_path = os.path.join(model_folder, "weights.hdf5")
    dataset = convert_to_dataset(songs, input_size, num_features, step)
    m = Model(input_size, num_features, units, learning_rate)
    if not train:
        m.load(model_path)
    else:
        m.train(dataset, batch_size, epochs, model_path)
    m.generate_from_nothing(40, num_features, input_size)


if __name__ == "__main__":
    init()
