import React from "react";
import { useNavigate } from "react-router-dom";

function HomePage(){

const navigate = useNavigate();

return(

<div style={{fontFamily:"Arial"}}>

{/* HERO SECTION */}

<div style={{

background:"#0f172a",
color:"white",
padding:"80px 20px",
textAlign:"center"

}}>

<h1 style={{
fontSize:"42px",
marginBottom:"10px",
color:"#cbd5e1"
}}>

🔍 Automated Job & Internship Finder System

</h1>

<p style={{
fontSize:"18px",
marginBottom:"30px",
color:"#cbd5e1"
}}>

Discover internships and job opportunities from multiple companies,
ATS platforms and career sites in one place.

</p>


<input
placeholder="Search Jobs, Companies, Internships..."

onClick={()=>navigate("/search")}

style={{

width:"450px",
padding:"15px",
borderRadius:"8px",
border:"none",
fontSize:"16px"

}}
/>


</div>


{/* FEATURES SECTION */}

<div style={{

padding:"50px",
display:"flex",
justifyContent:"center",
gap:"40px"

}}>



<div style={{

width:"300px",
border:"1px solid #ddd",
padding:"25px",
borderRadius:"12px",
textAlign:"center",
boxShadow:"0px 2px 8px rgba(0,0,0,0.1)"

}}>

<h2>Internships</h2>

<p>

Find internship opportunities for 1st, 2nd, 3rd and 4th year students.

</p>

<button
onClick={()=>navigate("/Internships")}

style={{

padding:"10px 20px",
marginTop:"10px",
borderRadius:"6px",
border:"none",
background:"#2563eb",
color:"white"

}}

>

Explore

</button>

</div>




<div style={{

width:"300px",
border:"1px solid #ddd",
padding:"25px",
borderRadius:"12px",
textAlign:"center",
boxShadow:"0px 2px 8px rgba(0,0,0,0.1)"

}}>

<h2>Jobs</h2>

<p>

Explore full-time job opportunities for final year students.

</p>

<button
onClick={()=>navigate("/Jobs")}

style={{

padding:"10px 20px",
marginTop:"10px",
borderRadius:"6px",
border:"none",
background:"#2563eb",
color:"white"

}}

>

Explore

</button>

</div>


</div>





</div>

)

}

export default HomePage;