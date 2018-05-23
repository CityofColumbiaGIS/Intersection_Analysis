#AUTHOR: Jeffrey King
#DATE: 8/18/2015
#ORGANIZATION: City of Columbia GIS Office

import arcpy
from arcpy import env
import os

def runAnalysis(featLyrIntersect, featLyrRoad, updating):
    print("PERFORMING INTERSECT ANALYSIS")
    
    #define the order of priority for which road comes first in the streets field.
    #i.e. Freeway comes first then local last("Freeway Road" & "Local Road")
    roadOrderList = ("Freeway", "Expressway", "Major Arterial", "Minor Arterial", "Major Collector",
                     "Minor Collector", "Neighborhood Collector", "Ramp", "Local Nonresidential", "Local Residential", "None")

    #define the fields we need to bring in
    fieldsRow = ("OID@", "STREETS", "INT_ID", "SHAPE@XY", "MAJOR_INT")
    fieldsCol = ("ROADWAY_NA", "TYPE", "ROADWAY_PL", "STATUS", "SHAPE@LENGTH")
    roads = arcpy.da.UpdateCursor(featLyrRoad, fieldsCol)      
    for road in roads:
        if(road[4] < 3.0):
            roads.deleteRow()

    del roads
    del road

    arcpy.ExtendLine_edit(featLyrRoad, "1 Meters", "")
    
    #create cursor to update intersections
    rows = arcpy.da.UpdateCursor(featLyrIntersect, fieldsRow)
    count = 1
    lastXY = [0,0]
    for row in rows:
        #Iterate through based on OID
        arcpy.SelectLayerByAttribute_management(featLyrIntersect, "NEW_SELECTION", "OBJECTID=" + str(row[0]))

        #Select roads within 1 meter of given intersection, to find connected roads
        arcpy.SelectLayerByLocation_management(featLyrRoad, "WITHIN_A_DISTANCE", featLyrIntersect, "1 Millimeters", "NEW_SELECTION")

        #create cursor to search through the roads selection
        cols = arcpy.da.SearchCursor(featLyrRoad, fieldsCol)        
        streetList = []
        orderList = []
        freewayBool = False
        rampBool = False
        majorBool = "YES"
        iterNum = 0
        for col in cols:
            if(str(col[2]) == roadOrderList[0]): #is Freeway
                freewayBool = True
            if(str(col[1]) == "RAMP"): #is ramp
                rampBool = True
            if(str(col[2]) == roadOrderList[8] or str(col[2]) == roadOrderList[9]): #is local
                majorBool = "NO"

            if(rampBool == False):
                subjRd = str(col[0]).upper() + " " + str(col[1]).upper()
            else:
                subjRd = str(col[0]).upper()
                
            #Ignore extra space
            if(subjRd.endswith(" ")):
                subjRd = subjRd[:-1]
            subjRd.replace("  ", " ")
                
            appendToStreet = True
            for street in streetList:
                #if the road is already going to be appended at same intersection, don't append it again
                if(subjRd == str(street)):
                    appendToStreet = False
            #If following holds true, then add to the streetList (and the orderList to sort if necessary)
            if(appendToStreet == True) and (subjRd != "None") and not (subjRd.isspace()) and (str(col[3]) == "EXISTING") and not (str(col[1]) == "CONNECTOR") and not (str(col[1]) == "COLLECTOR"):
                appendOrder = False
                for colType, item in enumerate(roadOrderList):
                    if(str(col[2]) == roadOrderList[colType]):
                        orderList.append(colType)
                        appendOrder = True
                if(appendOrder == False):
                    orderList.append(len(roadOrderList))
                streetList.append(subjRd)
                
            iterNum = iterNum+1

        #Sort based on orderList
        i=0
        while(i+1 < len(orderList)):
            if(orderList[i+1] < orderList[i]):
                temp = orderList[i+1]
                temp2 = streetList[i+1]
                orderList[i+1] = orderList[i]
                streetList[i+1] = streetList[i]
                orderList[i] = temp
                streetList[i] = temp2
                i=0
            i = i+1

            
        if(len(streetList) < 2) or (freewayBool == True and rampBool != True):
            #Delete unncecessary rows
            #print("DELETING ROW: " + str(row))
            rows.deleteRow()
        else:
            j = 0
            for street in streetList:
                #Create streets field
                if(j == 0):
                    row[1] = (str(street) + " & ")
                else:
                    row[1] = row[1] + str(street) + " & "
                j = j + 1

            row[1] = row[1][:-3] #cut off the last " & "
            if(updating != True):
                row[2] = count #add intersect ID
                row[4] = majorBool #yes or no for major road
            
            if(row[3][0] == lastXY[0] and row[3][1] == lastXY[1]):
                #row was the same as the last row, don't add duplicate
                #print("DELETING DUPLICATE: " + str(row))
                rows.deleteRow()
            else:
                #adding row
                #print("UPDATING ROW: " + str(row))
                lastXY = [row[3][0], row[3][1]]
                count = count + 1
                rows.updateRow(row)

    del row
    del col
    del rows
    del cols

    if(updating == True):
        print("SUCCESSFULLY UPDATED INTERSECTIONS")
    else:
        print("SUCCESSFULLY CREATED INTERSECTIONS")

if __name__ == '__main__':
    #RUN THE PROGRAM
    runAnalysis(featLyrIntersect, featLyrRoad, updating)
