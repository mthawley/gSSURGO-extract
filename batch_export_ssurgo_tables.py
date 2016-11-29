# Import system modules
import arcpy
from arcpy import env
from arcpy.sa import *
import os
import datetime
import numpy

#output_path = 'C:/EPA/data/ssurgo/gssurgo_csv'
#soilpath = 'C:/EPA/data/ssurgo/soils'

output_path = 'C:/Users/mthawley/Documents/SAM/ssurgo_processing/ssurgo_csv'
soilpath = 'C:/Users/mthawley/Documents/data/gSSURGO_2016/soils'

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

states = ['AL']
#states = ['AL','AR','AZ','CA']
##states = ['AR','AZ','CA','CO','CT','DC','DE','FL','GA','IA','ID','IL','IN','KS','KY','LA','MA','MD',
##    'ME','MI','MN','MO','MS','MT','NC','ND','NE','NH','NJ','NM','NV','NY','OH','OK','OR',
##    'PA','RI','SC','SD','TX','UT','VA','WA','WI','WV','WY']



for state in states:
    env.workspace = soilpath + '/gSSURGO_' + state + '.gdb'
    print("Processing State: " + state)
    print("Soil Location: " + env.workspace)

    try:
        tableList = ['muaggatt','component','chorizon']
        #tableList = ['chorizon']

        # Set local variables
        for key in tableList:
            print key
            intable = soilpath + '/gSSURGO_' + state + '.gdb/' + key
            arcpy.MakeTableView_management(intable, "intable")

            ##Export muaggatt
            outFn = output_path + '/' + state + '_' + key + '.txt'
        
            if key == 'muaggatt':
                #fields = ['mukey','hydgrpdcd','slopegradwta']
                fields = ['mukey','hydgrpdcd','slopegradwta']
                data_fmt = '%s,%s,%2.1f'
                
            if key == 'component':
                fields = ['mukey','cokey','majcompflag','comppct_r','slopelenusle_r','hydgrp']
                data_fmt = '%s,%s,%s,%2.1f,%2.1f,%s'
            if key == 'chorizon':
                fields = ['cokey','desgnmaster','om_r','hzdept_r','hzdepb_r','dbthirdbar_r','wthirdbar_r',
                          'wfifteenbar_r','ph1to1h2o_r','sandtotal_r','claytotal_r','kwfact']
                data_fmt = '%s,%s,%2.1f,%d,%d,%2.1f,%2.1f,%2.1f,%2.1f,%2.1f,%2.1f,%s'

##                  fields = ['cokey','om_r']
##                  data_fmt = '%s,%2.1f'
                
            params = ','.join(fields)
            
            # This business below was a cheap solution to an ESRI memory error
            # 
            result = arcpy.GetCount_management(intable)
            count = int(result.getOutput(0))
    
            if count > 100000 and count <= 200000:
               print(str(arcpy.GetCount_management(intable)))
               query1 = 'OBJECTID <= 50000'
               query2 = 'OBJECTID > 50000 AND OBJECTID <= 100000'
               query3 = 'OBJECTID > 100000'
               arr1 = arcpy.da.TableToNumPyArray(intable, fields, query1,null_value=-9999)
               arr2 = arcpy.da.TableToNumPyArray(intable, fields, query2,null_value=-9999)
               arr3 = arcpy.da.TableToNumPyArray(intable, fields, query3,null_value=-9999)

               arr = numpy.concatenate((arr1,arr2,arr3),axis=0)
               numpy.savetxt(outFn, arr, fmt=data_fmt,delimiter=',',header=params,comments='')

            elif count > 200000:
                query = []
                query.append('OBJECTID <= 50000')
                query.append('OBJECTID > 50000 AND OBJECTID <= 100000')
                query.append('OBJECTID > 100000 AND OBJECTID <= 150000')
                query.append('OBJECTID > 150000 AND OBJECTID <= 200000')
                query.append('OBJECTID > 200000')

                tempfiles = []
                for i in range(5):
                    arr = arcpy.da.TableToNumPyArray(intable, fields, query[i],null_value=-9999)
                    outPartialFn = output_path + '/' + state + '_' + key + '_' + str(i+1) + '.txt'
                    tempfiles.append(outPartialFn)
                    numpy.savetxt(outPartialFn, arr, fmt=data_fmt,delimiter=',',header=params,comments='')
                
                f = open(outFn,'w')
                for tempfile in tempfiles:
                    inf = open(tempfile,'r')
                    f.write(inf.read())
                    inf.close()
                f.close()
            else:
                arr = arcpy.da.TableToNumPyArray(intable, fields, null_value=-9999)
                numpy.savetxt(outFn, arr, fmt=data_fmt,delimiter=',',header=params,comments='')

            print("Finished " + state + ' at : ' + datetime.datetime.now().strftime("%d %b %Y %H:%M:%S"))
        
    except Exception, e:
        # If an error occurred, print line number and error message
        import traceback, sys
        tb = sys.exc_info()[2]
        print "Line %i" % tb.tb_lineno
        print e.message
        print 'error in ' + key

