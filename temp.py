repimport os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from vincenty import vincenty

# Set ipython's max row display
pd.set_option('display.max_row', 100)

# Set iPython's max column width to 50
pd.set_option('display.max_columns', 50)

os.chdir("C:/Users/prime/Dropbox/DESKSTOP/iSx_pYTHON")

def getModis():
    md = pd.read_csv("modis-data.csv", sep="\t")
    
    md["acq_date"] = pd.to_datetime(md.acq_date)
    
    md = md[["acq_date", "latitude", "longitude", "brightness", "frp"]]
    md.columns = ["Date", "Latitude", "Longitude", "Brightness", "Frp"]
    
    return md

def getNosdra():
    ns = pd.read_csv("nosdra-data.tab", sep="\t")
    ns["Incident_date"] = pd.to_datetime(ns.Incident_date)
    ns["Date1"] = ns.Incident_date - timedelta(days=3)
    ns["Date2"] = ns.Incident_date + timedelta(days=3)
    
    
    ns = ns[["Incident_date", "Date1", "Date2", "Latitude", "Longitude", "Estimated_quantity",
 "Type_of_facility", "Company", "Spill_area_habitat", 'Contaminant', 'Cause']]
    ns.columns = ["Date", "PastDate", "NextDate", "Latitude", "Longitude", "quantity", "Facility", "Company", "Habitat", 'Contaminant', 'Cause']
    
    return ns#.sort_values("Date")

md = getModis()
ns = getNosdra().sort_values("Date")
ns = ns.set_index(ns.Date)

results = []
sn = 0

for r in np.arange(0, ns.shape[0]):
    row = ns.ix[r]
    location1 = (row.Latitude, row.Longitude)
    
    #dd = md.loc[(row.PastDate <= md.Date <= row.Date) or (row.Date <= md.Date <= row.NextDate)]
    dd = md.loc[(((md.Date>=row.PastDate) & (md.Date<=row.Date)) | ((md.Date>=row.Date) & (md.Date<=row.NextDate)))]
    #dd = md.loc[((md.Date>=row.PastDate) & (md.Date<=row.Date)) | (md.Date>=row.Date) & (md.Date<=row.NextDate))]
        
    for m in np.arange(0, dd.shape[0]):
        mdata = dd.iloc[m]
        location2 = (mdata.Latitude, mdata.Longitude)
        
        distance = vincenty(location1, location2)
        
        if distance <= 1:
            sn+=1
            rr = {}
            rr["Sn"] = sn
            rr["NoDate"] = row.Date;
            rr["NoLatitude"] = row.Latitude;
            rr["NoLongitude"] = row.Longitude;
            rr["MoDate"] = mdata.Date;
            rr["MoLatitude"] = mdata.Latitude;
            rr["MoLongitude"] = mdata.Longitude;
                        
            rr["quantity"] = row.quantity;
            rr["Contaminant"] = row.Contaminant;
            rr["Cause"] = row.Cause;
            rr["Company"] = row.Company;
            rr["Facility"] = row.Facility;
            rr["Habitat"] = row.Habitat;
            
            rr["Distance"] = distance
            rr["Days"] =  np.abs((row.Date - mdata.Date).days)
              
            results.append(rr)


rs = pd.DataFrame(results)
sn = rs.Sn
rs = rs[['NoDate', 'NoLatitude', 'NoLongitude', 'MoDate', 'MoLatitude', 'MoLongitude', 'Days', 'Distance', 'Cause', 'quantity', 'Company', 'Contaminant', 'Facility', 'Habitat']]
rs = rs.set_index(sn)
         
rs.to_csv("gbenga-data-3.csv")
#np.savetxt("gbenga-data.csv", results, delimiter=",")

