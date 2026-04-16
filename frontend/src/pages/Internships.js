import React, { useEffect, useState } from "react";
import axios from "axios";
import "./Page.css";

function Internships() {
  const [jobs, setJobs] = useState([]);
  const [selectedYear, setSelectedYear] = useState("");
  const [selectedBranch, setSelectedBranch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const res = await axios.get("http://localhost:5000/api/jobs");

      // ✅ FIX: case-insensitive + correct filtering
      const data = res.data.filter(
        (j) => j.jobType?.toLowerCase() === "internship"
      );

      setJobs(data);
    } catch (err) {
      console.error("Fetch error:", err);
    }
    setLoading(false);
  };

  // ✅ FIXED FILTER LOGIC
  const filteredJobs = jobs.filter((job) => {
    const matchesBranch =
      selectedBranch === "" || job.branch?.includes(selectedBranch);

    const matchesYear =
      selectedYear === "" || job.eligibleYear?.includes(selectedYear);

    return matchesBranch && matchesYear;
  });

  return (
    <div className="page">
      <header className="page-header">
        <h1>Internship Opportunities</h1>
        <p>Verified internships for engineering students</p>
      </header>

      {/* ================= FILTERS ================= */}
      <div className="filters-bar">
        {/* Year Filter */}
        <div className="filter-item">
          <label>Eligible Batch</label>
          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(e.target.value)}
          >
            <option value="">All Candidates</option>
            <option value="2026-2029">2026–2029 Batch</option>
          </select>
        </div>

        {/* Branch Filter */}
        <div className="filter-item">
          <label>Branch</label>
          <select
            value={selectedBranch}
            onChange={(e) => setSelectedBranch(e.target.value)}
          >
            <option value="">All Branches</option>
            <option value="CSE">CSE / IT</option>
            <option value="ECE">ECE</option>
            <option value="EEE">EEE</option>
            <option value="Mechanical">Mechanical</option>
            <option value="Civil">Civil</option>
            <option value="General">General</option>
          </select>
        </div>

        <button className="btn-search" onClick={fetchJobs}>
          Refresh Feed
        </button>
      </div>

      {/* ================= JOBS GRID ================= */}
      {loading ? (
        <div className="loader">Updating internship feed...</div>
      ) : (
        <div className="jobs-grid">
          {filteredJobs.length > 0 ? (
            filteredJobs.map((job) => (
              <div key={job._id} className="job-card">
                <div className="card-body">
                  <div className="card-top">
                    <span className="type-badge intern">
                      {job.jobType}
                    </span>
                    <span className="source-tag">
                      {job.source || "Private"}
                    </span>
                  </div>

                  <h3 className="job-title">{job.jobTitle}</h3>
                  <h4 className="company-name">{job.companyName}</h4>

                  <div className="job-info">
                    <span>📍 {job.location || "Multiple Locations"}</span>
                    <span>
                      🎓 {job.eligibleYear?.join(", ") || "All Batches"}
                    </span>
                  </div>
                </div>

                <div className="card-footer">
                  <span className="scraped-date">
                    Sync:{" "}
                    {job.syncedAt
                      ? new Date(job.syncedAt).toLocaleDateString()
                      : "Recently"}
                  </span>

                  {/* ✅ FIXED */}
                  <a
                    href={job.applyLink}
                    target="_blank"
                    rel="noreferrer"
                    className="apply-link"
                  >
                    Apply Now
                  </a>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              No matching internships found.
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Internships;