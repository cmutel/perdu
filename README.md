# Perdu

Python library and webapp for matching against standard industry and product classifiers. Comes with NAICS, GS1, and USEEIO built-in.

[![Build Status](https://travis-ci.org/cmutel/perdu.svg?branch=master)](https://travis-ci.org/cmutel/perdu) [![Build status](https://ci.appveyor.com/api/projects/status/46fi2vroxh6rruka?svg=true)](https://ci.appveyor.com/project/cmutel/perdu) [![Coverage Status](https://coveralls.io/repos/github/cmutel/perdu/badge.svg?branch=master)](https://coveralls.io/github/cmutel/perdu?branch=master)

## Installation

Install using pip or conda:

    conda -c conda-forge -c cmutel perdu

-or-

    pip install perdu

Depends on:

* appdirs
* docopt
* flask
* peewee
* rdflib
* rdflib-jsonld
* whoosh

## Usage

As a webapp:

    conda_webapp

As a library:

    import perdu
    perdu.search_useeio("plastic toy")

# Search basics

Perdu uses [whoosh](https://whoosh.readthedocs.io/en/latest/intro.html) as the search engine. When you first import it, Perdu will import the three built-in catalogues in around one minute.

## Built-in catalogues

* [NAICS](https://www.census.gov/eos/www/naics/)
* [GS1 GPC](https://www.gs1.org/standards/gpc)
* [US 2014 EEIO](https://cfpub.epa.gov/si/si_public_record_report.cfm?Lab=NRMRL&dirEntryId=336332)

## Uploading data

Currently, the only possibility to upload data to the web interface is via CSV, with the first column being the item name or title, and the second (optional) column being the item description. See `perdu.test.fixtures` for examples.

## Adding other catalogues

See the files in `perdu.extraction` for examples on how to extract data from PDFs (NAICS), XML (GS1), and JSON (USEEIO). Each search catalogue will have its own schema, but Perdu expects these schemas to have at least the columns `name`, `description`, and `code` (see examples in `perdu.searching`). New catalogues will need to have suitable functions provided in `perdu.webapp.search_mapping`.

## Advanced searching

In addition to the default search method used in the web interface, Perdu also offers [search corrections](https://whoosh.readthedocs.io/en/latest/spelling.html) (`search_corrector_gs1`, `search_corrector_naics`, and `search_corrector_useeio`) and [disjunction maximization](https://whoosh.readthedocs.io/en/latest/api/qparser.html?highlight=dismaxparser#whoosh.qparser.DisMaxParser) (`search_gs1_disjoint`, `search_useeio_disjoint`, and `search_naics_disjoint`).
