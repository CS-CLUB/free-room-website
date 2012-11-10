#!/usr/bin/env python
# A script which parses the course entries displayed by the UOIT
# website http://www.uoit.ca/mycampus/avail_courses.html and stores
# each of the rooms, times t	ey are used, and other important information
# in a database
from BeautifulSoup import BeautifulSoup
from urllib import FancyURLopener
from termcolor import colored
from datetime import *
from regex import *
#from dbinterface import *
from util import *
import string
import sys
import traceback

################################################################################
# 
# The Opener class, define the browser user agent used
#
################################################################################
class Opener(FancyURLopener):
	version = 'Mozilla/5.0 (X11; Linux i686; rv:5.0) Gecko/20100101 Firefox/5.0'



################################################################################
# 
# Function which returns the html content of the course lookup
#
################################################################################
def CourseContent(url):
    content = BeautifulSoup(Opener().open(url).read())
    return content



################################################################################
# 
# Function which returns a url to get the course schedule based on the
# campus and faculty
#
################################################################################
def getURL(campus, faculty, semester, year):
    url = 'https://ssbprod.aac.mycampus.ca/prod/bwckschd.p_get_crse_unsec'
    url += '?TRM=U&begin_ap=a&begin_hh=0&begin_mi=0&end_ap=a&end_hh=0&end_mi=0&sel_attr=dummy'
    url += campuses[campus]
    url += '&sel_crse=&sel_day=dummy&sel_from_cred=&sel_insm=dummy&sel_instr=dummy&sel_levl=dummy&sel_ptrm=dummy'
    url += '&sel_schd=dummy&sel_sess=dummy&sel_subj=dummy&sel_subj='
    url += faculty
    url += '&sel_title=&sel_to_cred=&term_in='
    url += year
    url += semester
    return url



