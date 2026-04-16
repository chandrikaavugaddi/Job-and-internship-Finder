
fetch("http://localhost:5000/api/jobs")

.then(res=>res.json())

.then(data=>{

let html="";

data.forEach(job=>{

html+=`

<div class="card">

<h3>${job.title}</h3>

<p>${job.company}</p>

<p>${job.location}</p>

<p>${job.jobType}</p>

<a href="${job.applyLink}"
class="applyBtn"
target="_blank">
Apply
</a>

</div>

`;

});

document.getElementById("jobs").innerHTML=html;

});