import yaml
import logging


class C(object):
    ##########################################################################
    #
    # Only put values here that can be overridden in zenoss_defaults.yaml
    #
    ##########################################################################
    API_URI_HOST = 'localhost'
    API_URI_DOMAIN = 'localdomain'
    SSL_VERIFY = True

    # special-cases: Allow the user to override, but default is in the API_KEYWORD_DEFAULTS
    SNMP_COMMUNITY = ''
    SNMP_PORT = None
    ZENOSS_COLLECTOR = None

    # These values for these variables are set at the end of the file.
    # Declaring them here so that the IDE can find them.
    # (Prevent the IDE from complaining about undeclared variables)
    ERROR_CREDENTIALS_DICT_FORMAT = None
    ERROR_CREDENTIALS_LIST_FORMAT = None
    ERROR_CREDENTIALS_STR_FORMAT = None
    ERROR_CREDENTIALS_UNKNOWN_FORMAT = None
    ERROR_INVALID_HOSTNAME_GOT_S = None

    ERROR_EXPECTED_S_GOT_S = None

    ERROR_API_S_UNSUCCESSFUL_GOT_S = None
    ERROR_VALUES_S_NO_MATCH_S = None

    API_URI = None
    API_ENDPOINT = None
    API_DEVICES = None

    # API POST Data Keywords
    API_METHOD = None
    API_ACTION = None
    API_DATA = None
    API_TID = None
    API_DEVICE_NAME = None
    API_DEVICE_CLASS = None
    API_COLLECTOR = None
    API_MODEL = None
    API_TITLE = None
    API_PRODUCTION_STATE = None
    API_PRIORITY = None
    API_SNMP_COMMUNITY = None
    API_SNMP_PORT = None
    API_TAG = None
    API_RACK_SLOT = None
    API_SERIAL_NUMBER = None
    API_HW_MANUFACTURER = None
    API_HW_PRODUCT_NAME = None
    API_OS_MANUFACTURER = None
    API_OS_PRODUCT_NAME = None
    API_COMMENTS = None
    API_ID = None
    API_TARGET_UID = None
    API_QUERY = None
    API_TEMPLATE_UID = None
    API_NAME = None
    API_TYPE = None
    API_UID = None
    API_DATA_SOURCE_UID = None
    API_NODE_TYPE = None
    API_OID = None
    API_DIR = None
    API_SORT = None
    API_START = None
    API_PAGE = None
    API_LIMIT = None
    API_THRESHOLD_TYPE = None
    API_THRESHOLD_ID = None
    API_DATA_POINTS = None
    API_GRAPH_DEFINITION_ID = None
    API_MINY = None
    API_MAXY = None
    API_DATA_POINT_UID = None
    API_GRAPH_UID = None
    API_INCLUDE_THRESHOLDS = None
    API_UNITS = None
    API_LINE_TYPE = None
    API_RPN = None
    API_KEYS = None
    API_DEVICE_UID = None
    API_TEMPLATE_ID = None
    API_TEMPLATE_IDS = None
    API_RESULT = None
    API_SUCCESS = None
    API_MAX_VAL = None
    API_MIN_VAL = None
    API_NODE_CONFIG = None

    # Production States
    PRODUCTION_STATE_PRODUCTION = None
    PRODUCTION_STATE_PRE_PRODUCTION = None
    PRODUCTION_STATE_TEST = None
    PRODUCTION_STATE_MAINTENANCE = None
    PRODUCTION_STATE_DECOMMISSIONED = None

    API_KEYWORD_DEFAULTS = {}

    # API Device Classes:
    API_DEVICE_CLASS_CISCO_UCS = None
    API_DEVICE_CLASS_CISCO_UCS_CIMC = None
    API_DEVICE_CLASS_CISCO_UCS_UCS_MANAGER = None
    API_DEVICE_CLASS_CONTROL_CENTER = None
    API_DEVICE_CLASS_DISCOVERED = None
    API_DEVICE_CLASS_HTTP = None
    API_DEVICE_CLASS_KVM = None
    API_DEVICE_CLASS_NETWORK = None
    API_DEVICE_CLASS_NETWORK_BIG_IP = None
    API_DEVICE_CLASS_NETWORK_CHECK_POINT = None
    API_DEVICE_CLASS_NETWORK_CISCO = None
    API_DEVICE_CLASS_NETWORK_JUNIPER = None
    API_DEVICE_CLASS_NETWORK_NETSCREEN = None
    API_DEVICE_CLASS_NETWORK_ROUTER = None
    API_DEVICE_CLASS_NETWORK_SWITCH = None
    API_DEVICE_CLASS_PDU = None
    API_DEVICE_CLASS_PING = None
    API_DEVICE_CLASS_POWER = None
    API_DEVICE_CLASS_POWER_UPS = None
    API_DEVICE_CLASS_POWER_UPS_APC = None
    API_DEVICE_CLASS_PRINTER = None
    API_DEVICE_CLASS_PRINTER_INKJET = None
    API_DEVICE_CLASS_PRINTER_LASER = None
    API_DEVICE_CLASS_SERVER_CMD = None
    API_DEVICE_CLASS_SERVER_DARWIN = None
    API_DEVICE_CLASS_SERVER_JBOSS = None
    API_DEVICE_CLASS_SERVER_LINUX = None
    API_DEVICE_CLASS_SERVER_MICROSOFT = None
    API_DEVICE_CLASS_SERVER_REMOTE = None
    API_DEVICE_CLASS_SERVER_SCAN = None
    API_DEVICE_CLASS_SERVER_SOLARIS = None
    API_DEVICE_CLASS_SERVER_SSH = None
    API_DEVICE_CLASS_SERVER_TOMCAT = None
    API_DEVICE_CLASS_SERVER_WEBLOGIC = None
    API_DEVICE_CLASS_SERVER_WINDOWS = None
    API_DEVICE_CLASS_STORAGE = None
    API_DEVICE_CLASS_STORAGE_BROCADE = None
    API_DEVICE_CLASS_STORAGE_NETAPP = None
    API_DEVICE_CLASS_STORAGE_NETAPP_7MODE = None
    API_DEVICE_CLASS_STORAGE_NETAPP_CMODE = None
    API_DEVICE_CLASS_STORAGE_NETAPP_SNMP = None
    API_DEVICE_CLASS_VCLOUD = None
    API_DEVICE_CLASS_VSPHERE = None
    API_DEVICE_CLASS_WEB = None
    API_DEVICE_CLASS_WEB_SUGARCRM = None
    API_DEVICE_CLASS_WEB_WEB_TRANSACTIONS = None

    # API Template types:
    API_TEMPLATE_TYPE_RRD_TEMPLATES = None

    # API Path parts
    API_PATH_PART_DATA_SOURCES = None
    API_PATH_PART_THRESHOLDS = None
    API_PATH_PART_DATA_POINTS = None
    API_PATH_PART_GRAPH_DEFS = None
    API_PATH_PART_GRAPH_POINTS = None

    # API Endpoints
    API_ROUTER_DEVICE_ENDPOINT = None
    API_ROUTER_TEMPLATE_ENDPOINT = None
    API_ROUTER_MIB_ENDPOINT = None

    # API Endpoint Actions
    API_ACTION_DEVICE_ROUTER = None
    API_ACTION_TEMPLATE_ROUTER = None
    API_ACTION_MIB_ROUTER = None

    # API Methods
    API_METHOD_GET_INFO = None
    API_METHOD_SET_INFO = None
    # - Devices
    API_METHOD_GET_DEVICES = None
    API_METHOD_ADD_DEVICE = None
    API_METHOD_BIND_OR_UNBIND_TEMPLATE = None
    API_METHOD_GET_BOUND_TEMPLATES = None
    API_METHOD_GET_UNBOUND_TEMPLATES = None
    API_METHOD_ADD_LOCAL_TEMPLATE = None
    API_METHOD_REMOVE_LOCAL_TEMPLATE = None
    API_METHOD_GET_LOCAL_TEMPLATES = None
    API_METHOD_SET_BOUND_TEMPLATES = None
    # - Templates
    API_METHOD_ADD_TEMPLATE = None
    API_METHOD_GET_TEMPLATES = None
    API_METHOD_GET_DATA_SOURCE_TYPES = None
    API_METHOD_ADD_DATA_SOURCE = None
    API_METHOD_GET_DATA_SOURCES = None
    API_METHOD_ADD_DATA_POINT = None
    API_METHOD_GET_DATA_POINTS = None
    API_METHOD_GET_DATA_SOURCE_DETAILS = None
    API_METHOD_GET_THRESHOLD_TYPES = None
    API_METHOD_ADD_THRESHOLD = None
    API_METHOD_GET_THRESHOLD_DETAILS = None
    API_METHOD_ADD_GRAPH_DEFINITION = None
    API_METHOD_SET_GRAPH_DEFINITION = None
    API_METHOD_ADD_DATA_POINT_TO_GRAPH = None
    API_METHOD_GET_DATA_POINT_DETAILS = None
    API_METHOD_GET_THRESHOLDS = None
    API_METHOD_GET_GRAPHS = None
    API_METHOD_GET_GRAPH_DEFINITION = None
    API_METHOD_GET_GRAPH_POINTS = None
    API_METHOD_DELETE_TEMPLATE = None

    # - Mib
    API_METHOD_ADD_OID_MAPPING = None
    API_METHOD_GET_OID_MAPPINGS = None

    # API Data Source Types
    API_DATA_SOURCE_TYPE_APACHEMONITOR = None
    API_DATA_SOURCE_TYPE_BUILT_IN = None
    API_DATA_SOURCE_TYPE_CALCULATED_PERFORMANCE = None
    API_DATA_SOURCE_TYPE_CISCO_UCS_XML_API = None
    API_DATA_SOURCE_TYPE_COMMAND = None
    API_DATA_SOURCE_TYPE_CONTROL_CENTER = None
    API_DATA_SOURCE_TYPE_DATAPOINT_AGGREGATOR = None
    API_DATA_SOURCE_TYPE_DIGMONITOR = None
    API_DATA_SOURCE_TYPE_DNSMONITOR = None
    API_DATA_SOURCE_TYPE_FTPMONITOR = None
    API_DATA_SOURCE_TYPE_HTTPMONITOR = None
    API_DATA_SOURCE_TYPE_JMX = None
    API_DATA_SOURCE_TYPE_LDAPMONITOR = None
    API_DATA_SOURCE_TYPE_MAILTX = None
    API_DATA_SOURCE_TYPE_MYSQLMONITOR = None
    API_DATA_SOURCE_TYPE_NETAPPMONITOR_CMODE_EVENTS_ZAPI = None
    API_DATA_SOURCE_TYPE_NETAPPMONITOR_SNMP = None
    API_DATA_SOURCE_TYPE_NETAPPMONITOR_ZAPI = None
    API_DATA_SOURCE_TYPE_NTPMONITOR = None
    API_DATA_SOURCE_TYPE_NX_API_COMMAND = None
    API_DATA_SOURCE_TYPE_PING = None
    API_DATA_SOURCE_TYPE_PROPERTY = None
    API_DATA_SOURCE_TYPE_PYTHON = None
    API_DATA_SOURCE_TYPE_SNMP = None
    API_DATA_SOURCE_TYPE_SQL = None
    API_DATA_SOURCE_TYPE_UCS_CIMC = None
    API_DATA_SOURCE_TYPE_VCLOUD = None
    API_DATA_SOURCE_TYPE_VCLOUD_STATUS = None
    API_DATA_SOURCE_TYPE_VMWARE_VSPHERE = None
    API_DATA_SOURCE_TYPE_WBEM = None
    API_DATA_SOURCE_TYPE_WEBTX = None
    API_DATA_SOURCE_TYPE_WINDOWS_EVENTLOG = None
    API_DATA_SOURCE_TYPE_WINDOWS_IIS_SITE = None
    API_DATA_SOURCE_TYPE_WINDOWS_PERFMON = None
    API_DATA_SOURCE_TYPE_WINDOWS_PORTCHECK = None
    API_DATA_SOURCE_TYPE_WINDOWS_PROCESS = None
    API_DATA_SOURCE_TYPE_WINDOWS_SERVICE = None
    API_DATA_SOURCE_TYPE_WINDOWS_SHELL = None
    API_DATA_SOURCE_TYPE_WINRM_PING = None

    # API Data Source Types
    # These were created by getting them directly from the API.
    API_THRESHOLD_MIN_MAX = None
    API_THRESHOLD_VALUE_CHANGE = None
    API_THRESHOLD_CISCO_STATUS = None
    API_THRESHOLD_PREDICTIVE = None

    # API Graph Line Tyes
    API_LINE_TYPE_AREA = None
    API_LINE_TYPE_DONT_DRAW = None
    API_LINE_TYPE_LINE = None

    HEADER_CONTENT_TYPE = None
    HEADER_JSON = None

