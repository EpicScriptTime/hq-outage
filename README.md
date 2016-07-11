hq-outage
=========

[![Travis](https://img.shields.io/travis/EpicScriptTime/hq-outage.svg)](https://travis-ci.org/EpicScriptTime/hq-outage)
[![Release](https://img.shields.io/github/release/EpicScriptTime/hq-outage.svg)](https://github.com/EpicScriptTime/hq-outage/releases)
[![MIT License](https://img.shields.io/badge/license-MIT-8469ad.svg)](https://tldrlegal.com/license/mit-license)

Python script that sends a SMS notification when an power outage occurred at a watched location using Hydro-Québec API.

Requirements
------------

* Python3, `pip` and `virtualenv` installed
* GDAL installed
* Twilio account credentials (for SMS)

Setup
-----

1. Clone this repository
2. Setup the virtualenv and activate it
3. Install the requirements
4. Create a directory named `logs`
5. Install GDAL module and bindings (see GDAL section)
6. Configure your watched locations (see Locations section)
7. Configure your Twilio credentials (see Settings section)

GDAL
----

First, ensure that you have installed the GDAL library on your system. The Debian package is called `libgdal-dev` and the Homebrew package is called `gdal`.

To confirm that you have installed GDAL properly, this command should return the installed version:

    gdal-config --version

Second, with your virtualenv activated, run the following command to install the GDAL Python package:

    pip install GDAL==$(gdal-config --version) --global-option=build_ext --global-option="$(gdal-config --cflags)"

If you get the error "Could not find a version that satisfies the requirement", try to select a previous version from the same major and minor version.

For example, if I'm trying to install `1.10.1` and it's not available, I should try `1.10.0`:

    pip install GDAL==1.10.0 --global-option=build_ext --global-option="$(gdal-config --cflags)"

Note that might still not do it. I was able to install GDAL on Debian Jessie, but not on Wheezy.

Locations
---------

Create a copy of the file `config.yml.dist` named `config.yml`.

Add as much locations as you want, following this example:

    locations:
      Home:
        lat: 45.123
        lng: -73.456
      Work:
        lat: 35.123
        lng: -75.456

Be sure to write valid YAML document.

Settings
--------

Create a copy of the file `hqoutage/settings.py.dist` named `hqoutage/settings.py`.

Configure your Twilio credentials and phone numbers, following this example:

    TWILIO = {
        'ACCOUNT_SID': 'AC00000000000000000000000000000000',
        'AUTH_TOKEN': '00000000000000000000000000000000',
        'FROM': ' +15555555555',
        'TO': '+15555555555',
    }

Check your Twilio account to get your Account SID and Auth Token.

Crontab
-------

Install this crontab to run the script every minute:

    * * * * * /path/to/env/bin/python /path/to/hq-outage/hqoutage/check.py --log --quiet
