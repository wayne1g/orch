
from config_obj import *
import argparse

class ConfigShell():

    def __init__(self):
        self.parser_init()

    def env(self, *args, **kwargs):
        for arg in args:
            value = os.environ.get(arg, None)
            if value:
                return value
        return kwargs.get('default', '')

    def do_help(self, args):
        if args.obj_parser:
                args.obj_parser.print_help()
        else:
            self.parser.print_help()

    def parser_init(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--api-server', help = 'API server address')
        parser.add_argument('--username', help = 'User name')
        parser.add_argument('--password', help = 'Password')
        parser.add_argument('--tenant', help = 'Tenant name')
        parser.add_argument('--region', help = 'Region name')

        cmd_list = ['add', 'set', 'show', 'delete', 'help']
        parser.add_argument('cmd', choices = cmd_list)

        subparsers = parser.add_subparsers()
        self.sub_cmd_dict = {}

        sub_parser = subparsers.add_parser('vdns')
        sub_parser.set_defaults(obj_class = ConfigVirtualDns,
                obj_parser = sub_parser)
        sub_parser.add_argument('name', nargs = '?', default = None)
        sub_parser.add_argument('--domain-name', metavar = '<domain name>',
                help = 'The name of DNS domain')
        sub_parser.add_argument('--record-order',
                choices = ['fixed', 'random', 'round-robin'],
                default = 'random',
                metavar = 'random | fixed | round-robin',
                help = 'The order of DNS records')
        sub_parser.add_argument('--next-dns', metavar = '<next DNS>',
                help = 'The name of next virtual DNS service or the IP address of DNS server reachable by fabric.')

        sub_parser = subparsers.add_parser('ipam')
        sub_parser.set_defaults(obj_class = ConfigIpam,
                obj_parser = sub_parser)
        sub_parser.add_argument('name', nargs = '?', default = None)
        sub_parser.add_argument('--dns-type',
                choices = ['none', 'default', 'tenant', 'virtual'],
                metavar = 'none | default | virtual | tenant',
                help = 'The type of DNS service')
        sub_parser.add_argument('--virtual-dns', metavar = '<virtual DNS>',
                help = 'The name of virtual DNS service')
        sub_parser.add_argument('--tenant-dns', metavar = '<tenant DNS>',
                action = 'append',
                help = 'The address of tenant DNS')
        sub_parser.add_argument('--domain-name', metavar = '<domain name>',
                help = 'The name of DNS domain')
        sub_parser.add_argument('--ntp-server', metavar = '<NTP server>',
                help = 'The address of NTP server')

        sub_parser = subparsers.add_parser('policy')
        sub_parser.set_defaults(obj_class = ConfigPolicy,
                obj_parser = sub_parser)
        sub_parser.add_argument('name', nargs = '?', default = None)
        sub_parser.add_argument('--rule', metavar = '<rule index>',
                help = 'Rule index')
        sub_parser.add_argument('--direction', choices = ['<>', '>'],
                metavar = '<> | >', help = 'Direction')
        sub_parser.add_argument('--protocol',
                choices = ['any', 'tcp', 'udp', 'icmp'],
                metavar = 'any | tcp | udp | icmp', help = 'Protocol')
        sub_parser.add_argument('--src-net', action = 'append',
                metavar = '<source network>', help = 'Source network')
        sub_parser.add_argument('--dst-net', action = 'append',
                metavar = '<destination network>', help = 'Destination network')
        sub_parser.add_argument('--src-port', action = 'append', type = str,
                metavar = '<start:end>', help = 'The range of source port')
        sub_parser.add_argument('--dst-port', action = 'append', type = str,
                metavar = '<start:end>', help = 'The range of destination port')
        sub_parser.add_argument('--action',
                choices = ['pass', 'deny', 'drop', 'reject', 'alert',
                'log', 'service'],
                metavar = 'pass | deny | drop | reject | alert | log | service', help = 'Action')
        sub_parser.add_argument('--service', action = 'append',
                metavar = '<service>', help = 'Service')

        sub_parser = subparsers.add_parser('security-group')
        sub_parser.set_defaults(obj_class = ConfigSecurityGroup,
                obj_parser = sub_parser)
        sub_parser.add_argument('name', nargs = '?', default = None)
        sub_parser.add_argument('--rule', metavar = '<rule index>',
                help = 'Rule index')
        sub_parser.add_argument('--direction', choices = ['ingress', 'egress'],
                metavar = 'ingress | egress', help = 'Direction')
        sub_parser.add_argument('--protocol',
                choices = ['any', 'tcp', 'udp', 'icmp'],
                metavar = 'any | tcp | udp | icmp', help = 'Protocol')
        sub_parser.add_argument('--address', action = 'append',
                metavar = '<prefix/length>', help = 'Remote IP address')
        sub_parser.add_argument('--port', action = 'append', type = str,
                metavar = '<start:end>', help = 'The range of remote port')

        sub_parser = subparsers.add_parser('network')
        sub_parser.set_defaults(obj_class = ConfigNetwork,
                obj_parser = sub_parser)
        sub_parser.add_argument('name', nargs = '?', default = None)
        sub_parser.add_argument('--ipam', metavar = '<IPAM>',
                help = 'Name of IPAM')
        sub_parser.add_argument('--subnet', metavar = '<prefix/length>',
                help = 'Subnet prefix and length')
        sub_parser.add_argument('--gateway', metavar = '<gateway>',
                help = 'The gateway of subnet')
        sub_parser.add_argument('--policy', metavar = '<policy>',
                help = 'Network policy')
        sub_parser.add_argument('--route-target', metavar = '<route target>',
                help = 'Route target')
        sub_parser.add_argument('--route-table', metavar = '<route table>',
                help = 'Route table')
        sub_parser.add_argument('--l2', action = 'store_true',
                help = 'Layer 2 network, layer 2&3 by default')
        sub_parser.add_argument('--shared', action = 'store_true',
                help = 'Enable sharing with other tenants')
        sub_parser.add_argument('--external', action = 'store_true',
                help = 'Enable external access')

        sub_parser = subparsers.add_parser('floating-ip-pool')
        sub_parser.set_defaults(obj_class = ConfigFloatingIpPool,
                obj_parser = sub_parser)
        sub_parser.add_argument('name', nargs = '?', default = None)
        #sub_parser.add_argument('--floating-ip', action = 'store_true',
        #        help = 'Floating IP')

        sub_parser = subparsers.add_parser('vm')
        sub_parser.set_defaults(obj_class = ConfigVirtualMachine,
                obj_parser = sub_parser)
        sub_parser.add_argument('name', nargs = '?', default = None)
        sub_parser.add_argument('--image', metavar = '<image>',
                help = 'Name of image')
        sub_parser.add_argument('--flavor', metavar = '<flavor>',
                help = 'Name of flavor')
        sub_parser.add_argument('--network', action = 'append',
                metavar = '<network>',
                help = 'Name of network')
        sub_parser.add_argument('--user-data', metavar = '<fine name>',
                help = 'Full file name containing user data')
        sub_parser.add_argument('--node', metavar = '<node name>',
                help = 'Name of compute node')
        sub_parser.add_argument('--wait', action = 'store_true',
                help = 'Wait till VM is active')

        sub_parser = subparsers.add_parser('interface-route-table')
        sub_parser.set_defaults(obj_class = ConfigInterfaceRouteTable,
                obj_parser = sub_parser)
        sub_parser.add_argument('name', nargs = '?', default = None)
        sub_parser.add_argument('--route', action = 'append')

        sub_parser = subparsers.add_parser('route-table')
        sub_parser.set_defaults(obj_class = ConfigRouteTable,
                obj_parser = sub_parser)
        sub_parser.add_argument('name', nargs = '?', default = None)
        sub_parser.add_argument('--route', action = 'append',
                metavar = '<prefix>/<length>:<next-hop>',
                help = 'The route and next-hop')

        sub_parser = subparsers.add_parser('vm-interface')
        sub_parser.set_defaults(obj_class = ConfigVmInterface,
                obj_parser = sub_parser)
        sub_parser.add_argument('name', nargs = '?', default = None)
        sub_parser.add_argument('--interface-route-table',
                help = 'The name of interface route table')
        sub_parser.add_argument('--security-group', metavar = 'security group',
                help = 'The name of security group')
        sub_parser.add_argument('--address',
                metavar = '<IP address>',
                help = 'IP address')
        sub_parser.add_argument('--floating-ip',
                metavar = 'any | <floating IP>',
                help = 'Floating IP')
        sub_parser.add_argument('--floating-ip-pool',
                metavar = '<tenant>:<network>:<floating IP pool>',
                help = 'The floating IP pool to allocate a floating IP from')

        sub_parser = subparsers.add_parser('image')
        self.sub_cmd_dict['image'] = sub_parser
        sub_parser.set_defaults(obj_class = ConfigImage)
        sub_parser.add_argument('name', nargs = '?', default = None)

        sub_parser = subparsers.add_parser('flavor')
        self.sub_cmd_dict['flavor'] = sub_parser
        sub_parser.set_defaults(obj_class = ConfigFlavor)
        sub_parser.add_argument('name', nargs = '?', default = None)

        sub_parser = subparsers.add_parser('service-template')
        sub_parser.set_defaults(obj_class = ConfigServiceTemplate,
                obj_parser = sub_parser)
        sub_parser.add_argument('name', nargs = '?', default = None)
        sub_parser.add_argument('--mode',
                choices = ['transparent', 'in-network', 'in-network-nat'],
                metavar = 'transparent | in-network | in-network-nat',
                help = 'Service mode')
        sub_parser.add_argument('--type',
                choices = ['firewall', 'analyzer'],
                metavar = 'firewall | analyzer',
                help = 'Service type')
        sub_parser.add_argument('--image', metavar = '<image>',
                help = 'Name of image')
        sub_parser.add_argument('--flavor', metavar = '<flavor>',
                help = 'Name of flavor')
        sub_parser.add_argument('--scale', action = 'store_true',
                help = 'Enable service scaling')
        sub_parser.add_argument('--interface-type',
                choices = ['management', 'left', 'right', 'other'],
                metavar = 'management | left | right | other',
                action = 'append',
                help = 'Type of service interface')

        sub_parser = subparsers.add_parser('service-instance')
        sub_parser.set_defaults(obj_class = ConfigServiceInstance,
                obj_parser = sub_parser)
        sub_parser.add_argument('name', nargs = '?', default = None)
        sub_parser.add_argument('--template',
                metavar = '<service template>',
                help = 'Service template')
        sub_parser.add_argument('--management-network',
                metavar = '[<tenant>:]<management network>',
                help = 'Management network')
        sub_parser.add_argument('--left-network',
                metavar = '[<tenant>:]<left network>',
                help = 'Left network')
        sub_parser.add_argument('--left-route',
                metavar = '<prefix/length>',
                help = 'Static route to left interface')
        sub_parser.add_argument('--right-network',
                metavar = '[<tenant>:]<right network>',
                help = 'Right network')
        sub_parser.add_argument('--right-route',
                metavar = '<prefix/length>',
                help = 'Static route to right interface')
        sub_parser.add_argument('--scale-max',
                metavar = '<max number of instances>',
                help = 'The max number of instances')
        sub_parser.add_argument('--auto-policy', action = 'store_true',
                help = 'Enable automatic policy')

        sub_parser = subparsers.add_parser('link-local')
        sub_parser.set_defaults(obj_class = ConfigGlobalVrouter,
                obj_parser = sub_parser)
        sub_parser.add_argument('name', nargs = '?', default = None)
        sub_parser.add_argument('--link-local-address',
                metavar = '<link local address>:<link local port>',
                help = 'Link Local service address and port')
        sub_parser.add_argument('--fabric-address',
                metavar = '<fabric address>:<fabric port>',
                help = 'Fabric address and port')
        self.parser = parser

    def parse(self, argv = None):
        args = self.parser.parse_args(args = argv)
        return args

    def run(self, args, client):
        obj = args.obj_class(client = client)
        if args.cmd == 'show':
            obj.show(args.name)
        elif args.cmd == 'help':
            self.do_help(args)
        elif args.cmd == 'add':
            if (args.obj_class == ConfigVirtualDns):
                obj.add(args.name, args.record_order, args.next_dns)
            elif (args.obj_class == ConfigIpam):
                obj.add(args.name, args.dns_type, args.virtual_dns,
                        args.tenant_dns, args.domain_name, args.ntp_server)
            elif (args.obj_class == ConfigPolicy):
                obj.add(args.name, args.direction, args.protocol,
                        args.src_net, args.dst_net, args.src_port,
                        args.dst_port, args.action, args.service)
            elif (args.obj_class == ConfigSecurityGroup):
                obj.add(args.name, args.protocol, args.address, args.port,
                        args.direction)
            elif (args.obj_class == ConfigNetwork):
                obj.add(args.name, args.ipam, args.subnet, args.policy,
                        args.route_target, args.route_table, args.shared,
                        args.external, args.l2)
            elif (args.obj_class == ConfigFloatingIpPool):
                obj.add(args.name)
            elif (args.obj_class == ConfigServiceTemplate):
                obj.add(args.name, args.mode, args.type, args.image,
                        args.flavor, args.interface_type)
            elif (args.obj_class == ConfigServiceInstance):
                obj.add(args.name, args.template, args.management_network,
                        args.left_network, args.left_route,
                        args.right_network, args.right_route,
                        args.auto_policy, args.scale_max)
            elif (args.obj_class == ConfigVirtualMachine):
                obj.add(args.name, args.image, args.flavor, args.network,
                        args.node, args.user_data, args.wait)
            elif (args.obj_class == ConfigRouteTable):
                obj.add(args.name, args.route)
            elif (args.obj_class == ConfigInterfaceRouteTable):
                obj.add(args.name, args.route)
            elif (args.obj_class == ConfigVmInterface):
                obj.add(args.name, args.security_group,
                        args.interface_route_table, args.address,
                        args.floating_ip_pool, args.floating_ip)
            elif (args.obj_class == ConfigGlobalVrouter):
                obj.add(args.name, args.link_local_address,
                        args.fabric_address)
        elif args.cmd == 'delete':
            if (args.obj_class == ConfigVirtualDns):
                obj.delete(args.name)
            elif (args.obj_class == ConfigIpam):
                obj.delete(args.name, args.domain_name)
            elif (args.obj_class == ConfigPolicy):
                obj.delete(args.name, args.rule)
            elif (args.obj_class == ConfigSecurityGroup):
                obj.delete(args.name, args.rule)
            elif (args.obj_class == ConfigNetwork):
                obj.delete(args.name, args.ipam, args.policy,
                           args.route_target)
            elif (args.obj_class == ConfigFloatingIpPool):
                obj.delete(args.name)
            elif (args.obj_class == ConfigServiceTemplate):
                obj.delete(args.name)
            elif (args.obj_class == ConfigServiceInstance):
                obj.delete(args.name)
            elif (args.obj_class == ConfigVirtualMachine):
                obj.delete(args.name)
            elif (args.obj_class == ConfigRouteTable):
                obj.delete(args.name, args.route)
            elif (args.obj_class == ConfigInterfaceRouteTable):
                obj.delete(args.name, args.route)
            elif (args.obj_class == ConfigVmInterface):
                obj.delete(args.name, args.security_group,
                           args.interface_route_table, args.address,
                           args.floating_ip)
            elif (args.obj_class == ConfigGlobalVrouter):
                obj.delete(args.name)
        else:
            print 'Unknown action %s' %(args.cmd)
            return

    def main(self):
        args = self.parse()
        #print args
        #return
        client = ConfigClient(args.username, args.password, args.tenant,
                args.api_server, args.region)
        self.run(args, client)


if __name__ == '__main__':
    ConfigShell().main()

