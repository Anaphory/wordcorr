# -*- coding: cp1252 -*-
"""THIS PROGRAM WILL TAKE A TAB DELIMITED VERSION OF AN EXCEL TABLE AND
CONVERT IT TO xml IMPORTABLE INTO WORDCORR

USER GUIDE - DISREGARD IF YOU HAVE THE EXCEL USER GUIDE
Spreadsheet Conversion User Guide
B.R. Maria Faehndrich
System requirements:
Python 2.3 or higher (program may also run on versions as low as Python 2.1, but Python 2.3 is recommended.)

Instructions for getting Python:
This conversion program is written in Python. To get your own version of Python follow these steps:
1.������ Go to http://www.python.org/.
2.������ Click on Python 2.3 (or more recent version).
3.������ Follow instructions on the Web page.
4.������ I recommend installing Python under C:/Program Files.

Instructions for filling in the spreadsheet:
1.������ Follow the outline provided in the sample Put your data in the blank sheet.
2.������ Do not insert any additional cells, rows, or columns, except that you may add as many varieties with their metadata as you need, and as many entries as you need.
3.       For the fields "Your Role as Creator" and "Rights management", keep one of the items given in the sample spreadsheet. The program will not work if you fill in anything else.
4.       Separate multiple datums for one variety in the same entry by commas.

Instructions for converting spreadsheet to xml file:
1.������ Go to File, Save as.
2.������ Save as type: �Unicode Text� (only the active sheet can be saved, features incompatible with the format will be left out).
3.������ Save the file in the same folder that contains the Spreadsheet Conversion program (has to be within your Python folder).
4.������ Close the Excel file.
5.������ Open the text file you just created. Before you save it, please remove any empty lines and spaces at the end, as they may cause the conversion to crash.
6.������ Go to File, Save as:
   a)����� Keep file name location.
   b)����� Save as type: Text Documents (*.txt).
   c)����� Encoding: change to utf-8.
   d)����� If you are asked whether you want to replace the existing file, click Yes.
   e)����� Close the text file.
   f)����� Delete any empty lines at the bottom of the document.

Instructions for using conversion program:
1.������ Make sure that Python, the Spreadsheet Conversion script, and the text file with the input are all in the same directory.
2.������ To do this, create a new folder in your python folder and call it "Python WordCorr" (or any other name that will make sense to you).
3.������ Download the Python script Spreadsheet Conversion into this folder. (In order to make it easier for you to find it, you may want to put a shortcut on the desktop: right click, click on �create Shortcut�, and then drag the shortcut onto the desktop. This will make using the script a lot easier, especially if you are going to use option II below.)
4.������ Place your input file in your "Python WordCorr" folder in the Python folder.
5.������ There are two ways to start the conversion program:

I.
a)����� Go to Start, Programs, Python (2.3), IDLE (Python GUI).
b)����� the Python shell will open.
c)����� Go to File, Open. Find Spreadsheet Conversion in the Open window.
d)����� Double click on Spreadsheet Conversion.
e)����� In the window that opens with the conversion script, click on Run, Run Module (or you can hit the F5 button).
f)������ Follow the prompts that will be printed in the Python shell window.

II.
a)����� Find the Conversion script in My Computer. Double-click on it.
b)����� Follow the instructions in the window that opens.

To import your collection into WordCorr:
1. Open WordCorr.
2. Go to File, Import XML.
3. Find your collection in the Open window.
4. Double click on your file.

Note: WordCorr will attach the current user's ID, name, and email address as "publisher"
to any collection exported from WordCorr that does not already have these attached.
This means that if the person importing a collection into WordCorr is not the user indicated
in the spreadsheet, there will be a mismatch between the actual creator and publisher of the collection
and the user and publisher that appears in the exported file.

#####################################################################
"""

import sys
import argparse

def read_user_data_from_sprlist(sprlist1):
    userlistprelim = []           #create a list of all data filled in by the user
    stripstring = ''
    userlist = []
    for i in range(0, 5):                   #for all Collection metadata
        try:                                #try to append the data to preliminary datalist
            userlistprelim.append(sprlist1[i][3])
        except IndexError:                  #if a field is empty
            userlistprelim.append('*')      #append a '*' instead
    for i in range(0, len(userlistprelim)): #for this preliminary datalist
        string = userlistprelim[i]     #convert to string
        list = stripstring.strip()         #strip off trailing empty spaces (prevent linebreaks in xml document
        list = list.strip('"')
        userlist.append(list)               #append to datalist
    return dict(zip(
        ["id", "famname", "name", "affiliations", "email"],
        userlist))
 
def read_collection_data_from_sprlist(sprlist1):
    colllistprelim = []           #create a list of all data filled in by the user
    stripstring = ''
    colllist = []
    for i in range(6, 24):                  #for all Collection metadata
        try:                                #try to append the data to preliminary datalist
            colllistprelim.append(sprlist1[i][3])
        except IndexError:                  #if a field is empty
            colllistprelim.append('*')      #append a '*' instead
    for i in range(0, len(colllistprelim)): #for this preliminary datalist
        stripstring = colllistprelim[i]     #convert to string
        list = stripstring.strip()         #strip off trailing empty spaces (prevent linebreaks in xml document
        list = list.strip('"')
        colllist.append(list)               #append to datalist
    collection = {"collname":colllist[0],"collsname":colllist[1],
                "glosslg":colllist[4], "lgcode1":colllist[5], "glosslg2":colllist[6],
                "lgcode2":colllist[7], "creatorrole":colllist[2],
                "rights":colllist[15], "copyright":colllist[16]}
    collection["contributor"] = colllist[3]
    collection["description"] = colllist[9]
    collection["remarks"] = colllist[10]
    collection["keywords"] = (colllist[8])
    collection["coverage"] = colllist[13]
    collection["published"] = [i for i in colllist[11:13] if i]
    collection["stable"] = colllist[14]
    return collection

def read_varieties_metadata_from_sprlist(sprlist1):
    #SET UP LISTS FOR VARIETY INFORMATION:
    def read_variety_metadata(row, min_len=0):
        varietyproperty=[]
        varietypropertypre=[]
        for i in range(3, len(sprlist1[row])):
            varietypropertypre.append(sprlist1[row][i])

        while varietypropertypre and not varietypropertypre[-1]:
            varietypropertypre = varietypropertypre[:-1]
        varietypropertypre = varietypropertypre + [''] * max(
            min_len - len(varietypropertypre), 0)

        for stripstring in varietypropertypre:   #for this preliminary varietyethn.
            list = stripstring.strip()                 #strip off trailing empty spaces (prevent linebreaks in xml document
            list = list.strip('"')               #strip off quotation marks
            varietyproperty.append(list)              #append to varietyethn.
        return varietyproperty

    varnames = read_variety_metadata(26)
    varietyproperties = {
        "ethnologue": read_variety_metadata(25, len(varnames)),
        "name": varnames,
        "shortname": read_variety_metadata(27, len(varnames)),
        "abbr": read_variety_metadata(28, len(varnames)),
        "genclass": read_variety_metadata(29, len(varnames)),
        "quality": read_variety_metadata(30, len(varnames)),
        "altname": read_variety_metadata(31, len(varnames)),
        "locale": read_variety_metadata(32, len(varnames)),
        "collection_country": read_variety_metadata(33, len(varnames)),
        "remarks1": read_variety_metadata(34, len(varnames)),
        "remarks2": read_variety_metadata(35, len(varnames)),
        "remarks3": read_variety_metadata(36, len(varnames)),
        "unpub": read_variety_metadata(37, len(varnames)),
        "source1": read_variety_metadata(38, len(varnames)),
        "source2": read_variety_metadata(39, len(varnames)),
        "remarks": read_variety_metadata(40, len(varnames))}
    #vvvvvvvvvv Varieties Information End vvvvvvvvvv
    return varietyproperties

def read_data_from_sprlist(sprlist1):
    #Data starting line 65:
    #entry# | gloss1 | gloss2 | var1 | var2 | etc.

    #complete data, all info:
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
        data.append(row)
        for j in range(len(varietyproperties["name"])):  # data only, 
            # first three items are #, gl1, gl2, then all variety data
            row.append([token.strip().strip('"')
                        for token in sprlist1[i][j+3].split(",")])
    return entries, gloss1, gloss2, data


def write_xml(outp, userdata, collection, varietyproperties, entries, gloss1, gloss2, forms):
    #header information:
    encoding = '<?xml version="1.0" encoding="UTF-8"?>\n'
    #print encoding
    outp.write(encoding)

    release = '<WordCorr release="Release 2.0" version="2.1">\n'  
    #print release
    outp.write(release)

    #user info
    userid = '<user user-id="%(id)s" family-name="%(famname)s" given-name="%(name)s" email="%(email)s">\n' % userdata
    #print userid
    outp.write(userid)

    #affiliation
    affiliation = '<affiliations>%s</affiliations>\n'    % (userdata["affiliations"])
    #print affiliation
    outp.write(affiliation)

    #collection name and shortname:
    collname = '    <collection name="%(collname)s" short-name="%(collsname)s"' % collection
    #print collname
    outp.write(collname)

    #primary and secondary gloss languages and other info:
    glosslang = ' gloss-language="%(glosslg)s" gloss-language-code="%(lgcode1)s" secondary-gloss-language="%(glosslg2)s" secondary-gloss-language-code="%(lgcode2)s" creator-role="%(creatorrole)s" creator="" publisher="" rights-management="%(rights)s" rights-management-year-copyright-asserted="%(copyright)s" export-timestamp="">\n' % collection
    #print glosslang
    outp.write(glosslang)

    #contributor
    contributor = ' <contributor>%s</contributor>\n'  %collection["contributor"]
    #print contributor
    outp.write(contributor)

    #description
    description = '<description>%s</description>\n'   %collection["description"]
    #print description
    outp.write(description)

    #collection remarks:
    collrem = '        <remarks>%s</remarks>\n' % collection["remarks"]
    #print collrem
    outp.write(collrem)

    #keywords
    keywords = ' <keywords>%s</keywords>\n'   % collection["keywords"]
    #print keywords
    outp.write(keywords)

    #coverage
    coverage = ' <coverage>%s</coverage>\n'   % collection["coverage"]
    #print coverage
    outp.write(coverage)

    #published-source
    #This creates the input for the 'published source' field.
    #To avoid empty spaces or lines, the script takes into account which of the two lines
    #in the spreadsheet are filled.
    if collection["published"]:
        publishedsource = ' <published-source>%s</published-source>\n'    % ", ".join(collection["published"])
    else:
        publishedsource = ' <published-source />\n'    
    outp.write(publishedsource)    

    #stable-copy-location
    stablecopylocation = ' <stable-copy-location>%s</stable-copy-location>\n'  % collection["stable"]
    #print stablecopylocation
    outp.write(stablecopylocation)

    #varieties opener:
    var = '        <varieties>\n'
    #print var
    outp.write(var)

    #LOOP HERE FOR VARIETIES
    for i in range(0, len(varietyproperties["name"])):    #for however many varieties are there

        vxinf = '            <variety name="%(varname)s" short-name="%(varshortn)s" abbreviation="%(varabb)s" ethnologue-code="%(varethn)s">\n' %\
                    {"varname":varietyproperties["name"][i], "varshortn": varietyproperties["shortname"][i], 'varabb': varietyproperties["abbr"][i], 'varethn': varietyproperties["ethnologue"][i]}
        outp.write(vxinf)

        if varietyproperties["altname"][i] != '\n':
            vanl = '                <alternate-name-list>%s</alternate-name-list>\n'  %(varietyproperties["altname"][i])
            outp.write(vanl)

        if varietyproperties["genclass"][i] != '\n':
            vclass = '                <classification>%s</classification>\n'  %(varietyproperties["genclass"][i])
            outp.write(vclass)

        if varietyproperties["locale"][i] != '\n':
            vloc = '                <locale>%s</locale>\n' % varietyproperties["locale"][i]
            outp.write(vloc)

        if varietyproperties["quality"][i] != '\n':
            vqual = '                <quality>%s</quality>\n' % varietyproperties["quality"][i]
            outp.write(vqual)

        # To avoid empty spaces or lines, the script takes into
        # account which of the two lines available in the spreadsheet
        # are filled.
        if varietyproperties["source1"][i] != '' and varietyproperties["source2"][i] != '':
            vsour = '                <source>%(varsour)s</source>\n' %\
                    {'varsour': varietyproperties["source1"][i]+', '+varietyproperties["source2"][i]}
            outp.write(vsour)
        elif varietyproperties["source1"][i] == '':
            vsour = '                <source>%(varsour)s</source>\n' %\
                    {'varsour':varietyproperties["source2"][i]}
            outp.write(vsour)
        elif varietyproperties["source2"][i] == '':
            vsour = '                <source>%(varsour)s</source>\n' %\
                    {'varsour':varietyproperties["source1"][i]}
            outp.write(vsour)
        else:
            vsour = '                <source />\n'
            outp.write(vsour)

        vunpubsource = '                <unpublished-source>%s</unpublished-source>\n'    %(varietyproperties["unpub"][i])
        outp.write(vunpubsource)

        vccoll = '                <country-where-collected>%s</country-where-collected>\n'  %(varietyproperties["collection_country"][i])
        outp.write(vccoll)

        #This is a combination of three fields out of the spreadsheet.
        #The following script checks whether the fields in question
        #are filled, and if they are empty, they are not included in
        #Variety remarks, in order to avoid empty spaces and lines.
        remarks = []
        if varietyproperties["remarks"][i]:
            remarks.append(varietyproperties["remarks"][i])
        if varietyproperties["remarks1"][i]:
            remarks.append('Place where collected: '+varietyproperties["remarks1"][i])
        if varietyproperties["remarks2"][i]:
            remarks.append('Collected by: '+varietyproperties["remarks2"][i])
        if varietyproperties["remarks3"][i]:
            remarks.append('Date collected: '+varietyproperties["remarks3"][i])
        if remarks:
            vrem = '                <remarks>%s</remarks>\n'  %(
                ", ".join(remarks))
        else:
            vrem = '                <remarks />\n'
        outp.write(vrem)

        vxclos = '            </variety>\n'
        outp.write(vxclos)

    varclos = '        </varieties>\n'
    outp.write(varclos)

    #LOOP HERE FOR DATA AND GLOSS, generator for entry number:
    #data open:
    data = '        <data>\n'
    outp.write(data)
    varieties=varietyproperties["name"]

    #entry number, gloss1, gloss2
    m=0
    for i, entry in enumerate(entries):
        entrynumgl = '            <entry entry-number="%(no)s" gloss="%(gloss1)s" secondary-gloss="%(gloss2)s">\n' %\
                                                       {'no' : entries[i], 'gloss1' : gloss1[i], 'gloss2':gloss2[i]}
        outp.write(entrynumgl)

    #*********VARx DATA open***************       
    #datum number (generated here, only works if the collection has less than 10,000 datums )
    #variety short-name
    #datum: cycles through varieties and multiple datums
    #DATUM NUMBERS CREATED HERE ARE NOT UNIQUE.
    #NON-UNIQUE DATUM NUMBERS ARE NOT A PROBLEM, SINCE EACH DATUM IS ASSIGNED A NEW NUMBER UPON IMPORT INTO WORDCORR
    #DATUM NUMBERS ASSIGNED HERE WILL NOT PERSIST
    #IF THIS COLLECTION IS EXPORTED FROM WORDCORR, THE DATUM NUMBERS WILL BE DIFFERENT FROM THE NUMBERS ASSIGNED HERE
        for l in range(0, len(varieties)):
            for k, form in enumerate(forms[i][l]):
                if form:
                    datum = '                <datum datum-number="%(no)s" short-name="%(varshortn)s" datum="%(datm)s">\n' %\
                        {'no' : i+k+m+l, 'varshortn' : varietyproperties["shortname"][l], 'datm' : form}    
                    outp.write(datum)   #.encode('utf-8'))   #encode as unicode

                    #special semantics of datum
                    specsem = '                    <special-semantics />\n'
                    outp.write(specsem)

                    #remarks for datum
                    datrem = '                    <remarks />\n'
                    outp.write(datrem)

                    #close datum
                    datcls = '                </datum>\n'
                    outp.write(datcls)
        m=m+(len(varieties)-1)   #m=m+(len(varieties)-1)   
    #*********VARx DATA closed***************

    #close entry
        entrcls = '            </entry>\n'
    #    print entrcls
        outp.write(entrcls)

    #close data
    datacls = '        </data>\n'
    #print datacls
    outp.write(datacls)

    #open view information
    viewsop = '        <views>\n'
    #print viewsop
    outp.write(viewsop)

    #open view1
    viewop = '            <view view-name="Original" threshold="50">\n'
    #print viewop
    outp.write(viewop)

    #remarks view1
    remarks = '                <remarks />\n'
    #print remarks
    outp.write(remarks)

    #view info: short name, order number (generated here)
    #viewmember(x):
    for i in range(0, len(varietyproperties["name"])):    #for all varieties
        viewmem = '                <view-member short-name="%(varshortn)s" order-number="%(no)s" />\n' %\
                {'varshortn': varietyproperties["shortname"][i], 'no':i+1}
    #    print viewmem
        outp.write(viewmem)

    #annotations:
    annop = '                <annotations />\n'
    #print annop
    outp.write(annop)

    #results (Refine)
    results = '                  <results />\n'
    #print results
    outp.write(results)

    #tabulated groups
    tabgroups = '                <tabulated-groups />\n'
    #print tabgroups
    outp.write(tabgroups)

    #close view
    viewcls = '            </view>\n'
    #print viewcls
    outp.write(viewcls)

    #close views
    viewscls = '        </views>\n'
    #print viewscls
    outp.write(viewscls)

    #collection closer
    v = '    </collection>\n'
    #print v
    outp.write(v)

    #user closer
    useclos = '</user>\n'
    #print useclos
    outp.write(useclos)

    #WordCorr closer
    z = '</WordCorr>'
    #print z
    outp.write(z)

    #close "output"
    outp.close()

