import re
from io import StringIO
from pathlib import Path

import plotly.graph_objects as go
import polars as pl
import streamlit as st

from refidxdb.file.csv import CSV
from refidxdb.file.dat import DAT
from refidxdb.url.aria import Aria
from refidxdb.url.refidx import RefIdx

# from refidxdb import databases, files

# try:
#     from refidxdb.file.dat import DAT
#     from refidxdb.url.aria import Aria
#     from refidxdb.url.refidx import RefIdx
# except ImportError:
#     # If running outside of the refidxdb directory, add it to the path
#     import sys

#     root = Path(__file__).parent.absolute().as_posix()
#     print(root)
#     print(type(root))
#     sys.path.append(root)
#     from .file.dat import DAT
#     from .url.aria import Aria
#     from .url.refidx import RefIdx

databases = {
    item.__name__.lower(): item
    for item in [
        Aria,
        RefIdx,
    ]
}

st.set_page_config(layout="wide")
st.title("RefIdxDB")


db = st.radio(
    "Database",
    list(databases.keys()) + ["Upload"],
)

if db == "Upload":
    col1, col2 = st.columns([1, 3])
    file = col1.file_uploader(
        "Upload file",
        type=["csv", "txt", "ri", "dat"],
        label_visibility="collapsed",
        accept_multiple_files=False,
        key="uploaded_file",
        # on_change=load_new_file,
    )
    wavelength_file = col2.toggle("File: Wavenumber / Wavelength", True)
    scale_file = col2.number_input(
        "Exponent",
        value=-6 if wavelength_file else 2,
        format="%d",
        step=1,
        help="Scale for wavenumber to wavelength conversion. Default is 1e-2.",
    )
    scale_file = 10**scale_file
    col2.write(f"Sale: {scale_file:.0e}")

    if file is None:
        st.stop()
    name = file.name
    try:
        content = file.getvalue().decode("utf-8")
    except UnicodeError:
        print("Error decoding file content")
        print("Trying latin-1")
        content = file.getvalue().decode("latin-1")
    file = StringIO(content)
    match name.split(".")[-1]:
        case "dat" | "ri":
            db_class = DAT
            # st.write(np.loadtxt(StringIO(content)))
        case "csv":
            db_class = CSV
            # st.write(pl.read_csv(StringIO(content)))
        case _:
            st.write(file)
else:
    cache_dir = databases[db]().cache_dir
    files = [str(item) for item in Path(cache_dir).rglob("*") if item.is_file()]
    if db == "refidx":
        files = [item for item in files if re.search(r"/data-nk", item)]
    file = st.selectbox(
        "File",
        files,
        format_func=lambda x: "/".join(x.replace(cache_dir, "").split("/")[2:]),
    )
    db_class = databases[db]

wavelength = st.toggle("Plot: Wavenumber / Wavelength", True)
logx = st.checkbox("Log x-axis", False)
logy = st.checkbox("Log y-axis", False)

with st.expander("Full file path"):
    st.write(file)

if db == "Upload":
    data = db_class(
        path=file,
        wavelength=wavelength,
        w_column="wl" if wavelength_file else "wn",
        scale=scale_file,
    )
    # nk = data.nk.clone()
else:
    data = db_class(path=file, wavelength=wavelength)
scale = 1e-6 if wavelength else 1e2
nk = data.nk.clone().with_columns(pl.col("w").truediv(scale))
# nk = data.nk.clone()
# nk = data.nk.with_columns(pl.col("w").truediv(data.scale))

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
    )
)
fig.update_layout(
    xaxis=dict(
        title="Wavelength in μm" if wavelength else "Wavenumber in cm⁻¹",
        type="log" if logx else "linear",
        # ticksuffix=" (m)" if wavelength else " (m⁻¹)",
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
st.table(data.nk.select(pl.all().cast(pl.Utf8)))
