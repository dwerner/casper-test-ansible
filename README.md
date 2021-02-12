AWS Cluster Ansible scripts

- To register with stests:
```bash
cd stests

stests-register-dw <this_dir>/artifacts/<chain_name>/nodes
```

## Dependencies:

- aws-cli
- ansible
- ../casper-node (checkout of casper-node)
- ../casper-node-launcher (checkout of casper-node-launcher)

### `build-binaries`

Build the `casper-node` and `casper-node-launcher` binaries. Note that setting `debug = true` in the top-level Cargo.toml's `[profile.release]` node will make results from heaptrack more verbose.

### `build-chain`

Build the chainspec and config using `casper-tool.py` into `./artifacts/aws-chain-1` destructively.

### `casper-tool.py`

Tool for building the chainspec and config assets for each node. Depends on an ansible inventory file in yaml format resembling example-ansible-inventory.yaml.

### `clean <nodes_list>`

Remove all data and binaries from nodes.

### `clean-config-and-storage-only <nodes_list>`

Remove data only from nodes.

### `deploy <ansible_host_groups>`

Deploy assets and binaries to `<ansible_host_groups>`.

### `deploy-bin-only <ansible_host_groups>`

Deploy only binaries to `<ansible_host_groups>`.

### `deploy-config-only <ansible_host_groups>`

Deploy only chainspec and config to `<ansible_host_groups>`.

### `deploy-service-only <ansible_host_groups>`

Deploy only systemd service files to `<ansible_host_groups>`.

### `describe-aws-instances`

Dumps a list of instances that resemble our test nodes.

### `fetch-logs <ansible_host_groups>`

Fetch logs from all nodes into `./logs`.

### `fetch-profiling-data <ansible_host_groups>`

Fetch heaptrack profiling data from all nodes into `./profiling_data`.

### `rm-storage <ip_addr_list>`

Manually `rm -rf /storage/*` on all ip addresses passed. This is useful if multiple nodes have reached hard disk capacity and need to be cleaned off before ansible can run again.

### `setup-debugtools <ansible_host_groups>`

Install required debug tools on all machines.

### `start-run`

Will build binaries, chainspec, deploy to all nodes in `bootstrap, validators, zero_weight`, then start the services on those nodes in order. Doesn't take any arguments.

### `start-service <ansible_host_groups>`

Start the `casper-node.service` on `<ansible_host_groups>`.

### `start-service-heaptracked`

Start the `casper-node-heaptracked.service` on `<ansible_host_groups>`.

### `start-service-valgrind`

### `status`

Manually `curl -s` the status endpoint of all the nodes.

### `stop-service`

Start all `casper-node*.service`s on `<ansible_host_groups>`.

### `tag_instances.py`

Using `boto3`, rename matching instances (`danw-test*`) with `danw-test-<PublicIpAddress>`.


## Use examples:

To disable ansible host key checking, set: 

Useful to prevent a lot of manual "yes" answers to ssh host key checking:
```bash
export ANSIBLE_HOST_KEY_CHECKING=False
```

```
./build-binaries
./build-chain
./deploy "bootstrap, validators, zero_weight"

./start-service bootstrap
./start-service validators 
./start-service zero_weight 

# check memory consumption of the processes, from systemd's point of view:
ansible -u ubuntu --become -i aws-hosts.yaml "bootstrap, validators, zero_weight" -a 'bash -c "systemctl status casper-node-heaptracked.service | grep Memory"'

# check memory consumption using ps:
ansible -u ubuntu --become  -i aws-hosts.yaml "bootstrap, validators, zero_weight" -a 'bash -c "ps -o pid,rss,command ax | grep -v \"grep\" | grep -v \"heaptrack\" | grep \"casper-node validator\" | sort -b -k3 -r"'

...
# run stests tests
...

./stop-service bootstrap
./clean bootstrap
```