# Load the YAML file to override the defaults above.
try:
    # TODO: don't assume the file is in the cwd.
    fin = open('zenoss_defaults.yaml', 'r')
    yams = fin.read()
    fin.close()
    try:
        yamo = yaml.load(yams)
    except yaml.ParserError as e:
        logging.error('zenoss_defaults.yaml is incorrectly formatted. Bailing out.')
        raise e

    for k,v in yamo.items():
        setattr(C, k.strip().upper(), v)

    # cleanup memory since this file won't be removed from ram until the script exits.
    # FREE THE MALLOCS!
    del yamo
    del yams
except IOError:
    logging.warn('No zenoss_defaults.yaml was found. Using defaults.')

##########################################################################
#
# Only put values here that the users should not be allowed to override.
#
##########################################################################
C.ERROR_CREDENTIALS_DICT_FORMAT = 'The supplied credentials are in a dictionary, but not on the expected format.'\
                                  ' Should be in the format of {USERNAME:PASSWORD}.'
C.ERROR_CREDENTIALS_LIST_FORMAT = 'The supplied credentials are in an iterable, but not on the expected format.'\
                                  ' Should be in the format of [USERNAME, PASSWORD].'
C.ERROR_CREDENTIALS_STR_FORMAT = 'The supplied credentials are in a string, but not on the expected format.'\
                                 ' Should be in the format of "USERNAME:PASSWORD".'
