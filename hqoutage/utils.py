import datetime
import os
import pickle

import yaml

from twilio import TwilioRestException
from twilio.rest import TwilioRestClient

import settings


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

STATE_FILE = os.path.join(PACKAGE_DIR, 'state.pickle')
CONFIG_FILE = os.path.join(BASE_DIR, 'config.yml')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')


def load_pickle(filename):
    if os.path.isfile(filename):
        with open(filename, 'rb') as stream:
            return pickle.load(stream)

    return None


def save_pickle(data, filename):
    with open(filename, 'wb') as stream:
        pickle.dump(data, stream)


def load_yaml(filename):
    with open(filename, 'r') as stream:
        return yaml.load(stream)


def check_response_status(response):
    if response.status_code != 200:
        raise Exception('Request at "{}" return HTTP code {}'.format(response.url, response.status_code))


def notify(message):
    if not settings.DRY_RUN:
        _send_sms('HQ-OUTAGE: {} ({})'.format(message, get_current_timestamp()))


def _send_sms(body):
    try:
        client = TwilioRestClient(settings.TWILIO['ACCOUNT_SID'], settings.TWILIO['AUTH_TOKEN'])
        message = client.messages.create(body=body, to=settings.TWILIO['TO'], from_=settings.TWILIO['FROM'])

        return message.sid
    except TwilioRestException as e:
        raise e


def get_current_date():
    return datetime.datetime.now().strftime('%Y%m%d')


def get_current_timestamp():
    return datetime.datetime.now().strftime('%y%m%d%H%M%S')


def get_log_filename():
    return os.path.join(LOGS_DIR, 'hqoutage{}.log'.format(get_current_date()))
