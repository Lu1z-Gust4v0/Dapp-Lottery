from brownie import Lottery
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import fund_with_link


def main():
    if len(Lottery) <= 0:
        deploy_lottery()
    # You need testnet link to run this function, go to https://faucets.chain.link/rinkeby to get some
    fund_with_link(Lottery[-1].address)