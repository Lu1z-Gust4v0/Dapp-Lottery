from brownie import network, exceptions
from brownie.network.state import Chain
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import (
    get_account, 
    fund_with_link,
    get_contract,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS
)
from web3 import Web3
import pytest 

DAY_IN_SECONDS = 86400
LUCK_NUMBER = 777


def test_get_entry_fee():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    lottery = deploy_lottery()
    # Act
    entry_fee = lottery.getEntryFee()
    expected_entry_fee = Web3.toWei(0.0125, "ether")
    # Assert
    assert entry_fee == expected_entry_fee


def test_can_enter_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    lottery = deploy_lottery()
    # Start lottery
    tx = lottery.startLottery({"from": account})
    tx.wait(1)
    entry_fee = lottery.getEntryFee()
    # Act
    tx = lottery.enterLottery(1, {"from": account, "value": entry_fee})
    tx.wait(1)
    # Assert
    entry_counter = lottery.entryCounter()
    lottery_state = lottery.lotteryState()
    participant = lottery.entryIdToParticipant(entry_counter - 1)
    participant_entries = lottery.participantEntries(account)
    balance = lottery.balance()

    assert entry_counter == 1
    assert participant_entries == 1
    assert lottery_state == 1
    assert participant == account
    assert balance == entry_fee


def test_can_buy_multiple_entries():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    lottery = deploy_lottery()
    lottery.startLottery({"from": account})
    entry_fee = lottery.getEntryFee()
    # Act  
    expected_entries = 5
    tx = lottery.enterLottery(
        expected_entries, {"from": account, "value": entry_fee * expected_entries}
    )
    tx.wait(1)
    # Assert
    assert lottery.lotteryState() == 1
    assert lottery.balance() == entry_fee * expected_entries
    assert lottery.participantEntries(account) == expected_entries
    for id in range(expected_entries):
        assert lottery.entryIdToParticipant(id) == account


def test_cannot_enter_unless_started():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    lottery = deploy_lottery()
    entry_fee = lottery.getEntryFee()
    # Act/Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enterLottery(1, {"from": account, "value": entry_fee})


def test_can_end_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    lottery = deploy_lottery()
    # fund with link
    fund_with_link(lottery.address)
    lottery.startLottery({"from": account})
    entry_fee = lottery.getEntryFee()
    enter_lottery_tx = lottery.enterLottery(1, {"from": account, "value": entry_fee})
    enter_lottery_tx.wait(1)
    # Act
    # time travel 
    chain = Chain()
    chain.sleep(DAY_IN_SECONDS)
    end_lottery_tx = lottery.endLottery({"from": account})
    end_lottery_tx.wait(1)
    lottery_state = lottery.lotteryState()
    # Assert 
    assert end_lottery_tx.events["RequestedRandomness"]["requestId"] is not None
    assert lottery_state == 2


def test_can_pick_winner_correctly():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    expected_winner = get_account(index=1)
    lottery = deploy_lottery()
    # fund with link
    fund_with_link(lottery.address)
    # Act
    entry_fee = lottery.getEntryFee()
    lottery.startLottery({"from": account})
    lottery.enterLottery(1, {"from": account, "value": entry_fee})
    lottery.enterLottery(1, {"from": expected_winner, "value": entry_fee})
    lottery.enterLottery(1, {"from": get_account(index=2), "value": entry_fee})
    entry_counter = lottery.entryCounter()
    # get balances 
    contract_initial_balance = lottery.balance()
    owner_initial_balance = account.balance()
    winner_initial_balance = expected_winner.balance()
    # time travel 
    chain = Chain()
    chain.sleep(DAY_IN_SECONDS)
    end_lottery_tx = lottery.endLottery({"from": account})
    request_id = end_lottery_tx.events["RequestedRandomness"]["requestId"]
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, (LUCK_NUMBER + 1), lottery.address
    )
    # Assert
    amount_to_winner = contract_initial_balance * 0.9
    amount_to_owner = contract_initial_balance * 0.1
    # current balances
    contract_current_balance = lottery.balance()
    owner_current_balance = account.balance()
    winner_current_balance = expected_winner.balance()
    
    assert expected_winner == lottery.latestWinner()
    assert contract_current_balance == 0
    assert winner_current_balance == winner_initial_balance + amount_to_winner
    assert owner_current_balance == owner_initial_balance + amount_to_owner


def test_cannot_end_until_deadline():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    lottery = deploy_lottery()
    # fund with link
    fund_with_link(lottery.address)
    lottery.startLottery({"from": account})
    # Act/Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.endLottery({"from": account})


def test_can_change_entry_fee():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    lottery = deploy_lottery()
    # Act
    new_fee = Web3.toWei(10, "ether")
    lottery.changeEntryFee(new_fee, {"from": account})
    # assert
    assert lottery.entryFee() == new_fee


def test_can_change_lottery_duration():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    lottery = deploy_lottery()
    # Act 
    # 1 hour in seconds 
    new_duration = 3600 
    lottery.changeDuration(new_duration, {"from": account})
    # Assert
    assert lottery.lotteryDuration() == new_duration