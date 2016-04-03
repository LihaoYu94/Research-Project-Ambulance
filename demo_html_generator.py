#######
#BRIEF
#######
# Creates a demo html file that fills in the ambulance and calls data structures that are then fed into the viusalizer js script
# Name: Aayush Kumar (aayushk@andrew.cmu.edu)

##############
# ASSUMPTIONS
##############
# Assumes that the csv file is sorted according to time of call
# Assumes order of columns of the availed, busy, snr & unavailed files to be:
# CallID, lat, lng, Call Time, Total Time, Vehicle Number, Segment ID
# Note that in the vehicle busy case, there will be no associated ambulance number.  Leave that column blank (but do include it).
# Assumes order of ambulance active and inactive files to be:
# lat, lng, vehicle number


from datetime import datetime
from datetime import timedelta
from sets import Set

###################
# INPUT FILE NAMES
###################

# These are the input files needed
availed_file = "./availed.csv"
busy_file = "./busy.csv"
snr_file = "./snr.csv"
unavailed_file = "./unavailed.csv"

amb_active_file = "./amb_active_segs.csv"
amb_inactive_file = "./amb_inactive_segs.csv"
#amb_active_file = "simulator/current_ambulances.csv"
#amb_inactive_file = "./empty.csv"

interArrival  = "./seg_interArrival_rate.csv"

# Output html file name
html_file = "./demo_script.html"  

time_to_display_busy_marker = timedelta(hours=1)
time_to_display_snr_marker = timedelta(hours=1)

# Number of colored circles (each) to display
num_circles = 10

# Class that holds information about a patient call
class victim_t:
    #v_type: 0->availed, 1->busy, 2->SNR, 3->unavailed
    v_type=-1
    victim_lat=0
    victim_lng=0
    start_time=-1
    end_time=-1
    amb_num=-1
    victim_num = -1
    initialized = -1
    call_id = -1

# Class that holds information about an ambulance
class ambulance_t:
    lat=0
    lng=0
    seg_id = -1
    amb_num = -1
    arrival_rate = -1
    status = -1  #(0 for free, 1 for busy)

    def __cmp__(self, other):
        if (self.arrival_rate > other.arrival_rate):
            return 1
        elif (self.arrival_rate < other.arrival_rate):
            return -1
        else:
            return 0

    def __eq__(self, other):
        if (__cmp__(self, other) == 0):
            return True
        else:
            return False
    
    def __ne__(self, other):
        if (__cmp__(self, other) == 0):
            return False
        else:
            return True

# Writes the top part of a HTML File
def write_html_file_top():
    html_file.write("<html>\n\t")
    html_file.write("<head>\n\t\t")
    html_file.write("<style>\n\t\t\t")
    html_file.write("#demo-frame > div.demo { padding: 10px !important; };\n\t\t")
    html_file.write("</style>\n\t\t")
    html_file.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"visualizer.css\"></script>\n\t\t")
    html_file.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"jqueryui/css/smoothness/jquery-ui-1.7.2.custom.css\">\n\t\t")
    html_file.write("<script type=\"text/javascript\" src=\"jqueryui/js/jquery-1.3.2.min.js\"></script>\n\t\t")
    html_file.write("<script type=\"text/javascript\" src=\"jqueryui/js/jquery-ui-1.7.2.custom.min.js\"></script>\n\t\t")
    html_file.write("<script type=\"text/javascript\" src=\"http://maps.google.com/maps/api/js?sensor=false\"></script>\n\t\t")
    html_file.write("<script type=\"text/javascript\" src=\"visualizer.js\"></script>\n\t\t")
    html_file.write("<script type=\"text/javascript\" src=\"controls.js\"></script>\n\t\t")
    html_file.write("<script type=\"text/javascript\">\n\t\t\t")
    html_file.write("function initialize() {\n\t\t\t\t")
    html_file.write("// generating bases\n\t\t\t\t")
    html_file.write("// bases are indexed by segment id (for now)\n\t\t\t\t")
    html_file.write("var bases = new Array();\n\t\t\t\t")
    html_file.write("// generating calls.  calls need to be indexed in order starting from 0.  So all calls are pushed onto the array\n\t\t\t\t")
    html_file.write("var calls = [];\n\t\t\t\t")


