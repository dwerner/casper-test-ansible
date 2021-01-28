#!/usr/bin/env python3

from datetime import datetime, timedelta
import os
import subprocess

import click
import shutil
import toml
import yaml

#: List of WASM blobs required to be set up in chainspec.
CONTRACTS = [
        "add_bid",
        "withdraw_bid",
        "delegate",
        "undelegate",
        "transfer_to_account_u512_stored",
        "transfer_to_account_u512"
]


#: Relative directory to be appended to basedir in case WASM dir is not specified.
DEFAULT_WASM_SUBDIR = ["target", "wasm32-unknown-unknown", "release"]


#: The port the node is reachable on.
NODE_PORT = 34553


@click.group()
@click.option(
    "-b",
    "--basedir",
    help="casper-node source code base directory",
    type=click.Path(exists=True, dir_okay=True, file_okay=False, readable=True),
    default=os.path.join(os.path.dirname(__file__), "..", ".."),
)
@click.option(
    "--casper-client",
    help="path to casper client binary (compiled from basedir by default)",
    type=click.Path(exists=True, dir_okay=False, readable=True),
)
@click.option(
    "-p",
    "--production",
    is_flag=True,
    help="Use production chainspec template instead of dev/local",
)
@click.option(
    "-c",
    "--config-template",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help="Node configuration template to use",
)
@click.option(
    "-C",
    "--chainspec-template",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help="Chainspec template to use",
)
@click.option(
    "-w",
    "--wasm-dir",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help="directory containing compiled wasm contracts (defaults to `BASEDIR/{}`".format(
        os.path.join(*DEFAULT_WASM_SUBDIR)
    ),
)
@click.pass_context
def cli(
    ctx,
    basedir,
    production,
    chainspec_template,
    config_template,
    wasm_dir,
    casper_client,
):
    """Casper Network creation tool

    Can be used to create new casper-labs chains with automatic validator setups. Useful for testing."""
    obj = {}
    if chainspec_template:
        obj["chainspec_template"] = chainspec_template
    elif production:
        obj["chainspec_template"] = os.path.join(
            basedir, "resources", "production", "chainspec.toml"
        )
    else:
        obj["chainspec_template"] = os.path.join(
            basedir, "resources", "local", "chainspec.toml.in"
        )
    obj["wasm_dir"] = wasm_dir or os.path.join(basedir, *DEFAULT_WASM_SUBDIR)

    if config_template:
        obj["config_template"] = chainspec_template
    elif production:
        obj["config_template"] = os.path.join(
            basedir, "resources", "production", "config.toml"
        )
    else:
        obj["config_template"] = os.path.join(
            basedir, "resources", "local", "config.toml"
        )

    if casper_client:
        obj["casper_client_argv0"] = [casper_client]
    else:
        obj["casper_client_argv0"] = [
            "cargo",
            "run",
            "--quiet",
            "--manifest-path={}".format(os.path.join(basedir, "client", "Cargo.toml")),
            "--",
        ]

    ctx.obj = obj
    return


@cli.command("create-network")
@click.pass_obj
@click.argument("target-path", type=click.Path(exists=False, writable=True), default="chain-1")
@click.option(
    "-k",
    "--hosts-file",
    help="Parse an hosts.yaml file, using all.children.known_nodes for set of known nodes",
    default="hosts.yaml"
)
@click.option(
    "-n",
    "--network-name",
    help="The network name (also set in chainspec), defaults to output directory name",
)
@click.option(
    "-g",
    "--genesis-in",
    help="Number of seconds from now until Genesis",
    default=300,
    type=int,
)
def create_network(
    obj,
    target_path,
    hosts_file,
    network_name,
    genesis_in,
):
    if not network_name:
        network_name = os.path.basename(os.path.join(target_path))

    # Create the network output directories.
    show_val("Output path", target_path)
    os.mkdir(target_path)
    chain_path = os.path.join(target_path, "chain")
    os.mkdir(chain_path)

    # Prepare paths and copy over all contracts.
    show_val("WASM contracts", obj["wasm_dir"])
    contract_paths = {}
    for contract in CONTRACTS:
        source = os.path.join(obj["wasm_dir"], "{}.wasm".format(contract))
        target = os.path.join(chain_path, "{}.wasm".format(contract))
        shutil.copy(source, target)
        basename = "{}.wasm".format(contract)

        # We use relative paths when creating a self-contained network.
        contract_paths[contract] = basename

    # Update chainspec values.
    chainspec = create_chainspec(
        obj["chainspec_template"], network_name, genesis_in, contract_paths
    )

    chainspec_path = os.path.join(chain_path, "chainspec.toml")
    toml.dump(chainspec, open(chainspec_path, "w"))
    show_val("Chainspec", chainspec_path)

    # Setup each node, collecting all pubkey hashes.
    show_val("Node config template", obj["config_template"])
    pubkeys = list()

    hosts = yaml.load(open(hosts_file), Loader=yaml.FullLoader)
    known_nodes = hosts["all"]["children"]["known_nodes"]["hosts"]

    os.mkdir(os.path.join(target_path, "nodes"))

    for public_address in known_nodes:
        show_val("known node", public_address)

        node_path = os.path.join(target_path, "nodes/{}".format(public_address))
        os.mkdir(node_path)
        pubkey_hex = create_node(
            public_address,
            obj["casper_client_argv0"],
            network_name,
            obj["config_template"],
            node_path,
            list(node for node in known_nodes if node != public_address),
        )
        pubkeys.append(pubkey_hex)

    accounts_path = os.path.join(chain_path, "accounts.csv")
    show_val("accounts file", accounts_path)
    create_accounts_csv(open(accounts_path, "w"), pubkeys)


