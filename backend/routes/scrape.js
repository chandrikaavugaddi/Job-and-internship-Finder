const express = require("express");
const router = express.Router();

const {
scrapeIBMJobs
} = require("../scraper");



router.get("/scrape", async(req,res)=>{

    await scrapeIBMJobs();

    res.send("Scraping Finished");

});


module.exports = router;