C.ERROR_CREDENTIALS_UNKNOWN_FORMAT = 'The supplied credentials are in an unknown format. Expected list, tuple, str, or'\
                                     ' dict.'  # "now you done gone and fucked up.

C.ERROR_INVALID_HOSTNAME_GOT_S = 'Hostname could not be resolved to an IP. Check for typos and try the FQDN. Got: %s'

C.ERROR_EXPECTED_S_GOT_S = 'Expected type %s. Got type %s.'

C.ERROR_API_S_UNSUCCESSFUL_GOT_S = 'API call returned with "successful" state of %s.'
C.ERROR_VALUES_S_NO_MATCH_S = 'Values %s had no match in key %s.'

C.API_URI = 'https://{HOST}'.format(HOST=C.API_URI_HOST+C.API_URI_DOMAIN)
C.API_ENDPOINT = '/zport/dmd'
C.API_DEVICES = '/Devices'

# API POST Data Keywords
C.API_METHOD = 'method'
C.API_ACTION = 'action'
C.API_DATA = 'data'
C.API_TID = 'tid'  # no idea what this is for or what tid stands for........
C.API_DEVICE_NAME = "deviceName"
C.API_DEVICE_CLASS = "deviceClass"
C.API_COLLECTOR = "collector"
C.API_MODEL = "model"
C.API_TITLE = "title"
C.API_PRODUCTION_STATE = "productionState"
C.API_PRIORITY = "priority"
C.API_SNMP_COMMUNITY = "snmpCommunity"
C.API_SNMP_PORT = "snmpPort"
C.API_TAG = "tag"
C.API_RACK_SLOT = "rackSlot"
C.API_SERIAL_NUMBER = "serialNumber"
C.API_HW_MANUFACTURER = "hwManufacturer"
C.API_HW_PRODUCT_NAME = "hwProductName"
C.API_OS_MANUFACTURER = "osManufacturer"
C.API_OS_PRODUCT_NAME = "osProductName"
C.API_COMMENTS = "comments"
C.API_ID = 'id'
C.API_TARGET_UID = 'targetUid'
C.API_QUERY = 'query'
C.API_TEMPLATE_UID = 'templateUid'
C.API_NAME = 'name'
C.API_TYPE = 'type'
C.API_UID = 'uid'
C.API_DATA_SOURCE_UID = 'dataSourceUid'
C.API_NODE_TYPE = 'nodetype'
C.API_OID = 'oid'
C.API_DIR = 'dir'
C.API_SORT = 'sort'
C.API_START = 'start'
C.API_PAGE = 'page'
C.API_LIMIT = 'limit'
C.API_THRESHOLD_TYPE = 'thresholdType'
C.API_THRESHOLD_ID = 'thresholdId'
C.API_DATA_POINTS = 'dataPoints'
C.API_GRAPH_DEFINITION_ID = 'graphDefinitionId'
C.API_MINY = 'miny'
C.API_MAXY = 'maxy'
C.API_DATA_POINT_UID = 'dataPointUid'
C.API_GRAPH_UID = 'graphUid'
C.API_INCLUDE_THRESHOLDS = 'includeThresholds'
C.API_UNITS = 'units'
C.API_LINE_TYPE = 'lineType'
C.API_RPN = 'rpn'
C.API_KEYS = 'keys'
C.API_DEVICE_UID = 'deviceUid'
C.API_TEMPLATE_ID = 'templateId'
C.API_TEMPLATE_IDS = 'templateIds'
C.API_RESULT = 'result'
C.API_SUCCESS = 'success'
C.API_MAX_VAL = 'maxval'
C.API_MIN_VAL = 'minval'
C.API_NODE_CONFIG = 'nodeConfig'

