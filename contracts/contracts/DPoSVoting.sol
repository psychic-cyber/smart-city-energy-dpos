/**
 * SPDX-License-Identifier: MIT
 */
pragma solidity 0.8.28;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";

/**
 * @title DPoSVoting
 * @dev Delegate registration and voting contract for DPoS elections.
 */
contract DPoSVoting is Ownable, Pausable {
    struct Delegate {
        uint256 id;
        address account;
        string name;
        uint256 votes;
        uint256 registeredAt;
        bool active;
    }

    error DelegateAlreadyRegistered(address delegateAddress);
    error InvalidName();
    error DelegateNotFound(uint256 delegateId);
    error AlreadyVoted(address voter);
    error NoDelegatesRegistered();
    error AlreadyPaused();
    error AlreadyUnpaused();

    mapping(uint256 => Delegate) private delegates;
    mapping(address => bool) public isDelegate;
    mapping(address => bool) public hasVoted;
    uint256 public delegateCount;

    event DelegateRegistered(uint256 indexed delegateId, address indexed delegateAddress, string name, uint256 timestamp);
    event DelegateVoted(uint256 indexed delegateId, address indexed voter, uint256 timestamp);
    event ElectionPaused(uint256 timestamp);
    event ElectionResumed(uint256 timestamp);

    modifier delegateExists(uint256 delegateId) {
        if (delegateId == 0 || delegateId > delegateCount || !delegates[delegateId].active) {
            revert DelegateNotFound(delegateId);
        }
        _;
    }

    constructor() Ownable(msg.sender) {}

    /**
     * @notice Register the caller as a delegate.
     * @param name The display name for the delegate.
     * @return delegateId The assigned delegate identifier.
     */
    function registerDelegate(string calldata name) external whenNotPaused returns (uint256 delegateId) {
        if (bytes(name).length == 0) revert InvalidName();
        if (isDelegate[msg.sender]) revert DelegateAlreadyRegistered(msg.sender);

        delegateId = ++delegateCount;
        delegates[delegateId] = Delegate({
            id: delegateId,
            account: msg.sender,
            name: name,
            votes: 0,
            registeredAt: block.timestamp,
            active: true
        });

        isDelegate[msg.sender] = true;
        emit DelegateRegistered(delegateId, msg.sender, name, block.timestamp);
    }

    /**
     * @notice Cast a vote for a registered delegate.
     * @param delegateId The delegate identifier.
     */
    function voteDelegate(uint256 delegateId) external whenNotPaused delegateExists(delegateId) {
        if (hasVoted[msg.sender]) revert AlreadyVoted(msg.sender);

        hasVoted[msg.sender] = true;
        delegates[delegateId].votes += 1;
        emit DelegateVoted(delegateId, msg.sender, block.timestamp);
    }

    /**
     * @notice Return the current election winner.
     * @return winnerId The winning delegate identifier.
     * @return winnerAddress The winning delegate address.
     * @return winnerName The winning delegate name.
     * @return winnerVotes The total votes for the winner.
     */
    function electionWinner()
        external
        view
        returns (
            uint256 winnerId,
            address winnerAddress,
            string memory winnerName,
            uint256 winnerVotes
        )
    {
        if (delegateCount == 0) revert NoDelegatesRegistered();

        uint256 highestVotes;
        for (uint256 i = 1; i <= delegateCount; ++i) {
            if (!delegates[i].active) {
                continue;
            }
            if (delegates[i].votes > highestVotes) {
                highestVotes = delegates[i].votes;
                winnerId = delegates[i].id;
                winnerAddress = delegates[i].account;
                winnerName = delegates[i].name;
                winnerVotes = delegates[i].votes;
            }
        }
    }

    /**
     * @notice Return the vote count for a delegate.
     * @param delegateId The delegate identifier.
     * @return votes The number of votes received.
     */
    function voteCount(uint256 delegateId) external view delegateExists(delegateId) returns (uint256 votes) {
        votes = delegates[delegateId].votes;
    }

    /**
     * @notice Retrieve delegate details.
     * @param delegateId The delegate identifier.
     */
    function getDelegate(uint256 delegateId)
        external
        view
        delegateExists(delegateId)
        returns (
            uint256 id,
            address account,
            string memory name,
            uint256 votes,
            uint256 registeredAt,
            bool active
        )
    {
        Delegate storage delegate = delegates[delegateId];
        return (delegate.id, delegate.account, delegate.name, delegate.votes, delegate.registeredAt, delegate.active);
    }

    /**
     * @notice Pause the voting contract.
     */
    function pauseElection() external onlyOwner {
        _pause();
        emit ElectionPaused(block.timestamp);
    }

    /**
     * @notice Resume the voting contract.
     */
    function resumeElection() external onlyOwner {
        _unpause();
        emit ElectionResumed(block.timestamp);
    }
}
