#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""Read a CLDF Lexibank data set into WordCorr.

Take a data set as Lexibank uses it, and convert it into an XML file
in the format used for WordCorr backup/exchange.

"""

import itertools
import collections

import sys
import argparse

import json
import pandas
import xml.etree.cElementTree as ET

from soundcorrespondences import correspondences

from tsv2wordcorr import write_xml


def read_language_metadata(tsvfile):
    """Read varieties metadata from a tsv file.

    Read a TSV file containing language metadata in specific columns,
    and convert it into the list-of-dicts format expected by
    write_xml.

    """
    varieties = []
    for v, variety in pandas.read_csv(
            tsvfile, sep="\t", keep_default_na=False, na_values=[]).iterrows():
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
    for c, concept in pandas.read_csv(
            tsvfile, sep="\t", keep_default_na=False, na_values=[]).iterrows():
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
    >>> alignment_to_vector("* u l aN")
    'xx{xx}'

    """
    vector = ""
    token = ""
    for t in alignment_string.strip():
        if t == "*":
            # Ignore *initial* 'reconstructed' markers
            if vector.strip("/"):
                token += "x"
            else:
                continue
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

    data = pandas.read_csv(
        all_data_tsv, sep="\t", keep_default_na=False, na_values=[])
    for r, row in data.iterrows():
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
            continue
        all_data[c][l].append({
            "datum": row["IPA"].lstrip("*"),
            "tag": row["COGID"],
            "vector": alignment_to_vector(row["ALIGNMENT"])})

    sound_correspondences = correspondences(
        data, data["DOCULECT_ID"].unique(),
        "DOCULECT_ID", "ALIGNMENT", "COGID")

    return all_data, sound_correspondences


def correspondences_tag(soundcorrespondences):
    """Generate a wordcorr <results/> tag for sound correspondences.

    Given a {correspondence-tuple: ()} dict of sound correspondences,
    create an ElementTree object representing the <results> tag for a
    WordCorr XML representing these sound correspondences, each as a
    separate proto-segment.

    """
    xresults = ET.Element("results")
    protosegments = {}
    for correspondence, occurrences in soundcorrespondences.items():
        print(correspondence)
        protosegment = collections.Counter(correspondence)
        protosegment[None] = 0
        protosegment["-"] = 0
        protosegment, n = protosegment.most_common(1)[0]
        p = protosegments[protosegment] = protosegments.get(
            protosegment, -1) + 1
        protosegment = "{:}{:d}".format(protosegment, p)
        glyphs = []
        ignore = 0
        glyph_count = 0
        for c in correspondence:
            if c is None:
                glyphs.append(".")
                ignore += 1
            elif c == "-":
                glyphs.append("/")
            elif len(c) == 1:
                glyphs.append(c)
                glyph_count += 1
            else:
                glyphs.append("{"+c+"}")
                glyph_count += 1
        xsegment = ET.SubElement(xresults, "protosegment",
                                 symbol=protosegment,
                                 zone_row=str(1),
                                 zone_column=str(1))
        xcluster = ET.SubElement(xsegment, "cluster",
                                 environment="_",
                                 cluster_order=str(1))
        xcorrespondenceset = ET.SubElement(xcluster, "correspondence-set",
                                           ignore_count=str(ignore),
                                           glyph_count=str(glyph_count),
                                           order=str(1))
        ET.SubElement(xcorrespondenceset, "remarks")
        ET.SubElement(
            xcorrespondenceset, "glyph-string").text = "".join(glyphs)
        for concept, cognateclass, position in occurrences:
            print(concept, cognateclass, position)
            ET.SubElement(xcorrespondenceset, "citation",
                          entry_number=str(concepts[gloss1.index(concept)]),
                          tag=str(cognateclass),
                          glyph_position=str(position))
    return xresults


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

    #SORT THIS ALPHABETICALLY?
    concepts, gloss1, gloss2 = read_concept_metadata(
        args.concepts,
        glosses=[collection_data["glosslanguage1"],
                 collection_data["glosslanguage2"]])

    data, soundcorrespondences = read_data(args.data, languages, concepts)

    xresults = correspondences_tag(soundcorrespondences)

    write_xml(args.output, user_data, collection_data, languages,
              concepts, gloss1, gloss2, data,
              ET.tostring(xresults, encoding='unicode').replace("_", "-"))

    print("File generated.")
    import networkx as nx
    g = nx.Graph()
    for (c1, sc1), (c2, sc2) in itertools.combinations(
            soundcorrespondences.items(), 2):
        if len([c for c in c1 if c]) < 6:
            continue
        if len([c for c in c2 if c]) < 6:
            continue
        if {(concept, cogid)
            for (concept, cogid, pos) in sc1} & {
                    (concept, cogid)
                    for (concept, cogid, pos) in sc2}:
            g.add_edge(c1, c2)
        if all([((p1 is None) or (p1 == p2)
                for p1, p2 in zip(c1, c2))]) or all([
                        (p2 is None) or (p1 == p2)
                        for p1, p2 in zip(c1, c2)]):
            g.add_edge(c1, c2)
    print("Graph calculated.")
    nx.draw(g)
