import json
import geo
import settings


class Location:
    def __init__(self, name, lat, lng):
        self.name = name

        self.coord = Coord(lat, lng)

    def __str__(self):
        return '{}: [{}, {}]'.format(self.name, self.coord.lat, self.coord.lng)


class Coord:
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng

        self.point = geo.get_point_from_lat_lng(lat, lng)

    def __str__(self):
        return '[{}, {}]'.format(self.lat, self.lng)

    def __getstate__(self):
        return self.lat, self.lng

    def __setstate__(self, state):
        self.lat, self.lng = state
        self.point = geo.get_point_from_lat_lng(self.lat, self.lng)

    @staticmethod
    def create_from_json(data):
        lng, lat = json.loads(data)

        coord = Coord(lat, lng)

        return coord


class Outage:
    def __init__(self):
        self.nb_customers = None
        self.started_at = None
        self.ended_at = None
        self.type_id = None
        self.coord = None
        self.status_id = None
        self.cause_id = None

        self.type = None
        self.status = None
        self.cause = None
        self.poly = None

    def __str__(self):
        return '{} affecting {} customers at {} from {} to {} caused by {}. {}. Poly available: {}'.format(
            self.type, self.nb_customers, self.coord, self.started_at, self.ended_at, self.cause, self.status,
            self.has_poly()
        )

    def format_alert(self, verb, location, distance=None):
        distance = ' ({}m away)'.format(distance) if distance else ''

        return '{} {} at {}{} from {} to {} caused by {}. Affecting {} customers. {}.'.format(
            self.type, verb, location.name, distance, self.started_at, self.ended_at, self.cause, self.nb_customers,
            self.status
        )

    def __eq__(self, other):
        return (isinstance(other, Outage)
            and self.nb_customers == other.nb_customers
            and self.started_at == other.started_at
            and self.ended_at == other.ended_at
            and self.type_id == other.type_id
            and self.coord.lat == other.coord.lat
            and self.coord.lng == other.coord.lng
            and self.status_id == other.status_id
            and self.cause_id == other.cause_id
        )

    def __getstate__(self):
        return self.nb_customers, self.started_at, self.ended_at, self.type_id, self.coord, self.status_id, \
               self.cause_id

    def __setstate__(self, state):
        self.nb_customers, self.started_at, self.ended_at, self.type_id, self.coord, self.status_id, \
            self.cause_id = state

        self.type = self.get_type_str()
        self.status = self.get_status_str()
        self.cause = self.get_cause_str()

    @staticmethod
    def create_from_marker(data):
        outage = Outage()
        outage.nb_customers = data[0]
        outage.started_at = data[1]
        outage.ended_at = data[2]
        outage.type_id = data[3]
        outage.coord = Coord.create_from_json(data[4])
        outage.status_id = data[5]
        outage.cause_id = data[6]

        outage.type = outage.get_type_str()
        outage.status = outage.get_status_str()
        outage.cause = outage.get_cause_str()

        return outage

    def has_poly(self):
        return True if self.poly else False

    def get_type_str(self):
        return settings.TYPE_MAPPING.get(self.type_id, settings.TYPE_MAPPING['default'])

    def get_cause_str(self):
        return settings.CAUSES_MAPPING.get(self.cause_id, settings.CAUSES_MAPPING['default'])

    def get_status_str(self):
        return settings.STATUS_MAPPING.get(self.status_id, settings.STATUS_MAPPING['default'])
