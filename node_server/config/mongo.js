const { MongoClient } = require("mongodb");

const MONGO_URI = "mongodb://127.0.0.1:27017";
const DB_NAME = "smart_city_db";

let database = null;

async function getDatabase() {

    if (database) {
        return database;
    }

    const client = new MongoClient(MONGO_URI);

    await client.connect();

    database = client.db(DB_NAME);

    console.log("MongoDB Connected");

    return database;
}

module.exports = {
    getDatabase
};
