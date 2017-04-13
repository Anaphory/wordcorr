#!/usr/bin/env python

"""Find all the possible sound correspondences in some data."""

import pandas

import argparse


def correspondences(
        data,
        languages,
        language_column="Language_ID", alignment_col="Alignment",
        cogid_column="Cognate Class"):
    """Find sound correspondences in CLDF data frame.

    Alignments for cognate classes display sound
    correspondences. Display them.

    """
    allcorrespondences = {}
    for c, cognatedata in data.groupby(cogid_column):
        first = cognatedata.iloc[0]
        segments = first[alignment_col].split()
        correspondences = [[None for _ in languages] for _ in segments]
        for l, language in enumerate(languages):
            cognates = cognatedata[cognatedata[language_column] == language]
            if len(cognates):
                alignment = cognates.iloc[0][alignment_col].split()
                for s, segment in enumerate(alignment):
                    correspondences[s][l] = segment

        for s, correspondence in enumerate(correspondences):
            if any(correspondence):
                allcorrespondences.setdefault(
                    tuple(correspondence), []).append((first["CONCEPT"], c, s))

    return allcorrespondences

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
