const express = require('express');
const router = express.Router();
const Job = require('../models/job');

// GET /api/jobs - Get all jobs with optional filters
router.get('/', async (req, res) => {
  try {
    const { year, company, type } = req.query;
    let query = {};

    if (year) query.year = year;
    if (company) query.company = new RegExp(company, 'i');
    if (type) query.type = type;

    const jobs = await Job.find(query);
    res.json(jobs);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// GET /api/jobs/:id - Get a specific job by ID
router.get('/:id', async (req, res) => {
  try {
    const job = await Job.findById(req.params.id);
    if (!job) return res.status(404).json({ message: 'Job not found' });
    res.json(job);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

module.exports = router;
