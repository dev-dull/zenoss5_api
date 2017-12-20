import json
import yaml
import socket
import logging
import requests
from collections import Iterable

try:
    from zenoss5_api.CONSTS import C
except ImportError:
    from CONSTS import C


class ZenossError(Exception):
    pass


class ZenossAPI(object):
    def __init__(self, credentials, host=C.API_URI_HOST, ssl_verify=C.SSL_VERIFY):
        self.credentials = self._credentials_check(credentials)
        self.host = self._host_check(host)
        self.tid = self._generate_transaction_id()
        self.ssl_verify = ssl_verify

    def _host_check(self, host):
        try:
            socket.gethostbyname(host)
        except socket.gaierror:
            raise ZenossError(C.ERROR_INVALID_HOSTNAME_GOT_S % host)

        return C.API_URI_FORMAT.format(HOST=host)

    def _credentials_check(self, credentials):
        if isinstance(credentials, dict):
            if len(credentials) == 1:
                # Force type to be 'list' for python3 compatibility
                credentials = (list(credentials.keys())[0], list(credentials.values())[0])
            else:
                raise ZenossError(C.ERROR_CREDENTIALS_DICT_FORMAT)
        elif isinstance(credentials, str):
            if ':' not in credentials:
                raise ZenossError(C.ERROR_CREDENTIALS_STR_FORMAT)
            # Using splitlines to strip out any combo of \r and \n that might result from reading a file.
            credentials = tuple(credentials.splitlines()[-1].split(':'))
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
        :param raise_exception: Boolean, when true raise an error if the json is incorrectly formatted.
        :return: The object the json represented (e.g. list, dict, etc.)
        """
        try:
            return json.loads(text)
        except ValueError as e:
            # TODO: log the error
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
                    raise ZenossError(C.ERROR_API_S_UNSUCCESSFUL_GOT_S % json_obj[C.API_RESULT][C.API_SUCCESS])

                if data_key in json_obj[C.API_RESULT]:
                    return json_obj[C.API_RESULT][data_key], json_obj[C.API_RESULT][C.API_SUCCESS]
                return None, json_obj[C.API_RESULT][C.API_SUCCESS]
        elif raise_exception:
            raise ZenossError(C.ERROR_S_OBJECT_NO_ATTRIBUTE_S % (type(json_obj), C.API_RESULT))
        return None, None

    def _generate_transaction_id(self, start=0):
        # TODO: If zenoss accepts strings here & logs the values, we should make the TID include the hostname.
        # This will make changes trace-able.
        tid = start
        while True:
            yield tid
            tid += 1

    def api_request(self, endpoint, action, method, data=[{}], headers=C.HEADER_JSON, raise_json_exception=False,
                    validate_success=False):
        """
        :param endpoint: String, e.g. C.API_ROUTER_DEVICE_ENDPOINT - 'device_router'
        :param action: String, e.g. C.API_ACTION_DEVICE_ROUTER - 'DeviceRouter'
        :param method: String, e.g. C.API_METHOD_GET_DEVICES - 'getDevices'
        :param data: List of dicts, The values that the 'method' takes
        :param headers: Dict, It's here if you need to set something other than a json content type or add something extra.
        :param raise_json_exception: Boolean, when true, raise an error if the json from the API is incorrectly formatted.
        :param validate_success: Boolean, when true, will check if the Zenoss API returned 'success=true' in the JSON response.
        :return: When zenoss responds with status code 200: the unpacked json object (e.g. list, dict)
                 When zenoss responds with any other status code, a tuple (status_code, raw_text)
        """
        # TODO: Look at content-type in header to see if we got json back. Throw exception if HTML.

        uri = (self.host or C.API_URI)+C.API_ENDPOINT+endpoint
        payload = {C.API_ACTION: action, C.API_METHOD: method, C.API_DATA: data if isinstance(data, list) else [data],
                   C.API_TID: next(self.tid)}
        logging.debug(json.dumps(payload, indent=2))

        try:
            r = requests.post(uri, auth=self.credentials, data=json.dumps(payload),
                              headers=headers, verify=bool(self.ssl_verify))
            logging.debug('Status code: %s' % r.status_code)
            try:
                logging.debug('Result: %s' % json.dumps(json.loads(r.text), indent=2))
            except ValueError:
                logging.debug('Result: %s' % r.text)

            # TODO: we should be checking the status code and react+log accordingly.
            if r.status_code == 200:
                results = self._load_json(r.text, raise_exception=raise_json_exception)
                if validate_success and C.API_RESULT in results and C.API_SUCCESS in results[C.API_RESULT]:
                    if results[C.API_RESULT][C.API_SUCCESS]:
                        return results

                    error_message = C.ERROR_GENERIC_UNKNOWN_EXCEPTION_S_S_S_S % (C.API_URI, endpoint, action, method)
                    if C.API_RESULT in results and C.API_MSG in results[C.API_RESULT]:
                        error_message = results[C.API_RESULT][C.API_MSG]

                    raise ZenossError(error_message)
                return results
            else:
                return r.status_code, r.text
        except requests.exceptions.ConnectionError as e:
            # TODO: log it, then log e, then raise e.
            raise e

    ####################################################################################################################
    #  DEVICE functions
    ####################################################################################################################
    def get_devices(self, validate_success=False):
        """
        :param validate_success:
        :return:
        """
        return self.api_request(C.API_ROUTER_DEVICE_ENDPOINT, C.API_ACTION_DEVICE_ROUTER,
                                C.API_METHOD_GET_DEVICES, validate_success=validate_success)

    def add_device(self, hostname, device_class, validate_success=False, **kwargs):
        """
        :param hostname:
        :param device_class:
        :param validate_success:
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
                                C.API_METHOD_ADD_DEVICE, data=[payload], validate_success=validate_success)

    def remove_devices(self, uids, uid, hash_check=C.API_KEYWORD_DEFAULTS[C.API_HASH_CHECK], action=C.API_DELETE,
                       delete_events=C.API_KEYWORD_DEFAULTS[C.API_DELETE_EVENTS], validate_success=False):
        # {"action": "DeviceRouter", "method": "removeDevices", "data": [
        #     {"uids": ["/zport/dmd/Devices/Server/Linux/devices/etestv-joshui01.postdirect.com"], "hashcheck": 1,
        #      "uid": "/zport/dmd/Devices/Server", "action": "delete", "deleteEvents": true}], "type": "rpc", "tid": 29}
        payload = [{C.API_UIDS: uids,
                    C.API_UID: uid,
                    C.API_HASH_CHECK: hash_check,
                    C.API_ACTION: action,
                    C.API_DELETE_EVENTS: delete_events}]
        return self.api_request(C.API_ROUTER_DEVICE_ENDPOINT, C.API_ACTION_DEVICE_ROUTER, C.API_METHOD_REMOVE_DEVICES,
                                data=payload, validate_success=validate_success)

    def add_device_class_node(self, zid, context_uid, description=C.API_KEYWORD_DEFAULTS[C.API_DESCRIPTION],
                              connection_info=C.API_KEYWORD_DEFAULTS[C.API_CONNECTION_INFO],
                              ztype=C.API_KEYWORD_DEFAULTS[C.API_TYPE], validate_success=False):
        # {"action": "DeviceRouter", "method": "addDeviceClassNode", "data": [
        #     {"id": "TerraformBuilt", "description": "", "connectionInfo": [], "type": "organizer",
        #      "contextUid": "/zport/dmd/Devices/Server/Linux"}], "type": "rpc", "tid": 15}
        payload = [{
            C.API_ID: zid,
            C.API_DESCRIPTION: description,
            C.API_CONNECTION_INFO: connection_info,
            C.API_TYPE: ztype,
            C.API_CONTEXT_UID: context_uid
        }]
        return self.api_request(C.API_ROUTER_DEVICE_ENDPOINT, C.API_ACTION_DEVICE_ROUTER, C.API_METHOD_ADD_DEVICE_CLASS,
                                data=payload, validate_success=validate_success)

    def bind_or_unbind_template(self, uid, template_uid, validate_success=False):
        """
        :param uid:
        :param template_uid:
        :param validate_success:
        :return:
        """
        payload = [{C.API_UID: uid, C.API_TEMPLATE_UID: template_uid}]
        return self.api_request(C.API_ROUTER_DEVICE_ENDPOINT, C.API_ACTION_DEVICE_ROUTER,
                                C.API_METHOD_BIND_OR_UNBIND_TEMPLATE, data=payload, validate_success=validate_success)

    def get_device_info(self, uid, keys=None, validate_success=False):
        """
        :param uid:
        :param keys:
        :param validate_success:
        :return:
        """
        keys = self._non_str_iterable(keys)
        payload = [{C.API_UID: uid, C.API_KEYS: keys}]
        return self.api_request(C.API_ROUTER_DEVICE_ENDPOINT, C.API_ACTION_DEVICE_ROUTER,
                                C.API_METHOD_GET_INFO, data=payload, validate_success=validate_success)

    def get_tree(self, zid, validate_success=False):
        """
        :param zid:
        :param validate_success:
        :return:
        """
        payload = [{C.API_ID: zid}]
        return self.api_request(C.API_ROUTER_DEVICE_ENDPOINT, C.API_ACTION_DEVICE_ROUTER, C.API_METHOD_GET_TREE,
                                data=payload, validate_success=validate_success)

    def get_bound_templates(self, uid, validate_success=False):
        """
        :param uid:
        :param validate_success:
        :return:
        """
        payload = [{C.API_UID: uid}]
        return self.api_request(C.API_ROUTER_DEVICE_ENDPOINT, C.API_ACTION_DEVICE_ROUTER,
                                C.API_METHOD_GET_BOUND_TEMPLATES, data=payload, validate_success=validate_success)

    def get_unbound_templates(self, uid, validate_success=False):
        """
        :param uid:
        :param validate_success:
        :return:
        """
        payload = [{C.API_UID: uid}]
        return self.api_request(C.API_ROUTER_DEVICE_ENDPOINT, C.API_ACTION_DEVICE_ROUTER,
                                C.API_METHOD_GET_UNBOUND_TEMPLATES, data=payload, validate_success=validate_success)

    def add_local_template(self, device_uid, template_id, validate_success=False):
        """
        :param device_uid:
        :param template_id:
        :param validate_success:
        :return:
        """
        payload = [{C.API_DEVICE_UID: device_uid, C.API_TEMPLATE_ID: template_id}]
        return self.api_request(C.API_ROUTER_DEVICE_ENDPOINT, C.API_ACTION_DEVICE_ROUTER,
                                C.API_METHOD_ADD_LOCAL_TEMPLATE, data=payload, validate_success=validate_success)

    def remove_local_template(self, device_uid, template_uid, validate_success=False):
        """
        :param device_uid:
        :param template_uid:
        :param validate_success:
        :return:
        """
        payload = [{C.API_DEVICE_UID: device_uid, C.API_TEMPLATE_UID: template_uid}]
        return self.api_request(C.API_ROUTER_DEVICE_ENDPOINT, C.API_ACTION_DEVICE_ROUTER,
                                C.API_METHOD_REMOVE_LOCAL_TEMPLATE, data=payload, validate_success=validate_success)

    def get_local_templates(self, uid, query=None, validate_success=False):
        """
        :param uid:
        :param query:
        :param validate_success:
        :return:
        """
        payload = [{C.API_UID: uid, C.API_QUERY: query}]
        return self.api_request(C.API_ROUTER_DEVICE_ENDPOINT, C.API_ACTION_DEVICE_ROUTER,
                                C.API_METHOD_GET_LOCAL_TEMPLATES, data=payload, validate_success=validate_success)

    def set_bound_templates(self, uid, template_ids, validate_success=False):
        """
        :param uid:
        :param template_ids:
        :param validate_success:
        :return:
        """
        payload = [{C.API_UID: uid, C.API_TEMPLATE_IDS: self._non_str_iterable(template_ids)}]
        return self.api_request(C.API_ROUTER_DEVICE_ENDPOINT, C.API_ACTION_DEVICE_ROUTER,
                                C.API_METHOD_SET_BOUND_TEMPLATES, data=payload, validate_success=validate_success)

    def set_device_info(self, validate_success=False, **kwargs):
        """
        :param validate_success:
        :param kwargs:
        :return:
        """
        # {"action": "DeviceRouter", "method": "setInfo", "data":
        # [{"uid": "/zport/dmd/Devices/Server/Linux/devices/eprov-legacyws01.postdirect.com",
        # "productionState": 1000}], "type": "rpc", "tid": 36}
        payload = [kwargs]
        return self.api_request(C.API_ROUTER_DEVICE_ENDPOINT, C.API_ACTION_DEVICE_ROUTER, C.API_METHOD_SET_INFO,
                                data=payload, validate_success=validate_success)


    ####################################################################################################################
    #  TEMPLATE functions
    ####################################################################################################################
    def add_template(self, zid, target_uid, validate_success=False):
        """
        :param zid: The name to give the template.
        :param target_uid: The device path the template should apply to (e.g. /Server/Linux)
        :param validate_success: Validate that the API returned 'success=true' in the response.
        :return: When zenoss responds with status code 200: the unpacked json object (e.g. list, dict)
                 When zenoss responds with any other status code, a tuple (status_code, raw_text)
        """
        payload = [{C.API_ID: zid, C.API_TARGET_UID: target_uid}]

        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_ADD_TEMPLATE, data=payload, validate_success=validate_success)

    def get_templates(self, zid='', validate_success=False):
        """
        :param zid: String: not used. Exists to mirror Zenoss API and to support any future implementation.
        :param validate_success: Boolean, Validate that the API returned 'success=true' in the response.
        :return:
        """
        payload = [{C.API_ID: zid}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_TEMPLATES, data=payload, validate_success=validate_success)

    def add_data_source(self, template_uid, name, data_source_type=C.API_DATA_SOURCE_TYPE_SNMP, validate_success=False):
        """
        :param template_uid:
        :param name:
        :param data_source_type:
        :param validate_success:
        :return:
        """
        payload = [{C.API_TEMPLATE_UID: template_uid, C.API_NAME: name, C.API_TYPE: data_source_type}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_ADD_DATA_SOURCE, data=payload, validate_success=validate_success)

    def get_data_sources(self, uid, validate_success=False):
        """
        :param uid:
        :param validate_success:
        :return:
        """
        payload = [{C.API_UID: uid}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_DATA_SOURCES, data=payload, validate_success=validate_success)

    def get_data_source_details(self, uid, validate_success=False):
        """
        :param uid:
        :param validate_success:
        :return:
        """
        payload = [{C.API_UID: uid}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_DATA_SOURCE_DETAILS, data=payload, validate_success=validate_success)

    def get_data_source_types(self, query=None, validate_success=False):
        """
        :param query:
        :param validate_success:
        :return:
        """
        payload = [{C.API_QUERY: query or C.API_KEYWORD_DEFAULTS[C.API_QUERY]}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_DATA_SOURCE_TYPES, data=payload, validate_success=validate_success)

    def add_data_point(self, data_source_uid, name, validate_success=False):
        """
        :param data_source_uid:
        :param name:
        :param validate_success:
        :return:
        """
        payload = [{C.API_DATA_SOURCE_UID: data_source_uid, C.API_NAME: name}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_ADD_DATA_POINT, data=payload, validate_success=validate_success)

    def get_data_points(self, uid, query=C.API_KEYWORD_DEFAULTS[C.API_QUERY], validate_success=False):
        """
        :param uid:
        :param query:
        :param validate_success:
        :return:
        """
        payload = [{C.API_UID: uid, C.API_QUERY: query}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_DATA_POINTS, data=payload, validate_success=validate_success)

    def add_graph_definition(self, template_uid, graph_definition_id, validate_success=False):
        """
        :param template_uid:
        :param graph_definition_id:
        :param validate_success:
        :return:
        """
        payload = [{C.API_TEMPLATE_UID: template_uid, C.API_GRAPH_DEFINITION_ID: graph_definition_id}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_ADD_GRAPH_DEFINITION, data=payload, validate_success=validate_success)

    def add_data_point_to_graph(self, data_point_uid, graph_uid,
                                include_thresholds=C.API_KEYWORD_DEFAULTS[C.API_INCLUDE_THRESHOLDS],
                                validate_success=False):
        """
        :param data_point_uid:
        :param graph_uid:
        :param include_thresholds:
        :param validate_success:
        :return:
        """
        payload = [{C.API_DATA_POINT_UID: data_point_uid, C.API_GRAPH_UID: graph_uid,
                    C.API_INCLUDE_THRESHOLDS: include_thresholds}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_ADD_DATA_POINT_TO_GRAPH, data=payload, validate_success=validate_success)

    def set_graph_definition(self, uid, miny=C.API_KEYWORD_DEFAULTS[C.API_MINY],
                             maxy=C.API_KEYWORD_DEFAULTS[C.API_MAXY], units='', validate_success=False, **kwargs):
        """
        :param uid:
        :param miny:
        :param maxy:
        :param units:
        :param validate_success:
        :param kwargs:
        :return:
        """
        kwargs.update({C.API_UID: uid, C.API_MINY: miny, C.API_MAXY: maxy, C.API_UNITS: units})
        payload = [kwargs]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_SET_GRAPH_DEFINITION, data=payload, validate_success=validate_success)

    def get_template_info(self, uid, validate_success=False):
        """
        :param uid:
        :param validate_success:
        :return:
        """
        payload = [{C.API_UID: uid}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                         C.API_METHOD_GET_INFO, data=payload, validate_success=validate_success)

    def set_template_info(self, uid, validate_success=False, **kwargs):
        """
        :param uid:
        :param validate_success:
        :param kwargs:
        :return:
        """
        kwargs.update({C.API_UID: uid})
        payload = [kwargs]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                         C.API_METHOD_SET_INFO, data=payload, validate_success=validate_success)

    def get_threshold_types(self, query=C.API_KEYWORD_DEFAULTS[C.API_QUERY], validate_success=False):
        """
        :param query:
        :param validate_success:
        :return:
        """
        payload = [{C.API_QUERY: query}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_THRESHOLD_TYPES, data=payload, validate_success=validate_success)

    def add_threshold(self, uid, threshold_type, threshold_id, data_points, validate_success=False):
        """
        :param uid:
        :param threshold_type:
        :param threshold_id:
        :param data_points:
        :param validate_success:
        :return:
        """
        payload = [{C.API_UID: uid, C.API_THRESHOLD_ID: threshold_id, C.API_THRESHOLD_TYPE: threshold_type,
                    C.API_DATA_POINTS: data_points}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_ADD_THRESHOLD, data=payload, validate_success=validate_success)

    def get_threshold_details(self, uid, validate_success=False):
        """
        :param uid:
        :param validate_success:
        :return:
        """
        payload = [{C.API_UID: uid}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_THRESHOLD_DETAILS, data=payload, validate_success=validate_success)

    def get_data_point_details(self, uid, validate_success=False):
        """
        :param uid:
        :param validate_success:
        :return:
        """
        payload = [{C.API_UID: uid}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_DATA_POINT_DETAILS, data=payload, validate_success=validate_success)

    def get_thresholds(self, uid, query=C.API_KEYWORD_DEFAULTS[C.API_QUERY], validate_success=False):
        """
        :param uid:
        :param query:
        :param validate_success:
        :return:
        """
        payload = [{C.API_UID: uid, C.API_QUERY: query}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_THRESHOLDS, data=payload, validate_success=validate_success)

    def get_graphs(self, uid, query=C.API_KEYWORD_DEFAULTS[C.API_QUERY], validate_success=False):
        """
        :param uid:
        :param query:
        :param validate_success: UNUSED: The API response does not include a 'success' value for this function!!!
        :return:
        """
        payload = [{C.API_UID: uid, C.API_QUERY: query}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_GRAPHS, data=payload, validate_success=False)

    def get_graph_definition(self, uid, validate_success=False):
        """
        :param uid:
        :param validate_success:
        :return:
        """
        payload = [{C.API_UID: uid}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_GRAPH_DEFINITION, data=payload, validate_success=validate_success)

    def get_graph_points(self, uid, validate_success=False):
        """
        :param uid:
        :param validate_success:
        :return:
        """
        payload = [{C.API_UID: uid}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_GET_GRAPH_POINTS, data=payload, validate_success=validate_success)

    def delete_template(self, uid, validate_success=False):
        """
        :param uid:
        :param validate_success:
        :return:
        """
        payload = [{C.API_UID: uid}]
        return self.api_request(C.API_ROUTER_TEMPLATE_ENDPOINT, C.API_ACTION_TEMPLATE_ROUTER,
                                C.API_METHOD_DELETE_TEMPLATE, data=payload, validate_success=validate_success)

    ####################################################################################################################
    #  MIB functions
    ####################################################################################################################
    def add_oid_mapping(self, uid, zid, oid, node_type=C.API_KEYWORD_DEFAULTS[C.API_NODE_TYPE], validate_success=False):
        """
        :param uid:
        :param zid:
        :param oid:
        :param node_type:
        :param validate_success:
        :return:
        """
        payload = [{C.API_UID: uid, C.API_ID: zid, C.API_OID: oid, C.API_NODE_TYPE: node_type}]
        return self.api_request(C.API_ROUTER_MIB_ENDPOINT, C.API_ACTION_MIB_ROUTER, C.API_METHOD_ADD_OID_MAPPING,
                                data=payload, validate_success=validate_success)

    def get_oid_mappings(self, uid, direction=C.API_KEYWORD_DEFAULTS[C.API_DIR],
                         sort=C.API_KEYWORD_DEFAULTS[C.API_SORT], start=C.API_KEYWORD_DEFAULTS[C.API_START],
                         page=C.API_KEYWORD_DEFAULTS[C.API_PAGE], limit=C.API_KEYWORD_DEFAULTS[C.API_LIMIT],
                         validate_success=False):
        """
        :param uid:
        :param direction:
        :param sort:
        :param start:
        :param page:
        :param limit:
        :param validate_success:
        :return:
        """
        payload = [{C.API_UID: uid,
                    C.API_DIR: direction,
                    C.API_SORT: sort,
                    C.API_START: start,
                    C.API_PAGE: page,
                    C.API_LIMIT: limit}]
        return self.api_request(C.API_ROUTER_MIB_ENDPOINT, C.API_ACTION_MIB_ROUTER, C.API_METHOD_GET_OID_MAPPINGS,
                         data=payload, validate_success=validate_success)

    ####################################################################################################################
    #  Convenience functions
    ####################################################################################################################
    def _payload_filter(self, d):
        # Zenoss alerting behavior is sometimes conditional on what is and is not set. This filter prevents us from
        # setting values that have a blank value.
        return dict(filter(lambda v: v is not None, d.values()))

    def _path_validator(self, data, key, checks, values):
        for d in data:
            if key in d:
                path_parts = d[key].split('/')
                for k, v in checks.items():
                    func = getattr(path_parts[k], v)
                    if not func(values[k]):
                        break
                else:
                    # This else statement only happens when we didn't hit the 'break' statement (the loop
                    # completed and therefore, we found our match)
                    return d[key]
        # This 'else' belongs to the 'for' loop
        else:
            raise ZenossError(C.ERROR_VALUES_S_NO_MATCH_S % (values.values(), key))

    def add_new_snmp_monitor(self, zid, target_uid, oid='', threshold_max=None, threshold_min=None,  graph=True,
                             graph_min_y=-1, graph_max_y=-1, graph_units='', graph_line_type=C.API_LINE_TYPE_LINE,
                             rpn=None, overwrite=False, delete_on_fail=True):

        # declare that this is a thing so if we fail immediately, the 'except' statement doesn't blow up.
        template_uid = ''

        # If we already have the template and we don't want to overwrite it, simply return True.
        try:
            if not overwrite:
                results = self.get_templates(C.API_ENDPOINT+C.API_DEVICES)
                # TODO: is this REALLY any better? (see commit ID 7da529ce79c496f3170664503b3e52bfb362e6d9 - lines 535-538)
                try:
                    if self._path_validator(results[C.API_RESULT], C.API_ID, {0: '__eq__'}, {0: zid}):
                        # It exists and we don't want to overwrite it.
                        return True
                except ZenossError:
                    # It didn't exist, so ignore the error and create it.
                    pass

            if not target_uid.startswith(C.API_ENDPOINT):
                target_uid = C.API_ENDPOINT + target_uid

            datasource_name = '%s_%s' % (zid, C.API_PATH_PART_DATA_SOURCES)
            threshold_name = '%s_%s' % (zid, C.API_PATH_PART_THRESHOLDS)
            graph_name = '%s_%s' % (zid, C.API_PATH_PART_GRAPH_DEFS)

            results = self.add_template(zid, target_uid, validate_success=True)  # create template
            data, success = self._get_result_data(results, data_key=C.API_NODE_CONFIG)
            template_uid = self._path_validator([data], C.API_UID, {-2: '__eq__', -1: '__eq__'},
                                                {-2: C.API_TEMPLATE_TYPE_RRD_TEMPLATES[1:], -1: zid})

            self.add_data_source(template_uid, datasource_name, data_source_type=C.API_DATA_SOURCE_TYPE_SNMP,
                                 validate_success=True)

            results = self.get_data_sources(template_uid, validate_success=True)
            data, success = self._get_result_data(results)
            datasource_uid = self._path_validator(data, C.API_UID, {-2: '__eq__', -1: '__eq__'},
                                                  {-2: C.API_PATH_PART_DATA_SOURCES, -1: datasource_name})

            results = self.get_data_points(template_uid, validate_success=True)
            data, success = self._get_result_data(results)
            # Yes, the last check here really should be the dataSOURCE name (not dataPOINT).
            datapoint_uid = self._path_validator(data, C.API_UID, {-2: '__eq__', -1: '__eq__'},
                                                 {-2: C.API_PATH_PART_DATA_POINTS, -1: datasource_name})

            self.set_template_info(datasource_uid, validate_success=True, **{C.API_OID: oid})

            self.add_threshold(template_uid, C.API_THRESHOLD_MIN_MAX, threshold_name, [datapoint_uid],
                               validate_success=True)

            results = self.get_thresholds(template_uid, validate_success=True)
            data, success = self._get_result_data(results)
            threshold_uid = self._path_validator(data, C.API_UID, {-2: '__eq__', -1: '__eq__'},
                                                 {-2: C.API_PATH_PART_THRESHOLDS, -1: threshold_name})

            payload = self._payload_filter({C.API_MAX_VAL: threshold_max, C.API_MIN_VAL: threshold_min})
            if payload:
                self.set_template_info(threshold_uid, validate_success=True, **payload)

            if graph:
                self.add_graph_definition(template_uid, graph_name, validate_success=True)  # create graph

                # Note that the Zenoss is inconsistent here: No 'success' and no 'data' values returned from the API.
                results = self.get_graphs(template_uid)
                graph_uid = self._path_validator(results[C.API_RESULT], C.API_UID, {-2: '__eq__', -1: '__eq__'},
                                            {-2: C.API_PATH_PART_GRAPH_DEFS, -1: graph_name})

                self.add_data_point_to_graph(datapoint_uid, graph_uid, include_thresholds=True, validate_success=True)

                results = self.get_graph_points(graph_uid, validate_success=True)
                data, success = self._get_result_data(results)
                graph_point_datasource_uid = self._path_validator(data, C.API_UID, {-2: '__eq__', -1: 'endswith'},
                                                                  {-2: C.API_PATH_PART_GRAPH_POINTS, -1: datasource_name})

                payload = self._payload_filter({C.API_LINE_TYPE: graph_line_type, C.API_RPN: rpn})  # example RPN '8640000,/'
                if payload:
                    self.set_template_info(graph_point_datasource_uid, validate_success=True, **payload)
                self.set_graph_definition(graph_uid, miny=graph_min_y, maxy=graph_max_y, units=graph_units,
                                          validate_success=True)
            return self.bind_templates(target_uid, zid)
        except ZenossError as e:
            if delete_on_fail:
                if overwrite:
                    logging.warn(C.WARN_S_AND_S_CONFLICT % ('delete_on_fail', 'overwrite'))
                elif template_uid:
                    # If we don't have a template UID, then nothing happened, so nothing to delete.
                    self.delete_template(template_uid)
            raise e

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

    def add_linux_hosts(self, hostnames, **kwargs):
        """
        :param hostnames:
        :param kwargs:
        :return:
        """
        for hostname in hostnames:
            return self.add_linux_host(hostname, **kwargs)

    def remove_linux_host(self, hostname):
        """
        :param hostname:
        :return:
        """
        return self.remove_linux_hosts([hostname])

    def remove_linux_hosts(self, hostnames):
        """
        :param hostnames:
        :return:
        """
        uids = ['%s/%s' % (C.API_DEVICES_SERVER_LINUX_DEVICES, h) for h in hostnames]
        return self.remove_devices(uids, C.API_DEVICES_SERVER)

    def add_linux_device_class_node(self, zid, description=C.API_KEYWORD_DEFAULTS[C.API_DESCRIPTION],
                                    connection_info=C.API_KEYWORD_DEFAULTS[C.API_CONNECTION_INFO],
                                    ztype=C.API_KEYWORD_DEFAULTS[C.API_TYPE], validate_success=False):
        # {"action": "DeviceRouter", "method": "addDeviceClassNode", "data": [
        #     {"id": "TerraformBuilt", "description": "", "connectionInfo": [], "type": "organizer",
        #      "contextUid": "/zport/dmd/Devices/Server/Linux"}], "type": "rpc", "tid": 15}
        return self.add_device_class_node(zid, C.API_DEVICES_SERVER_LINUX, description=description,
                                          connection_info=connection_info, ztype=ztype,
                                          validate_success=validate_success)

    def set_production_level(self, uid, production_state, validate_success=False):
        """
        :param uid:
        :param production_state:
        :param validate_success:
        :return:
        """
        kwargs = {C.API_UID: uid, C.API_PRODUCTION_STATE: production_state}
        return self.set_device_info(validate_success=validate_success, **kwargs)


