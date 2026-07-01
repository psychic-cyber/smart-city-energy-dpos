/**
 * SPDX-License-Identifier: MIT
 */
pragma solidity 0.8.28;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";

/**
 * @title SmartEnergyToken
 * @dev ERC20 token for energy credits, mintable and burnable by the owner.
 *      A marketplace contract can be registered to execute token transfers during purchases.
 */
contract SmartEnergyToken is ERC20, Ownable, Pausable {
    error InvalidMarketplaceAddress(address marketplace);
    error InvalidAmount(uint256 amount);
    error MarketplaceNotSet();
    error NotMarketplace(address caller);
    error InsufficientAllowance(address owner, address spender, uint256 amount);

    address public marketplace;

    event MarketplaceUpdated(address indexed previousMarketplace, address indexed newMarketplace);

    constructor(string memory name_, string memory symbol_) ERC20(name_, symbol_) Ownable(msg.sender) {}

    /**
     * @notice Set the marketplace contract that is allowed to perform marketplace transfers.
     * @param marketplace_ The marketplace contract address.
     */
    function setMarketplace(address marketplace_) external onlyOwner {
        if (marketplace_ == address(0)) revert InvalidMarketplaceAddress(marketplace_);
        emit MarketplaceUpdated(marketplace, marketplace_);
        marketplace = marketplace_;
    }

    /**
     * @notice Mint energy credits to an account.
     * @param account The recipient address.
     * @param amount The amount to mint.
     */
    function mint(address account, uint256 amount) external onlyOwner whenNotPaused {
        if (amount == 0) revert InvalidAmount(amount);
        _mint(account, amount);
    }

    /**
     * @notice Burn energy credits from an account.
     * @param account The account whose tokens will be burned.
     * @param amount The amount to burn.
     */
    function burn(address account, uint256 amount) external onlyOwner whenNotPaused {
        if (amount == 0) revert InvalidAmount(amount);
        _burn(account, amount);
    }

    /**
     * @notice Marketplace-only transfer helper for purchases.
     * @param from The source address.
     * @param to The destination address.
     * @param amount The token amount.
     * @return True if the transfer succeeds.
     */
    function marketplaceTransferFrom(address from, address to, uint256 amount) external returns (bool) {
        if (marketplace == address(0)) revert MarketplaceNotSet();
        if (msg.sender != marketplace) revert NotMarketplace(msg.sender);
        if (amount == 0) revert InvalidAmount(amount);

        uint256 currentAllowance = allowance(from, msg.sender);
        if (currentAllowance < amount) {
            revert InsufficientAllowance(from, msg.sender, amount);
        }

        _spendAllowance(from, msg.sender, amount);
        _transfer(from, to, amount);
        return true;
    }

    /**
     * @notice Pause token minting, burning, and transfers.
     */
    function pause() external onlyOwner {
        _pause();
    }

    /**
     * @notice Unpause token minting, burning, and transfers.
     */
    function unpause() external onlyOwner {
        _unpause();
    }

    /**
     * @notice Transfer tokens when the contract is not paused.
     */
    function transfer(address to, uint256 amount) public virtual override whenNotPaused returns (bool) {
        return super.transfer(to, amount);
    }

    /**
     * @notice Transfer tokens from an approved account when the contract is not paused.
     */
    function transferFrom(address from, address to, uint256 amount) public virtual override whenNotPaused returns (bool) {
        return super.transferFrom(from, to, amount);
    }

    /**
     * @notice Approve tokens when the contract is not paused.
     */
    function approve(address spender, uint256 amount) public virtual override whenNotPaused returns (bool) {
        return super.approve(spender, amount);
    }
}
