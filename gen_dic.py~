
import csv

oneweek_file = "one_week_data.csv"


def genDict(infile):

    infile = open(oneweek_file, 'r')
    allAmbulance={}
    
    for line in infile:
        line = line.split(",")
        time = line[1].strip()
        plate = line[0].strip()
        location = (line[3].strip(), line[4].strip())
	
        if time not in allAmbulance:
	    allAmbulance[time] = {}
	    allAmbulance[time][plate] = location
	else:
            allAmbulance[time][plate] = location


    return allAmbulance


def genTimeArray(infile):

    reader1 = open(oneweek_file, "r")
    reader2 = open(oneweek_file, "r")


    file = reader1.readlines() 
    last = file[len(file)-1].split(",")[1]

    myData = []
    year=file[0].split(",")[1][0:4]
    month=file[0].split(",")[1][5:7]
    day=file[0].split(",")[1][8:10]
    hour=file[0].split(",")[1][11:13]
    minute=file[0].split(",")[1][14:16]
    second=file[0].split(",")[1][17:23]

    for line in reader2:
	if year + "-" + month + "-" + day + " " + hour + ":"+ minute + ":"+ second != last:
		myData.append(year + "-" + month + "-" + day + " " + hour + ":"+ minute + ":"+ second)
		
		if float(second)<9:
			second="0"+str(float(second)+1)+"00"
		else:
			second=str(float(second)+1)+"00"
		
		if second=='60.000':
			second='00.000'
			if int(minute)+2<9:
				minute="0"+str(int(minute)+2)
			else:
				minute=str(int(minute)+2)
	
		if minute=='60':
			minute='0'
			if int(hour)<9:
				hour="0"+str(int(hour)+1)
			else:
				hour=str(int(hour)+1)

		if hour=='24':
			hour='00'
			if int(day)<9:
				day="0"+str(int(day)+1)
			else:
				day=str(int(day)+1)
    myData.append(last)

    return myData


if __name__ == '__main__':

    ambDict = genDict(oneweek_file)
    timeArray = genTimeArray(oneweek_file)

    #print(ambDict)
    for time in timeArray:
	    print(time + "\n")
		#if time in ambDict:
	    	#for plate in ambDict[time]:
			#print(plate, ambDict[time][plate])
			#print("\n")
	    
