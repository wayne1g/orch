
import os
import sys
import time
import uuid
import argparse
import novaclient.v1_1.client
from vnc_api import vnc_api


class ConfigVirtualDns():
    def __init__(self, client):
        self.vnc = client.vnc
        self.nova = client.nova
        self.tenant = client.tenant

    def obj_list(self):
        list = self.vnc.virtual_DNSs_list()['virtual-DNSs']
        return list

    def obj_get(self, name):
        for item in self.obj_list():
            if (item['fq_name'][1] == name):
                return self.vnc.virtual_DNS_read(id = item['uuid'])

    def obj_show(self, obj):
        print 'Virtual DNS'
        print 'Name: %s' %(obj.get_fq_name())      
        print 'UUID: %s' %(obj.uuid)
        dns = obj.get_virtual_DNS_data()
        print 'Domain name: %s' %(dns.domain_name)
        print 'Record order: %s' %(dns.record_order)
        print 'Default TTL: %s seconds' %(dns.default_ttl_seconds)
        print 'Next DNS: %s' %(dns.next_virtual_DNS)

    def show(self, args):
        if args.name:
            obj = self.obj_get(args.name)
            if not obj:
                print 'ERROR: Object %s is not found!' %(args.name)
                return
            self.obj_show(obj)
        else:
            list = self.obj_list()
            for item in list:
                print '    %s' %(item['fq_name'][1])

    def add(self, args):
        data = vnc_api.VirtualDnsType(domain_name = args.domain_name,
                dynamic_records_from_client = True,
                record_order = args.record_order,
                default_ttl_seconds = 86400,
                next_virtual_DNS = 'default-domain:' + args.next_dns)
        obj = vnc_api.VirtualDns(name = args.name, virtual_DNS_data = data)
        try:
            self.vnc.virtual_DNS_create(obj)
        except Exception as e:
            print 'ERROR: %s' %(str(e))

    def set(self, args):
        pass

    def delete(self, args):
        try:
            self.vnc.virtual_DNS_delete(
                    fq_name = ['default-domain', args.name])
        except Exception as e:
            print 'ERROR: %s' %(str(e))


class ConfigIpam():
    def __init__(self, client):
        self.vnc = client.vnc
        self.tenant = client.tenant

    def obj_list(self):
        list = self.vnc.network_ipams_list()['network-ipams']
        return list

    def obj_get(self, name):
        for item in self.obj_list():
            if (item['fq_name'][1] == self.tenant.name) and \
                    (item['fq_name'][2] == name):
                return self.vnc.network_ipam_read(id = item['uuid'])

    def dns_show(self, mgmt):
        print '    DNS Type: %s' %(mgmt.ipam_dns_method)
        if (mgmt.ipam_dns_method == 'virtual-dns-server'):
            print '        Virtual DNS Server: %s' %(
                    mgmt.get_ipam_dns_server().virtual_dns_server_name)
        elif (mgmt.ipam_dns_method == 'tenant-dns-server'):
            list = mgmt.get_ipam_dns_server().get_tenant_dns_server_address().get_ip_address()
            print '        Tenant DNS Server:'
            for item in list:
                print '            %s' %(item)

    def dhcp_show(self, mgmt):
        dhcp_opt = {'4':'NTP Server', '15':'Domain Name'}
        print '    DHCP Options:'
        dhcp = mgmt.get_dhcp_option_list()
        if not dhcp:
            return
        for item in dhcp.get_dhcp_option():
            print '        %s: %s' %(dhcp_opt[item.dhcp_option_name],
                    item.dhcp_option_value)

    def obj_show(self, obj):
        print 'IPAM'
        print 'Name: %s' %(obj.get_fq_name())      
        print 'UUID: %s' %(obj.uuid)
        print 'Management:'
        mgmt = obj.get_network_ipam_mgmt()
        if not mgmt:
            return
        self.dns_show(mgmt)
        self.dhcp_show(mgmt)

    def show(self, args):
        if args.name:
            obj = self.obj_get(args.name)
            if not obj:
                print 'ERROR: Object %s is not found!' %(args.name)
                return
            self.obj_show(obj)
        else:
            list = self.obj_list()
            for item in list:
                if (item['fq_name'][1] == self.tenant.name):
                    print '    %s' %(item['fq_name'][2])

    def dns_add(self, args, mgmt):
        type = {'none':'none',
                'default':'default-dns-server',
                'virtual':'virtual-dns-server',
                'tenant':'tenant-dns-server'}
        if not args.dns_type:
            return
        mgmt.set_ipam_dns_method(type[args.dns_type])
        if args.virtual_dns:
            mgmt.set_ipam_dns_server(vnc_api.IpamDnsAddressType(
                    virtual_dns_server_name = args.virtual_dns))
        if args.tenant_dns:
            mgmt.set_ipam_dns_server(vnc_api.IpamDnsAddressType(
                    tenant_dns_server_address = vnc_api.IpAddressesType(
                    ip_address = args.tenant_dns)))

    def dhcp_add(self, args, mgmt):
        if args.domain_name:
            list = mgmt.get_dhcp_option_list()
            if not list:
                list = vnc_api.DhcpOptionsListType()
                mgmt.set_dhcp_option_list(list)
            list.add_dhcp_option(vnc_api.DhcpOptionType(
                    dhcp_option_name = '15',
                    dhcp_option_value = args.domain_name))
        if args.ntp_server:
            list = mgmt.get_dhcp_option_list()
            if not list:
                list = vnc_api.DhcpOptionsListType()
                mgmt.set_dhcp_option_list()
            list.add_dhcp_option(vnc_api.DhcpOptionType(
                    dhcp_option_name = '4',
                    dhcp_option_value = args.ntp_server))

    def add(self, args):
        create = False
        obj = self.obj_get(args.name)
        if not obj:
            obj = vnc_api.NetworkIpam(name = args.name,
                    parent_obj = self.tenant)
            create = True
        mgmt = obj.get_network_ipam_mgmt()
        if not mgmt:
            mgmt = vnc_api.IpamType()
            obj.set_network_ipam_mgmt(mgmt)
        self.dns_add(args, mgmt)
        self.dhcp_add(args, mgmt)
        if create:
            try:
                self.vnc.network_ipam_create(obj)
            except Exception as e:
                print 'ERROR: %s' %(str(e))
        else:
            self.vnc.network_ipam_update(obj)

    def set(self, args):
        pass

    def delete(self, args):
        update = False
        obj = self.obj_get(args.name)
        if not obj:
            print 'ERROR: Object %s is not found!' %(args.name)
            return
        if args.domain_name:
            mgmt = obj.get_network_ipam_mgmt()
            list = mgmt.get_dhcp_option_list()
            for item in list.get_dhcp_option():
                if (item.dhcp_option_name == '15') and \
                    (item.dhcp_option_value == args.domain_name):
                    list.delete_dhcp_option(item)
                    break
            update = True
        if update:
            self.vnc.network_ipam_update(obj)
        else:
            try:
                self.vnc.network_ipam_delete(
                        fq_name = ['default-domain', self.tenant.name,
                        args.name])
            except Exception as e:
                print 'ERROR: %s' %(str(e))


