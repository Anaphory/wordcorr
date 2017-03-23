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
1.       Go to http://www.python.org/.
2.       Click on Python 2.3 (or more recent version).
3.       Follow instructions on the Web page.
4.       I recommend installing Python under C:/Program Files.

Instructions for filling in the spreadsheet:
1.       Follow the outline provided in the sample Put your data in the blank sheet.
2.       Do not insert any additional cells, rows, or columns, except that you may add as many varieties with their metadata as you need, and as many entries as you need.
3.       For the fields "Your Role as Creator" and "Rights management", keep one of the items given in the sample spreadsheet. The program will not work if you fill in anything else.
4.       Separate multiple datums for one variety in the same entry by commas.

Instructions for converting spreadsheet to xml file:
1.       Go to File, Save as.
2.       Save as type: “Unicode Text” (only the active sheet can be saved, features incompatible with the format will be left out).
3.       Save the file in the same folder that contains the Spreadsheet Conversion program (has to be within your Python folder).
4.       Close the Excel file.
5.       Open the text file you just created. Before you save it, please remove any empty lines and spaces at the end, as they may cause the conversion to crash.
6.       Go to File, Save as:
   a)      Keep file name location.
   b)      Save as type: Text Documents (*.txt).
   c)      Encoding: change to utf-8.
   d)      If you are asked whether you want to replace the existing file, click Yes.
   e)      Close the text file.
   f)      Delete any empty lines at the bottom of the document.

Instructions for using conversion program:
1.       Make sure that Python, the Spreadsheet Conversion script, and the text file with the input are all in the same directory.
2.       To do this, create a new folder in your python folder and call it "Python WordCorr" (or any other name that will make sense to you).
3.       Download the Python script Spreadsheet Conversion into this folder. (In order to make it easier for you to find it, you may want to put a shortcut on the desktop: right click, click on “create Shortcut”, and then drag the shortcut onto the desktop. This will make using the script a lot easier, especially if you are going to use option II below.)
4.       Place your input file in your "Python WordCorr" folder in the Python folder.
5.       There are two ways to start the conversion program:

I.
a)      Go to Start, Programs, Python (2.3), IDLE (Python GUI).
b)      the Python shell will open.
c)      Go to File, Open. Find Spreadsheet Conversion in the Open window.
d)      Double click on Spreadsheet Conversion.
e)      In the window that opens with the conversion script, click on Run, Run Module (or you can hit the F5 button).
f)       Follow the prompts that will be printed in the Python shell window.

II.
a)      Find the Conversion script in My Computer. Double-click on it.
b)      Follow the instructions in the window that opens.

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
userlistprelim = []           #create a list of all data filled in by the user
stripstring = ''
userlist = []
for i in range(0, 6):                   #for all Collection metadata
    try:                                #try to append the data to preliminary datalist
        userlistprelim.append(sprlist1[i][3])
    except IndexError:                  #if a field is empty
        userlistprelim.append('*')      #append a '*' instead
for i in range(0, len(userlistprelim)): #for this preliminary datalist
    string = userlistprelim[i]     #convert to string
    list = stripstring.strip()         #strip off trailing empty spaces (prevent linebreaks in xml document
    list = list.strip('"')
    userlist.append(list)               #append to datalist
#print "USER INFO"
#for i in range(0,len(userlist)):
#    print userlist[i] 

#COLLECTION INFORMATION:
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
#print "COLLECTION INFO"
#for i in range(0,len(colllist)):
#    print colllist[i]

#vvvvvvvvvvv Varieties Information vvvvvvvvvvvv
#CREATES LISTS CONTAINING THE INFORMATION FROM THE VARIETIES

#SET UP LISTS FOR VARIETY INFORMATION:
varietyname=[]
varietyshortname=[]
varietyabbr=[]
varietygenclass=[]
varietyquality=[]
varietyaltname=[]
varietylocale=[]    #where spoken
varietycollcoun=[]
varietyunpub=[]
varietysource1=[]
varietysource2=[]
varietyremarks=[]
varietyremarks1=[]
varietyremarks2=[]
varietyremarks3=[]