# Writes the bottom part of a HTML File
def write_html_file_bottom():
    html_file.write("// initializing controls such as slider bar. This needs to be called after Visualizer starts\n\t\t\t\t")
    html_file.write("initControls();\n\t\t\t")
    html_file.write("}\n\t\t")
    html_file.write("</script>\n\t")
    html_file.write("</head>\n\t")
    html_file.write("<body onload=\"initialize()\">\n\t\t")
    html_file.write("<div id=\"map_canvas\" style=\"width:100%; height:100%;\"></div>\n\t\t")
    html_file.write("<div id=\"slider_container\">\n\t\t\t")
    html_file.write("<center>\n\t\t\t\t")
    html_file.write("<div name=\"slider\" id=\"slider\"></div>\n\t\t\t\t")
    html_file.write("<input type=\"text\" id=\"txt\" style=\"width:260px;\">\n\t\t\t\t")
    html_file.write("<button id=\"start_stop\">play/pause</button>\n\t\t\t")
    html_file.write("</center>\n\t\t")
    html_file.write("</div>\n\t")
    html_file.write("</body>\n")
    html_file.write("</html>")


ambulance = []
segCountMap = {}
html_file = open(html_file, 'w')

# Declares a new ambulance in demo html file
def write_new_amb(amb, nums, color):
    total_amb = nums.split(",")
    total_amb = len(total_amb)

    html_file.write("bases["+str(amb.seg_id)+"] = new Base("+str(amb.lat)+","+str(amb.lng))
    html_file.write(", genBasicBaseInfo(\'"+str(nums)+"\', \'"+str(amb.seg_id)+"\', \'"+str(amb.arrival_rate)+"\'), " + str(total_amb) + ","+str(color)+");\n")

# Function that reads each line of ambulance file and extracts ambulance information from it
def mark_ambulances(line, status):
    global index, ambulance_map, segMap
    amb = ambulance_t()
    line = line.split(",")
    amb.lat = line[0].strip()
    amb.lng = line[1].strip()
    amb.amb_num = line[2].strip()
    amb.seg_id = line[3].strip()
    amb.status = status

    if amb.seg_id in segMap:
        amb.arrival_rate = segMap[amb.seg_id]

    # If there is more than one ambulance in the segment then we store the diff
    # ambulance numbers in a hashmap
    nums=""
    if amb.seg_id in segCountMap:
        nums = segCountMap[amb.seg_id]
        nums+=","+str(amb.amb_num)
    else:
        nums = str(amb.amb_num)
    
    segCountMap[amb.seg_id] = nums

    ambulance.append(amb)
    ambulance_map[line[2].strip()] = index
    index+=1


write_html_file_top();

# Map from ambulance vehicle number to index in ambulance array of objects
ambulance_map={}

# Opening  and creating a hashmap of the interArrival rate file
interArrival  = open(interArrival, 'r')
header = interArrival.readline()
segMap = {}
for line in interArrival:
    line=line.split(",")
    segMap[line[0].strip()] = line[1].strip()

amb_active_file = open(amb_active_file, 'r')
amb_inactive_file = open(amb_inactive_file, 'r')

header = amb_active_file.readline()
header = amb_inactive_file.readline()
index = 0
# Declaring ambulance variables
for line in amb_active_file:
    mark_ambulances(line, 0)
    
for line in amb_inactive_file:
    mark_ambulances(line, -1)



"""
for i in range(0, len(ambulance)):
    amb = ambulance[i]
    if amb.arrival_rate == -1:
        continue

    if (len(top) < num_circles):
        top.append(amb)
        top.sort()
    elif top[num_circles-1].arrival_rate > amb.arrival_rate:
        top.append(amb)
        top.sort()
        top.pop(num_circles)
   
    if (len(bottom) < num_circles):
        bottom.append(amb)
        bottom.sort(reverse=True)
    elif bottom[num_circles-1].arrival_rate < amb.arrival_rate:
        bottom.append(amb)
        bottom.sort(reverse=True)
        bottom.pop(num_circles)
"""
# Finding top 5 and bottom 5 segments in which to draw circles
top=Set()
bottom=Set()
ambulance.sort()

for amb in ambulance:
    if len(top) == num_circles:
        break
    top.add(amb.seg_id)

ambulance.sort(reverse=True)

for amb in ambulance:
    if len(bottom) == num_circles:
        break
    bottom.add(amb.seg_id)

# Begin filling in the base datastructure in the demo html file
for amb in ambulance:
    if amb.seg_id in top:
        color = "\'#FF0000\'"  # Red color
    elif amb.seg_id in bottom:
        color = "\'#00FF00\'"  # Green color
    else:
        color = "null"
    write_new_amb(amb, segCountMap[amb.seg_id],color)
 

################################
# Now we are handling the calls
################################
# Opening the four csv files
availed = open(availed_file, 'r')
busy = open(busy_file, 'r')
snr = open(snr_file, 'r')
unavailed = open(unavailed_file, 'r')

availed_line = ""
busy_line = ""
snr_line = ""
unavailed_line = ""

# Reads each line of the four patient information files (availed, busy, snr, unavailed)
def read_each_file():
    global availed, busy, snr, unavailed
    global availed_line, busy_line, snr_line, unavailed_line

    availed_line = availed.readline()
    busy_line = busy.readline()
    snr_line = snr.readline()
    unavailed_line = unavailed.readline()