class ConfigPolicy():
    def __init__(self, client):
        self.vnc = client.vnc
        self.tenant = client.tenant

    def obj_list(self):
        list = self.vnc.network_policys_list()['network-policys']
        return list

    def obj_get(self, name):
        for item in self.obj_list():
            if (item['fq_name'][1] == self.tenant.name) and \
                    (item['fq_name'][2] == name):
                return self.vnc.network_policy_read(id = item['uuid'])

    def addr_show(self, addr_list):
        for item in addr_list:
            print '        Virtual Network: %s' %(item.get_virtual_network())

    def port_show(self, port_list):
        for item in port_list:
            print '        %d:%d' %(item.get_start_port(), item.get_end_port())

    def action_show(self, rule):
        list = rule.get_action_list()
        if not list:
            return
        action = list.get_simple_action()
        if action:
            print '        %s' %(action)
        else:
            for item in rule.get_action_list().get_apply_service():
                print '        %s' %(item)

    def rule_show(self, obj):
        rules_obj = obj.get_network_policy_entries()
        if (rules_obj == None):
            return
        list = rules_obj.get_policy_rule()
        count = 1
        for rule in list:
            print 'Rule #%d' %(count)
            print '    Direction: %s' %(rule.get_direction())
            print '    Protocol: %s' %(rule.get_protocol())
            print '    Source Addresses:'
            self.addr_show(rule.get_src_addresses())
            print '    Source Ports:'
            self.port_show(rule.get_src_ports())
            print '    Destination Addresses:'
            self.addr_show(rule.get_dst_addresses())
            print '    Destination Ports:'
            self.port_show(rule.get_dst_ports())
            print '    Action:'
            self.action_show(rule)
            count += 1

    def obj_show(self, obj):
        print 'Policy'
        print 'Name: %s' %(obj.get_fq_name())
        print 'UUID: %s' %(obj.uuid)
        self.rule_show(obj)
        list = obj.get_virtual_network_back_refs()
        if (list != None):
            print '[BR] network:'
            for item in list:
                print '    %s' %(item['to'][2])

    def show(self, args):
        if args.name:
            obj = self.obj_get(args.name)
            if not obj:
                print 'ERROR: Object %s is not found!' %(args.name)
                return
            self.obj_show(obj)
        else:
            list = self.obj_list()
            for item in list:
                if (item['fq_name'][1] == self.tenant.name):
                    print '    %s' %(item['fq_name'][2])

    def add(self, args):
        rule = vnc_api.PolicyRuleType()
        if args.direction:
            rule.set_direction(args.direction)
        else:
            rule.set_direction('<>')
        if args.protocol:
            rule.set_protocol(args.protocol)
        else:
            rule.set_protocol('any')

        net_list = []
        if args.src_net:
            for item in args.src_net:
                net = 'default-domain:%s:%s' %(self.tenant.name, item)
                net_list.append(vnc_api.AddressType(virtual_network = net))
        else:
            net_list.append(vnc_api.AddressType(virtual_network = 'any'))
        rule.set_src_addresses(net_list)

        net_list = []
        if args.dst_net:
            for item in args.dst_net:
                net = 'default-domain:%s:%s' %(self.tenant.name, item)
                net_list.append(vnc_api.AddressType(virtual_network = net))
        else:
            net_list.append(vnc_api.AddressType(virtual_network = 'any'))
        rule.set_dst_addresses(net_list)

        port_list = []
        if args.src_port:
            for item in args.src_port:
                if (item == 'any'):
                    port_list.append(vnc_api.PortType(
                            start_port = -1, end_port = -1))
                else:
                    s_e = item.split(':')
                    port_list.append(vnc_api.PortType(
                            start_port = int(s_e[0]), end_port = int(s_e[1])))
        else:
            port_list.append(vnc_api.PortType(start_port = -1, end_port = -1))
        rule.set_src_ports(port_list)

        port_list = []
        if args.dst_port:
            for item in args.dst_port:
                if (item == 'any'):
                    port_list.append(vnc_api.PortType(
                            start_port = -1, end_port = -1))
                else:
                    s_e = item.split(':')
                    port_list.append(vnc_api.PortType(
                            start_port = int(s_e[0]), end_port = int(s_e[1])))
        else:
            port_list.append(vnc_api.PortType(start_port = -1, end_port = -1))
        rule.set_dst_ports(port_list)

        if args.action:
            if (args.action == 'service'):
                service_list = []
                for item in args.service:
                    service_list.append('default-domain:%s:%s' \
                        %(self.tenant.name, item))
                action_list = vnc_api.ActionListType(
                        apply_service = service_list)
            else:
                action_list = vnc_api.ActionListType(
                        simple_action = args.action)
        else:
            action_list = vnc_api.ActionListType(simple_action = 'pass')
        rule.set_action_list(action_list)

        obj = self.obj_get(name = args.name)
        if obj:
            rules = obj.get_network_policy_entries()
            if not rules:
                rules = vnc_api.PolicyEntriesType(policy_rule = [rule])
            else:
                rules.add_policy_rule(rule)
            try:
                self.vnc.network_policy_update(obj)
            except Exception as e:
                print 'ERROR: %s' %(str(e))
        else:
            rules = vnc_api.PolicyEntriesType(policy_rule = [rule])
            obj = vnc_api.NetworkPolicy(name = args.name,
                    parent_obj = self.tenant,
                    network_policy_entries = rules)
            try:
                self.vnc.network_policy_create(obj)
            except Exception as e:
                print 'ERROR: %s' %(str(e))

    def set(self, args):
        pass

    def rule_del(self, obj, index):
        rules = obj.get_network_policy_entries()
        if not rules:
            return
        rule = rules.get_policy_rule()[index - 1]
        rules.delete_policy_rule(rule)
        self.vnc.network_policy_update(obj)

    def delete(self, args):
        obj = self.obj_get(args.name)
        if not obj:
            print 'ERROR: Object %s is not found!' %(args.name)
            return
        if args.rule:
            self.rule_del(obj, int(args.rule))
        else:
            try:
                self.vnc.network_policy_delete(fq_name = ['default-domain',
                        self.tenant.name, args.name])
            except Exception as e:
                print 'ERROR: %s' %(str(e))


