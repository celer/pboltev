#!/usr/bin/env python3

import ssl
import time
import json
import os
import logging
import logging.handlers
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import obd
from obd import OBDStatus

from commands import ext_commands


class OBDIIConnectionError(Exception):
    pass


class CanError(Exception):
    pass


def obd_connect(portstr, baudrate, fast=False, timeout=30, max_attempts=3):
    connection_count = 0
    obd_connection = None
    while (obd_connection is None or obd_connection.status() != OBDStatus.CAR_CONNECTED) and connection_count < max_attempts:
        connection_count += 1
        # Establish connection with OBDII dongle
        obd_connection = obd.OBD(portstr=portstr,
                                 baudrate=baudrate,
                                 fast=fast,
                                 timeout=timeout)
        if (obd_connection is None or obd_connection.status() != OBDStatus.CAR_CONNECTED) and connection_count < max_attempts:
            logger.warning("{}. Retrying in {} second(s)...".format(obd_connection.status(), connection_count))
            time.sleep(connection_count)

    if obd_connection.status() != OBDStatus.CAR_CONNECTED:
        raise OBDIIConnectionError(obd_connection.status())
    else:
        return obd_connection


def query_command(connection, command, max_attempts=3):
    command_count = 0
    cmd_response = None
    exception = False
    valid_response = False
    while not valid_response and command_count < max_attempts:
        command_count += 1
        try:
            cmd_response = connection.query(command, force=True)
        except Exception:
            exception = True
        valid_response = not(cmd_response is None or cmd_response.is_null() or cmd_response.value is None or cmd_response.value == "?" or cmd_response.value == "" or exception)
        if not valid_response and command_count < max_attempts:
            logger.warning("No valid response for {}. Retrying in {} second(s)...".format(command, command_count))
            time.sleep(command_count)

    if not valid_response:
        raise ValueError("No valid response for {}. Max attempts ({}) exceeded."
                         .format(command, max_attempts))
    else:
        logger.info("Got response from command: {} ".format(command))
        return cmd_response

def query_charging_level(connection):
    # Set header to 7E4
    query_command(connection, ext_commands["CAN_HEADER_7E4"])
    # Set the CAN receive address to 7EC
    query_command(connection, ext_commands["CAN_RECEIVE_ADDRESS_7EC"])

    resp = query_command(connection, ext_commands["CHARGING_LEVEL"],3)

    return resp.value

def query_ac_voltage(connection):
    logger.info("**** Querying battery information ****")
    # Set header to 7E4
    query_command(connection, ext_commands["CAN_HEADER_7E4"])
    # Set the CAN receive address to 7EC
    query_command(connection, ext_commands["CAN_RECEIVE_ADDRESS_7EC"])

    resp = query_command(connection, ext_commands["AC_VOLTAGE"],3)

    return resp.value

def query_ac_current(connection):
    logger.info("**** Querying battery information ****")
    # Set header to 7E4
    query_command(connection, ext_commands["CAN_HEADER_7E4"])
    # Set the CAN receive address to 7EC
    query_command(connection, ext_commands["CAN_RECEIVE_ADDRESS_7EC"])

    resp = query_command(connection, ext_commands["AC_CURRENT"],3)

    return resp.value


def query_elec_coolant_temp(connection):
    # Set header to 7E4
    query_command(connection, ext_commands["CAN_HEADER_7E4"])
    # Set the CAN receive address to 7EC
    query_command(connection, ext_commands["CAN_RECEIVE_ADDRESS_7EC"])

    resp = query_command(connection, ext_commands["ELEC_COOLANT_TEMP"],3)

    return resp.value

def query_ambient_air_temp(connection):
    # Set header to 7E4
    query_command(connection, ext_commands["CAN_HEADER_7E4"])
    # Set the CAN receive address to 7EC
    query_command(connection, ext_commands["CAN_RECEIVE_ADDRESS_7EC"])

    resp = query_command(connection, ext_commands["AMBIENT_AIR_TEMP"],3)

    return resp.value


def query_bat_coolant_temp(connection):
    logger.info("**** Querying battery information ****")
    # Set header to 7E4
    query_command(connection, ext_commands["CAN_HEADER_7E4"])
    # Set the CAN receive address to 7EC
    query_command(connection, ext_commands["CAN_RECEIVE_ADDRESS_7EC"])

    resp = query_command(connection, ext_commands["BAT_COOLANT_TEMP"],3)

    return resp.value


def query_bat_soc(connection):
    logger.info("**** Querying battery information ****")
    # Set header to 7E4
    query_command(connection, ext_commands["CAN_HEADER_7E4"])
    # Set the CAN receive address to 7EC
    query_command(connection, ext_commands["CAN_RECEIVE_ADDRESS_7EC"])

    resp = query_command(connection, ext_commands["BAT_SOC"],3)

    return resp.value


