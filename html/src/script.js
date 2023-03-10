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
        const value = [new Date()];

        rawJson.map((obj) => {
            value.push("\n-------------------------------");
            for (let key in obj) {
                value.push("  " + key + ": " + obj[key]);
            }
        });

        document.getElementById("last-textarea").value = value.join("\n");
    });
}

function update3() {
    d3.json("/mongo/fetchall?sort_timestamp=1&limit=5000").then((rawJson) => {
        console.log(rawJson);

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

        {
            const plt = Plot.plot({
                grid: { x: true, y: true },
                color: { legend: true },
                // facet: { data: allData, y: (d) => d.machineIP },
                marks: [
                    Plot.line(allData, {
                        x: "date",
                        y: "loadAverage",
                        stroke: "machineIP",
                    }),
                    Plot.ruleY([0]),
                ],
            });
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
        d.setHours(s1[0]);
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
