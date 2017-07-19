import json
import yaml
import socket
import logging
import requests
from CONSTS import C
from collections import Iterable

# TODO: just logging.getLogger() since this is a re-usable class.
formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class ZenossError(Exception):
    pass


class ZenossAPI(object):
    def __init__(self, credentials, host=C.API_URI_HOST):
        self.credentials = self._credentials_check(credentials)
        self.host = self._host_check(host)
        self.tid = 0

    def _host_check(self, host):
        try:
            socket.gethostbyname(host)
        except socket.gaierror:
            raise ZenossError(C.ERROR_INVALID_HOSTNAME_GOT_S % host)

        return host

    def _credentials_check(self, credentials):
        if isinstance(credentials, dict):
            if len(credentials) == 1:
                credentials = (credentials.keys()[0], credentials.values()[0])
            else:
                raise ZenossError(C.ERROR_CREDENTIALS_DICT_FORMAT)
        elif isinstance(credentials, str):
            if ':' not in credentials:
                raise ZenossError(C.ERROR_CREDENTIALS_STR_FORMAT)
            credentials = credentials.split(':')
        # 'str' type check MUST come before Iterable type check -- strings are iterable.
        elif isinstance(credentials, Iterable):
            if len(credentials) == 2:
                credentials = (credentials[0], credentials[1])  # force it to be a tuple -- just in case.
            else:
                raise ZenossError(C.ERROR_CREDENTIALS_LIST_FORMAT)
        else:
            raise ZenossError(C.ERROR_CREDENTIALS_UNKNOWN_FORMAT)

        return credentials

    def _load_json(self, text, raise_exception=True):
        """
        :param: String, The raw json formatted text to turn into an object
        :param fail: Boolean, when true raise an error if the json is incorrectly formatted.
        :return: The object the json represented (e.g. list, dict, etc.)
        """
        try:
            return json.loads(text)
        except ValueError as e:
            # TODO: log the error, exception, raise e
            if raise_exception:
                raise e

    def _non_str_iterable(self, values, t=list, always_t=False):
        if isinstance(values, str):
            return t([values])
        elif isinstance(values, Iterable) and always_t:
            return t(values)

        return values

    def _get_result_data(self, json_obj, data_key=C.API_DATA, raise_exception=False):
        if C.API_RESULT in json_obj:
            if C.API_SUCCESS in json_obj[C.API_RESULT]:
                if raise_exception and not json_obj[C.API_RESULT][C.API_SUCCESS]:
                    raise ZenossError()  # TODO: Error message

                if data_key in json_obj[C.API_RESULT]:
                    return json_obj[C.API_RESULT][data_key], json_obj[C.API_RESULT][C.API_SUCCESS]
                return None, json_obj[C.API_RESULT][C.API_SUCCESS]
        elif raise_exception:
            raise ZenossError()  # TODO: Error message
        return None, None

    def api_request(self, endpoint, action, method, data=[{}], headers=C.HEADER_JSON, raise_exception=False):
        """
        :param endpoint: String, e.g. C.API_ROUTER_DEVICE_ENDPOINT - 'device_router'
        :param action: String, e.g. C.API_ACTION_DEVICE_ROUTER - 'DeviceRouter'
        :param method: String, e.g. C.API_METHOD_GET_DEVICES - 'getDevices'
        :param data: List of dicts, The values that the 'method' takes
        :param headers: Dict, It's here if you need to set something other than a json content type or add something extra.
        :param raise_exception: Boolean, when true, raise an error if the json from the API is incorrectly formatted.
        :return: When zenoss responds with status code 200: the unpacked json object (e.g. list, dict)
                 When zenoss responds with any other status code, a tuple (status_code, raw_text)
        """
        # TODO: Look at content-type in header to see if we got json back. Throw exception if HTML.
        # TODO: take the parameter 'fail' and pass it forward to _load_json -- use the value here to log

        uri = C.API_URI+C.API_ENDPOINT+endpoint
        payload = {C.API_ACTION: action, C.API_METHOD: method, C.API_DATA: data if isinstance(data, list) else [data],
                   C.API_TID: C.API_KEYWORD_DEFAULTS[C.API_TID]}
        logger.debug(json.dumps(payload, indent=2))

        try:
            r = requests.post(uri, auth=self.credentials, data=json.dumps(payload),
                              headers=headers, verify=C.SSL_VERIFY)
            logger.debug('Status code: %s' % r.status_code)
            try:
                logger.debug('Result: %s' % json.dumps(json.loads(r.text), indent=2))
            except ValueError:
                logger.debug('Result: %s' % r.text)

            # TODO: we should be checking the status code and react+log accordingly.
            if r.status_code == 200:
                return self._load_json(r.text, raise_exception=raise_exception)
            else:
                return r.status_code, r.text
        except requests.exceptions.ConnectionError as e:
            # TODO: log it, then log e, then raise e.
            raise e

    ####################################################################################################################
    #  DEVICE functions
    ####################################################################################################################
    def get_devices(self):
        """
        :return:
        """
        r = self.api_request(C.API_ROUTER_DEVICE_ENDPOINT, C.API_ACTION_DEVICE_ROUTER, C.API_METHOD_GET_DEVICES)
        return self._load_json(r.text)

    def add_device(self, hostname, device_class, **kwargs):
        """
        :param hostname:
        :param device_class:
        :param kwargs:
        :return:
        """
        payload = {C.API_DEVICE_NAME: hostname,
                   C.API_DEVICE_CLASS: device_class,
                   C.API_COLLECTOR: C.API_KEYWORD_DEFAULTS[C.API_COLLECTOR],
                   C.API_MODEL: C.API_KEYWORD_DEFAULTS[C.API_MODEL],
                   C.API_TITLE: C.API_KEYWORD_DEFAULTS[C.API_TITLE],
                   C.API_PRODUCTION_STATE: C.API_KEYWORD_DEFAULTS[C.API_PRODUCTION_STATE],
                   C.API_PRIORITY: C.API_KEYWORD_DEFAULTS[C.API_PRIORITY],
                   C.API_SNMP_COMMUNITY: C.API_KEYWORD_DEFAULTS[C.API_SNMP_COMMUNITY],
                   C.API_SNMP_PORT: C.API_KEYWORD_DEFAULTS[C.API_SNMP_PORT],
                   C.API_TAG: C.API_KEYWORD_DEFAULTS[C.API_TAG],
                   C.API_RACK_SLOT: C.API_KEYWORD_DEFAULTS[C.API_RACK_SLOT],
                   C.API_SERIAL_NUMBER: C.API_KEYWORD_DEFAULTS[C.API_SERIAL_NUMBER],
                   C.API_HW_MANUFACTURER: C.API_KEYWORD_DEFAULTS[C.API_HW_MANUFACTURER],
                   C.API_HW_PRODUCT_NAME: C.API_KEYWORD_DEFAULTS[C.API_HW_PRODUCT_NAME],
                   C.API_OS_MANUFACTURER: C.API_KEYWORD_DEFAULTS[C.API_OS_MANUFACTURER],
                   C.API_OS_PRODUCT_NAME: C.API_KEYWORD_DEFAULTS[C.API_OS_PRODUCT_NAME],
                   C.API_COMMENTS: C.API_KEYWORD_DEFAULTS[C.API_COMMENTS]}

        payload.update(kwargs)
        return self.api_request(C.API_ROUTER_DEVICE_ENDPOINT, C.API_ACTION_DEVICE_ROUTER,
                                C.API_METHOD_ADD_DEVICE, data=[payload])

    def bind_or_unbind_template(self, uid, template_uid):
        """
        :param uid:
        :param template_uid:
        :return:
        """
        payload = [{C.API_UID: uid, C.API_TEMPLATE_UID: template_uid}]
        return self.api_request(C.API_ROUTER_DEVICE_ENDPOINT, C.API_ACTION_DEVICE_ROUTER,
                                C.API_METHOD_BIND_OR_UNBIND_TEMPLATE, data=payload)

    def get_device_info(self, uid, keys=None):
        """
        :param uid:
        :param keys:
        :return:
        """
        if isinstance(keys, str):
            raise ZenossError()  # TODO: error string
        elif isinstance(keys, Iterable):
            keys = list(keys)
        else:
            keys = None
        payload = [{C.API_UID: uid, C.API_KEYS: keys}]
        return self.api_request(C.API_ROUTER_DEVICE_ENDPOINT, C.API_ACTION_DEVICE_ROUTER,
                                C.API_METHOD_GET_INFO, data=payload)

    def get_bound_templates(self, uid):
        """
        :param uid:
        :return:
        """
        payload = [{C.API_UID: uid}]
        return self.api_request(C.API_ROUTER_DEVICE_ENDPOINT, C.API_ACTION_DEVICE_ROUTER,
                                C.API_METHOD_GET_BOUND_TEMPLATES, data=payload)

    def get_unbound_templates(self, uid):
        """
        :param uid:
        :return:
        """
        payload = [{C.API_UID: uid}]
        return self.api_request(C.API_ROUTER_DEVICE_ENDPOINT, C.API_ACTION_DEVICE_ROUTER,
                                C.API_METHOD_GET_UNBOUND_TEMPLATES, data=payload)

    def add_local_template(self, device_uid, template_id):
        """
        :param device_uid:
        :param template_id:
        :return:
        """
        payload = [{C.API_DEVICE_UID: device_uid, C.API_TEMPLATE_ID: template_id}]
        return self.api_request(C.API_ROUTER_DEVICE_ENDPOINT, C.API_ACTION_DEVICE_ROUTER,
                                C.API_METHOD_ADD_LOCAL_TEMPLATE, data=payload)

    def remove_local_template(self, device_uid, template_uid):
        """
        :param device_uid:
        :param template_uid:
        :return:
        """
        payload = [{C.API_DEVICE_UID: device_uid, C.API_TEMPLATE_UID: template_uid}]
        return self.api_request(C.API_ROUTER_DEVICE_ENDPOINT, C.API_ACTION_DEVICE_ROUTER,
                                C.API_METHOD_REMOVE_LOCAL_TEMPLATE, data=payload)

    def get_local_templates(self, uid, query=None):
        """
        :param uid:
        :param query: Unused
        :return:
        """
        payload = [{C.API_UID: uid, C.API_QUERY: query}]
        return self.api_request(C.API_ROUTER_DEVICE_ENDPOINT, C.API_ACTION_DEVICE_ROUTER,
                                C.API_METHOD_GET_LOCAL_TEMPLATES, data=payload)

    def set_bound_templates(self, uid, template_ids):
        """
        :param uid:
        :param template_ids:
        :return:
        """
        payload = [{C.API_UID: uid, C.API_TEMPLATE_IDS: self._non_str_iterable(template_ids)}]
        return self.api_request(C.API_ROUTER_DEVICE_ENDPOINT, C.API_ACTION_DEVICE_ROUTER,
                                C.API_METHOD_SET_BOUND_TEMPLATES, data=payload)

    ####################################################################################################################
    #  TEMPLATE functions
    ####################################################################################################################
    def add_template(self, zid, target_uid):
        """
        :param zid: The name to give the template.
        :param target_uid: The device path the template should apply to (e.g. /Server/Linux)
        :return: When zenoss responds with status code 200: the unpacked json object (e.g. list, dict)
                 When zenoss responds with any other status code, a tuple (status_code, raw_text)
        """
        payload = [{C.API_ID: zid, C.API_TARGET_UID: target_uid}]

        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_ADD_TEMPLATE, data=payload)

    def get_templates(self, zid=''):
        """
        :param zid: String: not used. Exists to mirror Zenoss API and to support any future implementation.
        :return:
        """
        payload = [{C.API_ID: zid}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_TEMPLATES, data=payload)

    def add_data_source(self, template_uid, name, data_source_type=C.API_DATA_SOURCE_TYPE_SNMP):
        """
        :param template_uid:
        :param name:
        :param data_source_type:
        :return:
        """
        payload = [{C.API_TEMPLATE_UID: template_uid, C.API_NAME: name, C.API_TYPE: data_source_type}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_ADD_DATA_SOURCE, data=payload)

    def get_data_sources(self, uid):
        """
        :param uid:
        :return:
        """
        payload = [{C.API_UID: uid}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_DATA_SOURCES, data=payload)

    def get_data_source_details(self, uid):
        """
        :param uid:
        :return:
        """
        payload = [{C.API_UID: uid}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_DATA_SOURCE_DETAILS, data=payload)

    def get_data_source_types(self, query=None):
        """
        :param query: Unused, according to the API docs. Still required for the query, however.
               Including for forward-compatibility.
        :return:
        """
        payload = [{C.API_QUERY: query or C.API_KEYWORD_DEFAULTS[C.API_QUERY]}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_DATA_SOURCE_TYPES, data=payload)

    def add_data_point(self, data_source_uid, name):
        """
        :param data_source_uid:
        :param name:
        :return:
        """
        payload = [{C.API_DATA_SOURCE_UID: data_source_uid, C.API_NAME: name}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_ADD_DATA_POINT, data=payload)

    def get_data_points(self, uid, query=C.API_KEYWORD_DEFAULTS[C.API_QUERY]):
        """
        :param uid:
        :param query:
        :return:
        """
        payload = [{C.API_UID: uid, C.API_QUERY: query}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_DATA_POINTS, data=payload)

    def add_graph_definition(self, template_uid, graph_definition_id):
        """
        :param template_uid:
        :param graph_definition_id:
        :return:
        """
        payload = [{C.API_TEMPLATE_UID: template_uid, C.API_GRAPH_DEFINITION_ID: graph_definition_id}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_ADD_GRAPH_DEFINITION, data=payload)

    def add_data_point_to_graph(self, data_point_uid, graph_uid,
                                include_thresholds=C.API_KEYWORD_DEFAULTS[C.API_INCLUDE_THRESHOLDS]):
        """
        :param data_point_uid:
        :param graph_uid:
        :param include_thresholds:
        :return:
        """
        payload = [{C.API_DATA_POINT_UID: data_point_uid, C.API_GRAPH_UID: graph_uid,
                    C.API_INCLUDE_THRESHOLDS: include_thresholds}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_ADD_DATA_POINT_TO_GRAPH, data=payload)

    def set_graph_definition(self, uid, miny=C.API_KEYWORD_DEFAULTS[C.API_MINY],
                             maxy=C.API_KEYWORD_DEFAULTS[C.API_MAXY], units='', **kwargs):
        """
        :param uid:
        :param miny:
        :param maxy:
        :param units:
        :param kwargs:
        :return:
        """
        kwargs.update({C.API_UID: uid, C.API_MINY: miny, C.API_MAXY: maxy, C.API_UNITS: units})
        payload = [kwargs]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_SET_GRAPH_DEFINITION, data=payload)

    def get_template_info(self, uid):
        """
        :param uid:
        :return:
        """
        payload = [{C.API_UID: uid}]
        self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                         C.API_METHOD_GET_INFO, data=payload)

    def set_template_info(self, uid, **kwargs):
        """
        :param uid:
        :param kwargs:
        :return:
        """
        kwargs.update({C.API_UID: uid})
        payload = [kwargs]
        self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                         C.API_METHOD_SET_INFO, data=payload)

    def get_threshold_types(self, query=C.API_KEYWORD_DEFAULTS[C.API_QUERY]):
        """
        :param query:
        :return:
        """
        payload = [{C.API_QUERY: query}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_THRESHOLD_TYPES, data=payload)

    def add_threshold(self, uid, threshold_type, threshold_id, data_points):
        """
        :param uid:
        :param threshold_id:
        :param threshold_type:
        :param data_points:
        :return:
        """
        payload = [{C.API_UID: uid, C.API_THRESHOLD_ID: threshold_id, C.API_THRESHOLD_TYPE: threshold_type,
                    C.API_DATA_POINTS: data_points}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_ADD_THRESHOLD, data=payload)

    def get_threshold_details(self, uid):
        """
        :param uid:
        :return:
        """
        payload = [{C.API_UID: uid}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_THRESHOLD_DETAILS, data=payload)

    def get_data_point_details(self, uid):
        """
        :param uid:
        :return:
        """
        payload = [{C.API_UID: uid}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_DATA_POINT_DETAILS, data=payload)

    def get_thresholds(self, uid, query=C.API_KEYWORD_DEFAULTS[C.API_QUERY]):
        """
        :param uid:
        :param query:
        :return:
        """
        payload = [{C.API_UID: uid, C.API_QUERY: query}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_THRESHOLDS, data=payload)

    def get_graphs(self, uid, query=C.API_KEYWORD_DEFAULTS[C.API_QUERY]):
        """
        :param uid:
        :param query:
        :return:
        """
        payload = [{C.API_UID: uid, C.API_QUERY: query}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_GRAPHS, data=payload)

    def get_graph_definition(self, uid):
        """
        :param uid:
        :return:
        """
        payload = [{C.API_UID: uid}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_GRAPH_DEFINITION, data=payload)

    def get_graph_points(self, uid):
        """
        :param uid:
        :return:
        """
        payload = [{C.API_UID: uid}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_GRAPH_POINTS, data=payload)

    ####################################################################################################################
    #  MIB functions
    ####################################################################################################################
    def add_oid_mapping(self, uid, zid, oid, node_type=C.API_KEYWORD_DEFAULTS[C.API_NODE_TYPE]):
        """
        :param uid:
        :param zid:
        :param oid:
        :param node_type:
        :return:
        """
        payload = [{C.API_UID: uid, C.API_ID: zid, C.API_OID: oid, C.API_NODE_TYPE: node_type}]
        self.api_request(C.API_ROUTER_MIB_ENDPOINT, C.API_ACTION_MIB_ROUTER, C.API_METHOD_ADD_OID_MAPPING, data=payload)

    def get_oid_mappings(self, uid, direction=C.API_KEYWORD_DEFAULTS[C.API_DIR],
                         sort=C.API_KEYWORD_DEFAULTS[C.API_SORT], start=C.API_KEYWORD_DEFAULTS[C.API_START],
                         page=C.API_KEYWORD_DEFAULTS[C.API_PAGE], limit=C.API_KEYWORD_DEFAULTS[C.API_LIMIT]):
        """
        :param uid:
        :param direction:
        :param sort:
        :param start:
        :param page:
        :param limit:
        :return:
        """
        payload = [{C.API_UID: uid,
                    C.API_DIR: direction,
                    C.API_SORT: sort,
                    C.API_START: start,
                    C.API_PAGE: page,
                    C.API_LIMIT: limit}]
        self.api_request(C.API_ROUTER_MIB_ENDPOINT, C.API_ACTION_MIB_ROUTER, C.API_METHOD_GET_OID_MAPPINGS,
                         data=payload)

    ####################################################################################################################
    #  Convenience functions
    ####################################################################################################################
    def add_new_snmp_monitor(self, zid, target_uid, oid='', threshold_max=None, threshold_min=None,
                             template_type=C.API_TEMPLATE_TYPE_RRD_TEMPLATES, graph=True, graph_min_y=-1,
                             graph_max_y=-1, graph_units='', graph_line_type=C.API_LINE_TYPE_LINE, RPN=None,
                             overwrite=False):

        # Zenoss alerting behavior is sometimes conditional on what is and is not set. This filter prevents us from
        # setting values that have a blank value.
        def _payload_filter(d):
            return dict(filter(lambda (x, v): v is not None, d.items()))

        def _path_validator(data, success, key, checks, values):
            if success:
                for d in data:
                    if key in d:
                        path_parts = d[key].split('/')
                        for k,v in checks.items():
                            func = getattr(path_parts[k], v)
                            if not func(values[k]):
                                break
                        else:
                            # This else statement only happens when we didn't hit the 'break' statement (the loop
                            # completed and therefore, we found our match)
                            return d[key]
                else:
                    raise ZenossError('')  # TODO: error message

        # If we already have the template and we don't want to overwrite it, simply return True.
        results = self.get_templates(C.API_ENDPOINT+C.API_DEVICES)
        for result in results[C.API_RESULT]:
            if C.API_ID in result and result[C.API_ID] == zid and not overwrite:
                return True

        if not target_uid.startswith(C.API_ENDPOINT):
            target_uid = C.API_ENDPOINT + target_uid

        datasource_name = '%s_%s' % (zid, C.API_PATH_PART_DATA_SOURCES)
        threshold_name = '%s_%s' % (zid, C.API_PATH_PART_THRESHOLDS)
        graph_name = '%s_%s' % (zid, C.API_PATH_PART_GRAPH_DEFS)

        results = self.add_template(zid, target_uid)  # create template
        data, success = self._get_result_data(results, data_key=C.API_NODE_CONFIG)
        template_uid = ''  # This is just to keep the IDE from complaining.
        if success:
            template_uid = data[C.API_UID]

        self.add_data_source(template_uid, datasource_name, data_source_type=C.API_DATA_SOURCE_TYPE_SNMP)
        junk, success = self._get_result_data(results)
        del junk

        datasource_uid = ''  # This is just to keep the IDE from complaining.
        if success:
            results = self.get_data_sources(template_uid)
            data, success = self._get_result_data(results)
            datasource_uid = _path_validator(data, success, C.API_UID, {-2: '__eq__', -1: '__eq__'},
                                             {-2: C.API_PATH_PART_DATA_SOURCES, -1: datasource_name})

        results = self.get_data_points(template_uid)
        data, success = self._get_result_data(results)
        # Yes, the last check here really should be the dataSOURCE name (not dataPOINT).
        datapoint_uid = _path_validator(data, success, C.API_UID, {-2: '__eq__', -1: '__eq__'},
                                        {-2: C.API_PATH_PART_DATA_POINTS, -1: datasource_name})


        self.set_template_info(datasource_uid, **{C.API_OID: oid})
        self.add_threshold(template_uid, C.API_THRESHOLD_MIN_MAX, threshold_name, [datapoint_uid])

        results = self.get_thresholds(template_uid)
        data, success = self._get_result_data(results)
        threshold_uid = _path_validator(data, success, C.API_UID, {-2: '__eq__', -1: '__eq__'},
                                        {-2: C.API_PATH_PART_THRESHOLDS, -1: threshold_name})

        payload = _payload_filter({C.API_MAX_VAL: threshold_max, C.API_MIN_VAL: threshold_min})
        if payload:
            self.set_template_info(threshold_uid, **payload)

        if graph:
            self.add_graph_definition(template_uid, graph_name)  # create graph
            results = self.get_graphs(template_uid)

            # Note that the Zenoss is inconsistent here: No 'success' and no 'data' values returned from the API.
            graph_uid = _path_validator(results[C.API_RESULT], True, C.API_UID, {-2: '__eq__', -1: '__eq__'},
                                        {-2: C.API_PATH_PART_GRAPH_DEFS, -1: graph_name})

            self.add_data_point_to_graph(datapoint_uid, graph_uid, include_thresholds=True)
            results = self.get_graph_points(graph_uid)
            data, success = self._get_result_data(results)
            graph_point_datasource_uid = _path_validator(data, success, C.API_UID, {-2: '__eq__', -1: 'endswith'},
                                                         {-2: C.API_PATH_PART_GRAPH_POINTS, -1: datasource_name})

            payload = _payload_filter({C.API_LINE_TYPE: graph_line_type, C.API_RPN: RPN})  # example RPN: '8640000,/'
            if payload:
                self.set_template_info(graph_point_datasource_uid, **payload)
            self.set_graph_definition(graph_uid, miny=graph_min_y, maxy=graph_max_y, units=graph_units)
        return self.bind_templates(target_uid, zid)

    def bind_templates(self, uid, template_uids):
        """
        :param uid:
        :param template_uids:
        :return:
        """

        if isinstance(template_uids, str):
            template_uids = [template_uids]
        elif isinstance(template_uids, Iterable):
            template_uids = list(template_uids)  # ensure known behavior in case of custom iterable type.

        results = self.get_bound_templates(uid)
        data, success = self._get_result_data(results)
        if success and data:
            bound_template_uids = [r[0] for r in data]
            add_template_ids = filter(lambda tid: tid not in bound_template_uids, template_uids)
            if add_template_ids:
                return self.set_bound_templates(uid, add_template_ids+bound_template_uids)
            return True  # Template was already bound
        return False  # UID probably doesn't exist.

    def add_linux_host(self, hostname, **kwargs):
        """
        :param hostname:
        :param kwargs:
        :return:
        """
        return self.add_device(hostname, C.API_DEVICE_CLASS_SERVER_LINUX, **kwargs)





