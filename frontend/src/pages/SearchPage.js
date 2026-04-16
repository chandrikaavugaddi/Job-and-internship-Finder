import React, { useEffect, useState } from "react";
import "./Page.css";

function SearchPage() {
  const [jobs, setJobs] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Initial fetch of all jobs
    fetch("http://localhost:5000/api/jobs")
      .then((res) => res.json())
      .then((data) => {
        setJobs(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Fetch Error:", err);
        setLoading(false);
      });
  }, []);

  // Filter logic: Checks title, company, location, and branches
  const filtered = jobs.filter((job) => {
    const searchTerm = search.toLowerCase();
    
    return (
      (job.jobTitle?.toLowerCase().includes(searchTerm)) ||
      (job.companyName?.toLowerCase().includes(searchTerm)) ||
      (job.location?.toLowerCase().includes(searchTerm)) ||
      // Also allows searching by branch (e.g., typing "CSE" will show CSE jobs)
      (job.eligible_branches?.some(branch => branch.toLowerCase().includes(searchTerm)))
    );
  });

  return (
    <div className="page">
      <header className="page-header">
        <h1>Global Search</h1>
        <p>Find roles across all branches and sectors</p>
      </header>

      <div className="search-container" style={{ textAlign: 'center', marginBottom: '40px' }}>
        <input
          className="search-input"
          placeholder="Search by Role, Company, Location, or Branch (e.g. 'Software', 'Google', 'CSE')..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            width: "100%",
            maxWidth: "600px",
            padding: "15px 25px",
            borderRadius: "30px",
            border: "1px solid #ddd",
            fontSize: "1.1rem",
            boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
            outline: "none"
          }}
        />
      </div>

      {loading ? (
        <div className="loader">Loading opportunities...</div>
      ) : (
        <div className="jobs-grid">
          {filtered.length > 0 ? (
            filtered.map((job) => (
              <div 
                key={job.jobId} 
                className={`job-card ${job.category === 'Government' ? 'govt-highlight' : ''}`}
              >
                {job.category === 'Government' && <span className="govt-badge">Official</span>}
                
                <div className="card-body">
                  <h3 className="job-title">{job.jobTitle}</h3>
                  <h4 className="company-name">{job.companyName}</h4>
                  
                  <div className="job-info">
                    <span>📍 {job.location || "Multiple"}</span>
                    <span className="type-tag">{job.jobType}</span>
                  </div>

                  <div className="job-tags">
                    {job.eligible_branches?.map((branch, index) => (
                      <span key={index} className="branch-tag">{branch}</span>
                    ))}
                  </div>
                </div>

                <div className="card-footer">
                  <span className="scraped-date">
                    Added: {new Date(job.scrapedAt).toLocaleDateString()}
                  </span>
                  <a 
                    href={job.applicationLink} 
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
            <div className="empty-state" style={{ textAlign: 'center', gridColumn: '1/-1', padding: '50px' }}>
              <h3>No jobs found for "{search}"</h3>
              <p>Try searching for "TCS", "Python", "Civil", or "Government".</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default SearchPage;