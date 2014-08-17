# Build Orchestration Python Sandbox

In a system with the integration of Contrail and OpenStack, the easiest way to trun orchestration Python program is to do that on the configuration node where all required libraries are already installed.

In the case that user wants to run orchestration on some remote host, user needs to either install all required libraries, or create a sandbox including those libraries. Other than prepare required libraries, couple more steps are also needed. Here are all steps.

####1. Prepare dependencies
Assume the basic Python package is already installed on the host. Run the program to find out what dependencies are required, and copy them into the sandbox. Here is an example script to copy OpenStack Nova client API, OpenContrail configuration API and their dependencies into the sandbox for running configuration utility.
```
#!/bin/sh

# CentOS
path="/usr/lib/python2.6/site-packages/"
# Ubuntu
#path="/usr/lib/python2.7/dist-packages/"

file_list="cfgm_common \
           chardet \
           novaclient \
           prettytable.py \
           requests \
           six.py \
           urllib3 \
           vnc_api"

mkdir sandbox

for file in $file_list
do
  cp -r $path$file ./sandbox
done
```
####2. Add endpoint to OpenStack
As a part of the system (Contrail and OpenStack) installation, an internal endpoint is configured for each service in OpenStack. Here is an example.
```
# keystone endpoint-list
+----------------------------------+-----------+-------------------------------------------------------+-------------------------------------------------------+-------------------------------------------------------+----------------------------------+
|                id                |   region  |                       publicurl                       |                      internalurl                      |                        adminurl                       |            service_id            |
+----------------------------------+-----------+-------------------------------------------------------+-------------------------------------------------------+-------------------------------------------------------+----------------------------------+
| 091de2b4d6a547dea59a82734bcbd8d5 | RegionOne | http://10.84.18.4:$(compute_port)s/v1.1/$(tenant_id)s | http://10.84.18.4:$(compute_port)s/v1.1/$(tenant_id)s | http://10.84.18.4:$(compute_port)s/v1.1/$(tenant_id)s | c810ef40150d407a97559670e17f6ca6 |
| 16fbe604747a4c18bed3a673c076c55f | RegionOne |        http://10.84.18.4:8776/v1/$(tenant_id)s        |        http://10.84.18.4:8776/v1/$(tenant_id)s        |        http://10.84.18.4:8776/v1/$(tenant_id)s        | 4030dc6ded464a92abe51b98612a8424 |
| 18f0403b87754b62b3f23f0cefbd81d7 | RegionOne |                 http://10.84.18.4:9696                |                 http://10.84.18.4:9696                |                 http://10.84.18.4:9696                | b4d3a66fa3e14297a83c13f14eb7d7fa |
| 5194f5f26d394c88a40a841b169421e6 | RegionOne |         http://10.84.18.4:$(public_port)s/v2.0        |         http://10.84.18.4:$(admin_port)s/v2.0         |         http://10.84.18.4:$(admin_port)s/v2.0         | e0faa68023644f3892219bf17fc2a0ea |
| 62cd67ddd8aa47dca5691d0784065a91 | RegionOne |          http://localhost:8773/services/Cloud         |          http://localhost:8773/services/Cloud         |          http://localhost:8773/services/Admin         | 3eadbebc08164d60990f9c032bc0d2aa |
| 978deac36747439e9de4ab15b392958d | RegionOne |               http://10.84.18.4:9292/v1               |               http://10.84.18.4:9292/v1               |               http://10.84.18.4:9292/v1               | f46048766b6743d0b35291216ba2436d |
+----------------------------------+-----------+-------------------------------------------------------+-------------------------------------------------------+-------------------------------------------------------+----------------------------------+
```
In the case that API server (configuration node) has multiple interfaces and orchestration will be done through some interface other than the default one, an endpoint needs to be created. Here is a script to create "RegionAdmin" for "nova" service.
```
#!/bin/sh

export OS_USERNAME=admin
export OS_PASSWORD=contrail123
export OS_TENANT_NAME=admin
export OS_AUTH_URL=http://127.0.0.1:35357/v2.0

# OpenStack Compute Nova API
ID=$(keystone service-list | awk '/\ nova\ / {print $2}')

PUBLIC="http://172.18.64.12:\$(compute_port)s/v1.1/\$(tenant_id)s"
ADMIN=$PUBLIC
INTERNAL=$PUBLIC

keystone endpoint-create --region RegionAdmin --service_id $ID --publicurl $PUBLIC --adminurl $ADMIN --internalurl $INTERNAL

```

####3. Patch Contrail API
Contrail API that always get authentication from local host, no matter which API server is specified. Here is the patch fix that. Note, apply this patch to the file in the sandbox.
```
sandbox/vnc_api/vnc_api.py.
--------
    self._authn_server = _read_cfg(cfg_parser, 'auth', 'AUTHN_SERVER',
-                                   self._DEFAULT_AUTHN_SERVER)
+                                   api_server_host)
--------
```

Now, the orchestration can be done on some remote host.

