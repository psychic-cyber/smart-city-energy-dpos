const { ethers } = require('ethers');
const { provider, wallet, getToken, getMarketplace, getVoting } = require('../config/provider');

const listingStatusNames = ['Open', 'Purchased', 'Completed', 'Cancelled'];

async function getTokenContract() {
  return getToken();
}

async function getMarketplaceContract() {
  return getMarketplace();
}

async function getVotingContract() {
  return getVoting();
}

async function getTokenInfo() {
  const token = await getToken();
  const [name, symbol, decimals, totalSupply, owner] = await Promise.all([
    token.name(),
    token.symbol(),
    token.decimals(),
    token.totalSupply(),
    token.owner(),
  ]);

  return {
    address: ethers.getAddress(token.target || token.address),
    name,
    symbol,
    decimals: Number(decimals),
    totalSupply: totalSupply.toString(),
    owner: ethers.getAddress(owner),
  };
}

async function getTokenBalance(address) {
  const normalizedAddress = ethers.getAddress(address);
  const token = await getToken();
  const balance = await token.balanceOf(normalizedAddress);

  return {
    wallet: normalizedAddress,
    balance: balance.toString(),
  };
}

async function transferToken(to, amount) {
  const recipient = ethers.getAddress(to);
  if (!amount || amount.toString().trim().length === 0) {
    throw new Error('Amount is required');
  }

  const token = await getToken();
  const decimals = await token.decimals();
  const amountParsed = ethers.parseUnits(amount.toString(), Number(decimals));
  const tx = await token.transfer(recipient, amountParsed);
  const receipt = await tx.wait();

  return {
    transactionHash: receipt.transactionHash,
    blockNumber: receipt.blockNumber,
    gasUsed: receipt.gasUsed.toString(),
  };
}

async function getMarketplaceOrders() {
  const marketplace = await getMarketplace();
  const filter = marketplace.filters.EnergyListingCreated();
  const events = await marketplace.queryFilter(filter, 0, 'latest');
  const sortedEvents = events.sort((a, b) => Number(a.args.listingId) - Number(b.args.listingId));

  const orders = [];

  for (const event of sortedEvents) {
    const listingId = event.args.listingId;
    const listing = await marketplace.getListing(listingId);

    orders.push({
      id: listing.id.toString(),
      seller: ethers.getAddress(listing.seller),
      buyer: ethers.getAddress(listing.buyer),
      quantity: listing.quantity.toString(),
      pricePerUnit: listing.pricePerUnit.toString(),
      createdAt: listing.createdAt.toString(),
      status: listingStatusNames[Number(listing.status)] || listing.status.toString(),
    });
  }

  return orders;
}

async function createMarketplaceListing(seller, energyAmount, price) {
  const normalizedSeller = ethers.getAddress(seller);
  if (!energyAmount || Number(energyAmount) <= 0) {
    throw new Error('Energy amount must be greater than zero');
  }
  if (!price || Number(price) <= 0) {
    throw new Error('Price must be greater than zero');
  }

  const marketplace = await getMarketplace();
  const walletAddress = await wallet.getAddress();

  if (normalizedSeller.toLowerCase() !== walletAddress.toLowerCase()) {
    throw new Error('Seller must be the connected wallet');
  }

  const token = await getToken();
  const decimals = await token.decimals();
  const pricePerUnit = ethers.parseUnits(price.toString(), Number(decimals));

  const tx = await marketplace.createEnergyListing(ethers.toBigInt(energyAmount), pricePerUnit);
  const receipt = await tx.wait();

  return {
    transactionHash: receipt.transactionHash,
    blockNumber: receipt.blockNumber,
    gasUsed: receipt.gasUsed.toString(),
  };
}

async function buyMarketplaceListing(listingId, buyer) {
  const normalizedBuyer = ethers.getAddress(buyer);
  if (!listingId || Number(listingId) <= 0) {
    throw new Error('ListingId must be greater than zero');
  }

  const marketplace = await getMarketplace();
  const walletAddress = await wallet.getAddress();

  if (normalizedBuyer.toLowerCase() !== walletAddress.toLowerCase()) {
    throw new Error('Buyer must be the connected wallet');
  }

  const tx = await marketplace.buyEnergy(ethers.toBigInt(listingId));
  const receipt = await tx.wait();

  return {
    transactionHash: receipt.transactionHash,
    blockNumber: receipt.blockNumber,
    gasUsed: receipt.gasUsed.toString(),
  };
}

async function getValidators() {
  const voting = await getVoting();
  const totalValidators = await voting.delegateCount();
  const validatorCount = Number(totalValidators);
  const validators = [];

  for (let i = 1; i <= validatorCount; i += 1) {
    const delegate = await voting.getDelegate(i);
    const normalizedAccount = ethers.getAddress(delegate.account.toLowerCase());
    validators.push({
      id: delegate.id.toString(),
      account: normalizedAccount,
      name: delegate.name,
      votes: delegate.votes.toString(),
      registeredAt: delegate.registeredAt.toString(),
      active: delegate.active,
    });
  }

  return validators;
}

async function getDelegateByAddress(address) {
  if (!ethers.isAddress(address)) {
    throw new Error('Invalid address');
  }

  const voting = await getVoting();
  const totalValidators = await voting.delegateCount();
  const delegateCount = Number(totalValidators);

  const normalizedAddress = ethers.getAddress(address.toLowerCase());
  for (let i = 1; i <= delegateCount; i += 1) {
    const delegate = await voting.getDelegate(i);
    if (delegate.account.toLowerCase() === normalizedAddress.toLowerCase()) {
      return {
        id: delegate.id.toString(),
        account: ethers.getAddress(delegate.account.toLowerCase()),
        name: delegate.name,
        votes: delegate.votes.toString(),
        registeredAt: delegate.registeredAt.toString(),
        active: delegate.active,
      };
    }
  }

  throw new Error('Delegate not found');
}

async function voteForDelegate(delegateId) {
  if (!delegateId || Number(delegateId) <= 0) {
    throw new Error('Delegate id must be greater than zero');
  }

  const voting = await getVoting();
  const tx = await voting.voteDelegate(ethers.toBigInt(delegateId));
  const receipt = await tx.wait();

  return {
    transactionHash: receipt.transactionHash,
    blockNumber: receipt.blockNumber,
    gasUsed: receipt.gasUsed.toString(),
  };
}

async function healthCheck() {
  try {
    const network = await provider.getNetwork();
    const walletAddress = await wallet.getAddress();
    const token = getToken();
    const marketplace = getMarketplace();
    const voting = getVoting();

    return {
      success: true,
      network: network.name || `chainId:${network.chainId}`,
      wallet: ethers.getAddress(walletAddress),
      tokenAddress: ethers.getAddress(token.target || token.address),
      marketplaceAddress: ethers.getAddress(marketplace.target || marketplace.address),
      votingAddress: ethers.getAddress(voting.target || voting.address),
    };
  } catch (error) {
    return {
      success: false,
      network: null,
      wallet: null,
      tokenAddress: null,
      marketplaceAddress: null,
      votingAddress: null,
      error: error.message,
    };
  }
}

module.exports = {
  getToken: getTokenContract,
  getMarketplace: getMarketplaceContract,
  getVoting: getVotingContract,
  getTokenInfo,
  getTokenBalance,
  transferToken,
  getMarketplaceOrders,
  createMarketplaceListing,
  buyMarketplaceListing,
  getValidators,
  getDelegateByAddress,
  voteForDelegate,
  healthCheck,
};
