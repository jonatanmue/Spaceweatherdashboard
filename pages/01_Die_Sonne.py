import streamlit as st
import polars as pl
import requests
import altair as alt
import datetime as dt

st.markdown("# Die Sonne")


@st.cache_data
def anzahl_der_sonnenflecken():
    response = requests.get("https://www.sidc.be/SILSO/INFO/sndtotcsv.php")
    return (
        pl.read_csv(
            response.content,
            separator=";",
            has_header=False,
            schema_overrides=[pl.Int64, pl.Int64, pl.Int64, pl.Float32, pl.Int64],
            new_columns=[
                "Jahr",
                "Monat",
                "Tag",
                "Anteil_des_Jahres",
                "Sunspotnumber",
                "Deviation",
                "Nummer der Beobachtungen",
                "Indikator",
            ],
        )
        .select(
            pl.date(pl.col("Jahr"), pl.col("Monat"), pl.col("Tag")),
            pl.col("Sunspotnumber").replace(-1, None),
            pl.col("Nummer der Beobachtungen"),
        )
        .filter(pl.col("date").dt.year() > 1849)
    )


Anzahl = anzahl_der_sonnenflecken()

chart = (
    alt.Chart(
        Anzahl.rolling(index_column="date", period="81d").agg(
            pl.mean("Sunspotnumber").alias("durchschnittliche Sonnenfleckenanzahl")
        )
    )
    .mark_line()
    .encode(x="date", y="durchschnittliche Sonnenfleckenanzahl")
    .properties(title="Diagramm der Sonnenflecken")
)

st.altair_chart(chart, use_container_width=True)
current_date = dt.datetime.now()
aktuelles_datum = st.date_input(
    "Datum auswählen", min_value=dt.datetime(1850, 1, 1), max_value=current_date
)
line_chart = (
    alt.Chart(
        Anzahl.rolling(index_column="date", period="27d")
        .agg(pl.mean("Sunspotnumber").alias("durchschnittliche Sonnenfleckenanzahl"))
        .filter(
            pl.col("date").is_between(
                aktuelles_datum - dt.timedelta(days=11 * 365),
                aktuelles_datum + dt.timedelta(days=11 * 365),
            )
        )
    )
    .mark_line()
    .encode(
        x=alt.X(
            "date:T",
        ),
        y="durchschnittliche Sonnenfleckenanzahl",
    )
)
st.altair_chart(line_chart, use_container_width=True)
with st.expander("Wie entstehen Sonnenflecken?"):
    st.write(
        "<p style='font-size: 12px;'>Ursache der Sonnenflecken sind Temperaturunterschiede auf der Sonnenoberfläche. Permanent wirbelt heiße Materie aus dem Inneren der Sonne an die Oberfläche. Diese so genannte Konvektion kann durch lokale Verstärkungen des Magnetfelds der Sonne behindert werden – etwas kältere Stellen auf der Sonnenoberfläche entstehen und werden als Sonnenflecken sichtbar.</p>",
        unsafe_allow_html=True,
    )
    st.write(
        "<p style='font-size: 12px;'>Quelle: https://www.dlr.de/next/desktopdefault.aspx/tabid-6554/10767_read-24305/</p>",
        unsafe_allow_html=True,
    )
    st.write(
        "<p style='font-size: 12px;'>Quelle der Sonnenfleckenanzahlen: https://www.sidc.be/SILSO/datafiles</p>",
        unsafe_allow_html=True,
    )
