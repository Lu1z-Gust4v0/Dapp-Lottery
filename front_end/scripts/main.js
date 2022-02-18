import { getContract, convertState, sliceLongValue } from "./helper_functions.js"

const web3 = new Web3(ethereum)
const chainId = "4" // rinkeby 
let userAccount
let entryFee
let contract 

// Accessing elements throught DOM
const prizePoolSpan = document.querySelector(".prize-pool span")
const countdownSpan = document.querySelector(".countdown span")
const lotteryStateSpan = document.querySelector(".state span")
const totalEntriesSpan = document.querySelector(".entry-counter span")
const userEntriesSpan = document.querySelector(".user-entry-counter span")
const userBalanceSpan = document.querySelector(".user-balance span")
const latestWinnerSpan = document.querySelector(".latest-winner span")
const randomNumberSpan = document.querySelector(".random-number span")
const entryFeeSpan = document.querySelector(".entry-price")

const connectBtn = document.querySelector(".connect-button")
const startBtn = document.querySelector(".start-lottery")
const entriesInput = document.querySelector("input#number-of-entries")
const enterBtn = document.querySelector(".enter-lottery")
const showBtn = document.querySelector(".show-results")

connectBtn.addEventListener("click", connectMetamask);
startBtn.addEventListener("click", startLottery)
entriesInput.addEventListener("input", updatePrice)
showBtn.addEventListener("click", endLottery)
enterBtn.addEventListener("click", (e) => {
    e.preventDefault()
    enterLottery(parseInt(entriesInput.value))     
})

async function main() {
    if (typeof ethereum == "undefined") {
        throw new Error("You don't have the metamask extension installed")
    }

    if (web3.currentProvider.chainId !== "0x4") {
        try {
            await ethereum.request({
                method: "wallet_switchEthereumChain",
                params: [{ chainId: "0x4"}]
            })
        } catch (error) {
            alert(error.message)
        }
    }
    contract = await getContract("Lottery", chainId)
    loadDappData()
}
main()
.catch(error => {
    alert(error.message)
})

// metamask event
ethereum.on("chainChanged", () => {
    window.location.reload()
})

async function connectMetamask() {
    try {
        const accounts = await ethereum.request({ method: "eth_requestAccounts" })
        userAccount = accounts[0]
        loadUserData()
        // change button styles
        connectBtn.classList.add("connected")
        connectBtn.textContent = sliceLongValue(userAccount)
    } catch (error) {
        if (err.code === 4001) {
            // EIP-1193 userRejectedRequest error
            // If this happens, the user rejected the connection request.
            console.log("Please connect to MetaMask.")
        } else {
            console.error(err)
        }
    }
}

function startLottery() {
    contract.methods.startLottery().send({
        from: userAccount
    }).on("transactionHash", (hash) => {
        console.log(hash)
    }).on("receipt", () => {
        loadDappData()
    }).on("error", (error) => {
        console.log(error)
    })
}

function enterLottery(entryNumber) {
    // the parameter of toWei should be a string or a big number to avoid imprecisions
    let cost = (entryNumber * entryFee).toString()
    contract.methods.enterLottery(entryNumber).send({
        from: userAccount,
        value: web3.utils.toWei(cost, "ether")
    }).on("transactionHash", (hash) => {
        console.log(hash)
    }).on("receipt", () => {
        resetDapp()
    }).on("error", (error) => {
        console.log(error)
    })
}

function endLottery() {
    contract.methods.endLottery().send({
        from: userAccount
    }).on("transactionHash", (hash) => {
        console.log(hash)
    }).on("receipt", () => {
        resetDapp()
    }).on("error", (error) => {
        console.log(error)
    })
    // Listen for the end of the lottery
    contract.events.LotteryFinished()
    .on("data", ()=>{
        resetDapp()
    })
}

async function loadUserData() {
    userEntriesSpan.textContent = await contract.methods.participantEntries(userAccount).call()
    userBalanceSpan.textContent = parseFloat(
        web3.utils.fromWei(
            await web3.eth.getBalance(userAccount),
            "ether"
        )
    ).toFixed(4)
}

function updatePrice(e) {
    let result = parseFloat(e.target.value * entryFee).toFixed(4)
    entryFeeSpan.textContent = `Price ${result}`
}

async function updateState() {
    let state = convertState(await contract.methods.lotteryState().call())
    let deadline = await contract.methods.lotteryDeadlineTimestamp().call()
    // convert miliseconds to seconds
    let timeStamp = Date.now() / 1000
    lotteryStateSpan.classList = state.toLowerCase()
    lotteryStateSpan.textContent = state
    if (state === "Closed") {
        startBtn.disabled = false
        showBtn.disabled = true
    } else if (state === "Opened" && timeStamp >= deadline) {
        startBtn.disabled = true
        showBtn.disabled = false
    } else {
        startBtn.disabled = true
        showBtn.disabled = true
    }
}

// Populates spans with data retrieved from the smart contract
async function loadDappData() {
    updateState()
    prizePoolSpan.textContent = parseFloat(
        web3.utils.fromWei(await web3.eth.getBalance(contract.options.address),"ether")
    ).toFixed(4)
    entryFee = parseFloat(
        web3.utils.fromWei(await contract.methods.getEntryFee().call(), "ether")
    ).toFixed(4)
    entryFeeSpan.textContent = `Price: ${entryFee}`
    totalEntriesSpan.textContent = await contract.methods.entryCounter().call()
    randomNumberSpan.textContent = sliceLongValue(
        await contract.methods.randomness().call()
    )
    latestWinnerSpan.textContent = sliceLongValue(
        await contract.methods.latestWinner().call()
    )
    startCountdown()
}

async function startCountdown() {
    let deadline = await contract.methods.lotteryDeadlineTimestamp().call()
    setInterval(updateCountdown, 100, deadline)
}

function updateCountdown(deadline) {
    let timestamp = deadline - (Date.now() / 1000) 
    if (timestamp <= 0) {
        countdownSpan.textContent = "00:00:00"
        return
    }
    let hours = Math.floor(timestamp / 3600) 
    let minutes = Math.floor((timestamp % 3600) / 60)
    let seconds = Math.floor(timestamp % 60)
    
    let tmp = [hours, minutes, seconds]
    tmp.forEach((item, index) => {
        tmp[index] = item.toLocaleString("en-US", {
            minimumIntegerDigits: 2,
            useGrouping: false  
        })  
    })
    countdownSpan.textContent = `${tmp[0]}:${tmp[1]}:${tmp[2]}`
}

function resetDapp() {
    loadDappData()
    loadUserData()
}