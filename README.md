# Dapp Lottery
Welcome to my first web3 project, this is a decentralized application (DAPP) that takes 
advantage of the use of smart contracts and VRFCoordinator to provide the user 
a trustless lottery experience.
## Languages + tools
- Javascript
- Python
- Solidity (Smart contracts programming language)
- Metamask (Wallet browser extension)
- Web3.js (Javascript library for interecting with ethereum nodes)
- Brownie (development and testing framework for smart contracts)

## Access the Dapp
* [Dapp Lottery](https://lu1z-gust4v0.github.io/Dapp-Lottery/front_end/index.html)
## Getting started
### Create a .env file following .env.example
```
export PRIVATE_KEY=$YOUR_PRIVATE_KEY
export WEB3_INFURA_PROJECT_ID=$YOUR_INFURA_ID
export ETHERSCAN_TOKEN=$YOUR_ETHEREUM_API_KEY 
```
### Install Brownie 
```
pip install eth-brownie
```
### Clone repository 
```
git clone https://github.com/Lu1z-Gust4v0/Dapp-Lottery.git
cd Dapp-Lottery
```
### Run tests
```
brownie test
```
### Compile the contract and create chain-info
```
brownie compile
brownie run scripts/update_front_end.py
```
### Fund the contract with testnet link
* [ETH + LINK faucet](https://faucets.chain.link/rinkeby)
```
brownie run scripts/fund_contract.py
```
## License MIT