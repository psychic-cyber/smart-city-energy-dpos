const { ethers } = require("hardhat");

async function main() {

    console.log("Deploying SmartEnergyToken...");

    const Token = await ethers.getContractFactory("SmartEnergyToken");

    const token = await Token.deploy(
        "Smart Energy Token",
        "SET"
    );

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

    await token.setMarketplace(marketplaceAddress);

    console.log("Deploying DPoSVoting...");

    const Voting = await ethers.getContractFactory("DPoSVoting");

    const voting = await Voting.deploy();

    await voting.waitForDeployment();

    const votingAddress = await voting.getAddress();

    console.log("Voting:", votingAddress);

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