# Production States
# TODO: Maybe: Move this up into the override-able section.
C.PRODUCTION_STATE_PRODUCTION = 1000
C.PRODUCTION_STATE_PRE_PRODUCTION = 500
C.PRODUCTION_STATE_TEST = 400
C.PRODUCTION_STATE_MAINTENANCE = 300
C.PRODUCTION_STATE_DECOMMISSIONED = -1

C.API_KEYWORD_DEFAULTS = {
    C.API_TID: 1,
    C.API_COLLECTOR: C.ZENOSS_COLLECTOR or 'localhost',
    C.API_MODEL: True,
    C.API_TITLE: '',
    C.API_PRODUCTION_STATE: C.PRODUCTION_STATE_PRODUCTION,
    C.API_PRIORITY: 3,
    C.API_SNMP_COMMUNITY: C.SNMP_COMMUNITY or '',
    C.API_SNMP_PORT: C.SNMP_PORT or 161,
    C.API_TAG: '',
    C.API_RACK_SLOT: '',
    C.API_SERIAL_NUMBER: '',
    C.API_HW_MANUFACTURER: '',
    C.API_HW_PRODUCT_NAME: '',
    C.API_OS_MANUFACTURER: '',
    C.API_OS_PRODUCT_NAME: '',
    C.API_COMMENTS: '',
    C.API_QUERY: '',
    C.API_NODE_TYPE: 'node',
    C.API_DIR: 'ASC',
    C.API_SORT: 'name',
    C.API_START: 0,
    C.API_PAGE: None,
    C.API_LIMIT: 256,
    C.API_MINY: -1,
    C.API_MAXY: -1,
    C.API_INCLUDE_THRESHOLDS: False,
}

