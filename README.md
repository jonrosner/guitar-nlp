# Guitar-NLP

A Natural Language Processing approach to generating guitar solos in tabulature format.

## Run locally

I advise on using a virtual environment to run it locally.

```bash
$ cd guitar-nlp
$ virtualenv nlp-venv
Installing setuptools, pip, wheel...done.
$ source nlp-venv/bin/activate
$ pip install -r requirements.txt
Installing collected packages...
Successfully installed Keras-2.2.4...
$ python main.py
```

This will start the scraping, parsing and then the training process.

All hyperparameters can be tuned in the main.py.
Logs will be saved into `logs.log`.

## Coming soon

A web interface and an API to access the neural network.