class ConfigSecurityGroup():
    def __init__(self, client):
        self.vnc = client.vnc
        self.tenant = client.tenant

    def obj_list(self):
        list = self.vnc.security_groups_list()['security-groups']
        return list

    def obj_get(self, name):
        for item in self.obj_list():
            if (item['fq_name'][1] == self.tenant.name) and \
                    (item['fq_name'][2] == name):
                return self.vnc.security_group_read(id = item['uuid'])

    def addr_show(self, addr_list):
        for item in addr_list:
            print '        Security Group: %s' %(item.get_security_group())
            subnet = item.get_subnet()
            if subnet:
                print '        Subnet: %s/%d' %(subnet.get_ip_prefix(), \
                        subnet.get_ip_prefix_len())
            else:
                print '        Subnet: None'

    def port_show(self, port_list):
        for item in port_list:
            print '        %d:%d' %(item.get_start_port(), item.get_end_port())

    def rule_show(self, obj):
        rules_obj = obj.get_security_group_entries()
        if (rules_obj == None):
            return
        list = rules_obj.get_policy_rule()
        count = 1
        for rule in list:
            print 'Rule #%d' %(count)
            print '    Direction: %s' %(rule.get_direction())
            print '    Protocol: %s' %(rule.get_protocol())
            print '    Source Addresses:'
            self.addr_show(rule.get_src_addresses())
            print '    Source Ports:'
            self.port_show(rule.get_src_ports())
            print '    Destination Addresses:'
            self.addr_show(rule.get_dst_addresses())
            print '    Destination Ports:'
            self.port_show(rule.get_dst_ports())
            count += 1

    def obj_show(self, obj):
        print 'Security Group'
        print 'Name: %s' %(obj.get_fq_name())
        print 'UUID: %s' %(obj.uuid)
        self.rule_show(obj)

    def show(self, args):
        if args.name:
            obj = self.obj_get(args.name)
            if not obj:
                print 'ERROR: Object %s is not found!' %(args.name)
                return
            self.obj_show(obj)
        else:
            list = self.obj_list()
            for item in list:
                if (item['fq_name'][1] == self.tenant.name):
                    print '    %s' %(item['fq_name'][2])

    def add(self, args):
        rule = vnc_api.PolicyRuleType()
        rule.set_direction('>')
        if args.protocol:
            rule.set_protocol(args.protocol)
        else:
            rule.set_protocol('any')

        addr_list = []
        if args.address:
            for item in args.address:
                prefix = item.split('/')[0]
                len = item.split('/')[1]
                addr_list.append(vnc_api.AddressType(
                        subnet = vnc_api.SubnetType(
                        ip_prefix = prefix, ip_prefix_len = int(len))))
        else:
            addr_list.append(vnc_api.AddressType(
                    subnet = vnc_api.SubnetType(
                    ip_prefix = '0.0.0.0', ip_prefix_len = 0)))

        local_addr_list = [vnc_api.AddressType(security_group = 'local')]

        port_list = []
        if args.port:
            for item in args.port:
                if (item == 'any'):
                    port_list.append(vnc_api.PortType(
                            start_port = -1, end_port = -1))
                else:
                    s_e = item.split(':')
                    port_list.append(vnc_api.PortType(
                            start_port = int(s_e[0]), end_port = int(s_e[1])))
        else:
            port_list.append(vnc_api.PortType(start_port = -1, end_port = -1))

        local_port_list = [vnc_api.PortType(start_port = -1, end_port = -1)]

        if (args.direction == 'ingress'):
            rule.set_src_addresses(addr_list)
            rule.set_src_ports(port_list)
            rule.set_dst_addresses(local_addr_list)
            rule.set_dst_ports(local_port_list)
        else:
            rule.set_src_addresses(local_addr_list)
            rule.set_src_ports(local_port_list)
            rule.set_dst_addresses(addr_list)
            rule.set_dst_ports(port_list)

        obj = self.obj_get(name = args.name)
        if obj:
            rules = obj.get_security_group_entries()
            if not rules:
                rules = vnc_api.PolicyEntriesType(policy_rule = [rule])
            else:
                rules.add_policy_rule(rule)
            try:
                self.vnc.security_group_update(obj)
            except Exception as e:
                print 'ERROR: %s' %(str(e))
        else:
            rules = vnc_api.PolicyEntriesType(policy_rule = [rule])
            obj = vnc_api.SecurityGroup(name = args.name,
                    parent_obj = self.tenant,
                    security_group_entries = rules)
            try:
                self.vnc.security_group_create(obj)
            except Exception as e:
                print 'ERROR: %s' %(str(e))

    def set(self, args):
        pass

    def rule_del(self, obj, index):
        rules = obj.get_security_group_entries()
        if not rules:
            return
        rule = rules.get_policy_rule()[index - 1]
        rules.delete_policy_rule(rule)
        self.vnc.security_group_update(obj)

    def delete(self, args):
        obj = self.obj_get(args.name)
        if not obj:
            print 'ERROR: Object %s is not found!' %(args.name)
            return
        if args.rule:
            self.rule_del(obj, int(args.rule))
        else:
            try:
                self.vnc.security_group_delete(fq_name = ['default-domain',
                        self.tenant.name, args.name])
            except Exception as e:
                print 'ERROR: %s' %(str(e))


