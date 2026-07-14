const { getDatabase } = require("../config/mongo");

async function getUserWallet(username) {

    if (!username) {
        throw new Error("Username is required");
    }

    const db = await getDatabase();

    const user = await db.collection("users").findOne(
        {
            username: username
        }
    );

    if (!user) {
        throw new Error("User not found");
    }

    if (!user.private_key) {
        throw new Error(
            `Private key not found for ${username}`
        );
    }

    return {
        username: user.username,
        wallet: user.wallet_address,
        privateKey: user.private_key
    };
}

module.exports = {
    getUserWallet
};
