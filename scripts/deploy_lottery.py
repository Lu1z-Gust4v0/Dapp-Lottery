from brownie import Lottery, network, config
from scripts.helpful_scripts import get_account, get_contract

ENTRY_FEE = 50 # USD

def deploy_lottery():
    print(f"Deploying Lottery at {network.show_active()}...")
    account = get_account()
    lottery_contract = Lottery.deploy(
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
    return lottery_contract


def main():
    deploy_lottery()