def publish_data_mqtt(msgs,
                      hostname,
                      port,
                      client_id,
                      user,
                      password,
                      keepalive=60,
                      will=None):
    """Publish all messages to MQTT."""
    try:
        logger.info("Publish messages to MQTT")
        for msg in msgs:
            logger.info("{}".format(msg))

        publish.multiple(msgs,
                         hostname=hostname,
                         port=port,
                         client_id=client_id,
                         keepalive=keepalive,
                         will=will,
                         auth={'username': user, 'password': password},
                         #tls={'tls_version': ssl.PROTOCOL_TLS},
                         #protocol=mqtt.MQTTv311,
                         transport="tcp"
                         )
        logger.info("{} message(s) published to MQTT".format(len(msgs)))
    except Exception as err:
        logger.error("Error publishing to MQTT: {}".format(err), exc_info=False)


def main():
    console_handler = logging.StreamHandler()  # sends output to stderr
    console_handler.setFormatter(logging.Formatter("%(asctime)s %(name)-10s %(levelname)-8s %(message)s"))
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    file_handler = logging.handlers.TimedRotatingFileHandler(os.path.dirname(os.path.realpath(__file__)) + '/../obdii_data.log',
                                                             when='midnight',
                                                             backupCount=15
                                                             )  # sends output to obdii_data.log file rotating it at midnight and storing latest 15 days
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(name)-10s %(levelname)-8s %(message)s"))
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    logger.setLevel(logging.DEBUG)

    obd.logger.setLevel(obd.logging.DEBUG)
    # Remove obd logger existing handlers
    for handler in obd.logger.handlers[:]:
        obd.logger.removeHandler(handler)
    # Add handlers to obd logger
    obd.logger.addHandler(console_handler)
    obd.logger.addHandler(file_handler)

    with open(os.path.dirname(os.path.realpath(__file__)) + '/obdii_data.config.json') as config_file:
        config = json.loads(config_file.read())


    broker_address = config['mqtt']['broker']
    port = int(config['mqtt']['port'])
    user = config['mqtt']['user']
    password = config['mqtt']['password']
    topic_prefix = config['mqtt']['topic_prefix']

    print(broker_address,user,topic_prefix) 

    mqtt_msgs = []

    try:
        logger.info("=== Script start ===")

        connection = obd_connect(portstr=config['serial']['port'],
                                 baudrate=int(config['serial']['baudrate']),
                                 fast=False,
                                 timeout=30)

        # Print supported commands
        # DTC = Diagnostic Trouble Codes
        # MIL = Malfunction Indicator Lamp
        logger.debug(connection.print_commands())

        bolt_state={}
        try:
            bolt_state['charge_voltage']=query_ac_voltage(connection)
        except (ValueError, CanError) as err:
            logger.warning("**** Error querying ac voltage: {} ****"
                           .format(err), exc_info=False)
        try:
            bolt_state["charge_current"]=query_ac_current(connection)
        except (ValueError, CanError) as err:
            logger.warning("**** Error querying ac voltage: {} ****"
                           .format(err), exc_info=False)
        
        try:
            bolt_state["charge_level"]=query_charging_level(connection)
        except (ValueError, CanError) as err:
            logger.warning("**** Error querying ac voltage: {} ****"
                           .format(err), exc_info=False)
        
        try:
            bolt_state["battery_charge"]=query_bat_soc(connection)
        except (ValueError, CanError) as err:
            logger.warning("**** Error querying ac voltage: {} ****"
                           .format(err), exc_info=False)
        try:
            bolt_state["battery_coolant_temp"]=query_bat_coolant_temp(connection)
        except (ValueError, CanError) as err:
            logger.warning("**** Error querying ac voltage: {} ****"
                           .format(err), exc_info=False)
        try:
            bolt_state["electronics_coolant_temp"]=query_elec_coolant_temp(connection)
        except (ValueError, CanError) as err:
            logger.warning("**** Error querying ac voltage: {} ****"
                           .format(err), exc_info=False)
        try:
            bolt_state["ambient_air_temp"]=query_ambient_air_temp(connection)
        except (ValueError, CanError) as err:
            logger.warning("**** Error querying ac voltage: {} ****"
                           .format(err), exc_info=False)


        mqtt_msgs.extend([{'topic': topic_prefix + "state",
                           'payload': json.dumps(bolt_state),
                           'qos': 0,
                           'retain': True}]
                         )

    except OBDIIConnectionError as err:
        logger.error("OBDII connection error: {0}".format(err),
                     exc_info=False)
    except ValueError as err:
        logger.error("Error found: {0}".format(err),
                     exc_info=False)
    except CanError as err:
        logger.error("Error found reading CAN response: {0}".format(err),
                     exc_info=False)
    except Exception as ex:
        logger.error("Unexpected error: {}".format(ex),
                     exc_info=True)

    finally:
        publish_data_mqtt(msgs=mqtt_msgs,
                          hostname=broker_address,
                          port=port,
                          client_id="battery-data-script",
                          user=user,
                          password=password)
        if 'connection' in locals() and connection is not None:
            connection.close()
        logger.info("===  Script end  ===")


if __name__ == '__main__':
    logger = logging.getLogger('obdii')
    main()