class ConfigNetwork():
    def __init__(self, client):
        self.vnc = client.vnc
        self.tenant = client.tenant

    def obj_list(self):
        list = self.vnc.virtual_networks_list()['virtual-networks']
        return list

    def obj_get(self, name):
        for item in self.obj_list():
            if (item['fq_name'][1] == self.tenant.name) and \
                    (item['fq_name'][2] == name):
                return self.vnc.virtual_network_read(id = item['uuid'])

    def prop_route_target_show(self, obj):
        print '[P] Route targets:'
        rt_list = obj.get_route_target_list()
        if not rt_list:
            return
        for rt in rt_list.get_route_target():
            print '    %s' %(rt)

    def child_floating_ip_pool_show(self, obj):
        print '[C] Floating IP pools:'
        pool_list = obj.get_floating_ip_pools()
        if not pool_list:
            return
        for pool in pool_list:
            print '    %s' %(pool['to'][3])
            pool_obj = self.vnc.floating_ip_pool_read(id = pool['uuid'])
            ip_list = pool_obj.get_floating_ips()
            if (ip_list != None):
                for ip in ip_list:
                    ip_obj = self.vnc.floating_ip_read(id = ip['uuid'])
                    print '        %s' %(ip_obj.get_floating_ip_address())

    def ref_ipam_show(self, obj):
        print '[R] IPAMs:'
        ipam_list = obj.get_network_ipam_refs()
        if not ipam_list:
            return
        for item in ipam_list:
            print '    %s' %(item['to'][2])
            subnet_list = item['attr'].get_ipam_subnets()
            for subnet in subnet_list:
                print '        subnet: %s/%d, gateway: %s' %(
                        subnet.get_subnet().get_ip_prefix(),
                        subnet.get_subnet().get_ip_prefix_len(),
                        subnet.get_default_gateway())

    def ref_policy_show(self, obj):
        print '[R] Policies:'
        policy_list = obj.get_network_policy_refs()
        if not policy_list:
            return
        for item in policy_list:
            print '    %s (%d.%d)' %(item['to'][2],
                    item['attr'].get_sequence().get_major(),
                    item['attr'].get_sequence().get_minor())

    def ref_route_table_show(self, obj):
        print '[R] Route Tables:'
        rt_list = obj.get_route_table_refs()
        if not rt_list:
            return
        for item in rt_list:
            print '    %s' %(item['to'][2])

    def obj_show(self, obj):
        print 'Virtual Network'
        print 'Name: %s' %(obj.get_fq_name())      
        print 'UUID: %s' %(obj.uuid)
        self.prop_route_target_show(obj)
        self.child_floating_ip_pool_show(obj)
        self.ref_ipam_show(obj)
        self.ref_policy_show(obj)
        self.ref_route_table_show(obj)

    def show(self, args):
        if args.name:
            obj = self.obj_get(args.name)
            if not obj:
                print 'ERROR: Object %s is not found!' %(args.name)
                return
            self.obj_show(obj)
        else:
            list = self.obj_list()
            for item in list:
                if (item['fq_name'][1] == self.tenant.name):
                    print '    %s' %(item['fq_name'][2])

    def ipam_add(self, obj, args):
        try:
            ipam_obj = self.vnc.network_ipam_read(fq_name = ['default-domain',
                    self.tenant.name, args.ipam])
        except Exception as e:
            print 'ERROR: %s' %(str(e))
            return
        cidr = args.subnet.split('/')
        subnet = vnc_api.SubnetType(ip_prefix = cidr[0],
                ip_prefix_len = int(cidr[1]))
        ipam_subnet = vnc_api.IpamSubnetType(subnet = subnet,
                default_gateway = args.gateway)
        obj.add_network_ipam(ref_obj = ipam_obj,    
                ref_data = vnc_api.VnSubnetsType([ipam_subnet]))

    def ipam_del(self, obj, args):
        try:
            ipam_obj = self.vnc.network_ipam_read(fq_name = ['default-domain',
                    self.tenant.name, args.ipam])
        except Exception as e:
            print 'ERROR: %s' %(str(e))
            return
        obj.del_network_ipam(ref_obj = ipam_obj)

    def policy_add(self, obj, args):
        try:
            policy_obj = self.vnc.network_policy_read(
                    fq_name = ['default-domain', self.tenant.name, args.policy])
        except Exception as e:
            print 'ERROR: %s' %(str(e))
            return
        seq = vnc_api.SequenceType(major = 0, minor = 0)
        obj.add_network_policy(ref_obj = policy_obj,
                ref_data = vnc_api.VirtualNetworkPolicyType(sequence = seq))

    def policy_del(self, obj, args):
        try:
            policy_obj = self.vnc.network_policy_read(
                    fq_name = ['default-domain', self.tenant.name, args.policy])
        except Exception as e:
            print 'ERROR: %s' %(str(e))
            return
        obj.del_network_policy(ref_obj = policy_obj)

    def route_target_add(self, obj, args):
        rt_list = obj.get_route_target_list()
        if not rt_list:
            rt_list = vnc_api.RouteTargetList()
            obj.set_route_target_list(rt_list)
        rt_list.add_route_target('target:%s' %(args.route_target))

    def route_target_del(self, obj, args):
        rt_list = obj.get_route_target_list()
        if not rt_list:
            return
        rt_list.delete_route_target('target:%s' %(args.route_target))

    def route_table_add(self, obj, args):
        try:
            rt_obj = self.vnc.route_table_read(fq_name = ['default-domain',
                    self.tenant.name, args.route_table])
        except Exception as e:
            print 'ERROR: %s' %(str(e))
            return
        obj.add_route_table(ref_obj = rt_obj)

    def route_table_del(self, obj, args):
        try:
            rt_obj = self.vnc.route_table_read(fq_name = ['default-domain',
                    self.tenant.name, args.route_table])
        except Exception as e:
            print 'ERROR: %s' %(str(e))
            return
        obj.del_route_table(ref_obj = rt_obj)

    def add(self, args):
        create = False
        obj = self.obj_get(args.name)
        if not obj:
            obj = vnc_api.VirtualNetwork(name = args.name,
                    parent_obj = self.tenant)
            create = True
        if args.ipam and args.subnet:
            self.ipam_add(obj, args)
        if args.policy:
            self.policy_add(obj, args)
        if args.route_target:
            self.route_target_add(obj, args)
        if args.route_table:
            self.route_table_add(obj, args)
        if create:
            try:
                self.vnc.virtual_network_create(obj)
            except Exception as e:
                print 'ERROR: %s' %(str(e))
        else:
            self.vnc.virtual_network_update(obj)

    def set(self, args):
        pass

    def delete(self, args):
        update = False
        obj = self.obj_get(args.name)
        if not obj:
            print 'ERROR: Object %s is not found!' %(args.name)
        if args.ipam:
            self.ipam_del(obj, args)
            update = True
        if args.policy:
            self.policy_del(obj, args)
            update = True
        if args.route_target:
            self.route_target_del(obj, args)
            update = True
        if args.route_table:
            self.route_table_del(obj, args)
            update = True
        if update:
            self.vnc.virtual_network_update(obj)
        else:
            try:
                self.vnc.virtual_network_delete(id = obj.uuid)
            except Exception as e:
                print 'ERROR: %s' %(str(e))


class ConfigFloatingIpPool():
    def __init__(self, client):
        self.vnc = client.vnc
        self.tenant = client.tenant

    def obj_list(self):
        list = self.vnc.floating_ip_pools_list()['floating-ip-pools']
        return list

    def obj_get(self, name):
        for item in self.obj_list():
            if (item['fq_name'][3] == name):
                return self.vnc.floating_ip_pool_read(id = item['uuid'])

    def prop_subnet_show(self, obj):
        print '[P] Subnet:'
        prefixes = obj.get_floating_ip_pool_prefixes()
        if not prefixes:
            return
        for item in prefixes.get_subnet():
            print '    %s/%s' %(item.get_ip_prefix(), item.get_ip_prefix_len())

    def child_ip_show(self, obj):
        print '[C] Floating IPs:'
        list = obj.get_floating_ips()
        if not list:
            return
        for ip in list:
            ip_obj = self.vnc.floating_ip_read(id = ip['uuid'])
            print '    %s' %(ip_obj.get_floating_ip_address())

    def back_ref_tenant_show(self, obj):
        print '[BR] Tenants:'
        list = obj.get_project_back_refs()
        if not list:
            return
        for item in list:
            print '    %s' %(item['to'][1])

    def obj_show(self, obj):
        print 'Floating IP Pool'
        print 'Name: %s' %(obj.get_fq_name())
        print 'UUID: %s' %(obj.uuid)
        self.prop_subnet_show(obj)
        self.child_ip_show(obj)
        self.back_ref_tenant_show(obj)

    def show(self, args):
        if args.name:
            obj = self.obj_get(args.name)
            if not obj:
                print 'ERROR: Object %s is not found!' %(args.name)
                return
            self.obj_show(obj)
        else:
            list = self.obj_list()
            for item in list:
                print '    %s' %(item['fq_name'][3])

    def fip_add(self, pool_obj):
        id = str(uuid.uuid4())
        obj = vnc_api.FloatingIp(name = id, parent_obj = pool_obj)
        obj.uuid = id
        self.vnc.floating_ip_create(obj)     

    def add(self, args):
        #obj = self.obj_get(args.name)
        #if obj:
        #    if args.floating_ip:
        #        self.fip_add(obj)
        #    return
        if not args.network:
            print 'ERROR: Parent virtual network is not specified!'
            return
        net = ConfigNetwork()
        net.handler_init(self.vnc, None, self.tenant)
        net_obj = net.obj_get(args.network)
        if not net_obj:
            print 'ERROR: Network %s is not found!' %(args.network)
            return
        obj = vnc_api.FloatingIpPool(name = args.name, parent_obj = net_obj)
        try:
            self.vnc.floating_ip_pool_create(obj)
        except Exception as e:
            print 'ERROR: %s' %(str(e))
            return
        self.tenant.add_floating_ip_pool(obj)
        self.vnc.project_update(self.tenant)

    def set(self, args):
        pass

    def fip_delete(self, pool_obj):
        pass

    def delete(self, args):
        obj = self.obj_get(args.name)
        if not obj:
            print 'ERROR: Object %s is not found!' %(args.name)
        #if args.floating_ip:
        #    self.fip_delete(obj)
        #    return
        self.tenant.del_floating_ip_pool(obj)
        self.vnc.project_update(self.tenant)
        try:
            self.vnc.floating_ip_pool_delete(id = obj.uuid)
        except Exception as e:
            print 'ERROR: %s' %(str(e))