# API Device Classes:
# TODO: Maybe: Move this up into the override-able section.
C.API_DEVICE_CLASS_CISCO_UCS = '/CiscoUCS'
C.API_DEVICE_CLASS_CISCO_UCS_CIMC = '/CiscoUCS/CIMC'
C.API_DEVICE_CLASS_CISCO_UCS_UCS_MANAGER = '/CiscoUCS/UCS-Manager'
C.API_DEVICE_CLASS_CONTROL_CENTER = '/ControlCenter'
C.API_DEVICE_CLASS_DISCOVERED = '/Discovered'
C.API_DEVICE_CLASS_HTTP = '/HTTP'
C.API_DEVICE_CLASS_KVM = '/KVM'
C.API_DEVICE_CLASS_NETWORK = '/Network'
C.API_DEVICE_CLASS_NETWORK_BIG_IP = '/Network/BIG-IP'
C.API_DEVICE_CLASS_NETWORK_CHECK_POINT = '/Check Point'
C.API_DEVICE_CLASS_NETWORK_CISCO = '/Network/Cisco'
C.API_DEVICE_CLASS_NETWORK_JUNIPER = '/Network/JUNIPER'
C.API_DEVICE_CLASS_NETWORK_NETSCREEN = '/Network/NetScreen'
C.API_DEVICE_CLASS_NETWORK_ROUTER = '/Network/Router'
C.API_DEVICE_CLASS_NETWORK_SWITCH = '/Network/Switch'
C.API_DEVICE_CLASS_PDU = '/PDU'
C.API_DEVICE_CLASS_PING = '/Ping'
C.API_DEVICE_CLASS_POWER = '/Power'
C.API_DEVICE_CLASS_POWER_UPS = '/Power/UPS'
C.API_DEVICE_CLASS_POWER_UPS_APC = '/Power/UPS/APC'
C.API_DEVICE_CLASS_PRINTER = '/Printer'
C.API_DEVICE_CLASS_PRINTER_INKJET = '/Printer/InkJet'
C.API_DEVICE_CLASS_PRINTER_LASER = '/Printer/Laser'
C.API_DEVICE_CLASS_SERVER_CMD = '/Server/CMD'
C.API_DEVICE_CLASS_SERVER_DARWIN = '/Server/Darwin'
C.API_DEVICE_CLASS_SERVER_JBOSS = '/Server/JBoss'
C.API_DEVICE_CLASS_SERVER_LINUX = '/Server/Linux'
C.API_DEVICE_CLASS_SERVER_MICROSOFT = '/Server/Microsoft'
C.API_DEVICE_CLASS_SERVER_REMOTE = '/Server/Remote'
C.API_DEVICE_CLASS_SERVER_SCAN = '/Server/Scan'
C.API_DEVICE_CLASS_SERVER_SOLARIS = '/Server/Solaris'
C.API_DEVICE_CLASS_SERVER_SSH = '/Server/SSH'
C.API_DEVICE_CLASS_SERVER_TOMCAT = '/Server/Tomcat'
C.API_DEVICE_CLASS_SERVER_WEBLOGIC = '/Server/WebLogic'
C.API_DEVICE_CLASS_SERVER_WINDOWS = '/Server/Windows'
C.API_DEVICE_CLASS_STORAGE = '/Storage'
C.API_DEVICE_CLASS_STORAGE_BROCADE = '/Storage/Brocade'
C.API_DEVICE_CLASS_STORAGE_NETAPP = '/Storage/NetApp'
C.API_DEVICE_CLASS_STORAGE_NETAPP_7MODE = '/Storage/NetApp/7-Mode'
C.API_DEVICE_CLASS_STORAGE_NETAPP_CMODE = '/Storage/NetApp/C-Mode'
C.API_DEVICE_CLASS_STORAGE_NETAPP_SNMP = '/Storage/NetApp/SNMP'
C.API_DEVICE_CLASS_VCLOUD = '/vCloud'
C.API_DEVICE_CLASS_VSPHERE = '/vSphere'
C.API_DEVICE_CLASS_WEB = '/Web'
C.API_DEVICE_CLASS_WEB_SUGARCRM = '/Web/SugarCRM'
C.API_DEVICE_CLASS_WEB_WEB_TRANSACTIONS = '/Web/WebTransactions'

