const mongoose = require("mongoose");

const JobSchema = new mongoose.Schema({

  jobId: String,

  companyName: String,

  jobTitle: String,

  skills: [String],

  location: String,

  jobType: String,

  eligibleYear: [String],

  isIT: Boolean,

  applyLink: String,

  sourceWebsite: String,

  postedDate: Date,

  lastUpdated: Date,

  expiryDate: Date

},{
  timestamps:true
});

module.exports =
mongoose.models.Job ||
mongoose.model("Job", JobSchema);