import re
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import polars as pl
import streamlit as st

from refidxdb import databases

st.set_page_config(layout="wide")
st.title("RefIdxDB")

db = st.radio(
    "Database",
    list(databases.keys()),
)
cache_dir = databases[db]().cache_dir
files = [str(item) for item in Path(cache_dir).rglob("*") if item.is_file()]
if db == "refidx":
    files = [item for item in files if re.search(r"/data-nk", item)]
file = st.selectbox(
    "File",
    files,
    format_func=lambda x: "/".join(x.replace(cache_dir, "").split("/")[2:]),
)

wavelength = st.toggle("Wavenumber / Wavelength", True)
logx = st.checkbox("Log x-axis", False)
logy = st.checkbox("Log y-axis", False)

with st.expander("Full file path"):
    st.write(file)

scale = 1e-6 if wavelength else 1e2
name = {True: "Wavelength", False: "Wavenumber"}
suffix = {True: "μm", False: "cm⁻¹"}

data = databases[db](path=file, wavelength=wavelength)
nk = data.nk.with_columns(pl.col("w").truediv(scale))

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=nk["w"],
        y=nk["n"],
        name="n",
    )
)
fig.add_trace(
    go.Scatter(
        x=nk["w"],
        y=nk["k"],
        name="k",
        # xaxis="x2",
    )
)
fig.update_layout(
    xaxis=dict(
        title=f"{name[wavelength]} in {suffix[wavelength]}",
        type="log" if logx else "linear",
        ticksuffix=suffix[wavelength],
    ),
    yaxis=dict(
        title="Values",
        type="log" if logy else "linear",
    ),
    # xaxis2=dict(
    #     title=f"{name[not wavelength]}",
    #     anchor="y",
    #     overlaying="x",
    #     side="top",
    #     autorange="reversed",
    #     # tickvals=nk["w"],
    #     # ticktext=np.round(1e4 / nk["w"], decimals=-2),
    #     ticksuffix=suffix[not wavelength],
    # ),
)
fig.update_traces(connectgaps=True)
st.plotly_chart(fig, use_container_width=True)
st.table(nk.select(pl.all().cast(pl.Utf8)))