al_split = []
bl_split = []
sl_split = []
ul_split = []

# Splits each line of the four patient information files (availed, busy, snr, unavailed)
def split_each_line():
    global al_split, bl_split, sl_split, ul_split
    global availed_line, busy_line, snr_line, unavailed_line

    al_split = availed_line.split(",")
    bl_split = busy_line.split(",")
    sl_split = snr_line.split(",")
    ul_split = unavailed_line.split(",")

# Reading header line of each file and making sure they all have the same 
# number of columns
read_each_file();
split_each_line();

if (len(al_split)==len(bl_split)==len(sl_split)==len(ul_split)):
    num_cols = len(al_split)
    read_each_file()
else:
    print "Files don't all have the same columns... exiting"
    exit(-1)

time_format = "%m/%d/%y %H:%M:%S" 
max_date = datetime(9999, 12, 31)  # Maximum date

def return_time(line_split):
    global num_cols, time_format, max_date

    if (len(line_split) == num_cols):
        return datetime.strptime(line_split[3], time_format)
    else:
        return max_date

# Finds the smallest start time amongst the four files (availed, unavailed, busy, snr)
def find_smallest_start_time():
    global al_split, bl_split, sl_split, ul_split
    global max_date

    split_each_line();
    
    time1 = return_time(al_split)
    time2 = return_time(bl_split)
    time3 = return_time(sl_split)
    time4 = return_time(ul_split)

    smallest = min(time1, time2, time3, time4)
    
    if (smallest == max_date):
        print "SMALLEST RETURNED max_date -> ERROR"
        exit(0);

    if (smallest == time1):
        return 0, al_split
    elif (smallest == time2):
        return 1, bl_split
    elif (smallest == time3):
        return 2, sl_split
    elif (smallest == time4):
        return 3, ul_split


victim_num = 0

# Format in which we write a new Date object in JS
def date_string(date):
    return date.strftime("%Y,%m-1,%d,%H,%M,%S,0")

# Declares a new call and appends it to the calls array in the JS
def write_new_call(victim):
    if victim.amb_num in ambulance_map:
        seg=str(ambulance[ambulance_map[victim.amb_num]].seg_id)
    else:
        seg = -1

    html_file.write("calls.push( new Call("+str(victim.lat)+","+str(victim.lng)+","+str(victim.v_type))
    html_file.write(",new Date("+date_string(victim.start_time)+"), new Date("+date_string(victim.end_time) + "), genBasicCallInfo("+str(victim.call_id)+","+str((victim.end_time-victim.start_time).seconds/60)+","+str(seg)+"), ");

    if seg == -1:
        html_file.write("null")
    else:
        html_file.write("bases["+str(seg)+"]")
    html_file.write("));\n")


num, line_split = find_smallest_start_time()
vis_start_time = return_time(line_split)
vis_end_time = vis_start_time

# Scanning through csv files and generating appropriate HTML code
while (availed_line or busy_line or snr_line or unavailed_line):
    num, line_split = find_smallest_start_time()
   
    # Extracting information about the patient call
    victim = victim_t();
    victim.v_type = num
    victim.lat = line_split[1]
    victim.lng = line_split[2]
    victim.start_time = return_time(line_split)
    victim.call_id = line_split[0]

    # Read next line from appropriate file
    if num==0:
        availed_line = availed.readline()
    elif num==1:
        busy_line = busy.readline()
    elif num==2:
        snr_line = snr.readline()
    else:
        unavailed_line = unavailed.readline()

    print num, line_split
    
    # If busy
    if num==1:
        victim.end_time = victim.start_time + time_to_display_busy_marker
        victim.amb_num=""
        victim.v_type = "TYPE_BUSY"
    # If snr
    elif num==2:
        victim.end_time = victim.start_time + time_to_display_snr_marker
        victim.amb_num=""
        victim.v_type="TYPE_SNR"
    else:
        if (line_split[4]==""):
            line_split[4] = time_to_display_busy_marker.seconds/60
        victim.end_time = victim.start_time + timedelta(minutes = float(line_split[4]))
        victim.amb_num = line_split[5].strip()

        if num==0:
            victim.v_type = "TYPE_AVAILED"
        else:
            victim.v_type = "TYPE_UNAVAILED"

    if victim.end_time > vis_end_time:
        vis_end_time = victim.end_time

    write_new_call(victim)


# The bottom part of the HTML
html_file.write("// starting simulation\n\t\t\t\t")
html_file.write("Visualizer.start(\"map_canvas\", calls, bases, new Date("+date_string(vis_start_time)+"), new Date("+date_string(vis_end_time)+"), refreshControls);\n\t\t\t\t")
write_html_file_bottom();

