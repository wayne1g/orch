#!/bin/sh

subscription-manager register --username aranjan.redhat --password H3Ub9pth3x

subscription-manager repos --enable=rhel-7-server-extras-rpms
subscription-manager repos --enable=rhel-7-server-optional-rpms
subscription-manager repos --enable=rhel-7-server-rpms
subscription-manager repos --enable=rhel-7-server-openstack-5.0-rpms

yum install -y wget

epel_pkg=epel-release-7-5.noarch.rpm
wget http://dl.fedoraproject.org/pub/epel/7/x86_64/e/$epel_pkg
rpm -ivh $epel_pkg

