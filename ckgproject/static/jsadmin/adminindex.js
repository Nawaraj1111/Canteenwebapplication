// This is for able to see chart. We are using Apex Chart. U can check the documentation of Apex Charts too..
var options = {
  series: [
    {
      name: "Total Sales"
      data: [44, 55, 57, 56, 61, 58, 63, 60, 66],
    },
    {
      name: "Total Turnover",
      data: [76, 85, 101, 98, 87, 105, 91, 114, 94],
    },

  ],
  chart: {
    type: "bar",
    height: 250, // make this 250
    sparkline: {
      enabled: true, // make this true
    },
  },
  plotOptions: {
    bar: {
      horizontal: false,
      columnWidth: "55%",
      endingShape: "rounded",
    },
  },
  dataLabels: {
    enabled: false,
  },
  stroke: {
    show: true,
    width: 2,
    colors: ["transparent"],
  },
  xaxis: {
    categories: ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "August", "September", "October", "November", "December"],
  },
  yaxis: {
    title: {
      text: "NRP (thousands)",
    },
  },
  fill: {
    opacity: 1,
  },
  tooltip: {
    y: {
      formatter: function (val) {
        return "NRP " + val + " thousands";
      },
    },
  },
};

var chart = new ApexCharts(document.querySelector("#apex1"), options);
chart.render();

// Sidebar Toggle Codes;

var sidebarOpen = false;
var sidebar = document.getElementById("sidebar");
var sidebarCloseIcon = document.getElementById("sidebarIcon");

function toggleSidebar() {
  if (!sidebarOpen) {
    sidebar.classList.add("sidebar_responsive");
    sidebarOpen = true;
  }
}

function closeSidebar() {
  if (sidebarOpen) {
    sidebar.classList.remove("sidebar_responsive");
    sidebarOpen = false;
  }
}
