#!/bin/sh

orig_path=`pwd`
fab_path=/opt/contrail/utils/fabfile

pre_fab()
{
    echo "Install RPM..."
    rpm -ivh contrail-install-packages-2.0-22~icehouse.el7.noarch.rpm

    cd /opt/contrail/contrail_packages
    sed -i -e 's/pip-python/pip/g' setup.sh
    ./setup.sh

    cp $orig_path/testbed.py $fab_path/testbeds/

    cp $orig_path/rdo.py $fab_path/tasks/
    sed -i -e '/tasks.kernel/a from tasks.rdo import *' $fab_path/__init__.py
    echo "Done."
}

update_testbed()
{
    fab get_token
    token_line=`grep '^admin_token' /opt/contrail/keystone.conf`
    idx=`expr index "$token_line" =`
    token=${token_line:idx}
    sed -i -e "s/__token__/$token/g" $fab_path/testbeds/testbed.py
}

pre_contrail_setup()
{
    ver=`rpm -qa | grep -m 1 openjdk`
    sed -i -e 's/jdk.tls.disabledAlgorithms=SSLv3/#jdk.tls.disabledAlgorithms=SSLv3/g' /usr/lib/jvm/$ver/jre/lib/security/java.security

    cp -r /lib/modules/3.10.0-123.el7.x86_64/extra/net /lib/modules/$(uname -r)/extra

}

pre_fab
cd /opt/contrail/utils
fab setup_rhosp_node
update_testbed
fab install_without_openstack
pre_contrail_setup
fab setup_without_openstack

