import utils

from entities import Location


class StateManager:
    def __init__(self):
        self.filename = utils.STATE_FILE
        self.state = {
            'version': 0,
            'outages': {},
        }

    def load(self):
        state = utils.load_pickle(self.filename)

        if state:
            self.state = state

    def save(self):
        utils.save_pickle(self.state, self.filename)

    def get_version(self):
        return self.state['version']

    def update_version(self, version):
        self.state['version'] = version

    def get_outage(self, location):
        return self.state['outages'].get(location.name)

    def update_outage(self, location, outage):
        self.state['outages'][location.name] = outage

    def delete_outage(self, location):
        del self.state['outages'][location.name]


class LocationManager:
    def __init__(self):
        self.locations = {}

    def load(self):
        data = utils.load_yaml(utils.CONFIG_FILE)

        for key, value in data.get('locations').items():
            location = Location(key, value.get('lat'), value.get('lng'))

            self.locations[key] = location

    def get(self, name):
        return self.locations.get(name)

    def get_all(self):
        return self.locations.values()
