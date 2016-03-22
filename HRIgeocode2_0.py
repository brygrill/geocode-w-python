#-------------------------------------------------------------------------------
# Name:        HRIgeocode
# Purpose:     Geocode HRI database, add URL fields, post to ArcGIS Online
#
# Author:      grillb
#
# Created:     29/01/2015
#-------------------------------------------------------------------------------

#Import Modules
import arcpy
import os
import sys
import subprocess
from datetime import datetime

now = datetime.now()

#Workspace:
projectFolder = "\\path\\to\\folder"
workgdb = os.path.join(projectFolder, "yourGDB.gdb")

#Table Variables:
excelname = "Excel_File"
excelHRI = os.path.join(projectFolder, "%s.xlsx") % (excelname)
tableHRItemp = os.path.join(workgdb, "%s_temp_%s%s%s") % (excelname, now.hour, now.minute, now.second)
tableHRI = os.path.join(workgdb, "%s_%s%s%s") % (excelname, now.hour, now.minute, now.second)
geocoded = os.path.join(workgdb, "%sgeocode_%s%s%s") % (excelname, now.hour, now.minute, now.second)

#Muni District Dictionary
muniDictionary = {"010" : "ADAMSTOWN BOROUGH", "020" : "AKRON BOROUGH", "030" : "BART TOWNSHIP", "040" : "BRECKNOCK TOWNSHIP", "050" : "CAERNARVON TOWNSHIP", "060" : "CHRISTIANA BOROUGH", "070" : "CLAY TOWNSHIP", "080" : "EAST COCALICO TOWNSHIP",
        "090" : "WEST COCALICO TOWNSHIP", "100" : "COLERAIN TOWNSHIP", "110" : "COLUMBIA BOROUGH", "120" : "CONESTOGA TOWNSHIP", "130" : "CONOY TOWNSHIP", "140" : "DENVER BOROUGH", "150" : "EAST DONEGAL TOWNSHIP", "160" : "WEST DONEGAL TOWNSHIP",
        "170" : "DRUMORE TOWNSHIP", "180" : "EAST DRUMORE TOWNSHIP", "190" : "EARL TOWNSHIP", "200" : "EAST EARL TOWNSHIP", "210" : "WEST EARL TOWNSHIP", "220" : "EAST PETERSBURG BOROUGH", "230" : "EDEN TOWNSHIP", "240" : "ELIZABETH TOWNSHIP",
        "250" : "ELIZABETHTOWN BOROUGH", "260" : "EPHRATA BOROUGH", "270" : "EPHRATA TOWNSHIP", "280" : "FULTON TOWNSHIP", "290" : "EAST HEMPFIELD TOWNSHIP", "300" : "WEST HEMPFIELD TOWNSHIP", "310" : "EAST LAMPETER TOWNSHIP", "320" : "WEST LAMPETER TOWNSHIP",
        "330" : "LANCASTER CITY", "340" : "LANCASTER TOWNSHIP", "350" : "LEACOCK TOWNSHIP", "360" : "UPPER LEACOCK TOWNSHIP", "370" : "LITITZ BOROUGH", "380" : "LITTLE BRITAIN TOWNSHIP", "390" : "MANHEIM TOWNSHIP", "400" : "MANHEIM BOROUGH",
        "410" : "MANOR TOWNSHIP", "420" : "MARIETTA BOROUGH", "430" : "MARTIC TOWNSHIP", "440" : "MILLERSVILLE BOROUGH", "450" : "MOUNT JOY BOROUGH", "460" : "MOUNT JOY TOWNSHIP", "470" : "MOUNTVILLE BOROUGH", "480" : "NEW HOLLAND BOROUGH",
        "490" : "PARADISE TOWNSHIP", "500" : "PENN TOWNSHIP", "510" : "PEQUEA TOWNSHIP", "520" : "PROVIDENCE TOWNSHIP", "530" : "QUARRYVILLE BOROUGH", "540" : "RAPHO TOWNSHIP", "550" : "SADSBURY TOWNSHIP", "560" : "SALISBURY TOWNSHIP",
        "570" : "STRASBURG BOROUGH", "580" : "STRASBURG TOWNSHIP", "590" : "TERRE HILL BOROUGH", "600" : "WARWICK TOWNSHIP"}

def prepData():
    #*********Prep Fields**********
    #Bring Excel Into File GDB
    arcpy.ExcelToTable_conversion(excelHRI, tableHRI, "")

    #Recalc MUNI
    arcpy.CalculateField_management(tableHRI, "MUNI", "!MUNI!.upper()", "PYTHON_9.3")

    #Add Full Address Field
    arcpy.AddField_management(tableHRI, "FULLADDR", "TEXT", "", "", "", "", "NULLABLE", "")
    #Calculate Full Address
    address_codeblock = """def ifBlock(House_Number, Street_Direction, Street_Name, Street_Type, MUNI):
        return House_Number + " " + Street_Direction + " " + Street_Name + " " + Street_Type + " " + MUNI"""
    arcpy.CalculateField_management(tableHRI, "FULLADDR", "ifBlock(!House_Number!, !Street_Direction!, !Street_Name!, !Street_Type!, !MUNI!)", "PYTHON_9.3", address_codeblock)

def geocodeData():
    #Geocode Addresses
    AddressPtLocator = "\\path\\to\\Locator"
    arcpy.GeocodeAddresses_geocoding(tableHRI, AddressPtLocator, "'Single Line Input' FULLADDR VISIBLE NONE", geocoded, "STATIC")

def calcURLfields():
    #add fields
    arcpy.AddField_management(geocoded, "RESOURCE_URL", "TEXT", "", "", "100", "Resource URL", "NULLABLE", "")
    arcpy.AddField_management(geocoded, "IMAGE_URL", "TEXT", "", "", "100", "Image URL", "NULLABLE", "")
    #calc fields
    arcpy.CalculateField_management(geocoded, "RESOURCE_URL", "www.example.com/resource/id= & !ResourceID!", "PYTHON_9.3")
    arcpy.CalculateField_management(geocoded, "IMAGE_URL", "www.example.com/image/id= & !ImageID!", "PYTHON_9.3")

#Run It
prepData()
geocodeData()
calcURLfields()

print "Done"

