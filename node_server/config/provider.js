const path = require("path");
const fs = require("fs");
const { ethers } = require("ethers");

require("dotenv").config({ path: path.resolve(__dirname, "../.env") });

const {
  RPC_URL,
  PRIVATE_KEY,
  TOKEN_ADDRESS,
  MARKETPLACE_ADDRESS,
  DPOS_ADDRESS,
} = process.env;

function loadAbi(contractName) {
  const artifactPath = path.resolve(
  __dirname,
  "../../contracts/artifacts/contracts",
  `${contractName}.sol`,
  `${contractName}.json`,
);

  if (!fs.existsSync(artifactPath)) {
    throw new Error(`ABI artifact not found: ${artifactPath}`);
  }

  const artifact = require(artifactPath);

  if (!artifact.abi) {
    throw new Error(`ABI not found in artifact: ${contractName}`);
  }

  return artifact.abi;
}

function getProvider() {
  if (!RPC_URL) {
    throw new Error("Missing RPC_URL in .env");
  }

  return new ethers.JsonRpcProvider(RPC_URL);
}

function getWallet() {
  if (!PRIVATE_KEY) {
    throw new Error("Missing PRIVATE_KEY in .env");
  }

  return new ethers.Wallet(PRIVATE_KEY, provider);
}

const provider = getProvider();
const wallet = getWallet();

function getToken() {
  if (!TOKEN_ADDRESS) {
    throw new Error("Missing TOKEN_ADDRESS in .env");
  }

  return new ethers.Contract(
    TOKEN_ADDRESS,
    loadAbi("SmartEnergyToken"),
    wallet,
  );
}

function getMarketplace() {
  if (!MARKETPLACE_ADDRESS) {
    throw new Error("Missing MARKETPLACE_ADDRESS in .env");
  }

  return new ethers.Contract(
    MARKETPLACE_ADDRESS,
    loadAbi("EnergyMarketplace"),
    wallet,
  );
}

function getVoting() {
  if (!DPOS_ADDRESS) {
    throw new Error("Missing DPOS_ADDRESS in .env");
  }

  return new ethers.Contract(DPOS_ADDRESS, loadAbi("DPoSVoting"), wallet);
}

module.exports = {
  provider,
  wallet,
  getToken,
  getMarketplace,
  getVoting,
};
