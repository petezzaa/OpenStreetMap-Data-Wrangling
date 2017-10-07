import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
import schema

OSM_PATH = "County_of_Hawaii.osm"

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

def update_name(name, key):
    """Programtically update names for street names that must be fixed."""
    expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Loop", "Highway", "Circle", "North", "South", "East", "West", "Way", ""]
    unexpected = ["Trl", "Roadd",'Ave', 'Ave.', 'Rd', 'St', 'Traill']
    mapping = { "Trl": "Trail",
            "Roadd": "Road",
            'Ave': 'Avenue',
            'Ave.': 'Avenue',
            'Rd': 'Road',
            'St': 'Street',
            'Traill':  'Trail'
            }
    
    key = key
    #Use titlecase to make street names that are in lowercase have uppercase letters for the first letter in each word
    name = titlecase(name)
    #Correct street names with abbreviated cardinal directions to be unabbreviated
    words = name.split()
    words = set(words)    #Create a set of words in the street name
    if words.intersection(['E', 'W', 'S', 'N']) != set():  #Check if N, S, E, or W is in the street name 
        if words.intersection(['Building', 'Road', 'Drive', '330']) == set():  #Exclude way names such "Building E" or "Road A"
            if 'S' in words:    #Replace the abbreviation with the appropriate unabbreviated direction
                name = name.replace('S', 'South')
                key = 'street'
            elif 'N' in words:
                name = name.replace('N', 'North')
                key = 'street'
            elif 'E' in words:
                name = name.replace('E', 'East')
                key = 'street'
            else:
                name = name.replace('W', 'West')
                key = 'street'
    #Replace all other abbreviations with unabbreviated names such as Street for St.
    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        if street_type in unexpected:
            new_road_type = mapping[street_type]
            road_name = name.rsplit(None, 1)[:-1]
            name = road_name[0] + ' ' + new_road_type
            key = 'street'
        elif street_type in expected:
            key = 'street'
        if len(street_type) == 1:  #Check is the last word in the street name is just one letter
            if name.startswith('Rd'):  #For example update Rd. A to Road A.  Do not update Building A to Road A.
                name = 'Road' + ' ' + street_type
                key = 'street'
    
    return name, key    #If name is a street name, change the key to "street."  If name is not a street is not a street name the key input will be returned.


def test_street():
    st_types = audit(OSMFILE)
    #pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name
            
#test_street()

def update_zip(zip_code):
    """Update erroneous zip codes"""
    if zip_code == '96770':    
        return '96785'    #Fix the zip code for Mauna Loa Estates
    elif zip_code == 'HI':
        return '96740'    #Fix zip code for Oahu Building
    elif zip_code == '99723':
        return '96720'    #Fix the zip code for Hilo Chevron
    else:
        return zip_code
        
def test_zip():
    zips = audit_zip_codes(OSMFILE)
    #pprint.pprint(dict(zips))
    
    for code in zips:
        better_zip = update_zip(code)
        print code, "=>", better_zip
    
#test_zip()

def update_phones(phone_number):
    """Updates phone numbers to the form (area code)-XXX-XXXX"""
    just_numbers = re.findall('\d+', phone_number)    #Find only digits in the phone number ie ignore "+", "(", ")", " "
    if len(just_numbers) == 4:
        return '(' + just_numbers[1] + ')' + '-' + just_numbers[2] + '-' + just_numbers[3]
    elif len(just_numbers) == 3:
        if just_numbers[0] == '1':
            return '(' + just_numbers[1] + ')' + '-' + just_numbers[2][0:3] + '-' + just_numbers[2][3:]
        else:
            return '(' + just_numbers[0] + ')' + '-' + just_numbers[1] + '-' + just_numbers[2]
    elif len(just_numbers) == 2:
                return '(808)' + '-' + just_numbers[0] + '-' + just_numbers[1]
    else:
        if just_numbers[0][0:3] == '808':
            return '(' + just_numbers[0][0:3] + ')' + '-' + just_numbers[0][3:6] + '-' + just_numbers[0][6:]
        else:
            return '(808)' + '-' + just_numbers[0][0:3] + '-' + just_numbers[0][3:]

def test_phone():
    phones = audit_phones(OSMFILE)
    #pprint.pprint(set(phones))
    
    for number in phones:
            better_number = update_phones(number)
            print number, "=>", better_number
    
#test_phone()

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # YOUR CODE HERE
    
    def child_tag(elem_tag):
        for child in element.iter():
            tag = {}
            #print child
            if child.tag == 'tag':
                #print element.attrib['id']
                k = child.attrib['k']
                #print k
                if LOWER_COLON.search(k):
                    new_k = k.split(':', 1)
                    tag['id'] = element.attrib['id']
                    tag['key'] = new_k[1]
                    if k == 'addr:street':
                        tag['value'] = update_name(child.attrib['v'], new_k[1])[0]  #Update street names
                    elif k == 'addr:postcode':
                        tag['value'] = update_zip(child.attrib['v'])  #Update zip codes
                    elif k == "contact:phone":
                        tag['value'] = update_phones(child.attrib['v'])  #Update phone numbers
                    else:
                        tag['value'] = child.attrib['v']
                    tag['type'] = new_k[0]
                    #print tag
                    tags.append(tag)
                elif PROBLEMCHARS.search(k):
                    continue
                else:
                    tag['id'] = element.attrib['id']
                    tag['key'] = k
                    tag['value'] = child.attrib['v']
                    if elem_tag == 'way':
                        if k == 'name':
                            tag['value'] = update_name(child.attrib['v'], k)[0]  #Update street names
                            tag['key'] = update_name(child.attrib['v'], k)[1]  #Update key to "street"
                    tag['type'] = default_tag_type
                    #print tag
                    tags.append(tag)

    if element.tag == 'node':
        for node_field in node_attr_fields:
            node_attribs[node_field] = element.attrib[node_field]
            
        child_tag(element.tag)

        return {'node': node_attribs, 'node_tags': tags}
    
    elif element.tag == 'way':
        for field in way_attr_fields:
            way_attribs[field] = element.attrib[field]
            
        child_tag(element.tag)
        
        n = 0
        for child in element.iter():
            if child.tag == 'nd':
                node = {}
                node['id'] = element.attrib['id']
                node['node_id'] = child.attrib['ref']
                node['position'] = n
                way_nodes.append(node)
                n += 1
        
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
        

# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)