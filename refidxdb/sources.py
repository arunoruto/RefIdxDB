"""Internal registry of downloadable database sources.

Imported by the CLI and the Streamlit app so the name-to-class mapping lives in
one place. This is an internal module; external users go through the public API
in ``refidxdb/__init__.py``.
"""

from refidxdb.url.aria import Aria
from refidxdb.url.refidx import RefIdx

DATABASES = {cls.__name__.lower(): cls for cls in (Aria, RefIdx)}
