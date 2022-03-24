from obd import OBDCommand
from obd.protocols import ECU
from obd.decoders import raw_string, percent
from decoders import *

# flake8: noqa

ext_commands = {
#                                          name                       description                                            cmd        bytes decoder               ECU         fast
    'CAN_HEADER_7E4':          OBDCommand("CAN_HEADER_7E4",          "Set CAN module ID to 7E4 - BMS battery information"  , b"ATSH7E4" ,  0, raw_string          , ECU.UNKNOWN, False),
    'CAN_HEADER_7C6':          OBDCommand("CAN_HEADER_7C6",          "Set CAN module ID to 7C6 - Odometer information"     , b"ATSH7C6" ,  0, raw_string          , ECU.UNKNOWN, False),
    'CAN_HEADER_7E2':          OBDCommand("CAN_HEADER_7E2",          "Set CAN module ID to 7E2 - VMCU information"         , b"ATSH7E2" ,  0, raw_string          , ECU.UNKNOWN, False),
    'CAN_HEADER_7A0':          OBDCommand("CAN_HEADER_7A0",          "Set CAN module ID to 7A0 - TPMS information"         , b"ATSH7A0" ,  0, raw_string          , ECU.UNKNOWN, False),
    'CAN_HEADER_7E6':          OBDCommand("CAN_HEADER_7E6",          "Set CAN module ID to 7E6 - External temp information", b"ATSH7E6" ,  0, raw_string          , ECU.UNKNOWN, False),

    'CAN_RECEIVE_ADDRESS_7EC': OBDCommand("CAN_RECEIVE_ADDRESS_7EC", "Set the CAN receive address to 7EC"                  , b"ATCRA7EC",  0, raw_string          , ECU.UNKNOWN, False),
    'CAN_RECEIVE_ADDRESS_7EA': OBDCommand("CAN_RECEIVE_ADDRESS_7EA", "Set the CAN receive address to 7EA"                  , b"ATCRA7EA",  0, raw_string          , ECU.UNKNOWN, False),
    'CAN_RECEIVE_ADDRESS_7A8': OBDCommand("CAN_RECEIVE_ADDRESS_7A8", "Set the CAN receive address to 7A8"                  , b"ATCRA7A8",  0, raw_string          , ECU.UNKNOWN, False),
    'CAN_RECEIVE_ADDRESS_7EE': OBDCommand("CAN_RECEIVE_ADDRESS_7EE", "Set the CAN receive address to 7EE"                  , b"ATCRA7EE",  0, raw_string          , ECU.UNKNOWN, False),

    'CAN_FILTER_7CE':          OBDCommand("CAN_FILTER_7CE",          "Set the CAN filter to 7CE"                           , b"ATCF7CE" ,  0, raw_string          , ECU.UNKNOWN, False),
    
    'BAT_SOC':                 OBDCommand("BAT_SOC",                "Battery State Of Charge"          , b"228334"    ,  0, bat_soc, ECU.ALL    , False),  
    'AMBIENT_AIR_TEMP':                 OBDCommand("AMBIENT_AIR_TEMP",                "Ambient Air Temp"          , b"220046"    ,  0, coolant_temp, ECU.ALL    , False),  
    'BAT_COOLANT_TEMP':                 OBDCommand("BAT_COOLANT_TEMP",                "Battery Coolant Temp"          , b"2241A4"    ,  0, coolant_temp, ECU.ALL    , False),  
    'ELEC_COOLANT_TEMP':                 OBDCommand("ELEC_COOLANT_TEMP",                "Electronics Coolant Temp"          , b"2241A4"    ,  0, coolant_temp, ECU.ALL    , False),  
    'AC_VOLTAGE':              OBDCommand("AC_VOLTAGE",                "AC Voltage"          , b"224368"    ,  0, ac_voltage, ECU.ALL    , False), 
    'AC_CURRENT':              OBDCommand("AC_CURRENT",                "AC Current"          , b"224369"    ,  0, ac_current, ECU.ALL    , False), 
    'CHARGING_LEVEL':              OBDCommand("CHARGING_LEVEL",                "Charging Level"          , b"224531"    ,  0, charging_level, ECU.ALL    , False), 
   

}
