const { ethers } = require("hardhat");

async function main() {

  console.log("Deploying SmartEnergyToken...");

  const Token = await ethers.getContractFactory("SmartEnergyToken");
  const token = await Token.deploy("Smart Energy Token", "SET");
  await token.waitForDeployment();

  const tokenAddress = await token.getAddress();
  console.log("Token:", tokenAddress);


  console.log("Deploying Marketplace...");

  const Marketplace = await ethers.getContractFactory("EnergyMarketplace");
  const marketplace = await Marketplace.deploy(tokenAddress);
  await marketplace.waitForDeployment();

  const marketplaceAddress = await marketplace.getAddress();
  console.log("Marketplace:", marketplaceAddress);


  console.log("Register Marketplace...");
  await (await token.setMarketplace(marketplaceAddress)).wait();


  console.log("Deploying DPoSVoting...");

  const Voting = await ethers.getContractFactory("DPoSVoting");
  const voting = await Voting.deploy();
  await voting.waitForDeployment();

  const votingAddress = await voting.getAddress();
  console.log("Voting:", votingAddress);


  const [owner] = await ethers.getSigners();


  console.log("Minting Tokens...");
  await (
    await token.mint(owner.address, ethers.parseUnits("100000", 18))
  ).wait();


  console.log("Register Producer...");
  await (
    await marketplace.registerEnergyProducer()
  ).wait();


  console.log("Register Consumer...");
  await (
    await marketplace.registerEnergyConsumer()
  ).wait();


  console.log("Approve Marketplace...");
  await (
    await token.approve(
      marketplaceAddress,
      ethers.parseUnits("100000", 18)
    )
  ).wait();


  console.log("Register Delegate...");
  await (
    await voting.registerDelegate("Main Validator")
  ).wait();


  console.log("Initialization Complete.");

  console.log("================================");
  console.log("TOKEN_ADDRESS=" + tokenAddress);
  console.log("MARKETPLACE_ADDRESS=" + marketplaceAddress);
  console.log("DPOS_ADDRESS=" + votingAddress);
  console.log("================================");

}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});