################################################################################
# 
# Function that stores course data in the database, accepts the 3-D dictionary
# generated by the get_course_data function
#
# TODO Clean up this mess of a function....
# TODO add support for this to use all the new functions in db-interface
################################################################################            
def store_course_data(con, course_data):
    # Algorithm for storing the data:
    # for each key 0..
        # for each key that is a..z (alphanumeric)
            # if table does not exist for current room [0..][a..][room_number]
                # create new table
            # insert into table all the values for current [0..][a..][<keys>]
            # and the values from the [0..][<keys>]
    for idx_key in course_data:
        for alp_key in course_data[idx_key]:
            if re.match(re.compile(r'^[a-zA-Z]{1}$'), alp_key):
                # Some courses such as capstone and online courses don't have a room
                #if 'room_number' not in course_data[idx_key][alp_key] or \
                #    'day' not in course_data[idx_key][alp_key]:
                #    break
                    
                #if 'start_time' not in course_data[idx_key][alp_key] and \
                #    'finish_time' not in course_data[idx_key][alp_key]:
                #    break
                
                # If table does not exist for current room, create a new table
                #if table_exists(con, course_data[idx_key][alp_key]['room_number']) is False:
                #    print "CREATING TABLE", course_data[idx_key][alp_key]['room_number']
                #    create_table_room(con, course_data[idx_key][alp_key]['room_number'])
                # Insert the data for the current table
                try:
                    if course_data[idx_key]['teacher_name'] is not None \
                        and len(course_data[idx_key]['teacher_name']) == 2:
                            teacher_name = ' '.join(course_data[idx_key]['teacher_name'])
                    

                    # Print out 'NONE' in red for anything that's set as None
                    for key in course_data[idx_key]:
                        if course_data[idx_key][key] is None:
                            course_data[idx_key][key] = colored('NONE', 'red')

                    for key in course_data[idx_key][alp_key]:
                        if course_data[idx_key][alp_key][key] is None:
                            course_data[idx_key][alp_key][key] = colored('NONE', 'red')

                    print "COURSE CRN:", course_data[idx_key]['crn']
                    print "PROGRAM CODE:", course_data[idx_key]['program_code']
                    print "COURSE CODE:", course_data[idx_key]['course_code']
                    print "TEACHER NAME:", course_data[idx_key]['teacher_name']

                    print "CAPACITY:", course_data[idx_key]['capacity']
                    print "REGISTERED:", course_data[idx_key]['registered']

                    print "WEEK ALT:", course_data[idx_key][alp_key]['week_alt']
                    print "START TIME:", course_data[idx_key][alp_key]['start_time']
                    print "FINISH TIME:", course_data[idx_key][alp_key]['finish_time']
                    print "DAY OF WEEK:", course_data[idx_key][alp_key]['day']
                    print "ROOM:", course_data[idx_key][alp_key]['room_number']
                    print "START DATE:", course_data[idx_key][alp_key]['date_start']
                    print "FINISH DATE:", course_data[idx_key][alp_key]['date_finish']
                    print "CLASS TYPE:", course_data[idx_key][alp_key]['class_type'], "\n"

                    """     
                    cur = con.cursor()
                    cur.execute("INSERT INTO %s VALUES ('%c', '%s', '%s', '%s', '%s', '%s', '%s', %d, " \
                                "%d, %d, %d, '%s', '%s', '%s', '%s', '%s', '%s', '%s');" \
                                    % ( course_data[idx_key][alp_key]['room_number'], 
                                        course_data[idx_key][alp_key]['day'], 
                                        course_data[idx_key][alp_key]['start_time'], 
                                        course_data[idx_key][alp_key]['finish_time'], 
                                        course_data[idx_key][alp_key]['date_start'], 
                                        course_data[idx_key][alp_key]['date_finish'],
                                        course_data[idx_key][alp_key]['class_type'], 
                                        teacher_name, 
                                        int(course_data[idx_key][alp_key]['week1']), 
                                        int(course_data[idx_key][alp_key]['week2']), 
                                        int(course_data[idx_key]['capacity']), 
                                        int(course_data[idx_key]['registered']), 
                                        course_data[idx_key]['term'][0], 
                                        course_data[idx_key]['crn'], 
                                        course_data[idx_key]['course_name'], 
                                        course_data[idx_key]['program_code'], 
                                        course_data[idx_key]['course_code'], 
                                        course_data[idx_key]['course_section'],  
                                        course_data[idx_key]['campus']
                                      ))
                    """
                except:
                    #print "Error %d: %s" % (e.args[0],e.args[1])
                    traceback.print_exc(file=sys.stdout)
                    sys.exit(1)



################################################################################
# 
# Function which parses the data and stores it in a multidimensional dictionary 
# with the following structure
#
#    <--                            dictionary                   -->
#    <key>               <--              dictionary             -->
#                                          <--     dictionary    -->
#                        <key>               <key>               <value>
#    {'0'     =>    {    {'a'        =>    'day'          =>  'M/T/W/R/F'
#                                          'start_time'   =>  ('8:10', 'am')
#                                          'finish_time'  =>  ('10:00', 'am')
#                                          'date_start'   =>  ('Jan', '09', '2012')
#                                          'date_finish'  =>  ('Apr', '13', '2012')
#                                          'class_type'   =>  'LEC/TUT/LAB'                    
#                                          'room_number'  =>  'UA1350'
#                                          'week1'        =>  True/False
#                                          'week2'        =>  True/False
#                         }
#                         'teacher_name' =>  ('Judith', 'Grant')
#                         'capacity'     =>  250
#                         'registered'   =>  236
#                         'term'         =>  ('Winter', '2012')
#                         'crn'          =>  '70483'
#                         'course_name'  =>  'Introductory Sociology'
#                         'program_code' =>  'SOCI'
#                         'course_code'  =>  '1000U'
#                         'course_secion'=>  '001'
#                         'campus'       =>  'UON/UOD/UOG'
#                   }
#    }
#
################################################################################
def get_course_data(campus, faculty, semester, year):
    # 3-D dictionary containing the course data and index keys
    course_data = {}

    # Get the html content from the uoit class schedule listing webpage
    course_content = CourseContent(getURL(campus, faculty, semester, year))
    
    # Parse all the course information in the first section of table
    parse_course_info(course_content, course_data)
    
    # Parse all the registration information in the second table
    parse_reg_info(course_content, course_data)
    
    # Parse all the classroom meeting times in the third table
    parse_class_time(course_content, course_data)
    
    return course_data



