const axios = require("axios");
const cheerio = require("cheerio");
const Job = require("./models/Job");
const { v4: uuidv4 } = require("uuid");


// Convert text to eligible years
function extractEligibleYears(text) {

    const years = [];

    if(text.includes("1") || text.includes("First"))
        years.push("1st");

    if(text.includes("2") || text.includes("Second"))
        years.push("2nd");

    if(text.includes("3") || text.includes("Third"))
        years.push("3rd");

    if(text.includes("4") || text.includes("Fourth"))
        years.push("4th");

    // Default if not mentioned
    if(years.length === 0)
        years.push("4th");

    return years;
}


// Clean Job Title Function
function cleanJobTitle(rawText){

    if(!rawText) return "";

    let lines = rawText
        .split("\n")
        .map(l => l.trim())
        .filter(l => l.length > 2);

    // Usually second line is actual role
    if(lines.length > 1){
        return lines[1];
    }

    return lines[0];
}




async function scrapeIBMJobs(){

    try{

        const url =
        "https://www.ibm.com/careers/search?q=Software";

        const response =
        await axios.get(url);

        const $ =
        cheerio.load(response.data);

        const jobs = [];


        $(".bx--card").each((i,el)=>{


            let rawTitle =
            $(el).find("h3").text();

            let title =
            cleanJobTitle(rawTitle);


            let company =
            "IBM";


            let link =
            $(el).find("a").attr("href");


            let desc =
            $(el).text();



            // Fix link
            if(link && !link.startsWith("http")){

                link =
                "https://www.ibm.com" + link;
            }



            const eligibleYears =
            extractEligibleYears(desc);



            // Validation

            if(!title || !link)
                return;



            jobs.push({

                jobId: uuidv4(),

                companyName: company,

                jobTitle: title,

                location: "Multiple Locations",

                applyLink: link,

                sourceWebsite: url,

                eligibleYear: eligibleYears,

                isIT: true,

                jobType: "Fulltime",

                postedDate: new Date(),

                lastUpdated: new Date(),

                expiryDate:
                new Date(
                    Date.now()
                    + 30*24*60*60*1000
                )

            });

        });



        console.log(
        "Valid Jobs:",
        jobs.length
        );



        // Prevent duplicates
        for(const job of jobs){

            const exists =
            await Job.findOne({

                companyName: job.companyName,
                jobTitle: job.jobTitle,
                applyLink: job.applyLink

            });


            if(!exists){

                await Job.create(job);

                console.log(
                "Saved:",
                job.jobTitle
                );

            }

        }



        console.log(
        "Scraping Completed"
        );


    }
    catch(err){

        console.log(err);

    }

}



module.exports = {

    scrapeIBMJobs

};