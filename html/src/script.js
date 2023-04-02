console.log("Script running");
console.log(d3, d3.version);

const myChartJsBuffer = {
  myChart: undefined,
};

function update1() {
  d3.json("/mongo/summary").then((rawJson) => {
    const value = [new Date()];

    rawJson.map((obj) => {
      value.push("\n-------------------------------");
      for (let key in obj) {
        value.push("  " + key + ": " + obj[key]);
      }
    });

    document.getElementById("summary-textarea").value = value.join("\n");
  });

  d3.json("/mongo/last").then((rawJson) => {
    // const value = [new Date()];
    console.log("Update mongo/last session by", rawJson);

    document.getElementById("last-status-h2").innerHTML =
      "Last status: " + new Date();

    const div = d3.select("#last-status-div");
    div.selectAll("div").data([]).exit().remove();

    const divs = div.selectAll("div").data(rawJson).enter().append("div");

    divs.append("h3").text((d) => d.machineIP);

    divs
      .append("textarea")
      .attr("class", "ta1")
      .text((obj) => {
        const value = [];
        ["uptime", "free", "timestamp", "ps", "df"].map((key) => {
          value.push("\n" + key + ":\n" + obj[key]);
        });
        return value.join("\n");
      });

    // rawJson.map((obj) => {
    //   value.push("\n-------------------------------");
    //   for (let key in obj) {
    // value.push("  " + key + ": " + obj[key]);
    //   }
    // });
    //
    // document.getElementById("last-textarea").value = value.join("\n");
  });
}

// 60 minutes x 240 hours x 5 machines
const mongoFetchallLimit = 60 * 240 * 5

function update3() {
  d3.json(`/mongo/fetchall?sort_timestamp=-1&limit=${mongoFetchallLimit}`).then((rawJson) => {
    console.log("Update mongo/fetchall session by", rawJson);

    document.getElementById("uptime-h2").innerHTML = "Uptime: " + new Date();

    const machineIPs = {},
      allData = [];

    rawJson.map((json) => {
      var { _id, free, machineIP, uptime, timestamp } = json;

      var date = parseDate(timestamp),
        loadAverage = parseUptime(uptime),
        freeMem = parseFree(free);

      machineIPs[machineIP] = machineIPs[machineIP]
        ? machineIPs[machineIP]
        : [];
      machineIPs[machineIP].push(
        Object.assign({}, { machineIP, date, loadAverage, freeMem })
      );

      allData.push(
        Object.assign({}, { machineIP, date, loadAverage, freeMem })
      );
    });

    console.log(machineIPs);

    const maxLoadAverage = d3.max(allData, (d) => d.loadAverage),
      scaler = document.getElementById("uptime-slider-1").value / 100;
    console.log(maxLoadAverage);

    {
      const plt = Plot.plot({
        grid: { x: true, y: true },
        color: { legend: true },
        y: { domain: [0, maxLoadAverage * scaler] },
        // facet: { data: allData, y: (d) => d.machineIP },
        marks: [
          Plot.line(allData, {
            x: (d) => d.date, // "date",
            y: "loadAverage",
            stroke: "machineIP",
          }),
          Plot.ruleY([0]),
        ],
      });

      if (document.getElementById("plotDiv").children.length > 0)
        document
          .getElementById("plotDiv")
          .removeChild(document.getElementById("plotDiv").children[0]);

      document.getElementById("plotDiv").append(plt);
    }

    {
      return;
      const { myChart } = myChartJsBuffer;

      for (var ip in machineIPs) {
        var label = ip,
          type = "bubble",
          data = machineIPs[ip].map((d) => {
            return { x: d.date, y: d.loadAverage };
          });
        myChart.data.datasets.push({
          type,
          label,
          data,
        });
      }

      myChart.update();
    }
  });

  function parseFree(free) {
    const s = free.split("\n");
    return s;
  }

  function parseUptime(uptime) {
    const s = uptime.split(":"),
      value = s[s.length - 1].split(",").map((d) => parseFloat(d))[1];
    return value;
  }

  function parseDate(timestamp) {
    // return "20" + timestamp;

    const s = timestamp.split(" "),
      s0 = s[0].split("-"),
      s1 = s[1].split(":"),
      d = new Date();

    d.setFullYear("20" + s0[0]);
    d.setMonth(s0[1]);
    d.setDate(s0[2]);
    // Convert into beijing's data zone, since the Plot will use it as the x-axis
    d.setHours(parseInt(s1[0]) + 8);
    d.setMinutes(s1[1]);
    d.setSeconds(s1[2]);

    return d;
  }
}

function update2() {
  return;
  const ctx = document.getElementById("myChart");

  if (myChartJsBuffer.myChart) myChartJsBuffer.myChart.destroy();

  myChartJsBuffer.myChart = new Chart(ctx, {
    // type: "bubble",
    data: {
      // labels: ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"],
      datasets: [
        // {
        //     label: "# of Votes",
        //     data: [12, 19, 3, 5, 2, 3],
        //     borderWidth: 1,
        // },
      ],
    },
    options: {
      scales: {
        x: {
          // type: "time",
        },
        y: {
          beginAtZero: true,
        },
      },
    },
  });
}
