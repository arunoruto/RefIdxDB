import re
from io import StringIO
from pathlib import Path
from shutil import copy

import numpy as np
import plotly.graph_objects as go
import polars as pl
import streamlit as st

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

files = {
    item.__name__.lower(): item
    for item in [
        DAT,
    ]
}

st.set_page_config(layout="wide")
st.title("RefIdxDB")


# def load_new_file():
#     with st.spinner("Please wait.. loading the file"):
#         new_file = st.session_state["uploaded_file"]
#         bytes_data = new_file.read()
#         print(bytes_data)
#         # upload_file_to_blob(STORAGE_CONNECTION_STRING, STORAGE_CONTAINER_NAME, "app_data/"+new_file.name, bytes_data)
#         # st.session_state.document_url = get_blob_sas_url(STORAGE_CONNECTION_STRING, STORAGE_CONTAINER_NAME, "app_data/"+new_file.name)
#     return


db = st.radio(
    "Database",
    list(databases.keys()) + ["Upload"],
)

if db == "Upload":
    file = st.file_uploader(
        "Upload file",
        type=["csv", "txt", "ri", "dat"],
        label_visibility="collapsed",
        accept_multiple_files=False,
        key="uploaded_file",
        # on_change=load_new_file,
    )
    if file is None:
        st.stop()
    name = file.name
    content = file.getvalue().decode("utf-8")
    file = StringIO(content)
    match name.split(".")[-1]:
        case "dat" | "ri":
            db_class = files["dat"]
            # st.write(np.loadtxt(StringIO(content)))
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

wavelength = st.toggle("Wavenumber / Wavelength", True)
logx = st.checkbox("Log x-axis", False)
logy = st.checkbox("Log y-axis", False)

with st.expander("Full file path"):
    st.write(file)

scale = 1e-6 if wavelength else 1e2
name = {True: "Wavelength", False: "Wavenumber"}
suffix = {True: "μm", False: "cm⁻¹"}

data = db_class(path=file, wavelength=wavelength)
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
# st.table(nk.select(pl.all().cast(pl.Utf8)))
