from pathlib import Path
import pandas as pd
import numpy as np

from flask import Flask, render_template, jsonify, request

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "Air_Quality_Prediction"

VIJAYAWADA_FILE = DATA_DIR / "air_quality.csv"
GUNTUR_FILE = DATA_DIR / "air quality guntur.csv"


app = Flask(__name__)


# ============================================================
# CSV FILES
# ============================================================

CSV_FILES = {
    "Vijayawada": VIJAYAWADA_FILE,
    "Guntur": GUNTUR_FILE
}

# ============================================================
# AQI BREAKPOINTS
# ============================================================

pm25_breakpoints = [
    (0, 30, 0, 50),
    (31, 60, 51, 100),
    (61, 90, 101, 200),
    (91, 120, 201, 300),
    (121, 250, 301, 400),
    (251, 500, 401, 500)
]

pm10_breakpoints = [
    (0, 50, 0, 50),
    (51, 100, 51, 100),
    (101, 250, 101, 200),
    (251, 350, 201, 300),
    (351, 430, 301, 400),
    (431, 500, 401, 500)
]

no2_breakpoints = [
    (0, 40, 0, 50),
    (41, 80, 51, 100),
    (81, 180, 101, 200),
    (181, 280, 201, 300),
    (281, 400, 301, 400),
    (401, 1000, 401, 500)
]

so2_breakpoints = [
    (0, 40, 0, 50),
    (41, 80, 51, 100),
    (81, 380, 101, 200),
    (381, 800, 201, 300),
    (801, 1600, 301, 400),
    (1601, 2620, 401, 500)
]

co_breakpoints = [
    (0, 1, 0, 50),
    (1.1, 2, 51, 100),
    (2.1, 10, 101, 200),
    (10.1, 17, 201, 300),
    (17.1, 34, 301, 400),
    (34.1, 50, 401, 500)
]

o3_breakpoints = [
    (0, 50, 0, 50),
    (51, 100, 51, 100),
    (101, 168, 101, 200),
    (169, 208, 201, 300),
    (209, 748, 301, 400),
    (749, 1000, 401, 500)
]


# ============================================================
# AQI CALCULATION
# ============================================================

def calculate_sub_index(concentration, breakpoints):

    if pd.isna(concentration):
        return np.nan

    for low_conc, high_conc, low_aqi, high_aqi in breakpoints:

        if low_conc <= concentration <= high_conc:

            return (
                ((high_aqi - low_aqi) /
                 (high_conc - low_conc))
                * (concentration - low_conc)
                + low_aqi
            )

    return np.nan


def calculate_aqi(row):

    values = []

    values.append(
        calculate_sub_index(row["pm25"], pm25_breakpoints)
    )

    values.append(
        calculate_sub_index(row["pm10"], pm10_breakpoints)
    )

    values.append(
        calculate_sub_index(row["no2"], no2_breakpoints)
    )

    values.append(
        calculate_sub_index(row["so2"], so2_breakpoints)
    )

    values.append(
        calculate_sub_index(row["co"], co_breakpoints)
    )

    values.append(
        calculate_sub_index(row["o3"], o3_breakpoints)
    )

    valid_values = [
        value for value in values
        if not pd.isna(value)
    ]

    if not valid_values:
        return np.nan

    return max(valid_values)


def get_aqi_level(aqi):

    if aqi <= 50:
        return "Good"

    elif aqi <= 100:
        return "Satisfactory"

    elif aqi <= 200:
        return "Moderate"

    elif aqi <= 300:
        return "Poor"

    elif aqi <= 400:
        return "Very Poor"

    return "Severe"


# ============================================================
# LOAD AND PROCESS CSV
# ============================================================

def process_csv(city, filename):

    df = pd.read_csv(filename)

    # Convert values to numeric
    df["value"] = pd.to_numeric(
        df["value"],
        errors="coerce"
    )

    # Reshape long data into timestamp rows
    df_wide = df.pivot_table(
        index="datetimeLocal",
        columns="parameter",
        values="value",
        aggfunc="mean"
    ).reset_index()

    required = [
        "datetimeLocal",
        "pm25",
        "pm10",
        "no2",
        "so2",
        "co",
        "o3",
        "temperature",
        "relativehumidity",
        "wind_speed",
        "wind_direction"
    ]

    # Make missing columns if necessary
    for column in required:

        if column not in df_wide.columns:
            df_wide[column] = np.nan

    df_wide = df_wide[required].copy()

    # Add location information
    df_wide["City"] = city
    df_wide["State"] = "Andhra Pradesh"

    # Calculate AQI
    df_wide["AQI"] = df_wide.apply(
        calculate_aqi,
        axis=1
    )

    df_wide["AQI_Level"] = df_wide["AQI"].apply(
        lambda x: get_aqi_level(x)
        if not pd.isna(x)
        else "Unavailable"
    )

    return df_wide