def create_chainspec(template, network_name, genesis_in, contract_paths):
    """Creates a new chainspec from a template.

    `contract_path` must be a dictionary mapping the keys of `CONTRACTS` to relative or absolute
    paths to be put into the new chainspec.

    Returns a dictionary that can be serialized using `toml`.
    """
    show_val("Chainspec template", template)
    chainspec = toml.load(open(template))

    show_val("Chain name", network_name)
    genesis_timestamp = (datetime.utcnow() + timedelta(seconds=genesis_in)).isoformat(
        "T"
    ) + "Z"

    # Update the chainspec.
    show_val("Genesis", "{} (in {} seconds)".format(genesis_timestamp, genesis_in))
    chainspec["genesis"]["name"] = network_name
    chainspec["genesis"]["timestamp"] = genesis_timestamp

    # Setup WASM contracts.
    for contract in CONTRACTS:
        key = "{}_installer_path".format(contract)
        chainspec["genesis"][key] = contract_paths[contract]

    # Use a relative path for accounts.csv
    chainspec["genesis"]["accounts_path"] = "accounts.csv"

    return chainspec


def create_node(
    public_address, client_argv0, network_name, config_template, node_path, known_nodes
):
    """Create a node configuration inside a network.

    Paths are assumed to be set up using `create_chainspec`.

    Returns the nodes public key as a string."""

    # Generate a key
    key_path = os.path.join(node_path, "keys")
    run_client(client_argv0, "keygen", key_path)

    config = toml.load(open(config_template))
    config["node"]["chainspec_config_path"] = "../chain/chainspec.toml"

    config["consensus"]["secret_key_path"] = os.path.join(
        os.path.relpath(key_path, node_path), "secret_key.pem"
    )

    config["logging"]["format"] = "json"

    # Set the public address to `casper-node-XX`, which will resolve to the internal
    # network IP, and use the automatic port detection by setting `:0`.
    config["network"]["public_address"] = "{}:{}".format(public_address, NODE_PORT)
    config["network"]["bind_address"] = "0.0.0.0:{}".format(NODE_PORT)

    config["network"]["known_addresses"] = [
        "{}:{}".format(n, NODE_PORT)
        for n in known_nodes
    ]

    # Setup for volume operation.
    config["storage"]["path"] = "/storage"
    config["consensus"]["unit_hashes_folder"] = "/storage"

    toml.dump(config, open(os.path.join(node_path, "config.toml"), "w"))

    return open(os.path.join(key_path, "public_key_hex")).read().strip()


def create_accounts_csv(output_file, pubkeys):
    items = pubkeys
    items.sort()
    for key_hex in items:
        motes = 1000000000000000
        weight = 10000000000000
        output_file.write("{},{},{}\n".format(key_hex, motes, weight))


def run_client(argv0, *args):
    """Run the casper client, compiling it if necessary, with the given command-line args"""
    return subprocess.check_output(argv0 + list(args))


def show_val(key, value):
    """Auxiliary function to display a value on the terminal."""

    key = "{:>20s}".format(key)
    click.echo("{}:  {}".format(click.style(key, fg="blue"), value))


if __name__ == "__main__":
    cli()
