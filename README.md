<!-- PROJECT SHIELDS -->
[![PyPI version][pypi-shield]][pypi-url]
[![Codecov][codecov-shield]][codecov-url]
[![DeepSource][deepsource-shield]][deepsource-url]
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

<!-- PROJECT LOGO -->
<p align="center">
  <img src="https://github.com/arunoruto/RefIdxDB/blob/main/.github/logo.png?raw=true" alt="RefIdxDB Logo"/>
</p>

<div align="center">

<h3 align="center">RefIdxDB</h3>

  <p align="center">
    Python interface for various refractive index databases
    <br />
    <a href="https://pypi.org/project/refidxdb/"><strong>Explore on PyPI »</strong></a>
    <br />
    <br />
    <a href="https://github.com/arunoruto/RefIdxDB/issues/new?labels=bug">Report Bug</a>
    &middot;
    <a href="https://github.com/arunoruto/RefIdxDB/issues/new?labels=enhancement">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#built-with">Built With</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li>
      <a href="#usage">Usage</a>
      <ul>
        <li><a href="#cli">CLI</a></li>
        <li><a href="#api">API</a></li>
      </ul>
    </li>
    <li><a href="#supported-databases">Supported Databases</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

Downloading and parsing refractive index databases from various sources is tedious — each database has its own format, conventions, and quirks. RefIdxDB unifies multiple databases under a single API so you can query any supported database the same way.

> If your source is not implemented, feel free to open an issue! You can also try to implement it yourself. Take `refidx` and `aria` as a reference on what needs to be implemented.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- BUILT WITH -->
## Built With