def read_variety_metadata(row, may_be_empty=True):
    varietyethnologue=[]
    varietyethnologuepre=[]
    for i in range(3, len(sprlist1[row])):
        if sprlist1[row][i] != '' or may_be_empty:         #don't append empty fields
            varietyethnologuepre.append(sprlist1[row][i])
            
    for i in range(0, len(varietyethnologuepre)):   #for this preliminary varietyethn.
        stripstring = varietyethnologuepre[i]       #convert to string
        list = stripstring.strip()                 #strip off trailing empty spaces (prevent linebreaks in xml document
        list = list.strip('"')               #strip off quotation marks
        varietyethnologue.append(list)              #append to varietyethn.
    return varietyethnologue

varietyethnologue = read_variety_metadata(25, True)
varietyname = read_variety_metadata(26, False)
varietyshortname = read_variety_metadata(27, True)
varietyabbr = read_variety_metadata(28, True)
varietygenclass = read_variety_metadata(29, True)

varietygenclasspre=[]
for i in range(3, len(sprlist1[29])):
    varietygenclasspre.append(sprlist1[29][i])
for i in range(0, len(varietygenclasspre)): #for this preliminary varietgenclass
    stripstring = varietygenclasspre[i]     #convert to string
    list = stripstring.strip()             #strip off trailing empty spaces (prevent linebreaks in xml document
    list = list.strip('"')
    varietygenclass.append(list)            #append to varietygenclass
#print "Genetic classification:"
#print varietygenclass

varietyqualitypre=[]
for i in range(3, len(sprlist1[30])):
    varietyqualitypre.append(sprlist1[30][i])
for i in range(0, len(varietyqualitypre)):      #for this preliminary varietyquality
    stripstring = varietyqualitypre[i]          #convert to string
    list = stripstring.strip()                 #strip off trailing empty spaces (prevent linebreaks in xml document
    list = list.strip('"')
    varietyquality.append(list)                 #append to varietyquality
#print "Variety quality:"
#print varietyquality

varietyaltnamepre=[]
for i in range(3, len(sprlist1[31])):
    varietyaltnamepre.append(sprlist1[31][i])
for i in range(0, len(varietyaltnamepre)):      #for this preliminary varietyaltname
    stripstring = varietyaltnamepre[i]          #convert to string
    list = stripstring.strip()                 #strip off trailing empty spaces (prevent linebreaks in xml document
    list = list.strip('"')
    varietyaltname.append(list)                 #append to varietyaltname
#print "Alternate language name(s):"
#print varietyaltname

varietylocalepre=[]
for i in range(3, len(sprlist1[32])):
    varietylocalepre.append(sprlist1[32][i])
for i in range(0, len(varietylocalepre)):   #for this preliminary varietylocale
    stripstring = varietylocalepre[i]       #convert to string
    list = stripstring.strip()             #strip off trailing empty spaces (prevent linebreaks in xml document
    list = list.strip('"')
    varietylocale.append(list)              #append to varietylocale
#print "Where spoken:"
#print varietylocale

varietycollcounpre=[]
for i in range(3, len(sprlist1[33])):
    varietycollcounpre.append(sprlist1[33][i])
for i in range(0, len(varietycollcounpre)):     #for this preliminary varietycollcoun
    stripstring = varietycollcounpre[i]         #convert to string
    list = stripstring.strip()                 #strip off trailing empty spaces (prevent linebreaks in xml document
    list = list.strip('"')
    varietycollcoun.append(list)                #append to varietycollcoun
#print "Country where collected:"
#print varietycollcoun

varietyunpubpre=[]
for i in range(3, len(sprlist1[37])):
    varietyunpubpre.append(sprlist1[37][i])
for i in range(0, len(varietyunpubpre)):    #for this preliminary varietyunpub
    stripstring = varietyunpubpre[i]        #convert to string
    list = stripstring.strip()             #strip off trailing empty spaces (prevent linebreaks in xml document
    list = list.strip('"')
    varietyunpub.append(list)               #append to varietyunpub
#print "Unpublished Source:"
#print varietyunpub

varietysource1pre=[]
for i in range(3, len(sprlist1[38])):
    varietysource1pre.append(sprlist1[38][i])
