// to get current year
function getYear() {
    var currentDate = new Date();
    var currentYear = currentDate.getFullYear();
    document.querySelector("#displayYear").innerHTML = currentYear;
}

getYear();

function readMore(){
    let lesstxt =document.getElementById("less-txt");
    let moretxt = document.getElementById("more-txt");
    let btn = document.getElementById("read-more-btn");
    if(lesstxt.style.display === "none"){
        lesstxt.style.display = "block";
        moretxt.style.display = "none";
        btn.innerText = "Read More"
    }
    else{
        lesstxt.style.display = "none";
        moretxt.style.display = "block";
        btn.innerText = "Read Less"
    }
}

// nice select
$(document).ready(function () {
    $('select').niceSelect();
});