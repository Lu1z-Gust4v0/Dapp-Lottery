from brownie import Lottery, network, config
from scripts.helpful_scripts import get_account, get_contract
from web3 import Web3

ENTRY_FEE = Web3.toWei(50, "ether") 

def deploy_lottery():
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
    return lottery


def main():
    deploy_lottery()