for i in range(0, len(varietysource1pre)):      #for this preliminary varietysource
    stripstring = varietysource1pre[i]          #convert to string
    list = stripstring.strip()                 #strip off trailing empty spaces (prevent linebreaks in xml document
    list = list.strip('"')
    varietysource1.append(list)                 #append to varietysource
#print "Source1:"
#print varietysource1

varietysource2pre=[]
for i in range(3, len(sprlist1[39])):
    varietysource2pre.append(sprlist1[39][i])
for i in range(0, len(varietysource2pre)):      #for this preliminary varietysource
    stripstring = varietysource2pre[i]          #convert to string
    list = stripstring.strip()                 #strip off trailing empty spaces (prevent linebreaks in xml document
    list = list.strip('"')
    varietysource2.append(list)                 #append to varietysource
#print "Source2:"
#print varietysource2

#Variety remarks: sprlist1[34], sprlist1[35], sprlist1[36]
varietyremarks1pre=[]
for i in range(3, len(sprlist1[34])):
    if sprlist1[34][i] != '\n' and sprlist1[34][i] != '':                 #don't append empty fields
        varietyremarks1pre.append(sprlist1[34][i])
    else:
        varietyremarks1pre.append('*')
for i in range(0, len(varietyremarks1pre)):     #for this preliminary varietyremarks
    stripstring = varietyremarks1pre[i]         #convert to string
    list = stripstring.strip()                 #strip off trailing empty spaces (prevent linebreaks in xml document
    list = list.strip('"')
    varietyremarks1.append(list)                #append to varietyremarks
#print "Remarks-1:"
#print varietyremarks1

varietyremarks2pre=[]
for i in range(3, len(sprlist1[35])):
    if sprlist1[35][i] != '\n' and sprlist1[35][i] != '':                 #don't append empty fields
        varietyremarks2pre.append(sprlist1[35][i])
    else:
        varietyremarks2pre.append('*')
for i in range(0, len(varietyremarks2pre)):     #for this preliminary varietyremarks
    stripstring = varietyremarks2pre[i]         #convert to string
    list = stripstring.strip()                 #strip off trailing empty spaces (prevent linebreaks in xml document
    list = list.strip('"')
    varietyremarks2.append(list)              #append to varietyremarks
#print "Remarks-2:"
#print varietyremarks2

varietyremarks3pre=[]
for i in range(3, len(sprlist1[36])):
    if sprlist1[36][i] != '\n' and sprlist1[36][i] != '':                 #don't append empty fields
        varietyremarks3pre.append(sprlist1[36][i])
    else:
        varietyremarks3pre.append('*')
for i in range(0, len(varietyremarks3pre)):     #for this preliminary varietyremarks
    stripstring = varietyremarks3pre[i]         #convert to string
    list = stripstring.strip()                 #strip off trailing empty spaces (prevent linebreaks in xml document
    list = list.strip('"')
    varietyremarks3.append(list)                #append to varietyremarks
#print "Remarks-3:"
#print varietyremarks3

varietyremarkspre=[]
for i in range(3, len(sprlist1[40])):
    if sprlist1[40][i] != '\n' and sprlist1[40][i] != '':                 #don't append empty fields
        varietyremarkspre.append(sprlist1[40][i])
    else:
        varietyremarkspre.append('*')
for i in range(0, len(varietyremarkspre)):      #for this preliminary varietyremarks
    stripstring = varietyremarkspre[i]          #convert to string
    list = stripstring.strip()                 #strip off trailing empty spaces (prevent linebreaks in xml document
    list = list.strip('"')
    varietyremarks.append(list)                 #append to varietyremarks
#print "Remarks:"
#print varietyremarks

#vvvvvvvvvv Varieties Information End vvvvvvvvvv


#XMLXMLXMLXMLXMLXMLXMLXMLXMLXMLXMLXMLXMLXMLXMLXMLXMLXMLXMLXMLXMLXMLXMLXMLXM

#PRODUCE XML FILE:
#print "\nXML FILE:"

outp = args.output

#header information:
encoding = '<?xml version="1.0" encoding="UTF-8"?>\n'
#print encoding
outp.write(encoding)

release = '<WordCorr release="Release 2.0" version="2.1">\n'  
#print release
outp.write(release)

