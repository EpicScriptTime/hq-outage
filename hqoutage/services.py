import geo
import logging
import os
import tempfile
import zipfile

import requests

import utils

from entities import Outage


HQ_API_URL_VERSION = 'http://pannes.hydroquebec.com/pannes/donnees/v2_0_1/bisversion.json'
HQ_API_URL_MARKERS = 'http://pannes.hydroquebec.com/pannes/donnees/v2_0_1/bismarkers{}.json'
HQ_API_URL_POLYS = 'http://pannes.hydroquebec.com/pannes/donnees/v2_0_1/bispoly{}.kmz'

REQUESTS_TIMEOUT = 30


class OutageService():
    def __init__(self):
        self._logger = logging.getLogger()

        self.version = None
        self.data_polys_kml_filename = None
        self.data_markers = None
        self.polys = []
        self.outages = []

        self.tempdir = tempfile.TemporaryDirectory()

    def query_api_version(self):
        self._logger.debug('Requesting %s', HQ_API_URL_VERSION)

        r = requests.get(HQ_API_URL_VERSION, timeout=REQUESTS_TIMEOUT)

        utils.check_response_status(r)

        self.version = r.json()

    def query_api_polys(self):
        self._logger.debug('Requesting %s', self.get_polys_api_url())

        r = requests.get(self.get_polys_api_url(), stream=True, timeout=REQUESTS_TIMEOUT)

        utils.check_response_status(r)

        self._logger.debug('Saving to %s', self.get_polys_kmz_filename())

        with open(self.get_polys_kmz_filename(), 'wb') as stream:
            # shutil.copyfileobj(r.raw, stream)  # Somehow, that fails sometimes
            for chunk in r.iter_content(1024):
                stream.write(chunk)

        with zipfile.ZipFile(self.get_polys_kmz_filename()) as zip:
            file = zip.infolist()[0]
            self.data_polys_kml_filename = zip.extract(file, path=self.tempdir.name)

    def query_api_markers(self):
        self._logger.debug('Requesting %s', self.get_markers_api_url())

        r = requests.get(self.get_markers_api_url(), timeout=REQUESTS_TIMEOUT)

        utils.check_response_status(r)

        self.data_markers = r.json()

    def parse_polys(self):
        self._logger.debug('Parsing from %s', self.get_polys_kml_filename())

        self.polys = geo.get_geometries_from_kml(self.get_polys_kml_filename())

    def parse_outages(self):
        outages = []

        for marker in self.data_markers:
            outage = Outage.create_from_marker(marker)

            for poly in self.polys:
                if poly.Contains(outage.coord.point):
                    outage.poly = poly

            outages.append(outage)

        self.outages = outages

    def fetch_changes(self):
        pass

    def get_markers_api_url(self):
        return HQ_API_URL_MARKERS.format(self.version)

    def get_polys_api_url(self):
        return HQ_API_URL_POLYS.format(self.version)

    def get_polys_kmz_filename(self):
        return os.path.join(self.tempdir.name, 'bispoly.kmz')

    def get_polys_kml_filename(self):
        return self.data_polys_kml_filename