# API Template types:
C.API_TEMPLATE_TYPE_RRD_TEMPLATES = '/rrdTemplates'

# API Path parts
C.API_PATH_PART_DATA_SOURCES = 'datasources'
C.API_PATH_PART_THRESHOLDS = 'thresholds'
C.API_PATH_PART_DATA_POINTS = 'datapoints'
C.API_PATH_PART_GRAPH_DEFS = 'graphDefs'
C.API_PATH_PART_GRAPH_POINTS = 'graphPoints'

# API Endpoints
C.API_ROUTER_DEVICE_ENDPOINT = '/device_router'
C.API_ROUTER_TEMPLATE_ENDPOINT = '/template_router'
C.API_ROUTER_MIB_ENDPOINT = '/mib_router'

# API Endpoint Actions
C.API_ACTION_DEVICE_ROUTER = 'DeviceRouter'
C.API_ACTION_TEMPLATE_ROUTER = 'TemplateRouter'
C.API_ACTION_MIB_ROUTER = 'MibRouter'

# API Methods
C.API_METHOD_GET_INFO = 'getInfo'
C.API_METHOD_SET_INFO = 'setInfo'
# - Devices
C.API_METHOD_GET_DEVICES = 'getDevices'
C.API_METHOD_ADD_DEVICE = 'addDevice'
C.API_METHOD_BIND_OR_UNBIND_TEMPLATE = 'bindOrUnbindTemplate'
C.API_METHOD_GET_BOUND_TEMPLATES = 'getBoundTemplates'
C.API_METHOD_GET_UNBOUND_TEMPLATES = 'getUnboundTemplates'
C.API_METHOD_ADD_LOCAL_TEMPLATE = 'addLocalTemplate'
C.API_METHOD_REMOVE_LOCAL_TEMPLATE = 'removeLocalTemplate'
C.API_METHOD_GET_LOCAL_TEMPLATES = 'getLocalTemplates'
C.API_METHOD_SET_BOUND_TEMPLATES = 'setBoundTemplates'
# - Templates
C.API_METHOD_ADD_TEMPLATE = 'addTemplate'
C.API_METHOD_GET_TEMPLATES = 'getTemplates'
C.API_METHOD_GET_DATA_SOURCE_TYPES = 'getDataSourceTypes'
C.API_METHOD_ADD_DATA_SOURCE = 'addDataSource'
C.API_METHOD_GET_DATA_SOURCES = 'getDataSources'
C.API_METHOD_ADD_DATA_POINT = 'addDataPoint'
C.API_METHOD_GET_DATA_POINTS = 'getDataPoints'
C.API_METHOD_GET_DATA_SOURCE_DETAILS = 'getDataSourceDetails'
C.API_METHOD_GET_THRESHOLD_TYPES = 'getThresholdTypes'
C.API_METHOD_ADD_THRESHOLD = 'addThreshold'
C.API_METHOD_GET_THRESHOLD_DETAILS = 'getThresholdDetails'
C.API_METHOD_ADD_GRAPH_DEFINITION = 'addGraphDefinition'
C.API_METHOD_SET_GRAPH_DEFINITION = 'setGraphDefinition'
C.API_METHOD_ADD_DATA_POINT_TO_GRAPH = 'addDataPointToGraph'
C.API_METHOD_GET_DATA_POINT_DETAILS = 'getDataPointDetails'
C.API_METHOD_GET_THRESHOLDS = 'getThresholds'
C.API_METHOD_GET_GRAPHS = 'getGraphs'
C.API_METHOD_GET_GRAPH_DEFINITION = 'getGraphDefinition'
C.API_METHOD_GET_GRAPH_POINTS = 'getGraphPoints'
C.API_METHOD_DELETE_TEMPLATE = 'deleteTemplate'

