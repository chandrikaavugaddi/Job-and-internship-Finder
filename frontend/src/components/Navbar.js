import { Link } from "react-router-dom";

function Navbar(){

return(

<div style={{
background:"#2563eb"}} className="navbar">

<h2 >🔍 Automated Job  and Finder system</h2>

<div>

<Link to="/">Home</Link>

<Link to="/internships">Internships</Link>

<Link to="/jobs">Jobs</Link>
<Link to="/search">Search</Link>

</div>

</div>

)

}

export default Navbar;