class ConfigServiceTemplate():
    def __init__(self, client):
        self.vnc = client.vnc
        self.tenant = client.tenant

    def obj_list(self):
        list = self.vnc.service_templates_list()['service-templates']
        return list

    def obj_get(self, name):
        for item in self.obj_list():
            if (item['fq_name'][1] == name):
                return self.vnc.service_template_read(id = item['uuid'])

    def obj_show(self, obj):
        print 'Service Template'
        print 'Name: %s' %(obj.get_fq_name())      
        print 'UUID: %s' %(obj.uuid)
        properties = obj.get_service_template_properties()
        print 'Service Mode: %s' %(properties.get_service_mode())
        print 'Service Type: %s' %(properties.get_service_type())
        print 'Service Image: %s' %(properties.get_image_name())
        print 'Service Flavor: %s' %(properties.get_flavor())
        print 'Service Interfaces:'
        for item in properties.get_interface_type():
            print '    %s' %(item.get_service_interface_type())

    def show(self, args):
        if args.name:
            obj = self.obj_get(args.name)
            if not obj:
                print 'ERROR: Object %s is not found!' %(args.name)
                return
            self.obj_show(obj)
        else:
            list = self.obj_list()
            for item in list:
                print '    %s' %(item['fq_name'][1])

    def add(self, args):
        obj = vnc_api.ServiceTemplate(name = args.name)
        properties = vnc_api.ServiceTemplateType(service_mode = args.mode,
                service_type = args.type, image_name = args.image,
                flavor = args.flavor, ordered_interfaces = True)
        if args.scale:
            properties.set_service_scaling(args.scale)
            for item in args.interface_type:
                if (args.mode == 'transparent') and \
                       ((item == 'left') or (item == 'right')):
                    shared_ip = True
                elif (args.mode == 'in-network') and (item == 'left'):
                    shared_ip = True
                else:
                    shared_ip = False
                type = vnc_api.ServiceTemplateInterfaceType(
                        service_interface_type = item,
                        shared_ip = shared_ip)
                properties.add_interface_type(type)
        else:
            for item in args.interface_type:
                type = vnc_api.ServiceTemplateInterfaceType(
                        service_interface_type = item,
                        static_route_enable = True)
                properties.add_interface_type(type)
        obj.set_service_template_properties(properties)
        try:
            self.vnc.service_template_create(obj)
        except Exception as e:
            print 'ERROR: %s' %(str(e))

    def set(self, args):
        pass

    def delete(self, args):
        obj = self.obj_get(args.name)
        if not obj:
            print 'ERROR: Object %s is not found!' %(args.name)
        try:
            self.vnc.service_template_delete(id = obj.uuid)
        except Exception as e:
            print 'ERROR: %s' %(str(e))


class ConfigServiceInstance():
    def __init__(self, client):
        self.vnc = client.vnc
        self.tenant = client.tenant

    def obj_list(self):
        list = self.vnc.service_instances_list()['service-instances']
        return list

    def obj_get(self, name):
        for item in self.obj_list():
            if (item['fq_name'][1] == self.tenant.name) and \
                    (item['fq_name'][2] == name):
                return self.vnc.service_instance_read(id = item['uuid'])

    def obj_show(self, obj):
        print 'Service Instance'
        print 'Name: %s' %(obj.get_fq_name())      
        print 'UUID: %s' %(obj.uuid)

    def show(self, args):
        if args.name:
            obj = self.obj_get(args.name)
            if not obj:
                print 'ERROR: Object %s is not found!' %(args.name)
                return
            self.obj_show(obj)
        else:
            list = self.obj_list()
            for item in list:
                if (item['fq_name'][1] == self.tenant.name):
                    print '    %s' %(item['fq_name'][2])

    def net_set(self, arg):
        if len(arg.split(':')) > 1:
            net = 'default-domain:%s:%s' %(arg.split(':')[0],
                    arg.split(':')[1])
        else:
            net = 'default-domain:%s:%s' %(self.tenant.name, arg)
        return net

    def add(self, args):
        obj = vnc_api.ServiceInstance(name = args.name,
                parent_obj = self.tenant)
        properties = vnc_api.ServiceInstanceType(
                auto_policy = args.auto_policy)

        if args.management_network:
            net = self.net_set(args.management_network)
            properties.set_management_virtual_network(net)
            properties.add_interface_list(vnc_api.ServiceInstanceInterfaceType(
                    virtual_network = net))

        if args.left_network:
            net = self.net_set(args.left_network)
        else:
            net = ''
        interface = vnc_api.ServiceInstanceInterfaceType(virtual_network = net)
        if args.left_route:
            route = vnc_api.RouteType(prefix = args.left_route)
            route_table = vnc_api.RouteTableType()
            route_table.add_route(route)
            interface.set_static_routes(route_table)
        properties.set_left_virtual_network(net)
        properties.add_interface_list(interface)

        if args.right_network:
            net = self.net_set(args.right_network)
        else:
            net = ''
        interface = vnc_api.ServiceInstanceInterfaceType(virtual_network = net)
        if args.left_route:
            route = vnc_api.RouteType(prefix = args.left_route)
            route_table = vnc_api.RouteTableType()
            route_table.add_route(route)
            interface.set_static_routes(route_table)
        properties.set_right_virtual_network(net)
        properties.add_interface_list(interface)

        if args.scale_max:
            scale = vnc_api.ServiceScaleOutType(
                    max_instances = int(args.scale_max),
                    auto_scale = True)
        else:
            scale = vnc_api.ServiceScaleOutType()
        properties.set_scale_out(scale)

        obj.set_service_instance_properties(properties)
        try:
            template = self.vnc.service_template_read(
                    fq_name = ['default-domain', args.template])
        except Exception as e:
            print 'ERROR: %s' %(str(e))
        obj.set_service_template(template)
        try:
            self.vnc.service_instance_create(obj)
        except Exception as e:
            print 'ERROR: %s' %(str(e))

    def set(self, args):
        pass

    def delete(self, args):
        obj = self.obj_get(args.name)
        if not obj:
            print 'ERROR: Object %s is not found!' %(args.name)
        try:
            self.vnc.service_instance_delete(id = obj.uuid)
        except Exception as e:
            print 'ERROR: %s' %(str(e))


class ConfigImage():
    def __init__(self, client):
        self.nova = client.nova

    def obj_list(self):
        list = self.nova.images.list()
        return list

    def obj_get(self, name):
        for item in self.obj_list():
            if (item.name == name):
                return item

    def obj_show(self, obj):
        print 'Image'
        print 'Name: %s' %(obj.name)      
        print 'UUID: %s' %(obj.id)

    def show(self, args):
        if args.name:
            obj = self.obj_get(args.name)
            if not obj:
                print 'ERROR: Object %s is not found!' %(args.name)
                return
            self.obj_show(obj)
        else:
            list = self.obj_list()
            for item in list:
                print '    %s' %(item.name)

    def add(self, args):
        pass
    def set(self, args):
        pass
    def delete(self, args):
        pass


