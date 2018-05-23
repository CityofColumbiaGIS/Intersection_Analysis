#AUTHOR: Jeffrey King
#DATE: 8/18/2015
#ORGANIZATION: City of Columbia GIS Office

import arcpy
from arcpy import env
import os
import datetime
import IntersectAnalysis

def update(roadsFC, cityBoundFC):
    print("UPDATING INTERSECTIONS")

    now = datetime.datetime.now()
    
    arcpy.env.overwriteOutput = True

    outFolder = "L:\\IntersectData"
    outWorkspace = "IntersectGDB.gdb"

    intersectFC = "Intersect"
    featLyrRoad = "FeatLayerRoads"
    featLyrCity = "FeatLayerCity"
    featLyrIntersect = "FeatLayerIntersect"

    env.workspace = outFolder + "\\" + outWorkspace

    #Convert to feature layer to select by location
    arcpy.MakeFeatureLayer_management(roadsFC, featLyrRoad)
    arcpy.MakeFeatureLayer_management(cityBoundFC, featLyrCity)
    arcpy.MakeFeatureLayer_management(intersectFC, featLyrIntersect)

    #select only features within the city limits
    arcpy.SelectLayerByLocation_management(featLyrRoad, "WITHIN", featLyrCity, "", "NEW_SELECTION")

    curYear = now.year - 2000
    curMonth = now.month

    #figure out the current and last month to include in updates
    pastMonth = curMonth - 1
    if(pastMonth < 1):
        pastMonth = 12
        curYear = curYear - 1

    curYear = str(curYear)
    curMonth = str(curMonth)
    pastMonth = str(pastMonth)
    if(len(curMonth) == 1):
        curMonth = "0" + curMonth
    if(len(pastMonth) == 1):
        pastMonth = "0" + pastMonth

    whereClause = "EDIT_CODE LIKE '" + curYear + curMonth + "%' OR EDIT_CODE LIKE '" + curYear + pastMonth + "%'"
    arcpy.SelectLayerByAttribute_management(featLyrRoad, "SUBSET_SELECTION", whereClause)
    arcpy.SelectLayerByLocation_management(featLyrIntersect, "WITHIN_A_DISTANCE", featLyrRoad, "1 Meters", "NEW_SELECTION")

    IntersectAnalysis.runAnalysis(featLyrIntersect, featLyrRoad, True)

if __name__ == '__main__':
    #RUN THE PROGRAM
    update(roadsFC, cityBoundFC)
