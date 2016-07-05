import getopt
import logging
import logging.handlers
import sys

import settings
import utils

from services import OutageService
from managers import StateManager, LocationManager


DISTANCE_THRESHOLD = 500  # In meters


def perform_check():
    logger = logging.getLogger()

    logger.info('Starting hq-outage')

    try:
        if settings.DRY_RUN:
            logger.info('Running check.py in dry-run (not sending any SMS)')

        locations = LocationManager()
        manager = StateManager()
        service = OutageService()

        logger.info('Fetching all locations')
        locations.load()

        logger.info('Loading previous state')
        manager.load()

        logger.info('Querying version from API')
        service.query_api_version()

        if not settings.FORCE and service.version == manager.get_version():
            logger.info('Version has not changed, skipping')
        else:
            logger.info('Querying polys and markers from API')
            service.query_api_polys()
            service.query_api_markers()

            logger.info('Parsing outages from data')
            service.parse_polys()
            service.parse_outages()

            for location in locations.get_all():
                logger.debug('Performing check of %s', location.name)

                matched_outage = None
                distance = None

                for outage in service.outages:
                    distance = None

                    if outage.has_poly():
                        if outage.poly.Contains(location.coord.point):
                            logger.debug('Matching outage found for %s: %s', location.name, outage)
                            matched_outage = outage
                            break

                    distance = int(outage.coord.point.Distance(location.coord.point))

                    if distance < DISTANCE_THRESHOLD:
                        logger.debug('Matching outage found for %s at %s meter away: %s', location.name, distance,
                                     outage)
                        matched_outage = outage
                        break

                saved_outage = manager.get_outage(location)

                if matched_outage:
                    if saved_outage:
                        if matched_outage != saved_outage:
                            logger.info('Updated outage found for %s', location.name)
                            utils.notify(matched_outage.format_alert('updated', location, distance))

                            manager.update_outage(location, matched_outage)
                        else:
                            logger.info('Unchanged outage found for %s, skipping', location.name)
                    else:
                        logger.info('New outage found for %s', location.name)
                        utils.notify(matched_outage.format_alert('occurred', location, distance))

                        manager.update_outage(location, matched_outage)
                else:
                    if saved_outage:
                        logger.info('Resolved outage found for %s', location.name)
                        utils.notify(saved_outage.format_alert('resolved', location, None))

                        manager.delete_outage(location)
                    else:
                        logger.info('No outage found for %s', location.name)

        manager.update_version(service.version)

        logger.info('Saving current state')
        manager.save()

    except Exception as e:
        if logger.isEnabledFor(logging.DEBUG):
            logger.exception(e)
        else:
            logger.error(e)
        logger.fatal('Exception occurred while performing a check')

        utils.notify('Exception occurred while performing a check.')

    logger.info('Finished hq-outage')


def main():
    opts, args = getopt.getopt(sys.argv[1:], 'l:n:f:v:q', ['log', 'dry-run', 'force', 'debug', 'quiet'])

    log_to_file = False

    logging_filename = utils.get_log_filename()
    logging_format = '%(asctime)s [%(levelname)s] %(message)s'
    logging_level = logging.INFO

    logging.getLogger("requests").setLevel(logging.WARNING)

    for opt in opts:
        if opt[0] in ('-l', '--log'):
            log_to_file = True
        elif opt[0] in ('-n', '--dry-run'):
            settings.DRY_RUN = True
        elif opt[0] in ('-f', '--force'):
            settings.FORCE = True
        elif opt[0] in ('-d', '--debug'):
            logging_level = logging.DEBUG
        elif opt[0] in ('-q', '--quiet'):
            logging_level = logging.WARNING

    if log_to_file:
        logging.basicConfig(filename=logging_filename, format=logging_format, level=logging_level)
    else:
        logging.basicConfig(format=logging_format, level=logging_level)

    perform_check()


if __name__ == '__main__':
    main()