* [![Python][python-shield]][python-url]
* [![Pydantic][pydantic-shield]][pydantic-url]
* [![Polars][polars-shield]][polars-url]
* [![NumPy][numpy-shield]][numpy-url]
* [![Rich][rich-shield]][rich-url]
* [![Plotly][plotly-shield]][plotly-url]
* [![Streamlit][streamlit-shield]][streamlit-url]
* [![uv][uv-shield]][uv-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

RefIdxDB requires Python 3.10 or later.

### Installation

```sh
pip install refidxdb
```

After installation, the `refidxdb` command is available in your terminal.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE -->
## Usage

### CLI

The main purpose of the CLI is to download and cache databases locally and interact with the data. Data is stored under `$HOME/.cache/refidxdb` in a folder named after the database class. Use `refidxdb --help` to explore all functionality.

**Download all databases:**

```console
$ refidxdb db --download all
Downloading the database for RefIdx from https://github.com/polyanskiy/refractiveindex.info-database/releases/download/v2024-08-14/rii-database-2024-08-14.zip to /home/mar/.cache/refidxdb/RefIdx
Downloading the database for Aria from https://eodg.atm.ox.ac.uk/ARIA/data_files/ARIA.zip to /home/mar/.cache/refidxdb/Aria
All databases downloaded!
Bye :)
```

**Display data in table or graph form:**

```console
$ refidxdb show --db aria --data "data_files/Minerals/Olivine/z_orientation_(Fabian_et_al._2001)/olivine_Z_Fabian_2001.ri" --display table --bounds 2.5,15.5
shape: (2_748, 3)
┌───────────┬──────────┬──────────┐
│ w         ┆ n        ┆ k        │
│ ---       ┆ ---      ┆ ---      │
│ f64       ┆ f64      ┆ f64      │
╞═══════════╪══════════╪══════════╡
│ 2.500617  ┆ 1.619696 ┆ 0.000053 │
│ 2.501381  ┆ 1.619685 ┆ 0.000053 │
│ 2.502144  ┆ 1.619674 ┆ 0.000053 │
│ 2.502909  ┆ 1.619663 ┆ 0.000053 │
│ 2.503674  ┆ 1.619652 ┆ 0.000053 │
│ …         ┆ …        ┆ …        │
│ 15.369648 ┆ 1.42662  ┆ 0.036282 │
│ 15.398545 ┆ 1.419686 ┆ 0.036761 │
│ 15.427528 ┆ 1.412672 ┆ 0.037256 │
│ 15.456643 ┆ 1.405576 ┆ 0.037768 │
│ 15.485869 ┆ 1.398394 ┆ 0.038299 │
└───────────┴──────────┴──────────┘
```

> Replace `--display table` with `--display plot` to view a terminal graph of the data.

**Explore databases interactively with Streamlit:**

```console
$ refidxdb explore

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://10.42.42.212:8501
```

### API

`RefIdxDB` is the blueprint class from which all database parsers inherit, providing a unified API. Every instance exposes the same methods:

`path` — the path to a file within the database (typically copied from the URL).

`data` — the raw content of the file at `path`.

`nk` — parsed real (`n`) and imaginary (`k`) parts of the refractive index, with wavelength as the index column (wave numbers are automatically converted).

`interpolate` — computes `n` and `k` at a target wavelength using interpolation.

> Only wavelengths are currently supported. If you have a proposal for adding wave-number support, please submit an issue or PR.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- SUPPORTED DATABASES -->
## Supported Databases

### [refractiveindex.info](https://refractiveindex.info/)

`refractiveindex.info` provides raw tabulated data (wavelengths in micrometers) and polynomial formulas valid over specified ranges. Data is stored in YAML files.

Supported data types:
- `tabulated_nk`
- `tabulated_n`
- `tabulated_k`
- `formula 1`
- `formula 2`
- `formula 3`

### [ARIA — Aerosol Refractive Index Archive](https://eodg.atm.ox.ac.uk/ARIA/)

ARIA uses `.ri` files with whitespace-separated values and `#`-prefixed headers. The `FORMAT` value specifies column labels. Both `WAVL` (wavelengths) and `WAVN` (wave numbers) are parsed and normalized to wavelengths in meters. Default units are 1e-6 m (micrometers) for wavelengths and 1e2 m⁻¹ (cm⁻¹) for wave numbers.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->
## Roadmap

- [x] URL-encoded characters in ARIA paths
- [x] Fix `refidx` data-nk parsing for mono.yml entries
- [ ] Additional database sources
- [ ] Wavelength-range filtering
- [ ] Wave-number support

See the [open issues](https://github.com/arunoruto/RefIdxDB/issues) for a full list of proposed features and known issues.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

Contributions are welcome! If you have a suggestion or fix:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'feat: add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Mirza Arnaut — [@arunoruto](https://github.com/arunoruto) — mirza.arnaut45@gmail.com

Project Link: [https://github.com/arunoruto/RefIdxDB](https://github.com/arunoruto/RefIdxDB)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

RefIdxDB is, to the best of my knowledge, the only project that unifies multiple refractive-index databases under one API. Similar work for single databases:

* [refractiveindex](https://pypi.org/project/refractiveindex/)
* [PyTMM](https://github.com/kitchenknif/PyTMM)
* [PyOptik](https://github.com/MartinPdeS/PyOptik)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<a id="readme-top"></a>

[pypi-shield]: https://img.shields.io/pypi/v/refidxdb?style=for-the-badge
[pypi-url]: https://pypi.org/project/refidxdb/
[codecov-shield]: https://codecov.io/gh/arunoruto/RefIdxDB/graph/badge.svg?token=NQEJ466GGK
[codecov-url]: https://codecov.io/gh/arunoruto/RefIdxDB
[deepsource-shield]: https://app.deepsource.com/gh/arunoruto/RefIdxDB.svg/?label=code+coverage&show_trend=true&token=6OxGvsq00pW0X5nKcAmq0vOQ
[deepsource-url]: https://app.deepsource.com/gh/arunoruto/RefIdxDB/
[contributors-shield]: https://img.shields.io/github/contributors/arunoruto/RefIdxDB.svg?style=for-the-badge
[contributors-url]: https://github.com/arunoruto/RefIdxDB/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/arunoruto/RefIdxDB.svg?style=for-the-badge
[forks-url]: https://github.com/arunoruto/RefIdxDB/network/members
[stars-shield]: https://img.shields.io/github/stars/arunoruto/RefIdxDB.svg?style=for-the-badge
[stars-url]: https://github.com/arunoruto/RefIdxDB/stargazers
[issues-shield]: https://img.shields.io/github/issues/arunoruto/RefIdxDB.svg?style=for-the-badge
[issues-url]: https://github.com/arunoruto/RefIdxDB/issues
[license-shield]: https://img.shields.io/github/license/arunoruto/RefIdxDB.svg?style=for-the-badge
[license-url]: https://github.com/arunoruto/RefIdxDB/blob/main/LICENSE
[python-shield]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[python-url]: https://python.org/
[pydantic-shield]: https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white
[pydantic-url]: https://docs.pydantic.dev/
[polars-shield]: https://img.shields.io/badge/Polars-CD792C?style=for-the-badge&logo=polars&logoColor=white
[polars-url]: https://pola.rs/
[numpy-shield]: https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white
[numpy-url]: https://numpy.org/
[rich-shield]: https://img.shields.io/badge/Rich-FAE742?style=for-the-badge&logo=python&logoColor=black
[rich-url]: https://github.com/Textualize/rich
[plotly-shield]: https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white
[plotly-url]: https://plotly.com/python/
[streamlit-shield]: https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white
[streamlit-url]: https://streamlit.io/
[uv-shield]: https://img.shields.io/badge/uv-261230?style=for-the-badge&logo=uv&logoColor=white
[uv-url]: https://docs.astral.sh/uv/
