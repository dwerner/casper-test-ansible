AWS Cluster Ansible scripts

Dependencies:

- aws-cli
- ansible

TODO:
- create template for security group and instances
- document helper scripts

To disable ansible host key checking, set: 

```bash
export ANSIBLE_HOST_KEY_CHECKING=False
```

```
./build-binaries
./build-chain
./deploy "bootstrap, validators"

./start-service bootstrap
./start-service validators 

./stop-service bootstrap
./clean bootstrap
```

