AWS Cluster Ansible scripts

- To register with stests:
```bash
cd stests

stests-register-dw <this_dir>/artifacts/<chain_name>/nodes

```

Dependencies:

- aws-cli
- ansible
- ../casper-node (checkout of casper-node)
- ../casper-node-launcher (checkout of casper-node-launcher)

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

ansible -u ubuntu --become  -i aws-hosts.yaml "bootstrap, validators" -a 'bash -c "systemctl status casper-node-heaptracked.service | grep Memory"'


ansible -u ubuntu --become  -i aws-hosts.yaml "bootstrap, validators" -a 'bash -c "ps -o pid,rss,command ax | grep -v \"grep\" | grep -v \"heaptrack\" | grep \"casper-node validator\" | sort -b -k3 -r"'
```

