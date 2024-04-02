const body = document.querySelector('body'),
      sideBar = body.querySelector('.sidebar'),
      toggleBtn = body.querySelector('.toggle'),
      searchBtn = body.querySelector('.search-box'),
      modeSwitch = body.querySelector('.toggle-switch'),
      modeText = body.querySelector('.mode-text'),
      tableBg = body.querySelector('.table');


    // used to add class to the toggle menu  
    toggleBtn.addEventListener('click', ()=>{
        sideBar.classList.toggle('close');
    });

    // adding dark class to body to change background color
    modeSwitch.addEventListener('click', ()=>{
        body.classList.toggle('dark');

        if(body.classList.contains('dark')){
            modeText.innerText = "Light Mode"
            tableBg.classList.add('table-dark');
            
        }else{
            modeText.innerText = "Dark Mode"
            tableBg.classList.remove('table-dark');
        }

    });



//line chart
var ctxL = document.getElementById("lineChart").getContext('2d');
var myLineChart = new Chart(ctxL, {
  type: 'line',
  data: {
    labels: ["Jan", "Feb", "March", "April", "May", "June", "July"],
    datasets: [{
      label: "Amount",
      data: [65, 59, 80, 41, 56, 65, 30],
      backgroundColor: [
        'rgba(105, 0, 132, .2)',
      ],
      borderColor: [
        'rgba(200, 99, 132, .7)',
      ],
      borderWidth: 2
    },
    {
      label: "Balance",
      data: [28, 48, 40, 19, 96, 77, 90],
      backgroundColor: [
        'rgba(0, 137, 132, .2)',
      ],
      borderColor: [
        'rgba(0, 10, 130, .7)',
      ],
      borderWidth: 2
    }
    ]
  },
  options: {
    responsive: true
  }
});


//line chart 2
var ctxL = document.getElementById("lineChart2").getContext('2d');
var myLineChart = new Chart(ctxL, {
  type: 'line',
  data: {
    labels: ["Jan", "Feb", "March", "April", "May", "June", "July"],
    datasets: [{
      label: "Current Transactions",
      data: [65, 53, 80, 91, 66, 55, 70],
      backgroundColor: [
        'rgba(48, 156, 21, .2)',
      ],
      borderColor: [
        'rgba(22, 222, 102, .7)',
      ],
      borderWidth: 2
    },
    {
      label: "Interest Rate",
      data: [28, 48, 40, 19, 86, 27, 90],
      backgroundColor: [
        'rgba(236, 51, 14, .2)',
      ],
      borderColor: [
        'rgba(220, 72, 43, .7)',
      ],
      borderWidth: 2
    }
    ]
  },
  options: {
    responsive: true
  }
});