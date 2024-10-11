import streamlit as st
import polars as pl
import requests
import altair as alt
import matplotlib as mp
import matplotlib.pyplot as plt

st.markdown("# Das heutige Weltraumwetter")


@st.cache_data
def load_solar_indices():
    response = requests.get(
        "https://kp.gfz-potsdam.de/app/files/Kp_ap_Ap_SN_F107_nowcast.txt"
    )
    return pl.read_csv(skip_rows=40, source=response.content, has_header=False).select(
        (pl.nth(0).str.slice(0, 10).str.to_date("%Y %m %d").alias("Datum")),
        (
            pl.nth(0)
            .str.slice(130, 4)
            .str.strip_chars()
            .alias("Ap")
            .cast(pl.Int32)
            .replace(-1, None)
        ),
        (
            pl.nth(0)
            .str.slice(139, 8)
            .str.strip_chars()
            .alias("F10.7adj")
            .cast(pl.Decimal)
            .replace(-1, None)
        ),
        (
            pl.nth(0)
            .str.slice(135, 3)
            .str.strip_chars()
            .alias("SN")
            .cast(pl.Int32)
            .replace(-1, None)
        ),
        (
            pl.nth(0)
            .str.slice(33, 6)
            .str.strip_chars()
            .alias("Kp1")
            .cast(pl.Decimal)
            .replace(-1, None)
        ),
        (
            pl.nth(0)
            .str.slice(40, 6)
            .str.strip_chars()
            .alias("Kp2")
            .cast(pl.Decimal)
            .replace(-1, None)
        ),
        (
            pl.nth(0)
            .str.slice(47, 6)
            .str.strip_chars()
            .alias("Kp3")
            .cast(pl.Decimal)
            .replace(-1, None)
        ),
        (
            pl.nth(0)
            .str.slice(54, 6)
            .str.strip_chars()
            .alias("Kp4")
            .cast(pl.Decimal)
            .replace(-1, None)
        ),
        (
            pl.nth(0)
            .str.slice(61, 6)
            .str.strip_chars()
            .alias("Kp5")
            .cast(pl.Decimal)
            .replace(-1, None)
        ),
        (
            pl.nth(0)
            .str.slice(68, 6)
            .str.strip_chars()
            .alias("Kp6")
            .cast(pl.Decimal)
            .replace(-1, None)
        ),
        (
            pl.nth(0)
            .str.slice(75, 6)
            .str.strip_chars()
            .alias("Kp7")
            .cast(pl.Decimal)
            .replace(-1, None)
        ),
        (
            pl.nth(0)
            .str.slice(82, 6)
            .str.strip_chars()
            .alias("Kp8")
            .cast(pl.Decimal)
            .replace(-1, None)
        ),
    )


solar_indices = load_solar_indices()

Ap = solar_indices["Ap"].drop_nulls().item(-1)
Ap_chg = Ap - solar_indices["Ap"].drop_nulls().item(-2)

F107 = solar_indices["F10.7adj"].drop_nulls().item(-1)
F107_chg = F107 - solar_indices["F10.7adj"].drop_nulls().item(-2)

Kp_indices = solar_indices.select(
    pl.concat_list([f"Kp{i}" for i in range(1, 9)]).alias("Kp").flatten(),
    pl.repeat(list(range(1, 9)), len(solar_indices)).alias("Index").flatten(),
).drop_nulls()
Kp = Kp_indices["Kp"].item(-1)


col1, col2 = st.columns(2)
col1.metric("Ap-Index heute: ", float(Ap), float(Ap_chg))
col2.metric("F10.7-Wert:", float(F107), float(F107_chg))

col3, col4 = st.columns(2)
with col3.expander("Was ist der Ap-Index?"):
    st.write(
        "Der Ap-Index liefert einen täglichen Durchschnittswert für die geomagnetische Aktivität. Der Durchschnitt aus 8 täglichen a-Werten ergibt den Ap-Index eines bestimmten Tages."
    )
    st.write(
        "Quelle: https://www.spaceweatherlive.com/de/hilfe/was-ist-der-ap-index.html"
    )

with col4.expander("Was ist der F10.7-Wert?"):
    st.write(
        "Der solare Radiofluss bei 10,7 cm (2800 MHz) ist ein ausgezeichneter Indikator für die Sonnenaktivität. Die F10.7-Radioemissionen entstehen hoch in der Chromosphäre und tief in der Korona der Sonnenatmosphäre."
    )
    st.write(
        "Quelle:https://www-swpc-noaa-gov.translate.goog/phenomena/f107-cm-radio-emissions?_x_tr_sl=en&_x_tr_tl=de&_x_tr_hl=de&_x_tr_pto=rq"
    )
data = pl.DataFrame({"a": ["A"], "b": [float(Kp)]})


def inferno_color(value):
    normalized_value = value / 9.5
    colormap = plt.get_cmap("YlOrRd")
    Farbe = colormap(normalized_value)
    return mp.colors.rgb2hex(Farbe[:3])


st.subheader("Kp-Index:")
chart = (
    alt.Chart(data)
    .mark_bar(color=inferno_color(float(Kp)))
    .encode(
        x=alt.X("a", axis=None),
        y=alt.Y("b", axis=alt.Axis(title=None), scale=alt.Scale(domain=[0, 9.5])),
    )
    .properties(width=150)
    .configure_view(stroke="black", strokeWidth=2)
)


image_url = "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIIC.jpg"

col5, col6 = st.columns(2)
col5.altair_chart(chart)
col6.image(image_url, caption="Das aktuelle Sonnenfoto", width=330)
col7, col8 = st.columns(2)
with col7.expander("Was ist der Kp-Index?"):
    st.write(
        "Der dreistündige geomagnetische Kp-Index wurde 1949 von Julius Bartels eingeführt, um die solare Teilchenstrahlung über ihre magnetischen Effekte zu messen. Heute ist Kp ein wichtiges Maß für den Energieeintrag aus dem Sonnenwind in das System Erde und wird in Echtzeit für viele Weltraumwetterdienste genutzt."
    )
    st.write("Quelle:https://kp.gfz-potsdam.de/")
image_url = "https://impc.dlr.de/SWE/Total_Electron_Content/TEC_Near_Real-Time/DLR_GNSS_GCG_L4_VTEC-NTCM-SCM_NC_GLOBAL/v2.0.0/latest/DLR_GNSS_GCG_L4_VTEC-NTCM-SCM_NC_GLOBAL_latest_I.png"
st.image(image_url)
st.write("Datenquellen:")
st.write(
    "https://impc.dlr.de/products/total-electron-content/near-real-time-tec/near-real-time-tec-maps-global"
)
st.write("https://kp.gfz-potsdam.de/")
st.write("https://sdo.gsfc.nasa.gov/data/")
