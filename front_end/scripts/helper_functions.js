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

function sliceLongValue(value) {
    // covert the value to string so that we can split it
    let str = value.toString()
    let strLen = str.length
    // return "0x000..0000"
    return str.slice(0, 5) + "..." + str.slice(strLen - 4, strLen)
}

export {
    getContractArtifact, 
    getContractAddress, 
    getContract, 
    convertState, 
    sliceLongValue
}