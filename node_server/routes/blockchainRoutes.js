const express = require("express");
const router = express.Router();
const blockchainController = require("../controllers/blockchainController");

router.get("/health", blockchainController.health);

router.post("/users/initialize", blockchainController.initialize);

router.get("/token/info", blockchainController.tokenInfo);
router.get("/token/balance/:address", blockchainController.tokenBalance);
router.post("/token/transfer", blockchainController.tokenTransfer);

router.get("/marketplace/orders", blockchainController.marketplaceOrders);
router.post("/marketplace/sell", blockchainController.marketplaceSell);
router.post("/marketplace/buy", blockchainController.marketplaceBuy);

router.get("/voting/validators", blockchainController.votingValidators);
router.get(
  "/voting/delegates/:address",
  blockchainController.votingDelegateInfo,
);
router.post("/voting/vote", blockchainController.votingVote);

module.exports = router;
