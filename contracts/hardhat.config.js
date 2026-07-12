// require("@nomicfoundation/hardhat-toolbox");
// require("dotenv").config();

// module.exports = {
//   solidity: "0.8.28",
//   networks: {
//     amoy: {
//       url: process.env.RPC_URL,
//       accounts: [process.env.PRIVATE_KEY],
//       chainId: 80002,
//     },
//   },
// };

require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

module.exports = {
  solidity: "0.8.28",

  networks: {

    localhost: {
      url: "http://127.0.0.1:8545",
    },

    amoy: {
      url: process.env.RPC_URL,
      accounts: [process.env.PRIVATE_KEY_OWNER],
      chainId: 80002,
},

  },
};