# ============================================================
# LOAD BOTH CITIES
# ============================================================

all_data = []

for city, filename in CSV_FILES.items():

    try:

        city_data = process_csv(
            city,
            filename
        )

        all_data.append(city_data)

        print(
            f"{city}: "
            f"{len(city_data)} timestamps loaded"
        )

    except Exception as e:

        print(
            f"Error loading {city}: {e}"
        )


if not all_data:
    raise FileNotFoundError(
        "No CSV files were loaded. "
        f"Please check that the CSV files exist in: {DATA_DIR}"
    )

master_df = pd.concat(
    all_data,
    ignore_index=True
)


# ============================================================
# MACHINE LEARNING
# ============================================================

FEATURES = [
    "pm25",
    "pm10",
    "no2",
    "so2",
    "co",
    "o3",
    "temperature",
    "relativehumidity",
    "wind_speed",
    "wind_direction"
]


ml_data = master_df.dropna(
    subset=FEATURES + ["AQI"]
).copy()


X = ml_data[FEATURES]
y = ml_data["AQI"]


model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    max_depth=12
)


# Train/test split
if len(ml_data) >= 10:

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    r2 = r2_score(
        y_test,
        predictions

    )

else:

    model.fit(X, y)

    mae = 0
    r2 = 0


print("\n================================")
print("AIR QUALITY ML MODEL")
print("================================")

print("Training records:", len(ml_data))
print("Features:", len(FEATURES))
print("MAE:", round(mae, 2))
print("R²:", round(r2, 2))


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ============================================================
# CITY LIST
# ============================================================

@app.route("/api/cities")
def cities():

    return jsonify(
        list(CSV_FILES.keys())
    )


# ============================================================
# CITY DATA
# ============================================================

@app.route("/api/city/<city>")
def city_data(city):

    if city not in CSV_FILES:

        return jsonify({
            "error": "City not found"
        }), 404

    data = master_df[
        master_df["City"] == city
    ].copy()

    data = data.sort_values(
        "datetimeLocal"
    )

    valid = data.dropna(
        subset=["AQI"]
    )

    if valid.empty:

        return jsonify({
            "error": "No AQI data available"
        }), 404

    latest = valid.iloc[-1]

    history = valid.tail(20)

    history_data = []

    for _, row in history.iterrows():

        history_data.append({
            "time": row["datetimeLocal"],
            "aqi": round(float(row["AQI"]))
        })

    return jsonify({

        "city": city,

        "state": "Andhra Pradesh",

        "aqi": round(
            float(latest["AQI"])
        ),

        "level": latest["AQI_Level"],

        "temperature": round(
            float(latest["temperature"]), 1
        ) if not pd.isna(
            latest["temperature"]
        ) else None,

        "humidity": round(
            float(latest["relativehumidity"]), 1
        ) if not pd.isna(
            latest["relativehumidity"]
        ) else None,

        "wind_speed": round(
            float(latest["wind_speed"]), 2
        ) if not pd.isna(
            latest["wind_speed"]
        ) else None,

        "wind_direction": round(
            float(latest["wind_direction"]), 1
        ) if not pd.isna(
            latest["wind_direction"]
        ) else None,

        "pm25": round(
            float(latest["pm25"]), 2
        ),

        "pm10": round(
            float(latest["pm10"]), 2
        ),

        "history": history_data

    })


# ============================================================
# ML PREDICTION
# ============================================================

@app.route("/api/predict", methods=["POST"])
def predict():

    data = request.json

    try:

        values = [
            float(data["pm25"]),
            float(data["pm10"]),
            float(data["no2"]),
            float(data["so2"]),
            float(data["co"]),
            float(data["o3"]),
            float(data["temperature"]),
            float(data["relativehumidity"]),
            float(data["wind_speed"]),
            float(data["wind_direction"])
        ]

        prediction = model.predict(
            [values]
        )[0]

        prediction = max(
            0,
            min(500, prediction)
        )

        prediction = round(
            prediction
        )

        level = get_aqi_level(
            prediction
        )

        return jsonify({

            "predicted_aqi": prediction,

            "level": level

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 400


# ============================================================
# MODEL INFORMATION
# ============================================================

@app.route("/api/model")
def model_info():

    return jsonify({

        "algorithm": "Random Forest Regression",

        "training_records": len(ml_data),

        "features": FEATURES,

        "mae": round(
            float(mae), 2
        ),

        "r2": round(
            float(r2), 2
        )

    })


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )