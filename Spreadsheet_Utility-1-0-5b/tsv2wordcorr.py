# ! /usr/bin/env python3
# -*- encoding: utf-8 -*-

"""THIS PROGRAM WILL TAKE A TAB DELIMITED VERSION OF AN EXCEL TABLE AND
CONVERT IT TO xml IMPORTABLE INTO WORDCORR

USER GUIDE - DISREGARD IF YOU HAVE THE EXCEL USER GUIDE

Spreadsheet Conversion User Guide
B.R. Maria Faehndrich

Instructions for filling in the spreadsheet:

1. Follow the outline provided in the sample Put your data in the blank sheet.

2. Do not insert any additional cells, rows, or columns, except that
   you may add as many varieties with their metadata as you need, and
   as many entries as you need.

3. For the fields "Your Role as Creator" and "Rights management", keep
   one of the items given in the sample spreadsheet. The program will
   not work if you fill in anything else.

4. Separate multiple datums for one variety in the same entry by commas.

To import your collection into WordCorr:
1. Open WordCorr.
2. Go to File, Import XML.
3. Find your collection in the Open window.
4. Double click on your file.

Note: WordCorr will attach the current user's ID, name, and email
address as "publisher" to any collection exported from WordCorr that
does not already have these attached.  This means that if the person
importing a collection into WordCorr is not the user indicated in the
spreadsheet, there will be a mismatch between the actual creator and
publisher of the collection and the user and publisher that appears in
the exported file.
"""

import sys
import argparse


def read_user_data_from_sprlist(sprlist1):
    user = {}
    for i, name in enumerate(
            ["id", "famname", "name", "affiliations", "email"]):
        try:
            # The user metadata is in rows 0–5 in the sheet. Column 3
            # contains our data, as opposed to field names etc.
            stripstring = sprlist1[i][3]
        except IndexError:
            # if a field is empty (which may lead to it being dropped
            # in export/stripped while reading), it's empty.
            stripstring = ''
        list = stripstring.strip() # It's never hurts to strip again.
        list = list.strip('"')
        user[name] = list
    return user


def read_collection_data_from_sprlist(sprlist1):
    collection_names = [
        "name",
        "id",
        "creatorrole",
        "contributor",
        "glosslg",
        "lgcode1",
        "glosslg2",
        "lgcode2",
        "keywords",
        "description",
        "remarks",
        "published1",
        "published2",
        "coverage",
        "stable",
        "rights",
        "copyright"]
    collection = {}
    for i, name in enumerate(collection_names):
        try:
            # The collection metadata is in rows 6–24 in the sheet (0–5 are
            # user metadata). Column 3 contains our data.
            stripstring = sprlist1[i + 6][3]
        except IndexError:
            # if a field is empty (which may lead to it being dropped
            # in export/stripped while reading), it's empty.
            stripstring = ''
        list = stripstring.strip() # It's never hurts to strip again.
        list = list.strip('"')
        collection[name] = list
    collection["published"] = filter(
        None, [collection.pop("published1"), collection.pop("published2")])
    return collection

def read_varieties_metadata_from_sprlist(sprlist1):
    # SET UP LISTS FOR VARIETY INFORMATION:
    def read_variety_metadata(row):
        varietyproperty=[]
        varietypropertypre=[]
        for i in range(3, len(sprlist1[row])):
            varietypropertypre.append(sprlist1[row][i])

        while varietypropertypre and not varietypropertypre[-1]:
            varietypropertypre = varietypropertypre[:-1]

        for stripstring in varietypropertypre:   # for this preliminary varietyethn.
            list = stripstring.strip()                 # strip off trailing empty spaces (prevent linebreaks in xml document
            list = list.strip('"')               # strip off quotation marks
            varietyproperty.append(list)              # append to varietyethn.
        return varietyproperty

    varnames = read_variety_metadata(26)
    varietyproperties = {
        "ethnologue": read_variety_metadata(25),
        "name": varnames,
        "shortname": read_variety_metadata(27),
        "abbr": read_variety_metadata(28),
        "genclass": read_variety_metadata(29),
        "quality": read_variety_metadata(30),
        "altname": read_variety_metadata(31),
        "locale": read_variety_metadata(32),
        "collection_country": read_variety_metadata(33),
        "collection_location": read_variety_metadata(34),
        "collector": read_variety_metadata(35),
        "collection_date": read_variety_metadata(36),
        "unpub": read_variety_metadata(37),
        "source1": read_variety_metadata(38),
        "source2": read_variety_metadata(39),
        "remarks": read_variety_metadata(40)}

    varieties = [{key: (value[i] if i < len(value) else "")
                  for key, value in varietyproperties.items()}
                 for i, var in enumerate(varnames)]

    for variety in varieties:
        variety["source"] = list(filter(
            None, [variety.pop("source1"),
                   variety.pop("source2")]))

    return varieties

def read_data_from_sprlist(sprlist1):
    # Data starting line 65:
    # entry# | gloss1 | gloss2 | var1 | var2 | etc.

    # complete data, all info:
    entries = []
    gloss1 = []
    gloss2=[]
    data=[]
    for i in range(43, len(sprlist1)):
        entries.append(sprlist1[i][0])

        list = sprlist1[i][1].strip('"').strip()
        gloss1.append(list)

        list = sprlist1[i][2].strip('"').strip()
        gloss2.append(list)

        row = []
        data.append({"datum": row})
        for j in range(len(varietyproperties)):  # data only, first
            # three items are entry, gl1, gl2, then all variety data
            row.append([token.strip().strip('"')
                        for token in sprlist1[i][j+3].split(",")])

    return entries, gloss1, gloss2, data


def write_xml(outp, userdata, collection, varietyproperties, entries, gloss1, gloss2, forms):
    # header information:
    encoding = '<?xml version="1.0" encoding="UTF-8"?>\n'
    # print encoding
    outp.write(encoding)

    release = '<WordCorr release="Release 2.1" version="2.1">\n'  
    # print release
    outp.write(release)

    # user info
    userid = '<user user-id="%(id)s" family-name="%(famname)s" given-name="%(name)s" email="%(email)s">\n' % userdata
    # print userid
    outp.write(userid)

    # affiliation
    affiliation = '<affiliations>%s</affiliations>\n' % (userdata["affiliations"])
    # print affiliation
    outp.write(affiliation)

    # collection name and shortname:
    collname = '    <collection name="%(id)s" short-name="%(name)s"' % collection
    # print name
    outp.write(collname)

    # primary and secondary gloss languages and other info:
    glosslang = ' gloss-language="%(glosslanguage1)s" gloss-language-code="%(lgcode1)s" secondary-gloss-language="%(glosslanguage2)s" secondary-gloss-language-code="%(lgcode2)s" creator-role="%(creatorrole)s" creator="" publisher="" rights-management="%(rights)s" rights-management-year-copyright-asserted="%(copyright)s" export-timestamp="">\n' % collection
    # print glosslang
    outp.write(glosslang)

    # contributor
    contributor = ' <contributor>%s</contributor>\n'  %collection["contributor"]
    # print contributor
    outp.write(contributor)

    # description
    description = '<description>%s</description>\n'   %collection["description"]
    # print description
    outp.write(description)

    # collection remarks:
    collrem = '        <remarks>%s</remarks>\n' % collection["remarks"].replace("&", "&amp;")
    # print collrem
    outp.write(collrem)

    # keywords
    keywords = ' <keywords>%s</keywords>\n'   % collection["keywords"]
    # print keywords
    outp.write(keywords)

    # coverage
    coverage = ' <coverage>%s</coverage>\n'   % collection["coverage"]
    # print coverage
    outp.write(coverage)

    # published-source
    # This creates the input for the 'published source' field.
    # To avoid empty spaces or lines, the script takes into account which of the two lines
    # in the spreadsheet are filled.
    if collection["published"]:
        publishedsource = ' <published-source>%s</published-source>\n'    % ", ".join(collection["published"])
    else:
        publishedsource = ' <published-source />\n'    
    outp.write(publishedsource)    

    # stable-copy-location
    stablecopylocation = ' <stable-copy-location>%s</stable-copy-location>\n'  % collection["stable"]
    # print stablecopylocation
    outp.write(stablecopylocation)

    # varieties opener:
    var = '        <varieties>\n'
    # print var
    outp.write(var)

    # LOOP HERE FOR VARIETIES
    for i, var in enumerate(varietyproperties):    # for however many varieties are there

        vxinf = '            <variety name="%(varname)s" short-name="%(varshortn)s" abbreviation="%(varabb)s" ethnologue-code="%(varethn)s">\n' %\
                    {"varname": var["name"].strip(),
                     "varshortn": var["shortname"].strip(),
                     'varabb': var["abbr"],
                     'varethn': var["ethnologue"]}
        outp.write(vxinf)

        if var["altname"] != '\n':
            vanl = '                <alternate-name-list>%s</alternate-name-list>\n'  %(var["altname"])
            outp.write(vanl)

        if var["genclass"] != '\n':
            vclass = '                <classification>%s</classification>\n'  %(var["genclass"])
            outp.write(vclass)

        if var["locale"] != '\n':
            vloc = '                <locale>%s</locale>\n' % var["locale"]
            outp.write(vloc)

        if var["quality"] != '\n':
            vqual = '                <quality>%s</quality>\n' % var["quality"]
            outp.write(vqual)

        # To avoid empty spaces or lines, the script takes into
        # account which of the two lines available in the spreadsheet
        # are filled.
        if var["source"]:
            vsour = '                <source>%s</source>\n' %\
                    "; ".join(var["source"])
        else:
            vsour = '                <source />\n'
        outp.write(vsour)

        vunpubsource = '                <unpublished-source>%s</unpublished-source>\n'    %(var["unpub"])
        outp.write(vunpubsource)

        vccoll = '                <country-where-collected>%s</country-where-collected>\n'  %(var["collection_country"])
        outp.write(vccoll)

        # This is a combination of three fields out of the spreadsheet.
        # The following script checks whether the fields in question
        # are filled, and if they are empty, they are not included in
        # Variety remarks, in order to avoid empty spaces and lines.
        remarks = []
        if var["remarks"]:
            remarks.append(var["remarks"])
        if var["collection_location"]:
            remarks.append(
                'Place where collected: ' + var["collection_location"])
        if var["collector"]:
            remarks.append('Collected by: ' + var["collector"])
        if var["collection_date"]:
            remarks.append('Date collected: ' + var["collection_date"])
        if remarks:
            vrem = '                <remarks>%s</remarks>\n' % (
                ", ".join(remarks))
        else:
            vrem = '                <remarks />\n'
        vrem = vrem.replace("&", "&amp;")
        outp.write(vrem)

        vxclos = '            </variety>\n'
        outp.write(vxclos)

    varclos = '        </varieties>\n'
    outp.write(varclos)

    # LOOP HERE FOR DATA AND GLOSS, generator for entry number:
    # data open:
    data = '        <data>\n'
    outp.write(data)

    # entry number, gloss1, gloss2

    annotations = []
    m=0
    for i, entry in enumerate(entries):
        entrynumgl = '            <entry entry-number="%(no)s" gloss="%(gloss1)s" secondary-gloss="%(gloss2)s">\n' % (
            {'no': entry, 'gloss1': gloss1[i], 'gloss2': gloss2[i]})
        outp.write(entrynumgl)

    # *********VARx DATA open***************       
    # datum number (generated here, only works if the collection has less than 10,000 datums )
    # variety short-name
    # datum: cycles through varieties and multiple datums
    # DATUM NUMBERS CREATED HERE ARE NOT UNIQUE.
    # NON-UNIQUE DATUM NUMBERS ARE NOT A PROBLEM, SINCE EACH DATUM IS ASSIGNED A NEW NUMBER UPON IMPORT INTO WORDCORR
    # DATUM NUMBERS ASSIGNED HERE WILL NOT PERSIST
    # IF THIS COLLECTION IS EXPORTED FROM WORDCORR, THE DATUM NUMBERS WILL BE DIFFERENT FROM THE NUMBERS ASSIGNED HERE
        for l, var in enumerate(varietyproperties):
            for k, form in enumerate(forms[i][l]):
                if form:
                    datum = '                <datum datum-number="%(no)s" short-name="%(varshortn)s" datum="%(datm)s">\n' %\
                        {'no': i+k+m+l,
                         'varshortn': var["shortname"],
                         'datm': form["datum"].replace("<", "&lt;").replace(">", "&gt;")}
                    outp.write(datum)   # .encode('utf-8'))   # encode as unicode

                    annotations.append(
                        """<annotated-datum entry-number="{conceptid:}" tag="{tag:}" datum-number="{no:}" vector="{xs:}" metathesis="">
                        <observations />
                        </annotated-datum>
                        """.format(conceptid=entry,
                                   tag=form.get("tag", "?"),
                                   no=i+k+m+l,
                                   xs=form.get("vector", "x"*len(form))))
                    # special semantics of datum
                    specsem = '                    <special-semantics />\n'
                    outp.write(specsem)

                    # remarks for datum
                    datrem = '                    <remarks />\n'
                    outp.write(datrem)

                    # close datum
                    datcls = '                </datum>\n'
                    outp.write(datcls)
        m=m+(len(varietyproperties)-1)   # m=m+(len(varieties)-1)   
    # *********VARx DATA closed***************

    # close entry
        entrcls = '            </entry>\n'
    # print entrcls
        outp.write(entrcls)

    # close data
    datacls = '        </data>\n'
    # print datacls
    outp.write(datacls)

    # open view information
    viewsop = '        <views>\n'
    # print viewsop
    outp.write(viewsop)

    # open view1
    viewop = '            <view view-name="Original" threshold="50">\n'
    # print viewop
    outp.write(viewop)

    # remarks view1
    remarks = '                <remarks />\n'
    # print remarks
    outp.write(remarks)

    # view info: short name, order number (generated here)
    # viewmember(x):
    for i, var in enumerate(varietyproperties):    # for all varieties
        viewmem = '                <view-member short-name="%(varshortn)s" order-number="%(no)s" />\n' %\
                {'varshortn': var["shortname"], 'no':i+1}
    # print viewmem
        outp.write(viewmem)

    if annotations:
        annop = """<annotations>
        %s
        </annotations>""" % "".join(annotations)
    else:
        annop = '                <annotations />\n'
    outp.write(annop)

    # results (Refine)
    results = '                  <results />\n'
    # print results
    outp.write(results)

    # tabulated groups
    tabgroups = '                <tabulated-groups />\n'
    # print tabgroups
    outp.write(tabgroups)

    # close view
    viewcls = '            </view>\n'
    # print viewcls
    outp.write(viewcls)

    # close views
    viewscls = '        </views>\n'
    # print viewscls
    outp.write(viewscls)

    # collection closer
    v = '    </collection>\n'
    # print v
    outp.write(v)

    # user closer
    useclos = '</user>\n'
    # print useclos
    outp.write(useclos)

    # WordCorr closer
    z = '</WordCorr>'
    # print z
    outp.write(z)

    # close "output"
    outp.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""This program will take a tab delimited version of an
        Excel table and convert it to xml importable into WordCorr""")
    parser.add_argument(
        "input", type=argparse.FileType("r"), nargs="?",
        default=sys.stdin,
        help="""The tab-separated spread sheet to read data from, must be in a
        very specific format.""")
    parser.add_argument(
        "output", type=argparse.FileType("w"), nargs="?",
        default=sys.stdout,
        help="Path of the xml file to be written")
    args = parser.parse_args()

    inp = args.input

    # CREATE LIST FROM DATA, SPLIT BY 'TAB'
    sprlist1 = []
    for i, line in enumerate(inp):
        if i < 5:
            # File header with instructions
            continue

        sprlist1.append(line.strip("\n").split('\t'))

    # USER INFORMATION:
    userdata = read_user_data_from_sprlist(sprlist1)

    # COLLECTION INFORMATION:
    collection = read_collection_data_from_sprlist(sprlist1)

    # CREATES DICT OF LISTS CONTAINING THE INFORMATION FROM THE VARIETIES
    varietyproperties = read_varieties_metadata_from_sprlist(sprlist1)

    entries, gloss1, gloss2, data = read_data_from_sprlist(sprlist1)
    write_xml(args.output, userdata, collection, varietyproperties,
              entries, gloss1, gloss2, data)
