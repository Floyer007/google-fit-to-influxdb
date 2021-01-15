# google-fit-to-influxdb
is a short python3 script to import health-data from Google Fit into a [influxdb](https://www.influxdata.com/) database which is filled by [Home Assistant](https://www.home-assistant.io/).

## Why should I use it?
I'm using a *Mi Body Composition Scale 2* with an [Home Assistant Addon](https://github.com/lolouk44/xiaomi_mi_scale) to see all my data.
Since I wrote down my weight into the Google Fit app in the past I don't want to miss this data.

## How to get the data?
Luckily you're able to download all your Google data (at least here in Germany).<br>
Just follow the instructions on the following sites.
I just checked "Google Fit" for the export which took about an hour in my case.<br>
[Google-Help](https://support.google.com/accounts/answer/3024190)<br>
[Google-Takeout](https://takeout.google.com/)

Your daily data has one csv for every day and one for all days together.
I only wanted to parse one file, which is the last one.
It's called *Tägliche Zusammenfassungen.csv* in german. I asume it will be *Daily summaries.csv* in english.
Unfortunately we lose the time for the weight measurement in this file, which will be assumed via the *default_time_* strings.
Just rename your csv to *all.csv* and place it next to *import.py* or edit the variable *csv\_file* itself.

**! This script is only tested with the big summarizing csv-file and assumes a modified schema for the HA to influxdb saving !**

**Please edit the schema *datapoint* for your needs.**

## HomeAssistant to influxdb modifications
My [Home Assistant](https://www.home-assistant.io/) configuration looks through a [modification](https://github.com/home-assistant/core/issues/34536#issuecomment-641506373) as followed:

influxdb:
  host: localhost
  port: 8086
  database: home_assistant
  default_measurement: state
  tags_attributes:
    - unit_of_measurement
  component_config_domain:
    device_tracker:
      override_measurement: device_tracker
    sensor:
      override_measurement: sensor
  include:
    entities:
      - sensor.my_weight

# Usage
Edit the configuration-variables.
Especially the *influxdb* ones.
To adapt the influxdb-schema please edit *datapoint* which is optimized for a modification like shown before.

A additional tag called *external_source_import* ensures a tracing of this import.

If you edit everything and did a dryrun (*dryrun* = True)

``$ ./import.py``

you can change the variable *dryrun* to False and run the script again.
Now everything will be written to your database.

# Installation

Install python3.
Then install the following:

### influxdb for Python

``$ python3 -m pip install influxdb``

https://www.influxdata.com/blog/getting-started-python-influxdb/

### Execution
Whitin linux you have to ensure, that the file is excecutable:

``$ chmod +x import.py``

Please make a Pull-Request or open an Issue if something is missing.