def main():
    # TODO: error handling.
    fin = open('credentials.yaml', 'r')
    credentials = yaml.load(fin.read())
    fin.close()
    zap = ZenossAPI(credentials)

    # zap.add_template('AlastairUptime', '/zport/dmd/Devices/Server/Linux')
    # zap.get_data_source_types()
    # zap.add_data_source('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptime', 'AlastairUptimeDS2')
    # zap.set_template_info('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptime/datasources/AlastairUptimeDS', **{'oid':'1.3.6.1.2.1.25.1.1.0'})
    # zap.get_template_info('/zport/dmd/Devices/Server/Linux/rrdTemplates/SystemUptime/datasources/uptime')
    # zap.get_data_source_details('/zport/dmd/Devices/Server/Linux/rrdTemplates/SystemUptime')  # ???

    # zap.get_data_sources('/zport/dmd/Devices/Server/Linux/rrdTemplates/Device/datasources/SystemUptime')
    # |_  /zport/dmd/Devices/Server/Linux/rrdTemplates/SystemUptime/datasources/uptime
    # zap.get_data_source_details('/zport/dmd/Devices/Server/Linux/rrdTemplates/SystemUptime/datasources/uptime')
    # zap.get_data_source_details('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptime/datasources/AlastairUptimeDS')

    # zap.get_data_sources('/zport/dmd/Devices/Server/Linux/rrdTemplates/Device/datasources/AlastairUptime')

    # zap.add_threshold('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptime', C.API_THRESHOLD_MIN_MAX,
    #                   '2_YEAR_UPTIME',
    #                   ['/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptime/datasources/AlastairUptimeDS/datapoints/AlastairUptimeDS'])
    # zap.add_graph_definition('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptime',
    #                          'AUptime')
    # zap.add_data_point_to_graph('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptime/datasources/AlastairUptimeDS/datapoints/AlastairUptimeDS',
    #                             '/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptime/graphDefs/AUptime', include_thresholds=True)
    # zap.set_template_info(
    #      '/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptime/graphDefs/AUptime/graphPoints/AlastairUptimeDS',
    #      **{C.API_LINE_TYPE: C.API_LINE_TYPE_LINE, C.API_RPN: '8640000,/'})
    # zap.set_graph_definition('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptime/graphDefs/AUptime',
    #                          miny=0, maxy=730, units='Days')
    #
    # zap.bind_or_unbind_template('/zport/dmd/Devices/Server/Linux/devices/eprov-legacyws01.postdirect.com',
    #                             '/zport/dmd/Devices/Server/Linux/rrdTemplates/SystemUptime')

    # zap.get_device_info('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptime')

    # zap.add_local_template('/zport/dmd/Devices/Server/Linux/',
    #                        '/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptime')
    # zap.get_local_templates('/zport/dmd/Devices/Server/Linux/devices/eprov-legacyws01.postdirect.com')
    # zap.set_bound_templates('/zport/dmd/Devices/Server/Linux/devices/eprov-legacyws01.postdirect.com',
    #                         ['Device', 'SystemUptime', 'AlastairUptime'])

    # for tid in ['/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptime',
    #             '/zport/dmd/Devices/Server/Linux/rrdTemplates/SystemUptime']:
    #     zap.bind_or_unbind_template('/zport/dmd/Devices/Server/Linux/devices/eprov-legacyws01.postdirect.com', tid)
    #     zap.bind_or_unbind_template('/zport/dmd/Devices/Server/Linux/devices/eprov-legacyws02.postdirect.com', tid)

    # zap.get_bound_templates('/zport/dmd/Devices/Server/Linux')
    # print zap.bind_templates('/zport/dmd/Devices/Server/Linux/devices/eprov-legacyws01.postdirect.com', ['AlastairUptime', 'SystemUptime', 'AlastairUptimeAUTO'])
    # zap.get_bound_templates('/zport/dmd/Devices/Server/Linux/devices/eprov-legacyws02.postdirect.com')
    #
    zap.add_new_snmp_monitor('AlastairUptimeAUTO', '/zport/dmd/Devices/Server/Linux', oid='1.3.6.1.2.1.25.1.1.0',
                             threshold_max=730, graph_max_y=735, graph_units='Days', RPN='8640000,/', overwrite=True)
    # zap.get_data_sources('/zport/dmd/Devices/Network/BIG-IP/rrdTemplates/BigIpDevice')
    # zap.get_data_points('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptimeAUTO')
    # zap.get_thresholds('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptimeAUTO')
    # zap.get_graphs('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptimeAUTO')
    # zap.get_data_points('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptimeAUTO')
    # zap.get_graph_definition('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptimeAUTO/graphDefs/AlastairUptimeAUTO_graphDefs')
    # zap.get_data_point_details('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptimeAUTO/datasources/AlastairUptimeAUTO_datasources/datapoints/AlastairUptimeAUTO_datasources')
    # zap.get_data_source_details('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptimeAUTO/datasources/AlastairUptimeAUTO_datasources')
    # zap.get_graph_points('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptimeAUTO/graphDefs/AlastairUptimeAUTO_graphDefs')



    # getDataPoints:
    # '/zport/dmd/Devices/Server/Linux/rrdTemplates/Device/datasources/SystemUptime'

    # zap.get_templates()
    # zap.add_linux_host('etestv-joshui01.postdirect.com', **{C.API_SNMP_COMMUNITY: 'qyjy8aka'})
    # zap.add_linux_host('etestv-ald')
    # zap.add_linux_host('eprov-legacyws02.postdirect.com')
    # zap.get_templates('/zport/dmd/Devices/Server/Linux/rrdTemplates')

if __name__ == "__main__":
    main()
