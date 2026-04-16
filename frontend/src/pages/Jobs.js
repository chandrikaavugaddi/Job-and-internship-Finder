import React, { useEffect, useState } from "react";
import axios from "axios";
import "./Page.css";

function Jobs() {
  const [jobs, setJobs] = useState([]);
  const [selectedYear, setSelectedYear] = useState("");
  const [selectedBranch, setSelectedBranch] = useState("");
  const [loading, setLoading] = useState(false);

  // ================= FETCH DATA =================
  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const response = await axios.get("http://localhost:5000/api/jobs");

      // ✅ FIX: case-insensitive jobType filter
      const fullTimeJobs = response.data.filter(
        (j) => j.jobType?.toLowerCase() === "job"
      );

      setJobs(fullTimeJobs);
    } catch (err) {
      console.error("Error fetching jobs:", err);
    }
    setLoading(false);
  };

  // ================= FILTER LOGIC =================
  const filteredJobs = jobs.filter((job) => {
    const matchesBranch =
      selectedBranch === "" || job.branch?.includes(selectedBranch);

    const matchesYear =
      selectedYear === "" || job.eligibleYear?.includes(selectedYear);

    return matchesBranch && matchesYear;
  });

  // ================= UI =================
  return (
    <div className="page">
      <header className="page-header">
        <h1>Full-Time Career Opportunities</h1>
        <p>
          Verified job openings for freshers and graduating engineering students
        </p>
      </header>

      {/* ================= FILTERS ================= */}
      <div className="filters-bar">
        {/* Year Filter */}
        <div className="filter-item">
          <label>Target Eligibility</label>
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

        {/* Refresh Button */}
        <button
          className="btn-search"
          onClick={fetchJobs}
          disabled={loading}
        >
          {loading ? "Refreshing..." : "Sync Database"}
        </button>
      </div>

      {/* ================= JOBS GRID ================= */}
      <div className="jobs-grid">
        {!loading && filteredJobs.length > 0 ? (
          filteredJobs.map((job) => (
            <div className="job-card" key={job._id}>
              {/* Government Badge */}
              {job.source === "Government" && (
                <span className="govt-badge">Official PSU</span>
              )}

              <div className="card-body">
                <div className="card-top">
                  <span className="type-badge job-type">
                    {job.jobType}
                  </span>
                  <span className="source-tag">
                    {job.source || "Private"}
                  </span>
                </div>

                <h3 className="job-title">{job.jobTitle}</h3>
                <h4 className="company-name">{job.companyName}</h4>

                <div className="job-meta">
                  <span>📍 {job.location || "Multiple Locations"}</span>
                </div>

                {/* Skills */}
                {job.skills?.length > 0 && (
                  <div className="skills-section">
                    <strong>Required:</strong>{" "}
                    {job.skills.join(", ")}
                  </div>
                )}
              </div>

              <div className="card-footer">
                <span className="scraped-date">
                  Updated:{" "}
                  {job.syncedAt
                    ? new Date(job.syncedAt).toLocaleDateString()
                    : "Recently"}
                </span>

                {/* ✅ FIX: correct field */}
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
          !loading && (
            <div className="empty-state">
              No jobs found. Try refreshing or changing filters.
            </div>
          )
        )}
      </div>

      {/* Loader */}
      {loading && (
        <div className="loader">
          Accessing CareerHub Database...
        </div>
      )}
    </div>
  );
}

export default Jobs;