if __name__=='__main__':
    parser = argparse.ArgumentParser(
        description = """This program will take a tab delimited version of an excel table
        and convert it to xml importable into WordCorr""")
    parser.add_argument(
        "input", type=argparse.FileType("r"), nargs="?",
        default=sys.stdin,
        help="""The tab-separated spread sheet to read data from, must be in a very
        specific format.""")
    parser.add_argument(
        "output", type=argparse.FileType("w"), nargs="?",
        default=sys.stdout,
        help="Path of the xml file to be written")
    args = parser.parse_args()

    inp = args.input

    #CREATE LIST FROM DATA, SPLIT BY 'TAB'
    sprlist1 = []
    for i, line in enumerate(inp):	#read each line in the input and do the following:  
        if i < 5:
            # File header with instructions
            continue

        list = line.strip("\n").split('\t')    #separate nos/glosses, nos or letters and header info
        sprlist1.append(list)


    #USER INFORMATION:
    userdata = read_user_data_from_sprlist(sprlist1)               

    #COLLECTION INFORMATION:
    collection = read_collection_data_from_sprlist(sprlist1)

    #CREATES DICT OF LISTS CONTAINING THE INFORMATION FROM THE VARIETIES
    varietyproperties = read_varieties_metadata_from_sprlist(sprlist1)
    
    entries, gloss1, gloss2, data = read_data_from_sprlist(sprlist1)
    write_xml(args.output, userdata, collection, varietyproperties, entries, gloss1, gloss2, data)