################################################################################
# 
# Function which parses all the course information in the first section of table
#
# Arguments are the BeatifulSoup object course_content containing the website
# HTML content and a 3-D dictionary containing the course data and index keys 
# which is used by get_course_data()
#
################################################################################
def parse_course_info(course_content, course_data):
    # Parses all the course information in the first table
    for course_table in course_content.findAll('table', {'class': "datadisplaytable", 'summary': 
                                "This layout table is used to present the sections found"}):
        # Finds all instances of course info
        idx_key = 0
        for row in course_table.findAll('th', {'class': "ddheader", 'scope': "col"}, True, re_course_info):
            match = re_course_info.search(str(row).strip())
            if match is not None:
                ##print "course info", idx_key
                # Store the course information parsed 3-D dictionary, course_data
                (course_name, crn, program_code, course_code, course_section) = match.group(1, 2, 3, 4, 5)
                # Remove all punctuation for the course name
                course_data[idx_key] = {'course_name': course_name.translate(string.maketrans("",""), string.punctuation)}
                course_data[idx_key]['crn'] = crn
                course_data[idx_key]['program_code'] = program_code
                course_data[idx_key]['course_code'] = course_code
                course_data[idx_key]['course_section'] = course_section
                idx_key += 1
                
        # Finds all instances of course term info
        idx_key = 0
        for row in course_table.findAll('span', {'class': "fieldlabeltext"}, True, re.compile(r'Associated\sTerm\:\s')):
            match = re_course_term.search(str(row.next).strip())
            if match is not None:
                #print "course term", idx_key
                course_data[idx_key]['term'] = match.group(2, 3)
                idx_key += 1
                     
        # Finds all instances of campus
        idx_key = 0
        for row in course_table.findAll(['span', 'b'], {'class': "fieldlabeltext"}, True, re.compile(r'Campus')):
            match = re_campus.search(str(row).strip())
            if match is not None:
                # Store the acronym for each campus, lookup acronym in dictionary
                #print "campus", idx_key
                course_data[idx_key]['campus'] = reverse_lookup(campus_acronyms, match.group(2).strip())
                idx_key += 1
            # TODO this needs to be handled because online courses are still linked to campus even thoug there is no room
            else:
               course_data[idx_key]['campus'] = None 

        # Parse the professors name
        idx_key = 0
        for meeting_table in course_table.findAll('table', {'class': "bordertable", 'summary': 
                                "This table lists the scheduled meeting times and assigned instructors for this class."}):
            # Grab the 2nd <tr> of meetings times table, to get the professors name
            for row in meeting_table.findAll('tr')[1:2]:
                for column in row.findAll('td', {'class': "dbdefault"}, True)[7:8]:
                    match = re_prof_name.search(str(column).strip())
                    
                    # Fuck guido I should be able to use this comparison...
                    # if (match.group(1), match.group(2)) is not (None, None):
                    if match.group(1) is not None or match.group(2) is not None:
                        course_data[idx_key]['teacher_name'] = match.group(1, 2)
                    # professor listed as TBA, None specfied for course
                    elif match.group(3) is not None:
                        course_data[idx_key]['teacher_name'] = None
                    # No professor name listed, None specfied for course
                    else:
                        course_data[idx_key]['teacher_name'] = None
                    idx_key += 1


                    

