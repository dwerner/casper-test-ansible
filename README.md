
```bash

./casper-tool.py -b ../casper-node create-network hetzner-test/ 

ansible -u root -i hosts.yaml known_nodes -m ping

ansible-playbook -u root -i hosts.yaml -e '{"chain_path":"hetzner-test"}' upload_chainspec.yaml



# TODO:
# playbook which installs openvpn, grabs the client.ovpn, tc.key, and sets up firewall rules
~# iptables -t nat -A POSTROUTING -o eth0 -s 10.8.0.0/24 -j MASQUERADE
~# iptables -t nat -A POSTROUTING -o eth0 -s 10.^C.0/24 -j MASQUERADE
~# iptables -A INPUT -i eth0 -p udp --dport 1194 -j ACCEPT
~# iptables -A INPUT -i tun0 -j ACCEPT
~# iptables -A FORWARD -i tun0 -o eth0 -s 10.8.0.0/24 -m state --state NEW,RELATED,ESTABLISHED -j ACCEPT
~# ip6tables -A INPUT -i eth0 -p udp --dport 1194 -j ACCEPT
~# ip6tables -A INPUT -i tun0 -j ACCEPT
~# ip6tables -A FORWARD -i tun0 -o eth0 -s 2a01:4f8:c2c:5fc7:80::/112 -m state --state NEW -j ACCEPT
~# iptables-save > /etc/iptables.rules
~# ip6tables-save > /etc/ip6tables.rules

```


./casper-tool.py -b ../casper-node create-network
