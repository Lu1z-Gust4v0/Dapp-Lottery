from brownie import (
    accounts, 
    config, 
    network, 
    MockV3Aggregator, 
    LinkToken, 
    VRFCoordinatorMock,
    Contract
)
from web3 import Web3

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
LINK_TO_FUND = Web3.toWei(1, "ether")
INITIAL_PRICE = 400000000000
DECIMALS = 8


def get_account(index=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else: 
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


def fund_with_link(contract_address, account=None, link_token=None, amount=LINK_TO_FUND):
    print(f"Funding {contract_address} with link...")
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    recipient = contract_address
    tx = link_token.transfer(recipient, amount, {"from": account})
    tx.wait(1)
    converted_amount = Web3.fromWei(amount, "ether")
    print(f"Contract funded with {converted_amount} LINK")
    return tx


def deploy_mocks():
    print(f"Your current network is {network.show_active()}")
    account = get_account()
    print("Deploying mocks...")
    print("Deploying MockV3Aggregator...")
    MockV3Aggregator.deploy(DECIMALS, INITIAL_PRICE, {"from": account})
    print("Deploying Link token...")
    link_token = LinkToken.deploy({"from": account})
    print("Deploying VRFCoordinatorMock...")
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Mocks deployed")