################################################################################
# 
# Function which parses all the registration information in the second table
#
# Arguments are the BeatifulSoup object course_content containing the website
# HTML content and a 3-D dictionary containing the course data and index keys 
# which is used by get_course_data()
#
################################################################################
def parse_reg_info(course_content, course_data):
    # Parses all the registration information in the second table
    idx_key = 0
    for reg_table in course_content.findAll('table', {'class': "bordertable", 'summary': 
                            "This layout table is used to present the seating numbers."}):
        # Finds all instances of the capacity
        for row in reg_table.findAll('td', {'class': 'dbdefault'}, True, re_capacity)[0:1]:
            # Store the capacity of the room
            course_data[idx_key]['capacity'] = int(row)
            
        # Finds all instances of the number students registered
        for row in reg_table.findAll('td', {'class': 'dbdefault'}, True, re_capacity)[1:2]:
            # Store the number students registered
            course_data[idx_key]['registered'] = int(row)
            idx_key += 1



################################################################################
# 
# Function which parses all the classroom meeting times in the third table
#
# Arguments are the BeatifulSoup object course_content containing the website
# HTML content and a 3-D dictionary containing the course data and index keys 
# which is used by get_course_data()
#
################################################################################
def parse_class_time(course_content, course_data):
    # Parses all the classroom meeting times
    idx_key = 0
    for meeting_table in course_content.findAll('table', {'class': "bordertable", 'summary': 
                            "This table lists the scheduled meeting times and assigned instructors for this class."}):
        # Find all the classroom meeting time info for each day
        alp_key = 'a'
        for row in meeting_table.findAll('tr'):
            ### Each column is the information for each day the classroom is used
            # Parse the week info, if room is used during week1, week2, or both
            for column in row.findAll('td', {'class': "dbdefault"}, True, re_week_info)[0:1]:
                # NO ALTERNATING WEEKS
                if re.match(re.compile(r'^&nbsp;$'), column.strip()):
                    course_data[idx_key][alp_key] = {'week_alt': None}
                # WEEK 1 ALTERNATING
                elif re.match(re.compile(r'^(&nbsp;)*W1$'), column.strip()):
                    course_data[idx_key][alp_key] = {'week_alt': True}
                # WEEK 2 ALTERNATING
                elif re.match(re.compile(r'^(&nbsp;)*W2$'), column.strip()):
                    course_data[idx_key][alp_key] = {'week_alt': False}
                    
            # Parse the course start and end time
            for column in row.findAll('td', {'class': "dbdefault"}, True)[2:3]:
                match = re_course_time.search(str(column).strip())
                if match is not None:
                    course_data[idx_key][alp_key]['start_time'] = convert_time(match.group(1, 2))
                    course_data[idx_key][alp_key]['finish_time'] = convert_time(match.group(3, 4))
                # The course does NOT have specific times for classes
                else:
                    course_data[idx_key][alp_key]['start_time'] = None
                    course_data[idx_key][alp_key]['finish_time'] = None
                    
            # Parse the course day of the week (single char, ie. M for Monday)
            for column in row.findAll('td', {'class': "dbdefault"}, True)[3:4]:
                match = re_course_day.search(str(column).strip())
                if match is not None:
                    course_data[idx_key][alp_key]['day'] = match.group(1)
                # The course does NOT have specific days for classes
                else:
                    course_data[idx_key][alp_key]['day'] = None
                    
            # Parse the room, right now only gets room number (ie. UA1350)
            for column in row.findAll('td', {'class': "dbdefault"}, True)[4:5]:
                # If it is an online course (ie. ONLINE) then there is no room specified
                # TODO online courses have no room but have a CAMPUS, may need to investigate handling this
                # for DB insert operations...
                # TODO this has to be here to handline instances such as ONLINE2 as it screws up the room number
                # for online courses where classroom is ONLINE2 the second regex will parse INE2.... lol
                match = re_room_online.search(str(column).strip())
                if match is not None:
                    course_data[idx_key][alp_key]['room_number'] = None
                    continue

                # Otherwise get the room number (ie. UA1350)    
                match = re_room.search(str(column).strip())
                if match is not None:
                    course_data[idx_key][alp_key]['room_number'] = match.group(1)
                # TODO see if there are any where the location is just blank...
                else:
                    course_data[idx_key][alp_key]['room_number'] = None
                    
            # Parse the course start and end date
            for column in row.findAll('td', {'class': "dbdefault"}, True)[5:6]:
                match = re_course_date.search(str(column).strip())
                if match is not None:
                    course_data[idx_key][alp_key]['date_start']  = convert_date(match.group(1, 2, 3))
                    course_data[idx_key][alp_key]['date_finish'] = convert_date(match.group(4, 5, 6))
                # TODO are there any courses where the start/end date is not specified? Should the DB require
                # a start and end date for a course, atm it can be NULL
                else:
                    course_data[idx_key][alp_key]['date_start']  = None
                    course_data[idx_key][alp_key]['date_finish'] = None
                    
            # Parse the type of class, Lecture, Tutorial, Laboratory
            for column in row.findAll('td', {'class': "dbdefault"}, True)[6:7]:
                match = re_class_type.search(str(column).strip())
                if match is not None:
                    #print "CLASS TYPE: ", ">>" + match.group(1) + "<<"
                    course_data[idx_key][alp_key]['class_type'] = reverse_lookup(class_types, match.group(1).strip())
                    #print "\n\nDEBUG:"
                    #print idx_key
                    #print alp_key
                    #print course_data[idx_key][alp_key]
                # TODO look for unhandled class types, need to add them to dictionary
                else:
                    course_data[idx_key][alp_key]['class_type'] = None
                
                alp_key = chr(ord(alp_key) + 1)

        idx_key += 1


