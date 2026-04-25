import streamlit as st
import requests
import pandas as pd
import json
from io import StringIO
import geopandas as gpd
import matplotlib.pyplot as plt

STATISTIKAAMETI_API_URL = "https://andmed.stat.ee/api/v1/et/stat/RV032"

JSON_PAYLOAD_STR =""" {
  "query": [
    {
      "code": "Aasta",
      "selection": {
        "filter": "item",
        "values": [
          "2014",
          "2015",
          "2016",
          "2017",
          "2018",
          "2019",
          "2020",
          "2021",
          "2022",
          "2023"
        ]
      }
    },
    {
      "code": "Maakond",
      "selection": {
        "filter": "item",
        "values": [
          "39",
          "44",
          "49",
          "51",
          "57",
          "59",
          "65",
          "67",
          "70",
          "74",
          "78",
          "82",
          "84",
          "86",
          "37"
        ]
      }
    },
    {
      "code": "Sugu",
      "selection": {
        "filter": "item",
        "values": [
          "2",
          "3"
        ]
      }
    }
  ],
  "response": {
    "format": "csv"
  }
}
"""

@st.cache_data
def import_data():
    headers = {"Content-Type": "application/json"}
    parsed_payload = json.loads(JSON_PAYLOAD_STR)

    response = requests.post(
        STATISTIKAAMETI_API_URL,
        json=parsed_payload,
        headers=headers
    )

    if response.status_code == 200:
        text = response.content.decode("utf-8-sig")
        return pd.read_csv(StringIO(text))
    else:
        st.error("Andmete laadimine ebaõnnestus")
        st.write(response.status_code)
        st.write(response.text)
        return None


st.title("Loomulik iive Eesti maakondades")

df = import_data()

if df is not None:
    df["Iive kokku"] = df["Mehed Loomulik iive"] + df["Naised Loomulik iive"]

    aasta = st.sidebar.selectbox(
        "Vali aasta",
        sorted(df["Aasta"].unique())
    )

    df_aasta = df[df["Aasta"] == aasta]

    st.subheader(f"Loomulik iive maakondades aastal {aasta}")
    st.dataframe(df_aasta)

    gdf = gpd.read_file("https://kangelane.eu/maakonnad.geojson")

    kaart = gdf.merge(df_aasta, left_on="MNIMI", right_on="Maakond")

    fig, ax = plt.subplots(figsize=(8, 8))
    kaart.plot(
        column="Iive kokku",
        ax=ax,
        legend=True,
        edgecolor="black"
    )

    ax.set_title(f"Loomulik iive maakonniti, {aasta}")
    ax.axis("off")

    st.pyplot(fig)
