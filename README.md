# Introduction

Given a background and specified ayahs, create a "poster" with English and Arabic.

![data/03_primary/quran_poster.png]

# Related work

# Setup

Create a virtual environment, e.g. through `conda`. Then install requirements.

`conda create --name qenv python=3.12`
`conda activate qenv`
`pip install -r requirements.txt`

# Usage

1. Select a background and save in `data/01_raw` folder.

2. Change `conf/base/catalog.yml` -> background image file path and save.

3. Change settings in `conf/base/parameters.yml`

4. In terminal or command line, `cd quran-poster` and `kedro run`

5. See output in `data/03_primary/quran_poster.jpg`

# Update log

2025-04-27: first version