def main():
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
    # zap.bind_templates('/zport/dmd/Devices/Server/Linux/devices/etestv-joshui01.postdirect.com', 'AlastairUptimeAUTO')

    # zap.bind_or_unbind_template('jfksdlafjlds', 'jfkdsalfjlasd', validate_success=True)
    # zap.set_production_level('/zport/dmd/Devices/Server/Linux/devices/eprov-legacyws01.postdirect.com', C.API_PRODUCTION_STATE_PRODUCTION)

    # zap.get_bound_templates('/zport/dmd/Devices/Server/Linux')
    # print zap.bind_templates('/zport/dmd/Devices/Server/Linux/devices/eprov-legacyws01.postdirect.com', ['AlastairUptime', 'SystemUptime', 'AlastairUptimeAUTO'])
    # zap.get_bound_templates('/zport/dmd/Devices/Server/Linux/devices/eprov-legacyws02.postdirect.com')

    ### THIS \/  \/  \/
    ### zap.add_new_snmp_monitor('AlastairUptimeAUTO', '/zport/dmd/Devices/Server/Linux', oid='1.3.6.1.2.1.25.1.1.0',
    ###                          threshold_max=730, graph_max_y=735, graph_units='Days', RPN='8640000,/', overwrite=True)

    # zap.get_data_sources('/zport/dmd/Devices/Network/BIG-IP/rrdTemplates/BigIpDevice')
    # zap.get_data_points('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptimeAUTO')
    # zap.get_thresholds('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptimeAUTO')
    # zap.get_graphs('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptimeAUTO')
    # zap.get_data_points('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptimeAUTO')
    # zap.get_graph_definition('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptimeAUTO/graphDefs/AlastairUptimeAUTO_graphDefs')
    # zap.get_data_point_details('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptimeAUTO/datasources/AlastairUptimeAUTO_datasources/datapoints/AlastairUptimeAUTO_datasources')
    # zap.get_data_source_details('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptimeAUTO/datasources/AlastairUptimeAUTO_datasources')
    # zap.get_graph_points('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptimeAUTO/graphDefs/AlastairUptimeAUTO_graphDefs')
    # zap.delete_template('/zport/dmd/Devices/Server/Linux/rrdTemplates/AlastairUptimeAUTO')



    # getDataPoints:
    # '/zport/dmd/Devices/Server/Linux/rrdTemplates/Device/datasources/SystemUptime'

    # zap.get_templates()
    # zap.add_linux_host('etestv-ald.postdirect.com', **{C.API_SNMP_COMMUNITY: 'qyjy8aka'})
    # zap.remove_devices(['/zport/dmd/Devices/Server/Linux/devices/etestv-ald.postdirect.com'],
    #                    '/zport/dmd/Devices/Server')
    # zap.remove_linux_host('etestv-joshui01.postdirect.com')
    # {"action": "DeviceRouter", "method": "removeDevices", "data": [
    #     {"uids": ["/zport/dmd/Devices/Server/Linux/devices/etestv-joshui01.postdirect.com"], "hashcheck": 1,
    #      "uid": "/zport/dmd/Devices/Server", "action": "delete", "deleteEvents": true}], "type": "rpc", "tid": 29}

    # zap.add_linux_device_class_node('TerraformBuilt/ThisIsATest')
    # zap.add_device_class_node('Testing', C.API_DEVICES_SERVER_LINUX+'/TerraformBuilt')
    #zap.get_tree(C.API_DEVICES_SERVER_LINUX)

    # {"action": "DeviceRouter", "method": "addDeviceClassNode", "data": [
    #     {"id": "TerraformBuilt", "description": "", "connectionInfo": [], "type": "organizer",
    #      "contextUid": "/zport/dmd/Devices/Server/Linux"}], "type": "rpc", "tid": 15}


    # zap.add_linux_host('etestv-ald.postdirect.com')
    # zap.add_linux_host('eprov-legacyws02.postdirect.com')
    # zap.get_templates('/zport/dmd/Devices/Server/Linux/rrdTemplates')

    # zap.add_device('etestv-ald.postdirect.com', C.API_DEVICE_CLASS_SERVER_LINUX + '/TerraformBuilt' + '/VMWARE_TEST')
    zap.add_device('etestv-ald.postdirect.com', C.API_DEVICE_CLASS_SERVER_LINUX)

if __name__ == "__main__":
    main()
