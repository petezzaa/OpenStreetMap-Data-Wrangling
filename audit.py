import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
from titlecase import titlecase
import bs4
from urllib import urlopen as ureq
from bs4 import BeautifulSoup

OSMFILE = "County_of_Hawaii.osm"

#Modified code from the Case Study lesson
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Loop", "Highway", "Circle", "South", "Way"]

#Unexpected is a list of names that were not in the expected list above that need to be changed
unexpected = ["Trl", "Roadd", "place", "street", "trail", 'Ave', 'Ave.', 'Rd', 'St', 'Traill']

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
            

def is_street_name_way(elem):
    """Checks if there is a tag with the k attribute "name" for a way tag"""
    return elem.attrib['k'] == "name"

def is_street_name_node(elem):
    """Checks if there is a tag with the k attribute "add:street" for a node tag"""
    return elem.attrib['k'] == "addr:street"

def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name_way(tag):
                    audit_street_type(street_types, tag.attrib['v'])
        elif elem.tag == "node":
            for tag in elem.iter("tag"):
                if is_street_name_node(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types

def test_street():
    st_types = audit(OSMFILE)
    pprint.pprint(dict(st_types))
    
test_street()

#Scrape from a webpage a list of all the zip codes used in the County of Hawaii using Beautiful Soup
my_url = 'http://www.zipcodestogo.com/Hawaii/HI/'
uclient = ureq(my_url)
html_page = uclient.read()
uclient.close()
soup = BeautifulSoup(html_page, 'html.parser')

expected_zip_list = []
table = soup.find('table', {'width': '100%'})
for zip_code in table.find_all('tr')[3:]:   #skip first three results in table since they contain table headings not zip codes
    a = str(zip_code.td.find('a'))
    expected_zip_list.append(re.findall(r'>(.*?)<', a)[0])    #use regex to extract the zipcode from the a tag and append it to the list
    
def audit_zip(zip_codes, zip_code):
    if zip_code not in expected_zip_list:
        zip_codes.add(zip_code)          

def is_zip_code(elem):
    return elem.attrib['k'] == "addr:postcode"

def audit_zip_codes(osmfile):
    osm_file = open(osmfile, "r")
    zip_codes = set()
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_zip_code(tag):
                    audit_zip(zip_codes, tag.attrib['v'])
    osm_file.close()
    return zip_codes

def test_zip():
    zips = audit_zip_codes(OSMFILE)
    pprint.pprint(set(zips))
    
test_zip()

def audit_phone(phone_types, phone_number):
    phone_types.add(phone_number)
          
def is_phone_number(elem):
    return elem.attrib['k'] == ("phone" or "contact:phone")
    
def audit_phones(osmfile):
    osm_file = open(osmfile, "r")
    phone_types = set()
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag =="way":
            for tag in elem.iter("tag"):
                if is_phone_number(tag):
                    audit_phone(phone_types, tag.attrib['v'])
    osm_file.close()
    return phone_types

def test_phone():
    phones = audit_phones(OSMFILE)
    pprint.pprint(set(phones))

test_phone()