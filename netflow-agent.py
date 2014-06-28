#! /usr/bin/env python

import requests
import random
import copy
import time
import ctypes
import struct
import socket
import json
import threading
import SocketServer
import logging
import logging.handlers
import commands

#ANALYTICS_SERVER = '66.129.237.67'
ANALYTICS_SERVER = '127.0.0.1'
#NETFLOW_SERVER = '50.76.54.133'
NETFLOW_SERVER = '10.10.39.201'
NUM_OF_SITES = 16
NUM_OF_APPS =4 
FLOW_PORT_BASE = 11000
EXPORT_PORT_BASE = 10000
PATH = '/root/guavus-demo'

EGRESS = 0
INGRESS = 1

netflow_header = {
    'version':       {'format': '!H', 'offset': 0, 'value': 5},
    'count':         {'format': '!H', 'offset': 2, 'value': 0},
    'sys_uptime':    {'format': '!I', 'offset': 4, 'value': 0},
    'unix_secs':     {'format': '!I', 'offset': 8, 'value': 0},
    'unix_nsecs':    {'format': '!I', 'offset': 12, 'value': 0},
    'flow_sequence': {'format': '!I', 'offset': 16, 'value': 0},
    'engine_type':   {'format': 'B',  'offset': 20, 'value': 0},
    'engine_id':     {'format': 'B',  'offset': 21, 'value': 0},
    'interval':      {'format': '!H', 'offset': 22, 'value': 0} 
}

query_flow_series_table = {
    "table": "FlowSeriesTable",
    "start_time": 0,
    "end_time": 0,
    "dir": 0,
    "select_fields": [
        "flow_class_id",
        "direction_ing",
        "T",
        "sourcevn",
        "destvn",
        "sourceip",
        "destip",
        "protocol",
        "sport",
        "dport",
        "bytes",
        "packets"
    ]
}

query_flow_record_table = {
    "table": "FlowRecordTable",
    "start_time": 0,
    "end_time": 0,
    "dir": 0,
    "select_fields": [
        "vrouter",
        "sourcevn",
        "sourceip",
        "sport",
        "destvn",
        "destip",
        "dport",
        "protocol",
        "direction_ing",
        "setup_time",
        "teardown_time",
        "agg-bytes",
        "agg-packets"
    ]
}


agent_logger = logging.getLogger('AgentLogger')
agent_logger.setLevel(logging.INFO)
agent_logger_handler = logging.handlers.RotatingFileHandler(
        PATH + '/agent.log', maxBytes = 1048576, backupCount = 5)
agent_logger_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
agent_logger_handler.setFormatter(agent_logger_formatter)
agent_logger.addHandler(agent_logger_handler)

class SnmpTrapHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        buf = repr(self.request[0])
        agent_logger.info('Got a trap')
        agent_logger.info(buf)
        cmd = '/bin/ln -fs %s/probe.py.normal %s/probe.py' %(PATH, PATH)
        status = commands.getstatusoutput(cmd)[0]
        agent_logger.info('Link to normal profile. Status: %d' %(status))
        cmd = 'source %s/openstack.env;/usr/bin/nova reboot generator' %(PATH)
        status = commands.getstatusoutput(cmd)[0]
        agent_logger.info('Reboot generator with normal profile. Status: %d' %(status))


class SnmpTrapServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    pass


class NetFlowClient(object):
    """ UDP client. """
    def __init__(self, port):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.count_total = 0

    def data_pack(self, records, count, boot_time_ms):
        self.count_total += count
        self.buf = ctypes.create_string_buffer(24 + 48 * count)

        header = dict(netflow_header)
        header['count']['value'] = count
        t = time.time()
        header['sys_uptime']['value'] = int(t * 1000) - boot_time_ms
        header['unix_secs']['value'] = int(t)
        header['unix_nsecs']['value'] = int((t - int(t))* 1000000000)
        header['flow_sequence']['value'] = self.count_total

        # Pack NetFlow header into buffer.
        for key in header.keys():
            struct.pack_into(header[key]['format'], self.buf,
                    header[key]['offset'], header[key]['value'])

        # Pack NetFlow flow records into buffer.
        idx = 0
        for rec in records:
            for key in rec.keys():
                #if key == 'first_time':
                #    print key, rec[key]['value']
                #if key == 'pkts':
                #    print key, rec[key]['value']
                #if key == 'octets':
                #    print key, rec[key]['value']
                if rec[key]['value'] < 0:
                    print 'WARNING:', key, rec[key]['value']
                    rec[key]['value'] = 0
                try:
                    struct.pack_into(rec[key]['format'], self.buf,
                            24 + idx * 48 + rec[key]['offset'],
                            rec[key]['value'])
                except:
                    print 'key:', key, 'value:', rec[key]['value']

            idx += 1

    def data_send(self):
        self.sock.sendto(self.buf, (NETFLOW_SERVER, self.port))
        #print 'Sent to port %s' %(self.port)


class QueryClient(object):
    def __init__(self, server, port):
        self.session_create()
        self.server = server
        self.port = port
        self.uri = '/analytics/query'
        self.url = "http://%s:%s%s" %(self.server, self.port, self.uri)
        self.headers = {
                'Content-type': 'application/json; charset="UTF-8"'}

    def session_create(self):
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
                pool_connections=100,
                pool_maxsize=100)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def http_get(self, url, headers = None, query_params = None):
        response = self.session.get(url, headers = headers,
                params = query_params)
        return (response.status_code, response.text)

    def http_post(self, url, headers, body):
        response = self.session.post(url, headers = headers,
                data = body)
        return (response.status_code, response.text)

    def http_delete(self, url, headers, body):
        response = self.session.delete(url, headers = headers,
                data = body)
        return (response.status_code, response.text)

    def http_put(self, url, headers, body):
        response = self.session.put(url, headers = headers,
                data = body)
        return (response.status_code, response.text)

    def http_request(self, op, url, data = None):
        if (op == 'GET'):
            (status, content) = self.http_get(url,
                    headers = self.headers,
                    query_params = data)
        elif (op == 'POST'):
            (status, content) = self.http_post(url,
                    headers = self.headers,
                    body = data)
        elif (op == 'DELETE'):
            (status, content) = self.http_delete(url,
                    headers = self.headers,
                    body = data)
        elif (op == 'PUT'):
            (status, content) = self.http_put(url,
                    headers = self.headers,
                    body = data)
        else:
            raise ValueError
        return content

    def query(self, dir):
        params = query_flow_series_table
        params['dir'] = dir
        # Query for the last 14 seconds
        params['end_time'] = int(time.time() * 1000000)
        params['start_time'] = int((time.time() - 14) * 1000000)
        result = self.http_request(
                op = 'POST',
                url = self.url,
                data = json.dumps(params))
        return json.loads(result)


class Site(object):
    def __init__(self, name, app_port):
        self.nf_client = NetFlowClient(app_port)
        self.record_list_init()
        self.boot_time_ms = int((time.time() - 6000) * 1000)
        self.name = name

    def record_list_init(self):
        self.record_list = []
        self.record_count = 0

    def record_dump(self):
        for rec in self.record_list:
            for key in rec.keys():
                print '%s : %s' %(key, rec[key]['value'])

    def record_send(self):
        if not self.record_count:
            return
        self.nf_client.data_pack(self.record_list, self.record_count,
                self.boot_time_ms)
        self.nf_client.data_send()
        #print 'site %s sent %d records.' %(self.name, self.record_count)
        self.record_list_init()

    def record_parse(self, item):
        record = {
            'src_addr':   {'format': '!I', 'offset': 0, 'value': 0},
            'dst_addr':   {'format': '!I', 'offset': 4, 'value': 0},
            'next_hop':   {'format': '!I', 'offset': 8, 'value': 0},
            'input_idx':  {'format': '!H', 'offset': 12, 'value': 0},
            'output_idx': {'format': '!H', 'offset': 14, 'value': 0},
            'pkts':       {'format': '!I', 'offset': 16, 'value': 0},
            'octets':     {'format': '!I', 'offset': 20, 'value': 0},
            'first_time': {'format': '!I', 'offset': 24, 'value': 0},
            'last_time':  {'format': '!I', 'offset': 28, 'value': 0},
            'src_port':   {'format': '!H', 'offset': 32, 'value': 0},
            'dst_port':   {'format': '!H', 'offset': 34, 'value': 0},
            'pad1':       {'format': 'B',  'offset': 36, 'value': 0},
            'tcp_flags':  {'format': 'B',  'offset': 37, 'value': 0},
            'protocol':   {'format': 'B',  'offset': 38, 'value': 0},
            'tos':        {'format': 'B',  'offset': 39, 'value': 0},
            'src_as':     {'format': '!H', 'offset': 40, 'value': 0},
            'dst_as':     {'format': '!H', 'offset': 42, 'value': 0},
            'src_mask':   {'format': 'B',  'offset': 44, 'value': 0},
            'dst_mask':   {'format': 'B',  'offset': 45, 'value': 0},
            'pad2':       {'format': '!H', 'offset': 46, 'value': 0}
        }
        record['protocol']['value'] = item['protocol']
        record['src_addr']['value'] = struct.unpack('!I',
                socket.inet_aton(item['sourceip']))[0]
        record['dst_addr']['value'] = struct.unpack('!I',
                socket.inet_aton(item['destip']))[0]
        record['src_port']['value'] = item['sport']
        record['dst_port']['value'] = item['dport']

        # Parse record from FlowRecordTable
        #record['pkts']['value'] = item['agg-packets']
        #record['octets']['value'] = item['agg-bytes']
        #record['first_time']['value'] = (
        #        int(item['setup_time'] / 1000) - self.boot_time_ms)
        #if record['first_time']['value'] < 0:
        #    record['first_time']['value'] = 0
        #if item['teardown_time'] > 0:
        #    record['last_time']['value'] = (
        #            int(item['teardown_time'] / 1000) - self.boot_time_ms)
        #    if record['last_time']['value'] < 0:
        #        record['last_time']['value'] = 0

        # Parse record from FlowSeriesTable
        record['pkts']['value'] = item['packets']
        record['octets']['value'] = item['bytes']
        record['first_time']['value'] = (
                int(item['T'] / 1000) - self.boot_time_ms)
        if record['first_time']['value'] < 0:
            record['first_time']['value'] = 0
        # Fake last time.
        record['last_time']['value'] = record['first_time']['value'] + \
                random.randint(1, 100)

        self.record_list.append(record)
        self.record_count += 1

        if (self.record_count == 30):
            self.record_send()


class Agent(object):
    """ Agent """
    def __init__(self):
        self.site_addr_list = []
        for i in range(NUM_OF_SITES):
            addr = '192.168.%d.253' %(i + 10)
            self.site_addr_list.append(addr)
        self.site_list = []
        for i in range(NUM_OF_SITES):
            site = Site(self.site_addr_list[i], EXPORT_PORT_BASE + i)
            self.site_list.append(site)

        self.query_client = QueryClient(
                server = ANALYTICS_SERVER,
                port = 8081)

    def run(self, dir):
        result = self.query_client.query(dir)['value']

        count_query = 0
        count_parse = 0
        for item in result:
            count_query += 1
            if (item['protocol'] != 17):
                continue
            if ((item['sourceip'] not in self.site_addr_list) or
                    (item['dport'] < FLOW_PORT_BASE or
                    item['dport'] >= FLOW_PORT_BASE + NUM_OF_APPS)):
                #print 'src IP: %s' %(item['sourceip'])
                #print 'dst port: %s' %(item['sport'])
                continue

            if (dir == INGRESS):
                site_idx = self.site_addr_list.index(item['sourceip'])
            elif (dir == EGRESS):
                site_idx = self.site_addr_list.index(item['destip'])
            self.site_list[site_idx].record_parse(item)
            count_parse += 1

        if count_query == 0:
            print 'No query result.'
            return
        #else:
            #print 'Received %d records' %(count_query)
            #print 'Parsed %d records' %(count_parse)

        for i in range(NUM_OF_SITES):
            self.site_list[i].record_send()

    def start(self):
        agent_logger.info('Agent starts...')
        count = 0
        while 1:
            self.run(EGRESS)
            time.sleep(4)
            self.run(INGRESS)
            time.sleep(4)
            count += 1
            if (count == 1500):
                cmd = '/bin/ln -fs %s/probe.py.burst %s/probe.py' %(PATH, PATH)
                commands.getstatusoutput(cmd)
                agent_logger.info('Apply burst profile.')
                cmd = 'source %s/openstack.env;/usr/bin/nova reboot generator' %(PATH)
                commands.getstatusoutput(cmd)
                agent_logger.info('Reboot generator with burst profile.')
                count = 0


if __name__ == '__main__':
    server = SnmpTrapServer(('0.0.0.0', 162), SnmpTrapHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    Agent().start()