class ConfigFlavor():
    def __init__(self, client):
        self.nova = client.nova

    def obj_list(self):
        list = self.nova.flavors.list()
        return list

    def obj_get(self, name):
        for item in self.obj_list():
            if (item.name == name):
                return item

    def obj_show(self, obj):
        print 'Flavor'
        print 'Name: %s' %(obj.name)      
        print 'UUID: %s' %(obj.id)

    def show(self, args):
        if args.name:
            obj = self.obj_get(args.name)
            if not obj:
                print 'ERROR: Object %s is not found!' %(args.name)
                return
            self.obj_show(obj)
        else:
            list = self.obj_list()
            for item in list:
                print '    %s' %(item.name)

    def add(self, args):
        pass
    def set(self, args):
        pass
    def delete(self, args):
        pass


class ConfigVirtualMachine():
    def __init__(self, client):
        self.vnc = client.vnc
        self.nova = client.nova
        self.tenant = client.tenant

    def obj_list(self):
        list = self.nova.servers.list()
        return list

    def obj_get(self, name):
        for item in self.obj_list():
            if (item.name == name):
                return item

    def obj_show(self, obj):
        print 'Virtual Machine'
        print 'Name: %s' %(obj.name)      
        print 'UUID: %s' %(obj.id)
        print 'Status: %s' %(obj.status)
        print 'Addresses:'
        for item in obj.addresses.keys():
            print '    %s  %s' %(obj.addresses[item][0]['addr'], item)

    def show(self, args):
        if args.name:
            obj = self.obj_get(args.name)
            if not obj:
                print 'ERROR: Object %s is not found!' %(args.name)
                return
            self.obj_show(obj)
        else:
            list = self.obj_list()
            for item in list:
                print '    %s' %(item.name)

    def add(self, args):
        try:
            image = self.nova.images.find(name = args.image)
        except Exception as e:
            print 'ERROR: %s' %(str(e))
            return
        try:
            flavor = self.nova.flavors.find(name = args.flavor)
        except Exception as e:
            print 'ERROR: %s' %(str(e))
            return

        networks = []
        net_list = self.vnc.virtual_networks_list()['virtual-networks']
        for item in args.network:
            for vn in net_list:
                if (vn['fq_name'][2] == item):
                    networks.append({'net-id': vn['uuid']})
                    break
            else:
                print 'ERROR: Network %s is not found!' %(item)

        node = None
        if args.node:
            zone = self.nova.availability_zones.list()[1]
            for item in zone.hosts.keys():
                if (item == args.node):
                    break
            else:
                print 'ERROR: Node %s is not found!' %(args.name)

        vm = self.nova.servers.create(name = args.name, image = image,
                flavor = flavor, availability_zone = node,
                nics = networks)
        if args.wait:
            timeout = 12
            while timeout:
                time.sleep(3)
                vm = self.nova.servers.get(vm.id)
                if vm.status != 'BUILD':
                    print 'VM %s is %s' %(vm.name, vm.status)
                    break
                timeout -= 1

    def set(self, args):
        pass

    def delete(self, args):
        obj = self.obj_get(args.name)
        if not obj:
            print 'ERROR: Object %s is not found!' %(args.name)
        self.nova.servers.delete(obj.id)


class ConfigRouteTable():
    def __init__(self, client):
        self.vnc = client.vnc
        self.tenant = client.tenant

    def obj_list(self):
        list = self.vnc.route_tables_list()['route-tables']
        return list

    def obj_get(self, name):
        for item in self.obj_list():
            if (item['fq_name'][1] == self.tenant.name) and \
                    (item['fq_name'][2] == name):
                return self.vnc.route_table_read(id = item['uuid'])

    def obj_show(self, obj):
        print 'Route Table'
        print 'Name: %s' %(obj.get_fq_name())      
        print 'UUID: %s' %(obj.uuid)
        routes = obj.get_routes()
        if not routes:
            return
        for item in routes.get_route():
            print '  %s next-hop %s' %(item.get_prefix(), item.get_next_hop())

    def show(self, args):
        if args.name:
            obj = self.obj_get(args.name)
            if not obj:
                print 'ERROR: Object %s is not found!' %(args.name)
                return
            self.obj_show(obj)
        else:
            list = self.obj_list()
            for item in list:
                if (item['fq_name'][1] == self.tenant.name):
                    print '    %s' %(item['fq_name'][2])

    def route_add(self, obj, route):
        routes = obj.get_routes()
        if not routes:
            routes = vnc_api.RouteTableType()
            obj.set_routes(routes)
        prefix = route.split(':')[0]
        nh = 'default-domain:%s:%s' %(self.tenant.name, route.split(':')[1])
        routes.add_route(vnc_api.RouteType(prefix = prefix, next_hop = nh))

    def route_del(self, obj, prefix):
        routes = obj.get_routes()
        if not routes:
            return
        for item in routes.get_route():
            if (item.get_prefix() == prefix):
                routes.delete_route(item)

    def add(self, args):
        create = False
        obj = self.obj_get(args.name)
        if not obj:
            obj = vnc_api.RouteTable(name = args.name,
                    parent_obj = self.tenant)
            create = True
        if args.route:
            for item in args.route:
                self.route_add(obj, item)
        if create:
            try:
                self.vnc.route_table_create(obj)
            except Exception as e:
                print 'ERROR: %s' %(str(e))
        else:
            self.vnc.route_table_update(obj)

    def set(self, args):
        pass

    def delete(self, args):
        obj = self.obj_get(args.name)
        if not obj:
            print 'ERROR: Object %s is not found!' %(args.name)
        if args.route:
            for item in args.route:
                self.route_del(obj, item)
            self.vnc.route_table_update(obj)
        else:
            try:
                self.vnc.route_table_delete(id = obj.uuid)
            except Exception as e:
                print 'ERROR: %s' %(str(e))


class ConfigInterfaceRouteTable():
    def __init__(self, client):
        self.vnc = client.vnc
        self.tenant = client.tenant

    def obj_list(self):
        list = self.vnc.interface_route_tables_list()['interface-route-tables']
        return list

    def obj_get(self, name):
        for item in self.obj_list():
            if (item['fq_name'][1] == self.tenant.name) and \
                    (item['fq_name'][2] == name):
                return self.vnc.interface_route_table_read(id = item['uuid'])

    def obj_show(self, obj):
        print 'Interface Route Table'
        print 'Name: %s' %(obj.get_fq_name())      
        print 'UUID: %s' %(obj.uuid)
        routes = obj.get_interface_route_table_routes()
        if not routes:
            return
        for item in routes.get_route():
            print '  %s' %(item.get_prefix())

    def show(self, args):
        if args.name:
            obj = self.obj_get(args.name)
            if not obj:
                print 'ERROR: Object %s is not found!' %(args.name)
                return
            self.obj_show(obj)
        else:
            list = self.obj_list()
            for item in list:
                if (item['fq_name'][1] == self.tenant.name):
                    print '    %s' %(item['fq_name'][2])

    def route_add(self, obj, prefix):
        routes = obj.get_interface_route_table_routes()
        if not routes:
            routes = vnc_api.RouteTableType()
            obj.set_interface_route_table_routes(routes)
        routes.add_route(vnc_api.RouteType(prefix = prefix))

    def route_del(self, obj, prefix):
        routes = obj.get_interface_route_table_routes()
        if not routes:
            return
        for item in routes.get_route():
            if (item.get_prefix() == prefix):
                routes.delete_route(item)

    def add(self, args):
        create = False
        obj = self.obj_get(args.name)
        if not obj:
            obj = vnc_api.InterfaceRouteTable(name = args.name,
                    parent_obj = self.tenant)
            create = True
        if args.route:
            for item in args.route:
                self.route_add(obj, item)
        if create:
            try:
                self.vnc.interface_route_table_create(obj)
            except Exception as e:
                print 'ERROR: %s' %(str(e))
        else:
            self.vnc.interface_route_table_update(obj)

    def set(self, args):
        pass

    def delete(self, args):
        obj = self.obj_get(args.name)
        if not obj:
            print 'ERROR: Object %s is not found!' %(args.name)
        if args.route:
            for item in args.route:
                self.route_del(obj, item)
            self.vnc.interface_route_table_update(obj)
        else:
            try:
                self.vnc.interface_route_table_delete(id = obj.uuid)
            except Exception as e:
                print 'ERROR: %s' %(str(e))


