# Link Local Service
Contrail supports link local service on link local address 169.254.0.0/16. The initial configuration enables metadata service on 169.254.169.254:80. User can configure other address and port to allow VM access physical devices.
## Orchestration on VM
Link local service allows VM to access physical devices. With configuration, VM will have access to API servers on physical node to orchestrate system. This is normally for the case of tenant self-management.

Here are steps to run [configuration utility](https://github.com/tonyliu0592/orch) on VM.
####1. Download configuration utiliy on API server (configuration node)
Git package is not installed as a part of the integration of Contrail and OpenStack. User can install git on API server and clone the utility, or clone it somewhere else and copy to API server.
```
# git clone https://github.com/tonyliu0592/orch.git
```
####2. Build sandbox
Run `mksb` to copy dependencies. This script is for CentOS. The Python library path needs to be updated for Ubuntu.
```
# cd orch
# ./mksb
```
####3. Patch Contrail API
Contrail API that always get authentication from local host, no matter which API server is specified. Here is the patch fix that. Note, apply this patch to the file in the sandbox.
```
vnc_api/vnc_api.py.
--------
    self._authn_server = _read_cfg(cfg_parser, 'auth', 'AUTHN_SERVER',
-                                   self._DEFAULT_AUTHN_SERVER)
+                                   api_server_host)
--------
```
####4. Add endpoint to OpenStack
Here is the script to create "RegionLinkLocal" for "nova" service.
```
#!/bin/sh

export OS_USERNAME=admin
export OS_PASSWORD=contrail123
export OS_TENANT_NAME=admin
export OS_AUTH_URL=http://127.0.0.1:35357/v2.0

# OpenStack Compute Nova API
ID=$(keystone service-list | awk '/\ nova\ / {print $2}')

PUBLIC="http://169.254.10.10:\$(compute_port)s/v1.1/\$(tenant_id)s"
ADMIN=$PUBLIC
INTERNAL=$PUBLIC

keystone endpoint-create --region RegionLinkLocal --service_id $ID --publicurl $PUBLIC --adminurl $ADMIN --internalurl $INTERNAL

```
####5. Configure link local service
Contrail link local service can be configured on Contrail Web UI, or by this [configuration utility](https://github.com/tonyliu0592/orch).
```
# config add link-local "SSH" --link-local-address 169.254.10.10:22 --fabric-address <API server>:35357
# config add link-local "Keystone Admin" --link-local-address 169.254.10.10:35357 --fabric-address <API server>:35357
# config add link-local "Nova Compute" --link-local-address 169.254.10.10:8774 --fabric-address <API server>:8774
# config add link-local "Contrail Config" --link-local-address 169.254.10.10:8082 --fabric-address <API server>:8082
```
####6. Orchestration in VM
Launch the VM with basic Python package installed. After VM is up and running, login and download sandbox from API server by scp.
```
# scp -r 169.254.10.10:<path to sandbox> ./
```
Now, this configuration utility can be used in VM to orchestrate system.

