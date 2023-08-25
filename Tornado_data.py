import os, numpy as np, pandas as pd, matplotlib.pyplot as plt, logging
import requests, pickle
from bs4 import BeautifulSoup as bs

from mpl_toolkits.basemap import Basemap as bm

#logging basis
logging.basicConfig(level=logging.INFO)

def plot_area(df):
	"""
	Plot the USA, Canada and Mexico over a certain area. This hase been reduced to only show the general area where the tornados are located.
	"""
	
	#first going to find the extremes of the values
	#lower left
	ll_lat=min(df['END_LAT'])-(max(df['END_LAT'])-min(df['END_LAT']))*.05
	ll_lon=min(df['END_LON'])-(max(df['END_LON'])-min(df['END_LON']))*.05
	#upper right
	ur_lat=max(df['END_LAT'])+(max(df['END_LAT'])-min(df['END_LAT']))*.05
	ur_lon=max(df['END_LON'])+(max(df['END_LON'])-min(df['END_LON']))*.05
	
	m = bm(projection='merc', resolution='c',llcrnrlat=ll_lat,llcrnrlon=ll_lon,urcrnrlat=ur_lat,urcrnrlon=ur_lon)
	m.drawcoastlines()
	m.drawcountries()
	m.drawstates()
	
	for i,row in df.iterrows():
		#need to have latlon=True so that it is parsed as lat and long.
		m.plot((row['BEGIN_LON'],row['END_LON']),(row['BEGIN_LAT'],row['END_LAT']),zorder=5,latlon=True)
	
	for i,row in df[(df['END_LON'].isna()) | (df['END_LAT'].isna())].iterrows():
		m.plot(row['BEGIN_LON'],row['BEGIN_LAT'],'.',ms=2,zorder=5,latlon=True)

def get_all_files(base=r'https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/'):
	"""
	This is going to get all of the files from the NOAA website:
	https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/
	Output a list of the data files with details.
	"""
	r=requests.get(base)
	soup=bs(r.text,'html.parser')
	file_name=[]
	for row in soup.findAll('table')[0].findAll('tr'):
		try:
			file_name.append(row.findAll('a')[0].text)
		except IndexError:
			pass
	return([i for i in file_name if (i[-7:]=='.csv.gz') and (i[:19]=='StormEvents_details')])

def get_information(name,base=r'https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/'):
	"""
	This is going to get the input file from the wesbite and output the data from the files. This will need some sorting
	"""
	logging.info(f'Pulling data for file {name}')
	df=pd.read_csv(base+name)
	#strip out anything that isn't a tornado
	df=df[df['EVENT_TYPE']=='Tornado']
	return(df)

def save_data(filename,df):
    try:
        with open(f'{filename}.pickle', "wb") as f:
            pickle.dump(df, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as ex:
        print("Error during pickling object (Possibly unsupported):", ex)

def load_data(filename):
    try:
        with open(f'{filename}.pickle', "rb") as f:
            return pickle.load(f)
    except Exception as ex:
        print("Error during unpickling object (Possibly unsupported):", ex)

if __name__=='__main__':
	base=r'https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/'
	files=get_all_files(base)
	
	## Trigger for new or old data. New_data=True pulls new data each time the script runs. Save_data=True will save a copy of the data locally, needs to be recorded for New_data=False.
	new_data=True
	save_data=True
	
	if new_data==True and save_data==False:
		df=pd.DataFrame()
		for i in files:
			df=pd.concat([df,get_information(i)])
	elif new_data==True and save_data==True:
		df=pd.DataFrame()
		for i in files:
			df=pd.concat([df,get_information(i)])
		save_data('tornado_data',df)
	elif new_data==False:
		df=load_data('tornado_data')
	else:
		logging.info(f'There was a problem, no data was loaded or saved.')
		
	plot_area(df)
	
	plt.show(block=False)