class ConfigVmInterface():
    def __init__(self, client):
        self.vnc = client.vnc
        self.tenant = client.tenant
        self.nova = client.nova

    def obj_list(self):
        list = []
        vm_list = self.nova.servers.list()
        vm_if_list = self.vnc.virtual_machine_interfaces_list()['virtual-machine-interfaces']
        for vm in vm_list:
            for vm_if in vm_if_list:
                if (vm_if['fq_name'][0] == vm.id):
                    if_obj = self.vnc.virtual_machine_interface_read(
                            id = vm_if['uuid'])
                    vn_name = if_obj.get_virtual_network_refs()[0]['to'][2]
                    name = '%s:%s' %(vm.name, vn_name)
                    list.append({'name':name, 'uuid':vm_if['uuid'],
                            'obj':if_obj})
        return list

    def obj_get(self, name):
        for item in self.obj_list():
            if (item['name'] == name):
                return item['obj']

    def prop_mac_show(self, obj):
        print '[P] MAC addresses:'
        mac = obj.get_virtual_machine_interface_mac_addresses()
        if not mac:
            return
        for item in mac.get_mac_address():
            print '    %s' %(item)

    def prop_prop_show(self, obj):
        prop = obj.get_virtual_machine_interface_properties()
        if not prop:
            return
        print '[P] Service interface type: %s' \
                %(prop.get_service_interface_type())
        print '[P] Interface mirror: %s' %(prop.get_interface_mirror())

    def ref_sg_show(self, obj):
        print '[R] Security groups:'
        refs = obj.get_security_group_refs()
        if refs:
            for item in obj.get_security_group_refs():
                print '    %s' %(item['to'][2])

    def ref_net_show(self, obj):
        print '[R] Virtual networks:'
        for item in obj.get_virtual_network_refs():
            print '    %s' %(item['to'][2])

    def ref_irt_show(self, obj):
        print '[R] Interface route tables:'
        list = obj.get_interface_route_table_refs()
        if list:
            for item in list:
                print '    %s' %(item['to'][2])

    def back_ref_ip_show(self, obj):
        print '[BR] Instance IPs:'
        list = obj.get_instance_ip_back_refs()
        if not list:
            return
        for item in list:
            ip = self.vnc.instance_ip_read(id = item['uuid'])
            print '    %s' %(ip.get_instance_ip_address())

    def back_ref_fip_show(self, obj):
        print '[BR] Floating IPs:'
        list = obj.get_floating_ip_back_refs()
        if not list:
            return
        for item in list:
            ip = self.vnc.floating_ip_read(id = item['uuid'])
            print '    %s' %(ip.get_floating_ip_address())

    def obj_show(self, obj, name):
        print 'Virtual Machine Interface'
        print 'Name: %s' %(name)      
        print 'UUID: %s' %(obj.uuid)
        self.prop_mac_show(obj)
        self.prop_prop_show(obj)
        self.ref_sg_show(obj)
        self.ref_net_show(obj)
        self.ref_irt_show(obj)
        self.back_ref_ip_show(obj)
        self.back_ref_fip_show(obj)

    def show(self, args):
        if args.name:
            obj = self.obj_get(args.name)
            if not obj:
                print 'ERROR: Object %s is not found!' %(args.name)
                return
            self.obj_show(obj, args.name)
        else:
            list = self.obj_list()
            for item in list:
                    print '    %s' %(item['name'])

    def sg_add(self, obj, args):
        try:
            sg_obj = self.vnc.security_group_read(
                    fq_name = ['default-domain', self.tenant.name,
                    args.security_group])
        except Exception as e:
            print 'ERROR: %s' %(str(e))
            return
        obj.add_security_group(sg_obj)

    def irt_add(self, obj, args):
        try:
            table_obj = self.vnc.interface_route_table_read(
                    fq_name = ['default-domain', self.tenant.name,
                    args.interface_route_table])
        except Exception as e:
            print 'ERROR: %s' %(str(e))
            return
        obj.add_interface_route_table(table_obj)

    def fip_add(self, if_obj, args):
        pool = ConfigFloatingIpPool()
        pool.handler_init(self.vnc, None, self.tenant)
        pool_obj = pool.obj_get(args.floating_ip_pool)
        if not pool_obj:
            print 'ERROR: Floating IP pool %s is not found!' \
                    %(args.floating_ip_pool)
            return
        id = str(uuid.uuid4())
        obj = vnc_api.FloatingIp(name = id, parent_obj = pool_obj)
        obj.uuid = id
        obj.add_project(self.tenant)
        obj.add_virtual_machine_interface(if_obj)
        self.vnc.floating_ip_create(obj)
        self.tenant.add_floating_ip_pool(pool_obj)
        self.vnc.project_update(self.tenant)

    def add(self, args):
        update = False
        obj = self.obj_get(args.name)
        if not obj:
            print 'ERROR: Object %s is not found!' %(args.name)
            return
        if args.security_group:
            self.sg_add(obj, args)
            update = True
        if args.interface_route_table:
            self.irt_add(obj, args)
            update = True
        if args.floating_ip and args.floating_ip_pool:
            self.fip_add(obj, args)
            update = True
        if update:
            self.vnc.virtual_machine_interface_update(obj)

    def set(self, args):
        pass

    def sg_del(self, obj, args):
        try:
            sg_obj = self.vnc.security_group_read(
                    fq_name = ['default-domain', self.tenant.name,
                    args.security_group])
        except Exception as e:
            print 'ERROR: %s' %(str(e))
            return
        obj.del_security_group(sg_obj)

    def irt_del(self, obj, args):
        try:
            table_obj = self.vnc.interface_route_table_read(
                    fq_name = ['default-domain', self.tenant.name,
                    args.interface_route_table])
        except Exception as e:
            print 'ERROR: %s' %(str(e))
            return
        obj.del_interface_route_table(table_obj)

    def fip_del(self, obj, args):
        list = obj.get_floating_ip_back_refs()
        if not list:
            return
        for item in list:
            ip = self.vnc.floating_ip_delete(id = item['uuid'])

    def delete(self, args):
        update = False
        obj = self.obj_get(args.name)
        if not obj:
            print 'ERROR: Object %s is not found!' %(args.name)
            return
        if args.security_group:
            self.sg_del(obj, args)
            update = True
        if args.interface_route_table:
            self.irt_del(obj, args)
            update = True
        if args.floating_ip:
            self.fip_del(obj, args)
            update = True
        if update:
            self.vnc.virtual_machine_interface_update(obj)


