# Introduction

Given a background and specified ayahs, create a "poster" with English and Arabic.

# Related work

- [Quran image generator](https://github.com/ZeyadAbbas/quran-image-generator)
- [Quran.com images](https://github.com/quran/quran.com-images)
- [Quran companion](https://github.com/0xzer0x/quran-companion)
- [Indopak font](https://github.com/marwan/indopak-quran-text)

# Setup

Create a virtual environment, e.g. through `conda`. Then install requirements.

`conda create --name qenv python=3.12`

`conda activate qenv`

`pip install -r requirements.txt`

# Usage

## Changing parameter files

1. Select a background and save in `data/01_raw` folder.

2. Change `conf/base/catalog.yml` -> background image file path and save. Also change the output file path `quran_poster.jpg` if you want.

3. Change settings in `conf/base/parameters.yml`

4. In terminal or command line, `cd quran-poster` and `kedro run`

5. See output in `data/03_primary/quran_poster.jpg`

Alternatively, instead of using `base` yamls, create a new folder, and instead of `kedro run`, use `kedro run --env={folder}`

## CLI

## Examples

`kedro run --env=nur`

![nur](quran-poster/data/03_primary/quran_poster_nur.png)


`kedro run --env=mz`

![mz](quran-poster/data/03_primary/quran_poster_mz.png)


`kedro run --env=asr`

![asr](quran-poster/data/03_primary/quran_poster_asr.png)

`kedro run --env=kahf`

![asr](quran-poster/data/03_primary/quran_poster_kahf.png)


# Update log

- 2025-04-27: first version
- 2025-04-28: bug fixes and examples