const express = require("express");
const cors = require("cors");

const app = express();
const PORT = 3000;

app.use(cors());

//Route
app.get("/", (req, res) => {
    res.send("Welcome to the node server!");
});

// Another Route
app.get("/api/hello", (req, res) => {
    res.json({message : "Hello from the API!"});
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});