class ConfigGlobalVrouter():
    def __init__(self, client):
        self.vnc = client.vnc
        self.tenant = client.tenant

    def obj_list(self):
        list = self.vnc.interface_route_tables_list()['interface-route-tables']
        return list

    def obj_get(self, name):
        obj = self.vnc.global_vrouter_config_read(
                fq_name = ['default-global-system-config',
                'default-global-vrouter-config'])
        return obj

    def obj_show(self, obj):
        pass

    def show(self, args):
        obj = self.obj_get('dummy')
        print 'Link Local Service'
        for item in obj.get_linklocal_services().get_linklocal_service_entry():
            print '  %s  %s:%s  %s:%s' %(item.get_linklocal_service_name(),
                    item.get_linklocal_service_ip(),
                    item.get_linklocal_service_port(),
                    item.get_ip_fabric_service_ip()[0],
                    item.get_ip_fabric_service_port())

    def add(self, args):
        obj = self.obj_get('dummy')
        list = obj.get_linklocal_services().get_linklocal_service_entry()
        list.append(vnc_api.LinklocalServiceEntryType(
                linklocal_service_name = args.name,
                linklocal_service_ip = args.link_local_address.split(':')[0],
                linklocal_service_port = int(args.link_local_address.split(':')[1]),
                ip_fabric_service_ip = [args.fabric_address.split(':')[0]],
                ip_fabric_service_port = int(args.fabric_address.split(':')[1])))
        self.vnc.global_vrouter_config_update(obj)

    def set(self, args):
        pass

    def delete(self, args):
        obj = self.obj_get('dummy')
        list = obj.get_linklocal_services().get_linklocal_service_entry()
        for item in list:
            if (item.get_linklocal_service_name() == args.name):
                list.remove(item)
                break
        self.vnc.global_vrouter_config_update(obj)

class ConfigClient():
    def __init__(self, args):
        self.vnc = vnc_api.VncApi(username = args.username,
                password = args.password, tenant_name = args.tenant,
                api_server_host = args.api_server)
        self.nova = novaclient.v1_1.client.Client(username = args.username,
                api_key = args.password, project_id = args.tenant,
                region_name = args.region,
                auth_url = 'http://%s:35357/v2.0' %(args.api_server))
        self.tenant = self.vnc.project_read(
                fq_name = ['default-domain', args.tenant])

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
                metavar = '[ random | fixed | round-robin ]',
                help = 'The order of DNS records')
        sub_parser.add_argument('--next-dns', metavar = '<next DNS>',
                help = 'The name of next virtual DNS service or the IP address of DNS server reachable by fabric.')

        sub_parser = subparsers.add_parser('ipam')
        sub_parser.set_defaults(obj_class = ConfigIpam,
                obj_parser = sub_parser)
        sub_parser.add_argument('name', nargs = '?', default = None)
        sub_parser.add_argument('--dns-type',
                choices = ['none', 'default', 'tenant', 'virtual'],
                metavar = '[ none | default | virtual | tenant ]',
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
                metavar = '[ <> | > ]', help = 'Direction')
        sub_parser.add_argument('--protocol',
                choices = ['any', 'tcp', 'udp', 'icmp'],
                metavar = '[any | tcp | udp | icmp]', help = 'Protocol')
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
                metavar = '[ pass | deny | drop | reject | alert | log | service ]', help = 'Action')
        sub_parser.add_argument('--service', action = 'append',
                metavar = '<service>', help = 'Service')

        sub_parser = subparsers.add_parser('security-group')
        sub_parser.set_defaults(obj_class = ConfigSecurityGroup,
                obj_parser = sub_parser)
        sub_parser.add_argument('name', nargs = '?', default = None)
        sub_parser.add_argument('--rule', metavar = '<rule index>',
                help = 'Rule index')
        sub_parser.add_argument('--direction', choices = ['ingress', 'egress'],
                metavar = '[ ingress | egress ]', help = 'Direction')
        sub_parser.add_argument('--protocol',
                choices = ['any', 'tcp', 'udp', 'icmp'],
                metavar = '[any | tcp | udp | icmp]', help = 'Protocol')
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

        sub_parser = subparsers.add_parser('floating-ip-pool')
        sub_parser.set_defaults(obj_class = ConfigFloatingIpPool,
                obj_parser = sub_parser)
        sub_parser.add_argument('name', nargs = '?', default = None)
        sub_parser.add_argument('--network', metavar = '<network>',
                help = 'The name of parent virtual network')
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
        sub_parser.add_argument('--node', metavar = '<node name>',
                help = 'Name of compute node')
        sub_parser.add_argument('--wait', action = 'store_true',
                help = 'Wait till VM is active')

        sub_parser = subparsers.add_parser('interface-route-table')
        sub_parser.set_defaults(obj_class = ConfigInterfaceRouteTable,
                obj_parser = sub_parser)
        sub_parser.add_argument('name', nargs = '?', default = None)
        sub_parser.add_argument('--route', action = 'append')

        sub_parser = subparsers.add_parser('vm-interface')
        sub_parser.set_defaults(obj_class = ConfigVmInterface,
                obj_parser = sub_parser)
        sub_parser.add_argument('name', nargs = '?', default = None)
        sub_parser.add_argument('--interface-route-table',
                help = 'The name of interface route table')
        sub_parser.add_argument('--security-group', metavar = 'security group',
                help = 'The name of security group')
        sub_parser.add_argument('--floating-ip', action = 'store_true',
                help = 'Floating IP')
        sub_parser.add_argument('--floating-ip-pool',
                metavar = '<floating Ip pool>',
                help = 'The floating IP pool to allocate a floating IP')

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
        sub_parser.add_argument('--floating-ip', action = 'store_true',
                help = 'Floating IP')
        sub_parser.add_argument('--floating-ip-pool',
                metavar = '<floating Ip pool>',
                help = 'The floating IP pool to allocate a floating IP')

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
                metavar = '[ transparent | in-network | in-network-nat ]',
                help = 'Service mode')
        sub_parser.add_argument('--type',
                choices = ['firewall', 'analyzer'],
                metavar = '[ firewall | analyzer ]',
                help = 'Service type')
        sub_parser.add_argument('--image', metavar = '<image>',
                help = 'Name of image')
        sub_parser.add_argument('--flavor', metavar = '<flavor>',
                help = 'Name of flavor')
        sub_parser.add_argument('--scale', action = 'store_true',
                help = 'Enable service scaling')
        sub_parser.add_argument('--interface-type',
                choices = ['management', 'left', 'right', 'other'],
                metavar = '[ management | left | right | other ]',
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
                metavar = '<management network>',
                help = 'Management network')
        sub_parser.add_argument('--left-network',
                metavar = '<left network>',
                help = 'Left network')
        sub_parser.add_argument('--left-route',
                metavar = '<prefix/length>',
                help = 'Static route to left interface')
        sub_parser.add_argument('--right-network',
                metavar = '<right network>',
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
        if args.cmd == 'add':
            obj.add(args)
        elif args.cmd == 'set':
            obj.set(args)
        elif args.cmd == 'show':
            obj.show(args)
        elif args.cmd == 'delete':
            obj.delete(args)
        elif args.cmd == 'help':
            self.do_help(args)
        else:
            print 'Unknown action %s' %(args.cmd)
            return

    def main(self):
        args = self.parse()
        client = ConfigClient(args)
        self.run(args, client)


if __name__ == '__main__':
    ConfigShell().main()