#user info
userid = '<user user-id="%(id)s" family-name="%(famname)s" given-name="%(name)s" email="%(email)s">\n' %\
         {"id":userlist[0], "famname":userlist[1], "name":userlist[2], "email":userlist[4]}
#print userid
outp.write(userid)

#affiliation
affiliation = '<affiliations>%s</affiliations>\n'    % (userlist[3])
#print affiliation
outp.write(affiliation)

#collection name and shortname:
collname = '    <collection name="%(collname)s" short-name="%(collsname)s"' %\
           {"collname":colllist[0],"collsname":colllist[1]}
#print collname
outp.write(collname)

#primary and secondary gloss languages and other info:
glosslang = ' gloss-language="%(glosslg)s" gloss-language-code="%(lgcode1)s" secondary-gloss-language="%(glosslg2)s" secondary-gloss-language-code="%(lgcode2)s" creator-role="%(creatorrole)s" creator="" publisher="" rights-management="%(rights)s" rights-management-year-copyright-asserted="%(copyright)s" export-timestamp="">\n' %\
            {"glosslg":colllist[4], "lgcode1":colllist[5], "glosslg2":colllist[6], "lgcode2":colllist[7], "creatorrole":colllist[2], "rights":colllist[15], "copyright":colllist[16]}
#print glosslang
outp.write(glosslang)

#contributor
contributor = ' <contributor>%s</contributor>\n'  %(colllist[3])
#print contributor
outp.write(contributor)

#description
description = '<description>%s</description>\n'   %(colllist[9])
#print description
outp.write(description)

#collection remarks:
collrem = '        <remarks>%s</remarks>\n' % (colllist[10])
#print collrem
outp.write(collrem)

#keywords
keywords = ' <keywords>%s</keywords>\n'   %(colllist[8])
#print keywords
outp.write(keywords)

#coverage
coverage = ' <coverage>%s</coverage>\n'   %(colllist[13])
#print coverage
outp.write(coverage)

#published-source
#This creates the input for the 'published source' field.
#To avoid empty spaces or lines, the script takes into account which of the two lines
#in the spreadsheet are filled.
if colllist[11] != '' and colllist[12] != '':
    publishedsource = ' <published-source>%s</published-source>\n'    %(colllist[11]+', '+colllist[12])
#    print publishedsource
    outp.write(publishedsource)
elif colllist[11] != '' and colllist[12] == '':
    publishedsource = ' <published-source>%s</published-source>\n'    %(colllist[11])
#    print publishedsource
    outp.write(publishedsource)
elif colllist[11] == '' and colllist[12] != '':
    publishedsource = ' <published-source>%s</published-source>\n'    %(colllist[12])
#    print publishedsource
    outp.write(publishedsource)
else:
    publishedsource = ' <published-source />\n'    
#    print publishedsource
    outp.write(publishedsource)    

#stable-copy-location
stablecopylocation = ' <stable-copy-location>%s</stable-copy-location>\n'  %(colllist[14]) 
#print stablecopylocation
outp.write(stablecopylocation)

#varieties opener:
var = '        <varieties>\n'
#print var
outp.write(var)

#LOOP HERE FOR VARIETIES
n=0
for i in range(0, len(varietyname)):    #for however many varieties are there

#var(x) name, shortname, abbreviation:
    vxinf = '            <variety name="%(varname)s" short-name="%(varshortn)s" abbreviation="%(varabb)s" ethnologue-code="%(varethn)s">\n' %\
                {"varname":varietyname[i], "varshortn": varietyshortname[i], 'varabb': varietyabbr[i], 'varethn': varietyethnologue[i]}
#    print vxinf
    outp.write(vxinf)

#var(x) alternate-name-list:
    if varietyaltname[i] != '\n':
        vanl = '                <alternate-name-list>%s</alternate-name-list>\n'  %(varietyaltname[i])
#        print vanl
        outp.write(vanl)

#var(x) classification:
    if varietygenclass[i] != '\n':
        vclass = '                <classification>%s</classification>\n'  %(varietygenclass[i])
#       print vclass
        outp.write(vclass)

#var(x) locale:
    if varietylocale[i] != '\n':
        vloc = '                <locale>%s</locale>\n' % varietylocale[i]
#       print vloc
        outp.write(vloc)

#var(x) quality:str
    if varietyquality[i] != '\n':
        vqual = '                <quality>%s</quality>\n' % varietyquality[i]
#       print vqual
        outp.write(vqual)

#var(x) source:
#To avoid empty spaces or lines, the script takes into account which of the two lines
#available in the spreadsheet are filled.
    if varietysource1[i] != '' and varietysource2[i] != '':
        vsour = '                <source>%(varsour)s</source>\n' %\
                {'varsour': varietysource1[i]+', '+varietysource2[i]}
#        print vsour
        outp.write(vsour)
    elif varietysource1[i] == '':
        vsour = '                <source>%(varsour)s</source>\n' %\
                {'varsour':varietysource2[i]}
#        print vsour
        outp.write(vsour)
    elif varietysource2[i] == '':
        vsour = '                <source>%(varsour)s</source>\n' %\
                {'varsour':varietysource1[i]}
#        print vsour
        outp.write(vsour)
    else:
        vsour = '                <source />\n'
#        print vsour
        outp.write(vsour)

#var(x) unpublished source:
    vunpubsource = '                <unpublished-source>%s</unpublished-source>\n'    %(varietyunpub[i])
#    print vunpubsource
    outp.write(vunpubsource)

#var(x) country where collected:
    vccoll = '                <country-where-collected>%s</country-where-collected>\n'  %(varietycollcoun[i])
#    print vccoll
    outp.write(vccoll)

#var(x) remarks:
#This is a combination of three fields out of the spreadsheet.
#The following script checks whether the fields in question are filled,
#and if they are empty, they are not included in Variety remarks,
#in order to avoid empty spaces and lines.
    if varietyremarks1[i] != '*': #or varietyremarks1[i] != '\n':
        varietyremarks1x = 'Place where collected: '+varietyremarks1[i]
    else:
        varietyremarks1x = varietyremarks1[i]
#    print varietyremarks1x

    if varietyremarks2[i] != '*': #or varietyremarks2[i] !='\n':
        varietyremarks2x = 'Collected by: '+varietyremarks2[i]
    else:
        varietyremarks2x = varietyremarks2[i]
#    print varietyremarks2x

    if varietyremarks3[i] != '*': #or varietyremarks3[i] !='\n':
        varietyremarks3x = 'Date collected: '+varietyremarks3[i]
    else:
        varietyremarks3x = varietyremarks3[i]
#    print varietyremarks3x

#all there:
    if varietyremarks[i] != '*' and varietyremarks1[i] != '*' and varietyremarks2[i] != '*' and varietyremarks3[i] != '*':
        vrem = '                <remarks>%s</remarks>\n'  %(varietyremarks[i]+ ', ' +varietyremarks1x+', '+varietyremarks2x +', '+varietyremarks3x)
#        print vrem
        outp.write(vrem)

#varietyremarks missing:
    if varietyremarks[i] == '*' and varietyremarks1[i] != '*' and varietyremarks2[i] != '*' and varietyremarks3[i] != '*':
        vrem = '                <remarks>%s</remarks>\n'  %(varietyremarks1x+', '+varietyremarks2x +', '+varietyremarks3x)
#        print vrem
        outp.write(vrem)

#varietyremarks + varietyremarks1 missing:
    if varietyremarks[i] == '*' and varietyremarks1[i] == '*' and varietyremarks2[i] != '*' and varietyremarks3[i] != '*':
        vrem = '                <remarks>%s</remarks>\n'  %(varietyremarks2x +', '+varietyremarks3x)
#        print vrem
        outp.write(vrem)

#varietyremarks + varietyremarks2 missing:
    if varietyremarks[i] == '*' and varietyremarks1[i] != '*' and varietyremarks2[i] == '*' and varietyremarks3[i] != '*':
        vrem = '                <remarks>%s</remarks>\n'  %(varietyremarks1x+', '+varietyremarks3x)
#        print vrem
        outp.write(vrem)

#varietyremarks + varietyremarks3 missing:
    if varietyremarks[i] == '*' and varietyremarks1[i] != '*' and varietyremarks2[i] != '*' and varietyremarks3[i] == '*':
        vrem = '                <remarks>%s</remarks>\n'  %(varietyremarks1x+', '+varietyremarks2x)
#        print vrem
        outp.write(vrem)

#varietyremarks + varietyremarks1 + varietyremarks2 missing:
    if varietyremarks[i] == '*' and varietyremarks1[i] == '*' and varietyremarks2[i] == '*' and varietyremarks3[i] != '*':
        vrem = '                <remarks>%s</remarks>\n'  %(varietyremarks3x)
#        print vrem
        outp.write(vrem)

#varietyremarks + varietyremarks1 + varietyremarks3 missing:
    if varietyremarks[i] == '*' and varietyremarks1[i] == '*' and varietyremarks2[i] != '*' and varietyremarks3[i] == '*':
        vrem = '                <remarks>%s</remarks>\n'  %(varietyremarks2x)
#        print vrem
        outp.write(vrem)

#varietyremarks + varietyremarks2 + varietyremarks3 missing:
    if varietyremarks[i] == '*' and varietyremarks1[i] != '*' and varietyremarks2[i] == '*' and varietyremarks3[i] == '*':
        vrem = '                <remarks>%s</remarks>\n'  %(varietyremarks1x)
#        print vrem
        outp.write(vrem)

#varietyremarks1 missing:
    if varietyremarks[i] != '*' and varietyremarks1[i] == '*' and varietyremarks2[i] != '*' and varietyremarks3[i] != '*':
        vrem = '                <remarks>%s</remarks>\n'  %(varietyremarks[i]+ ', ' +varietyremarks2x +', '+varietyremarks3x)
#        print vrem
        outp.write(vrem)        

#varietyremarks1 + varietyremarks2 missing:
    if varietyremarks[i] != '*' and varietyremarks1[i] == '*' and varietyremarks2[i] == '*' and varietyremarks3[i] != '*':
        vrem = '                <remarks>%s</remarks>\n'  %(varietyremarks[i]+ ', ' +varietyremarks3x)
#        print vrem
        outp.write(vrem)

#varietyremarks1 + varietyremarks3 missing:
    if varietyremarks[i] != '*' and varietyremarks1[i] == '*' and varietyremarks2[i] != '*' and varietyremarks3[i] == '*':
        vrem = '                <remarks>%s</remarks>\n'  %(varietyremarks[i]+ ', ' +varietyremarks2x)
#        print vrem
        outp.write(vrem)

#varietyremarks1 + varietyremarks2 + varietyremarks3 missing:
    if varietyremarks[i] != '*' and varietyremarks1[i] == '*' and varietyremarks2[i] == '*' and varietyremarks3[i] == '*':
        vrem = '                <remarks>%s</remarks>\n'  %(varietyremarks[i])
#        print vrem
        outp.write(vrem)

#varietyremarks2 missing:
    if varietyremarks[i] != '*' and varietyremarks1[i] != '*' and varietyremarks2[i] == '*' and varietyremarks3[i] != '*':
        vrem = '                <remarks>%s</remarks>\n'  %(varietyremarks[i]+ ', ' +varietyremarks1x+', '+varietyremarks3x)
#        print vrem
        outp.write(vrem)

#varietyremarks2 + varietyremarks3 missing:
    if varietyremarks[i] != '*' and varietyremarks1[i] != '*' and varietyremarks2[i] == '*' and varietyremarks3[i] == '*':
        vrem = '                <remarks>%s</remarks>\n'  %(varietyremarks[i]+ ', ' +varietyremarks1x)
#        print vrem
        outp.write(vrem)

#all varietyremarks missing:
    if varietyremarks[i] == '*' and varietyremarks1[i] == '*' and varietyremarks2[i] == '*' and varietyremarks3[i] == '*':
        vrem = '                <remarks />\n'
#        print vrem
        outp.write(vrem)

#var(x) close
    vxclos = '            </variety>\n'
#    print vxclos
    outp.write(vxclos)

#varieties close:
varclos = '        </varieties>\n'
#print varclos
outp.write(varclos)

#LOOP HERE FOR DATA AND GLOSS, generator for entry number:
#data open:
data = '        <data>\n'
#print data
outp.write(data)

#Data starting line 65:
#entry# | gloss1 | gloss2 | var1 | var2 | etc.

