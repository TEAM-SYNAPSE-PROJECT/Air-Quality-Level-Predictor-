import pandas as pd

# =========================================
# STEP 1: LOAD DATASET
# =========================================

df = pd.read_csv("air quality guntur.csv")

print("\n========== ORIGINAL DATASET ==========")
print(df.head())

print("\nColumn Names:")
print(df.columns)

print("\nDataset Size:")
print(df.shape)


# =========================================
# STEP 2: BASIC INFORMATION
# =========================================

print("\nParameters Available:")
print(df["parameter"].unique())

print("\nDate Range:")
print("Start:", df["datetimeLocal"].min())
print("End:", df["datetimeLocal"].max())

print("\nNumber of unique timestamps:")
print(df["datetimeLocal"].nunique())


# =========================================
# STEP 3: RESHAPE DATA
# =========================================

df_wide = df.pivot(
    index="datetimeLocal",
    columns="parameter",
    values="value"
).reset_index()

print("\n========== RESHAPED DATASET ==========")
print(df_wide.head())


# =========================================
# STEP 4: SELECT FEATURES
# Pollution + Weather + Wind
# =========================================

required_columns = [
    "datetimeLocal",

    # Pollution
    "pm25",
    "pm10",
    "no2",
    "so2",
    "co",
    "o3",

    # Other pollution information
    "no",

    # Weather
    "temperature",
    "relativehumidity",

    # Wind
    "wind_speed",
    "wind_direction"
]

df_final = df_wide[required_columns].copy()

print("\n========== FINAL DATASET ==========")
print(df_final.head())


# =========================================
# STEP 5: CHECK MISSING VALUES
# =========================================

print("\n========== MISSING VALUES ==========")
print(df_final.isnull().sum())


# =========================================
# STEP 6: REMOVE ROWS WITH MISSING
# POLLUTANT VALUES FOR AQI CALCULATION
# =========================================

aqi_pollutants = [
    "pm25",
    "pm10",
    "no2",
    "so2",
    "co",
    "o3"
]

df_aqi = df_final.dropna(
    subset=aqi_pollutants
).copy()

print("\n========== AFTER AQI CLEANING ==========")
print("Rows before cleaning:", len(df_final))
print("Rows after cleaning:", len(df_aqi))
print("Rows removed:", len(df_final) - len(df_aqi))


# =========================================
# STEP 7: AQI SUB-INDEX FUNCTION
# =========================================

def calculate_sub_index(concentration, breakpoints):

    for low_conc, high_conc, low_aqi, high_aqi in breakpoints:

        if low_conc <= concentration <= high_conc:

            aqi = (
                (high_aqi - low_aqi)
                / (high_conc - low_conc)
            ) * (concentration - low_conc) + low_aqi

            return aqi

    return None


# =========================================
# STEP 8: AQI BREAKPOINTS
# =========================================

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


# =========================================
# STEP 9: CALCULATE SUB-INDICES
# =========================================

df_aqi["PM25_AQI"] = df_aqi["pm25"].apply(
    lambda x: calculate_sub_index(
        x, pm25_breakpoints
    )
)

df_aqi["PM10_AQI"] = df_aqi["pm10"].apply(
    lambda x: calculate_sub_index(
        x, pm10_breakpoints
    )
)

df_aqi["NO2_AQI"] = df_aqi["no2"].apply(
    lambda x: calculate_sub_index(
        x, no2_breakpoints
    )
)

df_aqi["SO2_AQI"] = df_aqi["so2"].apply(
    lambda x: calculate_sub_index(
        x, so2_breakpoints
    )
)

df_aqi["CO_AQI"] = df_aqi["co"].apply(
    lambda x: calculate_sub_index(
        x, co_breakpoints
    )
)

df_aqi["O3_AQI"] = df_aqi["o3"].apply(
    lambda x: calculate_sub_index(
        x, o3_breakpoints
    )
)


# =========================================
# STEP 10: CALCULATE OVERALL AQI
# =========================================

aqi_columns = [
    "PM25_AQI",
    "PM10_AQI",
    "NO2_AQI",
    "SO2_AQI",
    "CO_AQI",
    "O3_AQI"
]

df_aqi["AQI"] = df_aqi[aqi_columns].max(axis=1)


# =========================================
# STEP 11: ROUND AQI
# =========================================

df_aqi["AQI"] = df_aqi["AQI"].round().astype(int)


# =========================================
# STEP 12: AQI LEVEL
# =========================================

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

    else:
        return "Severe"


df_aqi["AQI_Level"] = df_aqi["AQI"].apply(
    get_aqi_level
)


# =========================================
# STEP 13: DISPLAY AQI RESULTS
# =========================================

print("\n========== AQI RESULTS ==========")

print(
    df_aqi[
        [
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
            "AQI",
            "AQI_Level"
        ]
    ].head(10)
)


# =========================================
# STEP 14: FINAL DATASET INFORMATION
# =========================================

print("\n========== FINAL INFORMATION ==========")

print("Final number of rows:", len(df_aqi))

print("Final number of columns:", len(df_aqi.columns))

print("\nFinal columns:")
print(df_aqi.columns.tolist())