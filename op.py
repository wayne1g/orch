
import os
import time
import argparse
import requests
import json


class OpClient(object):
    def __init__(self, server, port):
        self.session_create()
        self.server = server
        self.port = port
        self.uri = '/analytics'
        self.url = "http://%s:%s%s" %(self.server, self.port, self.uri)
        self.headers = {
                'Content-type': 'application/json; charset="UTF-8"'}

    def session_create(self):
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections = 100,
                pool_maxsize = 100)
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

    def query(self, uri = None, params = None):
        if params:
            result = self.http_request(op = 'POST', url = self.url + uri,
                    data = json.dumps(params))
        else:
            result = self.http_request(op = 'GET', url = self.url + uri)
        return json.loads(result)


class OpUve():
    def __init__(self):
        pass

    def query(self, client, args):
        if args.name:
            uri = '/uves/%s/%s' %(args.type, args.name)
        else:
            uri = '/uves/%ss' %(args.type)

        result = client.query(uri = uri)
        print json.dumps(result, indent = 4, separators = (':', ','))


class OpFlow():
    def __init__(self):
        self.field_record = {'direction':'direction_ing', 'protocol':'protocol',
                'src-net':'sourcevn', 'dst-net':'destvn',
                'src-ip':'sourceip', 'dst-ip':'destip',
                'src-port':'sport', 'dst-port':'dport',
                'byte-count':'agg-bytes', 'packet-count':'agg-packets',
                'start-time':'setup_time', 'stop-time':'teardown_time'}
        self.field_series = {'direction':'direction_ing', 'protocol':'protocol',
                'src-net':'sourcevn', 'dst-net':'destvn',
                'src-ip':'sourceip', 'dst-ip':'destip',
                'src-port':'sport', 'dst-port':'dport',
                'byte-count':'bytes', 'packet-count':'packets',
                'start-time':'T'}

    def result_print(self, result, args, field_map):
        for item in result['value']:
            line = ''
            for f in args.field:
                line += str(item[field_map[f]]) + '  '
            print line

    def query(self, client, args):
        dir = {'egress':0, 'ingress':1}
        params = {}
        if args.direction:
            params['dir'] = dir[args.direction]
        else:
            params['dir'] = 0
        if args.time:
            sec = int(args.time)
        else:
            sec = 10
        params['end_time'] = int(time.time() * 1000000)
        params['start_time'] = int((time.time() - sec) * 1000000)
        if args.table == 'record':
            params['table'] = 'FlowRecordTable'
            field_map = self.field_record
        elif args.table == 'series':
            params['table'] = 'FlowSeriesTable'
            field_map = self.field_series
        else:
            print 'ERROR: Unknown flow table %s!' %(args.table)
        if args.field:
            params['select_fields'] = []
            for item in args.field:
                params['select_fields'].append(field_map[item])
        else:
            print 'ERROR: Diplay fields are not specified!'
            return
        if args.sort:
            params['sort'] = 1
            params['sort_fields'] = []
            for item in args.sort:
                params['sort_fields'].append(field_map[item])

        result = client.query(uri = '/query', params = params)
        self.result_print(result, args, field_map)


class OpShell():

    def __init__(self):
        pass

    def env(self, *args, **kwargs):
        for arg in args:
            value = os.environ.get(arg, None)
            if value:
                return value
        return kwargs.get('default', '')

    def do_help(self, args):
        if args.sub_cmd:
            self.sub_cmd_dict[args.sub_cmd].print_help()
        else:
            self.parser.print_help()

    def main(self, op_server = None):
        flow = OpFlow()
        uve = OpUve()

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--op-server', default = op_server,
                help = 'Operation server address')

        subparsers = self.parser.add_subparsers()
        self.sub_cmd_dict = {}

        sub_parser = subparsers.add_parser('help')
        sub_parser.set_defaults(obj = self, obj_parser = sub_parser)
        sub_parser.add_argument('sub_cmd', nargs = '?', default = None)

        sub_parser = subparsers.add_parser('flow')
        self.sub_cmd_dict['flow'] = sub_parser
        sub_parser.set_defaults(obj = flow, obj_parser = sub_parser)
        sub_parser.add_argument('table', choices = ['record', 'series'],
                metavar = '[ record | series ]',
                help = 'Flow table')
        sub_parser.add_argument('--time', metavar = '<time in second>',
                help = 'The time frame in second, last 10 sec by default')
        sub_parser.add_argument('--direction',
                choices = ['ingress', 'egress'],
                metavar = '[ ingress | egress ]',
                default = 'egress',
                help = 'The direction, egress by default')
        sub_parser.add_argument('--protocol', help = 'The protocol')
        sub_parser.add_argument('--vrouter', help = 'The vRouter')
        sub_parser.add_argument('--src-net', help = 'The source network')
        sub_parser.add_argument('--dst-net', help = 'The destination network')
        sub_parser.add_argument('--src-ip', help = 'The source IP')
        sub_parser.add_argument('--dst-ip', help = 'The destination IP')
        sub_parser.add_argument('--src-port', help = 'The source port')
        sub_parser.add_argument('--dst-port', help = 'The destination port')
        sub_parser.add_argument('--field', action = 'append',
                choices = ['direction', 'protocol', 'src-net', 'dst-net', \
                'src-ip', 'dst-ip', 'src-port', 'dst-port', 'byte-count',
                'packet-count', 'start-time', 'stop-time'],
                metavar = '[ direction | protocol | src-net | dst-net | ' + \
                'src-ip | dst-ip | src-port | dst-port | byte-count | ' + \
                'packet-count | start-time | stop-time ]',
                help = 'The field to display')
        sub_parser.add_argument('--sort', action = 'append',
                choices = ['direction', 'protocol', 'src-net', 'dst-net', \
                'src-ip', 'dst-ip', 'src-port', 'dst-port', 'byte-count',
                'packet-count', 'start-time', 'stop-time'],
                metavar = '[ direction | protocol | src-net | dst-net | ' + \
                'src-ip | dst-ip | src-port | dst-port | byte-count | ' + \
                'packet-count | start-time | stop-time ]',
                help = 'The field to sort by')

        sub_parser = subparsers.add_parser('uve')
        self.sub_cmd_dict['uve'] = sub_parser
        sub_parser.set_defaults(obj = uve, obj_parser = sub_parser)
        sub_parser.add_argument('type', choices = ['xmpp-peer',
                'service-instance', 'module', 'config-node',
                'virtual-machine', 'bgp-router', 'collector',
                'service-chain', 'generator', 'bgp-peer',
                'virtual-network', 'vrouter', 'dns-node'],
                metavar = '[ xmpp-peer | service-instance | module | ' + \
                'config-node | virtual-machine | bgp-router | ' + \
                'collector | service-chain | generator | bgp-peer | ' + \
                'virtual-network | vrouter | dns-node ]',
                help = 'The type of UVE')
        sub_parser.add_argument('name', nargs = '?', default = None,
                help = 'The name of UVE')

        sub_parser = subparsers.add_parser('log')
        self.sub_cmd_dict['log'] = sub_parser

        args = self.parser.parse_args()
        if (args.obj == self):
            self.do_help(args)
            return

        client = OpClient(server = op_server, port = 8081)

        args.obj.query(client, args)


if __name__ == '__main__':
    OpShell().main()

