#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""Read a CLDF Lexibank data set into WordCorr.

Take a data set as Lexibank uses it, and convert it into an XML file
in the format used for WordCorr backup/exchange.

"""

import sys
import argparse

import csv
import json

from tsv2wordcorr import write_xml


def read_language_metadata(tsvfile):
    """Read varieties metadata from a tsv file.

    Read a TSV file containing language metadata in specific columns,
    and convert it into the list-of-dicts format expected by
    write_xml.

    """

    varieties = []
    for variety in csv.DictReader(tsvfile, sep="\t"):
        varieties.append({
            "ethnologue": variety["ISO_code"],
            "name": variety["Language name (-dialect)"],
            "shortname": variety["Language name (-dialect)"].split("-")[-1],
            "abbr": variety["Language ID"],
            "genclass": variety["Family"],
            "quality": '',
            "altname": '',
            "locale": '{:f}, {:f}'.format(variety["Lat"],
                                          variety["Lon"]),
            "collection_country": variety["Region"],
            "collection_location": '',
            "collector": '',
            "collection_date": '',
            "unpub": '',
            "source": '',
            "remarks": variety["Comments"]})
    return varieties


def read_collection_metadata(jsonfile):
    metadata = json.load(jsonfile)
    [
        "creatorrole",
        "contributor",
        "glosslg",
        "lgcode1",
        "glosslg2",
        "lgcode2",
        "keywords",
        "description",
        "remarks",
        "published",
        "coverage",
        "stable",
        "rights",
        "copyright"]
    return metadata


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__)
    parser.add_argument(
        "data", type=argparse.FileType("r"),
        default=sys.stdin,
        help="""The file containing all data""")
    parser.add_argument(
        "collection", type=argparse.FileType("r"),
        default=sys.stdin,
        help="""The json file containing the collection metadata""")
    parser.add_argument(
        "languages", type=argparse.FileType("r"),
        default=sys.stdin,
        help="""The tsv file containing the languages metadata""")
    parser.add_argument(
        "output", type=argparse.FileType("w"), nargs="?",
        default=sys.stdout,
        help="Path of the xml file to be written")
    parser.add_argument(
        "--username", default="N., N.",
        help="Your name, in the format 'SURNAME, GIVENNAME'")
    args = parser.parse_args()

    surname, givenname = map(str.strip, args.username.split(","))
    user_data = {
        "id": givenname[0] + surname[0],
        "famname": surname,
        "name": givenname,
        "affiliations": "None",
        "email": givenname + "@None"}

    collection_data = read_collection_metadata(args.collection)

    varietyproperties = read_language_metadata(args.languages)

    entries, gloss1, gloss2, data = ...

    write_xml(args.ouput, user_data, collection_data, varietyproperties,
              entries, gloss1, gloss2, data)
