#!/bin/sh

nic_device=eth0
ip_addr=10.161.208.134
netmask=255.255.255.224
gateway=10.161.208.142
dns=8.8.8.8
hostname=vm134

setup_nic()
{
    echo "Setup NIC..."

    cat << __EOT__ > /etc/sysconfig/network-scripts/ifcfg-$nic_device
DEVICE=$nic_device
TYPE=Ethernet
ONBOOT=yes
BOOTPROTO=static
IPADDR=$ip_addr
NETMASK=$netmask
GATEWAY=$gateway
DNS1=$dns
NM_CONTROLLED=no
__EOT__
    echo "Done."
}

setup_hostname()
{
    echo "Setup hostname..."
    hostname $hostname
    echo $hostname > /etc/hostname
    echo "$ip_addr  $hostname" >> /etc/hosts
    echo "Done."
}

disable_selinux()
{
    setenforce 0
    sed -i -e 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
}

setup_sshd()
{
    echo "Setup sshd..."
    sed -i -e 's/PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config
    echo "Done."
}

setup_nic
setup_hostname
service network restart
disable_selinux
setup_sshd
reboot

