/**
 * SPDX-License-Identifier: MIT
 */
pragma solidity 0.8.28;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "./SmartEnergyToken.sol";

/**
 * @title EnergyMarketplace
 * @dev Marketplace for energy listings that accepts SmartEnergyToken payments.
 */
contract EnergyMarketplace is Ownable, Pausable, ReentrancyGuard {
    enum ListingStatus {
        Open,
        Purchased,
        Completed,
        Cancelled
    }

    struct Listing {
        uint256 id;
        address seller;
        address buyer;
        uint256 quantity;
        uint256 pricePerUnit;
        uint256 createdAt;
        ListingStatus status;
    }

    error InvalidAddress(address account);
    error AlreadyRegisteredProducer(address producer);
    error AlreadyRegisteredConsumer(address consumer);
    error UnauthorizedProducer(address caller);
    error UnauthorizedConsumer(address caller);
    error InvalidQuantity(uint256 quantity);
    error InvalidPrice(uint256 pricePerUnit);
    error ListingNotFound(uint256 listingId);
    error ListingInactive(uint256 listingId, ListingStatus currentStatus);
    error CannotBuyOwnListing(address seller);
    error TransferFailed(uint256 listingId, address buyer, address seller);
    error NotListingSeller(address caller, uint256 listingId);
    error AlreadyPurchased(uint256 listingId);
    error AlreadyCompleted(uint256 listingId);

    SmartEnergyToken public immutable token;
    uint256 private nextListingId;

    mapping(address => bool) public producers;
    mapping(address => bool) public consumers;
    mapping(uint256 => Listing) private listings;

    event EnergyProducerRegistered(address indexed producer);
    event EnergyConsumerRegistered(address indexed consumer);
    event EnergyListingCreated(uint256 indexed listingId, address indexed seller, uint256 quantity, uint256 pricePerUnit, uint256 timestamp);
    event EnergyListingPurchased(uint256 indexed listingId, address indexed buyer, uint256 totalPrice, uint256 timestamp);
    event EnergyListingCancelled(uint256 indexed listingId, uint256 timestamp);
    event EnergyListingCompleted(uint256 indexed listingId, uint256 timestamp);

    modifier onlyProducer() {
        if (!producers[msg.sender]) revert UnauthorizedProducer(msg.sender);
        _;
    }

    modifier onlyConsumer() {
        if (!consumers[msg.sender]) revert UnauthorizedConsumer(msg.sender);
        _;
    }

    modifier listingExists(uint256 listingId) {
        if (listings[listingId].seller == address(0)) revert ListingNotFound(listingId);
        _;
    }

    modifier onlySeller(uint256 listingId) {
        if (msg.sender != listings[listingId].seller) revert NotListingSeller(msg.sender, listingId);
        _;
    }

    modifier onlyOpenListing(uint256 listingId) {
        if (listings[listingId].status != ListingStatus.Open) revert ListingInactive(listingId, listings[listingId].status);
        _;
    }

    constructor(SmartEnergyToken tokenAddress) Ownable(msg.sender) {
        if (address(tokenAddress) == address(0)) revert InvalidAddress(address(tokenAddress));
        token = tokenAddress;
        nextListingId = 1;
    }

    /**
     * @notice Register the caller as an energy producer.
     */
    function registerEnergyProducer() external whenNotPaused {
        if (msg.sender == address(0)) revert InvalidAddress(msg.sender);
        if (producers[msg.sender]) revert AlreadyRegisteredProducer(msg.sender);

        producers[msg.sender] = true;
        emit EnergyProducerRegistered(msg.sender);
    }

    /**
     * @notice Register the caller as an energy consumer.
     */
    function registerEnergyConsumer() external whenNotPaused {
        if (msg.sender == address(0)) revert InvalidAddress(msg.sender);
        if (consumers[msg.sender]) revert AlreadyRegisteredConsumer(msg.sender);

        consumers[msg.sender] = true;
        emit EnergyConsumerRegistered(msg.sender);
    }

    /**
     * @notice Create a new energy listing.
     * @param quantity Amount of energy units available.
     * @param pricePerUnit Token price per energy unit.
     */
    function createEnergyListing(uint256 quantity, uint256 pricePerUnit) external onlyProducer whenNotPaused returns (uint256) {
        if (quantity == 0) revert InvalidQuantity(quantity);
        if (pricePerUnit == 0) revert InvalidPrice(pricePerUnit);

        uint256 listingId = nextListingId++;
        listings[listingId] = Listing({
            id: listingId,
            seller: msg.sender,
            buyer: address(0),
            quantity: quantity,
            pricePerUnit: pricePerUnit,
            createdAt: block.timestamp,
            status: ListingStatus.Open
        });

        emit EnergyListingCreated(listingId, msg.sender, quantity, pricePerUnit, block.timestamp);
        return listingId;
    }

    /**
     * @notice Buy an active energy listing with the caller's approved tokens.
     * @param listingId The listing to purchase.
     */
    function buyEnergy(uint256 listingId) external onlyConsumer whenNotPaused nonReentrant listingExists(listingId) onlyOpenListing(listingId) {
        Listing storage listing = listings[listingId];
        if (listing.seller == msg.sender) revert CannotBuyOwnListing(listing.seller);

        uint256 totalPrice = listing.quantity * listing.pricePerUnit;
        bool success = token.marketplaceTransferFrom(msg.sender, listing.seller, totalPrice);
        if (!success) revert TransferFailed(listingId, msg.sender, listing.seller);

        listing.buyer = msg.sender;
        listing.status = ListingStatus.Purchased;
        emit EnergyListingPurchased(listingId, msg.sender, totalPrice, block.timestamp);
    }

    /**
     * @notice Cancel an open energy listing.
     * @param listingId The listing to cancel.
     */
    function cancelListing(uint256 listingId) external whenNotPaused listingExists(listingId) onlySeller(listingId) onlyOpenListing(listingId) {
        Listing storage listing = listings[listingId];
        listing.status = ListingStatus.Cancelled;
        emit EnergyListingCancelled(listingId, block.timestamp);
    }

    /**
     * @notice Complete a purchased energy listing.
     * @param listingId The listing to complete.
     */
    function completeListing(uint256 listingId) external whenNotPaused listingExists(listingId) onlySeller(listingId) {
        Listing storage listing = listings[listingId];
        if (listing.status == ListingStatus.Cancelled) revert ListingInactive(listingId, listing.status);
        if (listing.status == ListingStatus.Completed) revert AlreadyCompleted(listingId);
        if (listing.status != ListingStatus.Purchased) revert ListingInactive(listingId, listing.status);

        listing.status = ListingStatus.Completed;
        emit EnergyListingCompleted(listingId, block.timestamp);
    }

    /**
     * @notice Pause marketplace activity.
     */
    function pauseMarketplace() external onlyOwner {
        _pause();
    }

    /**
     * @notice Resume marketplace activity.
     */
    function resumeMarketplace() external onlyOwner {
        _unpause();
    }

    /**
     * @notice Retrieve listing data.
     * @param listingId The listing identifier.
     */
    function getListing(uint256 listingId) external view listingExists(listingId) returns (Listing memory) {
        return listings[listingId];
    }
}
