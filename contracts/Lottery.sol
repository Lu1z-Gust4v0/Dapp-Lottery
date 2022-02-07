// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Lottery is VRFConsumerBase, Ownable {
    // Lottery states
    enum LOTTERY_STATE {
        CLOSED,
        OPENED,
        PROCESSING_WINNER
    }
    LOTTERY_STATE lotteryState;
    uint256 public entryFee;
    uint256 public fee; // in USD
    uint256 public lotteryDuration;
    uint256 public lotteryDeadlineTimestamp;
    bytes32 public keyhash;
    address payable[] public participants;
    address payable public lastestWinner;
    mapping(address => uint256) public participantEntries;
    AggregatorV3Interface public priceFeed;

    // events
    event LotteryStarted(uint256 timeStamp);
    event LotteryFinished(address winner, uint256 timeStamp);
    event NewEntry(address participant, uint256 entryCouter);
    event UserPaid(address user, uint256 amount);
    event RequestedRandomness(bytes32 requestId);

    constructor(
        address _priceFeedAddress,
        address _vrfCoordinator,
        address _linkTokenAddress,
        uint256 _entryFee,
        uint256 _fee,
        bytes32 _keyhash
    ) VRFConsumerBase(_vrfCoordinator, _linkTokenAddress) {
        priceFeed = AggregatorV3Interface(_priceFeedAddress);
        // amount players must pay in order to enter the lottery
        entryFee = _entryFee;
        fee = _fee;
        keyhash = _keyhash;
        lotteryState = LOTTERY_STATE.CLOSED;
        // 24 hours
        lotteryDuration = 60 * 60 * 24;
    }

    function getEntryFee() public view returns (uint256) {
        (, int256 price, , , ) = priceFeed.latestRoundData();
        uint256 ethPrice = uint256(price) * 10**10;
        uint256 precision = 10**18;
        return (entryFee * precision) / ethPrice;
    }

    function enterLottery() public payable {
        uint256 _fee = getEntryFee();
        require(_fee > 0, "Fee cannot be 0");
        require(msg.sender != address(0), "invalid user address");
        require(msg.value >= _fee, "You need to spend more ETH!");
        // In case of the user send an amount greater than the necessary, refund the user
        uint256 amountToBeRefund = msg.value - _fee;
        if (amountToBeRefund > 0) {
            payUser(msg.sender, amountToBeRefund);
        }
        // If the lottery is closed, start it
        if (participants.length == 0) {
            startLottery();
        }
        participants.push(payable(msg.sender));
        participantEntries[msg.sender]++;
        emit NewEntry(msg.sender, participantEntries[msg.sender]);
    }

    function payUser(address _user, uint256 _amount) internal {
        require(_user != address(0), "invalid user address");
        require(_amount > 0, "You have nothing to recieve");
        payable(_user).transfer(_amount);
        emit UserPaid(_user, _amount);
    }

    function startLottery() internal {
        require(lotteryState == LOTTERY_STATE.CLOSED, "Lottery must be closed");
        lotteryState = LOTTERY_STATE.OPENED;
        lotteryDeadlineTimestamp = block.timestamp + lotteryDuration;
        emit LotteryStarted(block.timestamp);
    }

    function endLottery() public onlyOwner {
        require(lotteryState == LOTTERY_STATE.OPENED, "The lottery is not open");
        require(block.timestamp >= lotteryDeadlineTimestamp, "The lottery is not finished yet");
        lotteryState = LOTTERY_STATE.PROCESSING_WINNER;
        bytes32 requestId = requestRandomness(keyhash, fee);
        emit RequestedRandomness(requestId);
    }

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness) internal override {
        require(
            lotteryState == LOTTERY_STATE.PROCESSING_WINNER, 
            "The contract is not processing the winner yet"
        );
        require(_randomness != 0, "Random not found");
        uint256 indexOfWinner = _randomness % participants.length;
        lastestWinner = participants[indexOfWinner]; 
        // The winner recieves 90% of the contract balance
        // The other 10% goes to the owner
        uint256 contractBalance = address(this).balance;
        uint256 amountToPayWinner = (contractBalance * 90) / 100;
        uint256 amountToPayOwner = (contractBalance * 10) / 100;
        payUser(lastestWinner, amountToPayWinner);
        payUser(owner(), amountToPayOwner);
        emit LotteryFinished(lastestWinner, block.timestamp);
    }

    function changeEntryFee(uint256 _newEntryFee) public onlyOwner {
        require(_newEntryFee > 0, "Entry fee cannot be 0");
        require(
            lotteryState == LOTTERY_STATE.CLOSED, 
            "Lottery must be closed to change entry fee"
        );
        entryFee = _newEntryFee;
    }
}   
