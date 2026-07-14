const blockchainService = require("../services/blockchainService");

async function health(req, res) {
  try {
    const result = await blockchainService.healthCheck();
    return res.status(result.success ? 200 : 500).json(result);
  } catch (error) {
    return res.status(500).json({
      success: false,
      message: "Health check failed",
      error: error.message,
    });
  }
}

async function tokenInfo(req, res) {
  try {
    const data = await blockchainService.getTokenInfo();
    return res
      .status(200)
      .json({ success: true, message: "Token info retrieved", data });
  } catch (error) {
    return res.status(500).json({
      success: false,
      message: "Unable to retrieve token info",
      error: error.message,
    });
  }
}

async function tokenBalance(req, res) {
  try {
    const { address } = req.params;
    const data = await blockchainService.getTokenBalance(address);
    return res
      .status(200)
      .json({ success: true, message: "Token balance retrieved", data });
  } catch (error) {
    return res.status(400).json({
      success: false,
      message: "Unable to retrieve token balance",
      error: error.message,
    });
  }
}

async function tokenTransfer(req, res) {
  try {
    const { fromUsername, to, amount } = req.body;
    const data = await blockchainService.transferToken(
      fromUsername,
      to,
      amount,
    );
    return res
      .status(200)
      .json({ success: true, message: "Token transfer submitted", data });
  } catch (error) {
    return res.status(400).json({
      success: false,
      message: "Unable to transfer tokens",
      error: error.message,
    });
  }
}

async function marketplaceOrders(req, res) {
  try {
    const data = await blockchainService.getMarketplaceOrders();
    return res
      .status(200)
      .json({ success: true, message: "Marketplace orders retrieved", data });
  } catch (error) {
    return res.status(500).json({
      success: false,
      message: "Unable to retrieve marketplace orders",
      error: error.message,
    });
  }
}

async function marketplaceSell(req, res) {
  try {
    const { seller, energyAmount, price } = req.body;
    const data = await blockchainService.createMarketplaceListing(
      seller,
      energyAmount,
      price,
    );
    return res
      .status(200)
      .json({ success: true, message: "Marketplace listing created", data });
  } catch (error) {
    console.log("========== MARKETPLACE SELL ERROR ==========");
    console.error(error);
    console.error(error.reason);
    console.error(error.shortMessage);
    console.error(error.info);
    console.error(error.stack);
    console.log("============================================");

    return res.status(400).json({
      success: false,
      message: "Unable to create marketplace listing",
      error: error.shortMessage || error.reason || error.message,
    });
  }
}

async function marketplaceBuy(req, res) {
  try {
    const { listingId, buyer } = req.body;

    const data = await blockchainService.buyMarketplaceListing(
      listingId,
      buyer,
    );

    return res.status(200).json({
      success: true,
      message: "Marketplace purchase submitted",
      data,
    });
  } catch (error) {
    console.log("========== MARKETPLACE BUY ERROR ==========");
    console.error(error);
    console.error("reason:", error.reason);
    console.error("short:", error.shortMessage);
    console.error("info:", error.info);
    console.error(error.stack);
    console.log("===========================================");

    return res.status(400).json({
      success: false,
      message: "Unable to purchase marketplace listing",
      error: error.shortMessage || error.reason || error.message,
    });
  }
}

// async function votingValidators(req, res) {
//   try {
//     const data = await blockchainService.getValidators();
//     return res.status(200).json({ success: true, message: 'Validators retrieved', data });
//   } catch (error) {
//     return res.status(500).json({ success: false, message: 'Unable to retrieve validators', error: error.message });
//   }
// }

async function votingValidators(req, res) {
  try {
    const data = await blockchainService.getValidators();
    return res.status(200).json({
      success: true,
      message: "Validators retrieved",
      data,
    });
  } catch (error) {
    console.error("========== VALIDATOR ERROR ==========");
    console.error(error);
    console.error(error.stack);
    console.error("====================================");

    return res.status(500).json({
      success: false,
      message: "Unable to retrieve validators",
      error: error.message,
    });
  }
}

async function votingDelegateInfo(req, res) {
  try {
    const { address } = req.params;
    const data = await blockchainService.getDelegateByAddress(address);
    return res
      .status(200)
      .json({ success: true, message: "Delegate info retrieved", data });
  } catch (error) {
    return res.status(400).json({
      success: false,
      message: "Unable to retrieve delegate info",
      error: error.message,
    });
  }
}

async function votingVote(req, res) {
  try {
    const { voter, delegate } = req.body;
    const data = await blockchainService.voteForDelegate(voter, delegate);
    return res
      .status(200)
      .json({ success: true, message: "Vote submitted", data });
  } catch (error) {
    return res.status(400).json({
      success: false,
      message: "Unable to submit vote",
      error: error.message,
    });
  }
}

module.exports = {
  health,
  tokenInfo,
  tokenBalance,
  tokenTransfer,
  marketplaceOrders,
  marketplaceSell,
  marketplaceBuy,
  votingValidators,
  votingDelegateInfo,
  votingVote,
};
