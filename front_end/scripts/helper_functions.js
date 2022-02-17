const web3 = new Web3(ethereum)

async function getContractArtifact(contractName) {
    try {
        let response = await fetch(`./chain-info/contracts/${contractName}.json`)
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }
        let artifact = await response.json()
        return artifact

    } catch (error) {
        console.error(error)
    }    
}

async function getContractAddress(contractName, chainId) {
    try {
        let response = await fetch("./chain-info/deployments/map.json")

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }

        let map = await response.json()
        let address = map[chainId][contractName][0]
        return address

    } catch (error) {
        console.error(error)
    }    
}

async function getContract(contractName, chainId) {
    let artifact = await getContractArtifact(contractName)
    let address = await getContractAddress(contractName, chainId)
    let contract = new web3.eth.Contract(artifact.abi, address)
    return contract
}

function convertState(state) {
    let stateMapping = ["Closed", "Opened", "Processing"]
    return stateMapping[state]
}

function sliceAddress(address) {
    return address.slice(0, 5) + "..." + address.slice(38, 42)
}

export {getContractArtifact, getContractAddress, getContract, convertState, sliceAddress}