#!/usr/bin/env python3

#MIT License

#Copyright (c) 2021 Florian Völker

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

###############################################################################
#influxdb connection inspired by Noah Crowley https://www.influxdata.com/blog/getting-started-python-influxdb/
#!!!!!!! This script assumes a modified HomeAssistant schema: https://github.com/home-assistant/core/issues/34536#issuecomment-641506373
###############################################################################

from influxdb import InfluxDBClient
import csv

###############################################################################
# Configuration
dryrun = True #To test the csv without writing to influxdb
verbose = True #Output each datapoint with date, weight and bmi

calculate_bmi = True #Don't forget to edit the height!
height = 1.49 #[m] Necessary to calc your bmi

csv_file = "all.csv"
entity_id = "my_weight" #HomeAssistant entity_id for the scale
friendly_name_str = "My Weight"

influxdb_host = "localhost"
influxdb_port = 8086 #default 8086
influxdb_db = "home_assistant"
###############################################################################
# Since the csv with all days doesn't include a timestamp we have to create our own
default_time_influx = "T12:00:00.000000Z"
default_time_ha = " 12:00:00.000000"
default_timestamp = "120000.000"
###############################################################################
datapoint_counter = 0 #Just for a statistic output at the end.
###############################################################################

client = InfluxDBClient(host=influxdb_host, port=influxdb_port)
#If there is a password protection for the database please use the following definition:
#client = InfluxDBClient(host=influxdb_host, port=influxdb_port, username='myuser', password='mypass' ssl=True, verify_ssl=True)

client.switch_database(influxdb_db)

def bmi_calc(weight, height):
    bmi = weight / (height **2)
    bmi = round(bmi, 2)
    return bmi

def datetime_create_influx(date):
    datetime = date + default_time_influx
    return datetime

def datetime_create_ha(date):
    datetime = date + default_time_ha
    return datetime

def datetime_create_timestamp(date):
    date = date.replace('-', '')
    datetime = date + default_timestamp
    return datetime

###############################################################################
# Start to parse the csv-file
with open(csv_file, newline='') as csvfile:
    filereader = csv.reader(csvfile, delimiter=',', quotechar='|')
    next(filereader) #skip the first csv-line which includes the header
    for row in filereader:
        test_weight = row[1]

        if test_weight != '': #Skip the dataset if there is no mean weight available
            datapoint_counter += 1
            weight = round(float(row[1]),2)
            date = row[0]

            if calculate_bmi:
                bmi = bmi_calc(weight, height)
            else:
                bmi = None

            influx_datetime = datetime_create_influx(date)
            ha_timestamp_str = datetime_create_ha(date)
            ha_timestamp = float(datetime_create_timestamp(date))

            datapoint = [
                    {
                    "measurement": "sensor",
                    "tags":{
                      "unit_of_measurement": "kg",
                      "domain": "sensor",
                      "entity_id": entity_id,
                      "external_source_import": "google-fit"
                    },
                    "fields":{
                      "value": weight,
                      "weight": weight,
                      "bmi": bmi,
                      "timestamp": ha_timestamp,
                      "timestamp_str": ha_timestamp_str,
                      "weight_unit_str": "kg",
                      "friendly_name_str": friendly_name_str,
                      "icon_str": 'mdi:scale-bathroom',
                      "visceral_fat": None,
                      "water": None,
                      "lean_body_mass": None,
                      "metabolic_age": None,
                      "muscle_mass": None,
                      "on": None,
                      "protein": None,
                      "body_fat": None,
                      "body_type_str": None,
                      "bone_mass": None,
                      "device_class_str": None,
                      "basal_metabolism": None
                    },
                    "time": influx_datetime,
                    }
            ]

            if verbose:
                print(date)
                print(weight)
                print(bmi)
                #print(ha_timestamp)
                #print(ha_timestamp_str)
                #print(influx_datetime)
                print("----------")

            if not dryrun:
                client.write_points(datapoint)

print("Imported datasets: " + str(datapoint_counter))
client.close()
