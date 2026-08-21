let currentCityData = null;

let aqiChart = null;


// ======================================================
// LOAD CITIES
// ======================================================

async function loadCities() {

    const response =
        await fetch("/api/cities");

    const cities =
        await response.json();

    const select =
        document.getElementById("citySelect");

    select.innerHTML = "";

    cities.forEach(city => {

        const option =
            document.createElement("option");

        option.value = city;
        option.textContent = city;

        select.appendChild(option);

    });

    if (cities.length > 0) {

        select.value = cities[0];

        await loadCity();
    }
}


// ======================================================
// LOAD CITY
// ======================================================

async function loadCity() {

    const city =
        document.getElementById(
            "citySelect"
        ).value;

    if (!city) return;


    const response =
        await fetch(
            `/api/city/${city}`
        );


    const data =
        await response.json();


    if (data.error) {

        alert(data.error);

        return;
    }


    currentCityData = data;


    // ------------------------------------
    // Main AQI
    // ------------------------------------

    document.getElementById(
        "cityName"
    ).textContent =
        data.city;


    document.getElementById(
        "aqiValue"
    ).textContent =
        data.aqi;


    document.getElementById(
        "aqiLevel"
    ).textContent =
        data.level;


    document.getElementById(
        "heroAQI"
    ).textContent =
        data.aqi;


    document.getElementById(
        "heroLevel"
    ).textContent =
        data.level;


    // ------------------------------------
    // Weather
    // ------------------------------------

    document.getElementById(
        "temperature"
    ).textContent =
        data.temperature ?? "--";


    document.getElementById(
        "humidity"
    ).textContent =
        data.humidity ?? "--";


    document.getElementById(
        "windSpeed"
    ).textContent =
        data.wind_speed ?? "--";


    document.getElementById(
        "windDirection"
    ).textContent =
        data.wind_direction ?? "--";


    document.getElementById(
        "heroTemp"
    ).textContent =
        `${data.temperature ?? "--"}°C`;


    document.getElementById(
        "heroWind"
    ).textContent =
        `${data.wind_speed ?? "--"} m/s`;


    // ------------------------------------
    // Pollution
    // ------------------------------------

    document.getElementById(
        "pm25"
    ).textContent =
        data.pm25;


    document.getElementById(
        "pm10"
    ).textContent =
        data.pm10;


    // ------------------------------------
    // AQI bar
    // ------------------------------------

    const bar =
        document.getElementById(
            "aqiBar"
        );

    bar.style.width =
        `${Math.min(data.aqi / 5, 100)}%`;


    // ------------------------------------
    // Description
    // ------------------------------------

    document.getElementById(
        "aqiDescription"
    ).textContent =
        getDescription(data.level);


    // ------------------------------------
    // Chart
    // ------------------------------------

    createChart(data.history);

}


// ======================================================
// AQI DESCRIPTION
// ======================================================

function getDescription(level) {

    if (level === "Good") {

        return "Air quality is in a good range.";

    }

    if (level === "Satisfactory") {

        return "Air quality is acceptable, with some pollutants at elevated levels.";

    }

    if (level === "Moderate") {

        return "Air quality may affect sensitive individuals.";

    }

    if (level === "Poor") {

        return "Pollution levels are high. Sensitive groups should take care.";

    }

    if (level === "Very Poor") {

        return "Air quality is very poor and may affect health.";

    }

    return "Air quality is severe and requires immediate attention.";

}


// ======================================================
// CREATE CHART
// ======================================================

function createChart(history) {

    const canvas =
        document.getElementById(
            "aqiChart"
        );


    if (aqiChart) {

        aqiChart.destroy();

    }


    const labels =
        history.map(item =>
            item.time.substring(11, 16)
        );


    const values =
        history.map(item =>
            item.aqi
        );


    aqiChart =
        new Chart(
            canvas,
            {

                type: "line",

                data: {

                    labels: labels,

                    datasets: [{

                        label: "AQI",

                        data: values,

                        borderWidth: 3,

                        tension: 0.4,

                        fill: true,

                        backgroundColor:
                            "rgba(53,214,255,0.08)",

                        borderColor:
                            "#35d6ff",

                        pointBackgroundColor:
                            "#48e0a4"

                    }]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {

                        legend: {

                            display: false

                        }

                    },

                    scales: {

                        x: {

                            ticks: {

                                color: "#8fa4bd"

                            },

                            grid: {

                                display: false

                            }

                        },

                        y: {

                            beginAtZero: true,

                            ticks: {

                                color: "#8fa4bd"

                            },

                            grid: {

                                color:
                                    "rgba(255,255,255,0.06)"

                            }

                        }

                    }

                }

            }
        );

}


// ======================================================
// RUN ML PREDICTION
// ======================================================

async function runPrediction() {

    if (!currentCityData) {

        alert(
            "Please select a city first."
        );

        return;
    }


    // We need the other pollutant values.
    // Fetch them from the latest timestamp
    // through a small backend request.

    const city =
        currentCityData.city;


    const response =
        await fetch(
            `/api/predict-city/${city}`
        );


    if (!response.ok) {

        alert(
            "Prediction data could not be loaded."
        );

        return;
    }


    const data =
        await response.json();


    document.getElementById(
        "predictionValue"
    ).textContent =
        data.predicted_aqi;


    document.getElementById(
        "predictionLevel"
    ).textContent =
        data.level;

}


// ======================================================
// MODEL INFORMATION
// ======================================================

async function loadModelInfo() {

    const response =
        await fetch(
            "/api/model"
        );


    const data =
        await response.json();


    document.getElementById(
        "trainingRecords"
    ).textContent =
        data.training_records;


    document.getElementById(
        "modelMAE"
    ).textContent =
        data.mae;


    document.getElementById(
        "modelR2"
    ).textContent =
        data.r2;

}


// ======================================================
// SCROLL
// ======================================================

function scrollToDashboard() {

    document.getElementById(
        "dashboard"
    ).scrollIntoView({
        behavior: "smooth"
    });

}


// ======================================================
// START
// ======================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadCities();

        loadModelInfo();

    }
);