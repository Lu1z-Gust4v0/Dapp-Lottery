from brownie import Lottery, network, config
from scripts.helpful_scripts import get_account, get_contract
from web3 import Web3
import yaml
import json
import os
import shutil


ENTRY_FEE = Web3.toWei(50, "ether") 


def deploy_lottery(front_end_update=False):
    print(f"Deploying Lottery at {network.show_active()}...")
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed"),
        get_contract("vrf_coordinator"),
        get_contract("link_token"),
        ENTRY_FEE,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"]
    )  
    print("Lottery deployed")

    if front_end_update:
        update_front_end()

    return lottery


def update_front_end(): 
    # Send the build folder
    copy_folders_to_front_end("./build", "./front_end/chain-info")


    # Sending the config file in JSON format
    with open("brownie-config.yaml", "r") as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)
        with open("./front_end/brownie-config.json", "w") as brownie_config_json:
            json.dump(config_dict, brownie_config_json)
    print("Front end updated")


def copy_folders_to_front_end(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def main():
    deploy_lottery()