#complete data, all info:
entrylist=[]
for i in range(43, len(sprlist1)):
    entrylist.append(sprlist1[i])
#print entrylist

#entrynumbers:
entrynumbers=[]
for i in range(43, len(sprlist1)):
    if sprlist1[i][0] != '':
        entrynumbers.append(sprlist1[i][0])
#print entrynumbers

#for i in range(43, len(sprlist1)):
#    print sprlist1[i]
#print '*******************'

#gloss1:
gloss1=[]
for i in range(43, len(sprlist1)):
    list = sprlist1[i][1].strip('"').strip()
    gloss1.append(list)
#print gloss1

#gloss2:
gloss2=[]
for i in range(43, len(sprlist1)):
    list = sprlist1[i][2].strip('"').strip()
    gloss2.append(list)
#print gloss2

#data:
#sprlist1: #, gl1, gl2, var1dat, var2dat, var3dat, var4dat, etc.
datapre=[]
for i in range(43, len(sprlist1)):          #excluding metadata
    for j in range(3, len(varietyname)+3):  #data only, '+3' to get all data (first three items are #, gl1, gl2, then all variety data, '+3' to make up for first three skipped
        datapre.append(sprlist1[i][j])

#this a list containing all datums in the following order:
#var1 dat1, var2 dat1, etc., var1 dat2, var2 dat2, etc.

datastrip=[]
for i in range(0, len(datapre)):
    strip = datapre[i]      #convert to string
    list = strip.strip()   #strip off trailing empty spaces (prevent linebreaks in xml document)
    list = list.strip('"')
    list = list.strip('\n')
    datastrip.append(list)  #append to data
#for i in range(0, 50):
#    print [i]
#    print datastrip[i]

#split multiple data per entry/variety:
#The Text (*.txt) file format saves only the text and values as they are displayed
#in cells of the active worksheet. All rows and all characters in each cell are saved.
#Columns of data are separated by tab characters, and each row of data ends in a
#carriage return. If a cell contains a comma, the cell contents are enclosed in double quotation marks
#which is stripped off in the script above. 
splitstring = ''
datasplit = []
list = ''
for i in range(0, len(datastrip)):
    splitstring = datastrip[i]          #this makes the list splitable
    list = splitstring.split(',')      #separate multiple data
    datasplit.append(list)     

#mult. datums are split, but still belong together per variety

#count number of varieties in data
varieties=[]
for i in range(26, 27):
    del sprlist1[i][0]
for i in range(2, len(sprlist1[26])):
    if sprlist1[26][i] != '\n' and sprlist1[26][i] != '':
        varieties.append(sprlist1[26][i])
#print varieties
#print '######################'

#entry number, gloss1, gloss2
m=0
for i in range(0, len(entrynumbers)):              #full length: entrynumbers
    if entrynumbers[i] != '' and entrynumbers[i] != '\n':
            entrynumgl = '            <entry entry-number="%(no)s" gloss="%(gloss1)s" secondary-gloss="%(gloss2)s">\n' %\
                                {'no' : entrynumbers[i], 'gloss1' : gloss1[i], 'gloss2':gloss2[i]}
#        print entrynumgl
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
        for k in range(0, len(datasplit[i+l+m])):
            if datasplit[i+l+m][k] != '' and datasplit[i+l+m][k] != '\n':
                datum = '                <datum datum-number="%(no)s" short-name="%(varshortn)s" datum="%(datm)s">\n' %\
                    {'no' : i+k+m+l, 'varshortn' : varietyshortname[l], 'datm' : (datasplit[i+l+m][k]).strip()}    
#                print datum
                outp.write(datum)   #.encode('utf-8'))   #encode as unicode

#special semantics of datum
                specsem = '                    <special-semantics />\n'
#                print specsem
                outp.write(specsem)
       
#remarks for datum
                datrem = '                    <remarks />\n'
#                print datrem
                outp.write(datrem)
    
#close datum
                datcls = '                </datum>\n'
#               print datcls
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
for i in range(0, len(varietyname)):    #for all varieties
    viewmem = '                <view-member short-name="%(varshortn)s" order-number="%(no)s" />\n' %\
            {'varshortn': varietyshortname[i], 'no':i+1}
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
