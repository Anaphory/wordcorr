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
    for variety in csv.DictReader(tsvfile, dialect="excel-tab"):
        varieties.append({
            "ethnologue": variety["ISO_code"],
            "name": variety["Language name (-dialect)"].strip(),
            "shortname": variety["Language name (-dialect)"].split("-")[-1][:7].strip(),
            "abbr": variety["Language ID"].strip(),
            "genclass": variety["Family"],
            "quality": '',
            "altname": '',
            "locale": '{:}, {:}'.format(variety["Lat"],
                                        variety["Lon"]),
            "collection_country": variety["Region"],
            "collection_location": '',
            "collector": '',
            "collection_date": '',
            "unpub": '',
            "source": '',
            "remarks": variety["Comments"]})
    return varieties


def read_concept_metadata(tsvfile, glosses=["English", "Indonesian"]):
    """Read concept metadata from a tsv file.

    Read a TSV file containing concept metadata (in particular
    glosses) in specific columns, and convert it into the
    three-list format expected by write_xml.

    """
    entries = []
    gloss1 = []
    gloss2 = []
    for concept in csv.DictReader(tsvfile, dialect="excel-tab"):
        entries.append(concept["Concept ID"])
        gloss1.append(concept[glosses[0]])
        gloss2.append(concept[glosses[1]])
    return entries, gloss1, gloss2


def read_collection_metadata(jsonfile):
    metadata = json.load(jsonfile)
    for key in [
            "creatorrole",
            "contributor",
            "glosslanguage1",
            "lgcode1",
            "glosslanguage2",
            "lgcode2",
            "keywords",
            "description",
            "remarks",
            "published",
            "coverage",
            "stable",
            "rights",
            "copyright"]:
        metadata.setdefault(key, "")
    return metadata


def alignment_to_vector(alignment_string):
    """Translate an Edictor alignment string to a WordCorr vector.

    >>> alignment_to_vector("l a t")
    'xxx'
    >>> alignment_to_vector("o:")
    '{xx}'
    >>> alignment_to_vector("- t o: - l æ: ŋ")
    '/x{xx}/x{xx}x'
    >>> alignment_to_vector("b u l aN")
    'xxx{xx}'

    """
    vector = ""
    token = ""
    for t in alignment_string.strip():
        if t == "-":
            token = "/"
        elif t == " ":
            if len(token) > 1:
                vector += "{" + token + "}"
            else:
                vector += token
            token = ""
        else:
            token += "x"
    if len(token) > 1:
        vector += "{" + token + "}"
    else:
        vector += token
    return vector


def read_data(all_data_tsv, languages, concepts):
    """Read all counterpart data into the desired format.

    Read an edictor tsv. The output is a list (per concept) of lists
    (per language) of lists (per synonym) of strings.

    """
    languages_rl = {language["abbr"]: i
                    for i, language in enumerate(languages)}
    concepts_rl = {concept: i
                   for i, concept in enumerate(concepts)}
    all_data = [[[] for l in languages]
                for c in concepts]

    missing_languages = languages_rl.copy()

    for row in csv.DictReader(all_data_tsv, dialect='excel-tab'):
        try:
            c = concepts_rl[row["CONCEPT_ID"]]
        except KeyError:
            # Try cutting of a floating point, otherwise assume we got
            # a sublist of concepts and continue quietly.
            if row["CONCEPT_ID"].endswith(".0"):
                try:
                    c = concepts_rl[row["CONCEPT_ID"][:-2]]
                except KeyError:
                    continue
            else:
                continue
        try:
            l = languages_rl[row["DOCULECT_ID"]]
            missing_languages.pop(row["DOCULECT_ID"], None)
        except KeyError:
            pass
        all_data[c][l].append({
            "datum": row["IPA"].lstrip("*"),
            "tag": row["COGID"],
            "vector": alignment_to_vector(row["ALIGNMENT"])})
        
    # for language, index in sorted(empty.items(), key=lambda x: x[1],
    #                               reverse=True):
    #     del languages[index]
    #     for concept in data:
    #         del concept[index]
    
    return all_data


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
        "concepts", type=argparse.FileType("r"),
        default=sys.stdin,
        help="""The tsv file containing the concepts metadata""")
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
        "email": givenname + "@None",
        "creatorrole": "compiler"}

    collection_data = read_collection_metadata(args.collection)

    if not collection_data["glosslanguage1"]:
        collection_data["glosslanguage1"] = "English"
        collection_data["lgcode1"] = "eng"
    if not collection_data["glosslanguage2"]:
        collection_data["glosslanguage2"] = "Indonesian"
        collection_data["lgcode2"] = "ind"

    languages = read_language_metadata(args.languages)

    concepts, gloss1, gloss2 = read_concept_metadata(
        args.concepts,
        glosses=[collection_data["glosslanguage1"],
                 collection_data["glosslanguage2"]])

    data = read_data(args.data, languages, concepts)

    write_xml(args.output, user_data, collection_data, languages,
              concepts, gloss1, gloss2, data)
