const { ethers } = require("hardhat");
require("dotenv").config();

async function main() {
  const provider = ethers.provider;

  const owner = new ethers.Wallet(process.env.PRIVATE_KEY_OWNER, provider);
  const hospital = new ethers.Wallet(
    process.env.PRIVATE_KEY_HOSPITAL,
    provider,
  );
  const solar = new ethers.Wallet(process.env.PRIVATE_KEY_SOLAR, provider);
  const university = new ethers.Wallet(
    process.env.PRIVATE_KEY_UNIVERSITY,
    provider,
  );

  const token = await ethers.getContractAt(
    "SmartEnergyToken",
    process.env.TOKEN_ADDRESS,
    owner,
  );

  const marketplace = await ethers.getContractAt(
    "EnergyMarketplace",
    process.env.MARKETPLACE_ADDRESS,
    owner,
  );

  const voting = await ethers.getContractAt(
    "DPoSVoting",
    process.env.DPOS_ADDRESS,
    owner,
  );

  console.log("========== INITIALIZATION ==========");

  console.log("Mint Tokens...");

  await (
    await token.mint(owner.address, ethers.parseUnits("40000", 18))
  ).wait();

  await (
    await token.mint(hospital.address, ethers.parseUnits("20000", 18))
  ).wait();

  await (
    await token.mint(solar.address, ethers.parseUnits("20000", 18))
  ).wait();

  await (
    await token.mint(university.address, ethers.parseUnits("20000", 18))
  ).wait();

  console.log("Approve Marketplace...");

  await (
    await token
      .connect(owner)
      .approve(process.env.MARKETPLACE_ADDRESS, ethers.parseUnits("40000", 18))
  ).wait();

  await (
    await token
      .connect(hospital)
      .approve(process.env.MARKETPLACE_ADDRESS, ethers.parseUnits("20000", 18))
  ).wait();

  await (
    await token
      .connect(solar)
      .approve(process.env.MARKETPLACE_ADDRESS, ethers.parseUnits("20000", 18))
  ).wait();

  await (
    await token
      .connect(university)
      .approve(process.env.MARKETPLACE_ADDRESS, ethers.parseUnits("20000", 18))
  ).wait();

  console.log("Register Hospital Producer...");
  await (await marketplace.connect(hospital).registerEnergyProducer()).wait();

  console.log("Register Solar Producer...");
  await (await marketplace.connect(solar).registerEnergyProducer()).wait();

  console.log("Register University Consumer...");
  await (await marketplace.connect(university).registerEnergyConsumer()).wait();

  console.log("Register Hospital Delegate...");
  await voting.connect(hospital)
    .registerDelegate("SmartCity-Hospital01");

  console.log("Register Solar Delegate...");
  await voting.connect(solar)
    .registerDelegate("SmartCity-SolarFarm01");

  console.log("Register University Delegate...");
  await voting.connect(university)
    .registerDelegate("SmartCity-University01");

  console.log("====================================");
  console.log("Initialization Complete");
  console.log("====================================");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
