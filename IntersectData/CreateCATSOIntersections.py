#AUTHOR: Jeffrey King
#DATE: 8/18/2015
#ORGANIZATION: City of Columbia GIS Office

import arcpy
from arcpy import env
import os
import UpdateCATSOIntersections
import IntersectCATSOAnalysis

def deleteFiles(roadsFC, newRoadsFC, cityBoundFC):
    arcpy.Delete_management(roadsFC)
    arcpy.Delete_management(newRoadsFC)
    arcpy.Delete_management(cityBoundFC)
    print("DELETED EXTRA FILES")

def setupFiles(roadsFC, newRoadsFC, cityBoundFC):
    arcpy.env.overwriteOutput = True

    #Make sure that you set these flags to Disabled or else there is an issue with some of the functions and the roads
    env.outputMFlag = "Disabled"
    env.outputZFlag = "Disabled"

    intersectFC = "Intersect"
    featLyrIntersect = "FeatLayerPt"
    featLyrRoad = "FeatLayerLine"
    
    outFolder = "L:\\IntersectData"
    outWorkspace = "IntersectGDB.gdb"

    featLyrCity = "FeatLayerCity"
    featLyrTemp = "FeatLayerTemp"

    env.workspace = outFolder + "\\" + outWorkspace
    
    #Delete old data
    if(arcpy.Exists(env.workspace + "\\" + intersectFC)):
        print("Copying Features")
        arcpy.CopyFeatures_management("Database Connections\\ARCSDE_10.sde\\City.DBO.CATSO\\City.DBO.CATSOMRP", roadsFC)
        arcpy.CopyFeatures_management("Database Connections\\ARCSDE_10.sde\\City.DBO.PW_zoning\\City.DBO.columbia_corp_limit", cityBoundFC)
        print("Copied Features")
        UpdateCATSOIntersections.update(roadsFC, cityBoundFC) #If it already exists, reroute to the update script
        return
    #Create Geodatabase
    arcpy.CreateFileGDB_management(outFolder, outWorkspace)
    env.workspace = outFolder + "\\" + outWorkspace

    print("CREATING INTERSECTIONS")

    #Copy features from SDE
    print("Copying Features")
    arcpy.CopyFeatures_management("Database Connections\\ARCSDE_10.sde\\City.DBO.CATSO\\City.DBO.CATSOMRP", roadsFC)
    arcpy.CopyFeatures_management("Database Connections\\ARCSDE_10.sde\\City.DBO.PW_zoning\\City.DBO.columbia_corp_limit", cityBoundFC)
    print("Copied Features")

    #Convert to feature layer to select by location
    arcpy.MakeFeatureLayer_management(roadsFC, featLyrTemp)
    arcpy.MakeFeatureLayer_management(cityBoundFC, featLyrCity)

    #select only features within the city limits
    arcpy.SelectLayerByLocation_management(featLyrTemp, "INTERSECT", featLyrCity, "", "NEW_SELECTION")

    #Perform feature to line tool, to split the lines at vertices for more precise intersection output
    arcpy.FeatureToLine_management(featLyrTemp, newRoadsFC, "", "ATTRIBUTES")

    print("Feature to Line Completed")

    #Find all of the intersections
    arcpy.Intersect_analysis(newRoadsFC, intersectFC, "ONLY_FID", "", "POINT")

    print("Found Intersects")
    
    #Add fields to the output intersect feature
    arcpy.AddField_management(intersectFC, "STREETS", "TEXT", "", "", 150, "STREET_NAMES", "", "", "")
    arcpy.AddField_management(intersectFC, "INT_ID", "LONG", "", "", "", "INTERSECT_ID", "", "", "")
    arcpy.AddField_management(intersectFC, "MAJOR_INT", "TEXT", "", "", 10, "MAJOR_INTERSECTION", "", "", "")

    #Convert to feature layer to make later selections
    arcpy.MakeFeatureLayer_management(newRoadsFC, featLyrRoad)
    arcpy.MakeFeatureLayer_management(intersectFC, featLyrIntersect)

    IntersectCATSOAnalysis.runAnalysis(featLyrIntersect, featLyrRoad, False)

if __name__ == '__main__':
    #RUN THE PROGRAM
    print("DECIDING BETWEEN CREATING OR UPDATING INTERSECTIONS")

    roadsFC = "RoadsIntersect"
    newRoadsFC = "SplitRoadsIntersect"
    cityBoundFC = "CityBound"

    deleteFiles(roadsFC, newRoadsFC, cityBoundFC)
    setupFiles(roadsFC, newRoadsFC, cityBoundFC)
    deleteFiles(roadsFC, newRoadsFC, cityBoundFC)