# Mysql Database connection information
con = None
user = 'jon'
passwd = 'test123'
domain = 'localhost'


# Dictionary mapping campus acronyms to the full campus name
campus_acronyms = { 'UON': 'North Oshawa Campus',
                    'UOD': 'Downtown Oshawa Campus',
                    'UOG': 'Campus-Georgian Campus',
                    'TRN': 'Trent at Oshawa Thornton Campus',
                    'WEB': 'Web Course' }

# Dictionary mapping class types to acronyms
class_types =  {'LEC': 'Lecture', 
                'TUT': 'Tutorial', 
                'LAB': 'Laboratory', 
                'THS': 'Thesis/Project', 
                'WEB': 'Web Course',
                'SEM': 'Seminar',
                'FLD': 'Field Placement'}

# Dictionary mapping the semesters to the appropriate post data
semester = {'winter': '01', 'fall': '09', 'summer': '05'}

# Current month, year semester
cur_month = datetime.now().month
cur_year = str(datetime.now().year)     # Year is ALWAYS used as a string
cur_semester = None

# Dictionary mapping campus querys to the appropriate post data
campuses = generate_dictionary('campuses', ' ')

# Dictionary of faculties mapping faculty acronyms to full faculty name
faculties = generate_dictionary('faculties', ' - ')


# Get the current semester based on the current month, anything from 01 - 04
# is winter, 05 - 08 is summer, 09 - 12 is winter
if cur_month >= 1 and cur_month < 5:
    cur_semester = 'winter'
elif cur_month >= 5 and cur_month < 9:
    cur_semester = 'summer'
else:
    cur_semester = 'fall'


# Create a new database for the current semester and year, if
# an existing database exists it will be deleted and overwritten
#con = connect_db(user, passwd, domain, '')
#create_db(con, cur_semester, cur_year)
#con = connect_db(user, passwd, domain, cur_semester + str(cur_year))


# Get the course data for each faculty and store it in the database
for faculty in faculties:
    course_data = get_course_data('ALL', faculty, semester[cur_semester], cur_year)
    store_course_data(con, course_data)
    
# Finally, close connection to database
#con.close()