# - Mib
C.API_METHOD_ADD_OID_MAPPING = 'addOidMapping'
C.API_METHOD_GET_OID_MAPPINGS = 'getOidMappings'

# API Data Source Types
# These were created by getting them directly from the API.
C.API_DATA_SOURCE_TYPE_APACHEMONITOR = 'ApacheMonitor'
C.API_DATA_SOURCE_TYPE_BUILT_IN = 'Built-In'
C.API_DATA_SOURCE_TYPE_CALCULATED_PERFORMANCE = 'Calculated Performance'
C.API_DATA_SOURCE_TYPE_CISCO_UCS_XML_API = 'Cisco UCS XML API'
C.API_DATA_SOURCE_TYPE_COMMAND = 'COMMAND'
C.API_DATA_SOURCE_TYPE_CONTROL_CENTER = 'Control Center'
C.API_DATA_SOURCE_TYPE_DATAPOINT_AGGREGATOR = 'Datapoint Aggregator'
C.API_DATA_SOURCE_TYPE_DIGMONITOR = 'DigMonitor'
C.API_DATA_SOURCE_TYPE_DNSMONITOR = 'DnsMonitor'
C.API_DATA_SOURCE_TYPE_FTPMONITOR = 'FtpMonitor'
C.API_DATA_SOURCE_TYPE_HTTPMONITOR = 'HttpMonitor'
C.API_DATA_SOURCE_TYPE_JMX = 'JMX'
C.API_DATA_SOURCE_TYPE_LDAPMONITOR = 'LDAPMonitor'
C.API_DATA_SOURCE_TYPE_MAILTX = 'MAILTX'
C.API_DATA_SOURCE_TYPE_MYSQLMONITOR = 'MySqlMonitor'
C.API_DATA_SOURCE_TYPE_NETAPPMONITOR_CMODE_EVENTS_ZAPI = 'NetAppMonitor Cmode Events ZAPI'
C.API_DATA_SOURCE_TYPE_NETAPPMONITOR_SNMP = 'NetAppMonitor SNMP'
C.API_DATA_SOURCE_TYPE_NETAPPMONITOR_ZAPI = 'NetAppMonitor ZAPI'
C.API_DATA_SOURCE_TYPE_NTPMONITOR = 'NtpMonitor'
C.API_DATA_SOURCE_TYPE_NX_API_COMMAND = 'NX-API Command'
C.API_DATA_SOURCE_TYPE_PING = 'PING'
C.API_DATA_SOURCE_TYPE_PROPERTY = 'Property'
C.API_DATA_SOURCE_TYPE_PYTHON = 'Python'
C.API_DATA_SOURCE_TYPE_SNMP = 'SNMP'
C.API_DATA_SOURCE_TYPE_SQL = 'SQL'
C.API_DATA_SOURCE_TYPE_UCS_CIMC = 'UCS CIMC'
C.API_DATA_SOURCE_TYPE_VCLOUD = 'vCloud'
C.API_DATA_SOURCE_TYPE_VCLOUD_STATUS = 'vCloudStatus'
C.API_DATA_SOURCE_TYPE_VMWARE_VSPHERE = 'VMware vSphere'
C.API_DATA_SOURCE_TYPE_WBEM = 'WBEM'
C.API_DATA_SOURCE_TYPE_WEBTX = 'WebTx'
C.API_DATA_SOURCE_TYPE_WINDOWS_EVENTLOG = 'Windows EventLog'
C.API_DATA_SOURCE_TYPE_WINDOWS_IIS_SITE = 'Windows IIS Site'
C.API_DATA_SOURCE_TYPE_WINDOWS_PERFMON = 'Windows Perfmon'
C.API_DATA_SOURCE_TYPE_WINDOWS_PORTCHECK = 'Windows PortCheck'
C.API_DATA_SOURCE_TYPE_WINDOWS_PROCESS = 'Windows Process'
C.API_DATA_SOURCE_TYPE_WINDOWS_SERVICE = 'Windows Service'
C.API_DATA_SOURCE_TYPE_WINDOWS_SHELL = 'Windows Shell'
C.API_DATA_SOURCE_TYPE_WINRM_PING = 'WinRM Ping'

# API Data Source Types
# These were created by getting them directly from the API.
C.API_THRESHOLD_MIN_MAX = 'MinMaxThreshold'
C.API_THRESHOLD_VALUE_CHANGE = 'ValueChangeThreshold'
C.API_THRESHOLD_CISCO_STATUS = 'CiscoStatus'
C.API_THRESHOLD_PREDICTIVE = 'PredictiveThreshold'

# API Graph Line Tyes
C.API_LINE_TYPE_AREA = 'AREA'
C.API_LINE_TYPE_DONT_DRAW = 'DONTDRAW'
C.API_LINE_TYPE_LINE = 'LINE'

C.HEADER_CONTENT_TYPE = 'Content-Type'
C.HEADER_JSON = {C.HEADER_CONTENT_TYPE: 'application/json'}

