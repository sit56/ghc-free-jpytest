# USD/JPY Daily Chart

A small static dashboard that tracks the daily USD/JPY reference rate. GitHub
Actions fetches the latest available rate and commits it to
`data/usd-jpy.json`; GitHub Pages serves the chart from `docs/`.

## Setup

1. In the repository, open **Settings → Pages** and choose **GitHub Actions**
   as the build and deployment source.
2. Run **Actions → Update USD/JPY rate → Run workflow** to collect the first
   observation. Subsequent runs happen automatically at 00:15 UTC (09:15 JST).

The provider may publish rates later than the scheduled time. The workflow
records the effective date returned by the provider and skips the run when
that date is already present.

## Data source and meaning

Rates come from the public [Frankfurter API](https://www.frankfurter.dev/), which
requires no API key. Each observation is the provider's USD-to-JPY reference
rate for its effective date, not a live or executable market quote. Rates are
stored in ascending date order in `data/usd-jpy.json`.

## Tests

Run the data updater tests with:

```sh
python3 -m unittest discover -s tests -v
```
