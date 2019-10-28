from datetime import datetime 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib as mp
import numpy as np

def draw_year(bar_colours, x, y, pi_id,  path):
#year graph will have this year and one before [date,date]
    font = {'family' : 'DejaVu Sans',
	    'weight' : 'bold',
	    'size'   : 22}
	    
    params = {"ytick.color" : "w",
	      "xtick.color" : "w",
	      "axes.labelcolor" : "w",
	      "axes.edgecolor" : "w",
	      }
    plt.rcParams.update(params)

    plt.rc('font', **font)   
    
    plt.clf()
    plt.bar(x,y, color = bar_colours)
    plt.xticks([])

    for xs,ys in zip(x,y):

        label = int(xs)

        plt.annotate(label, # this is the text
		     (xs,ys), # this is the point to label
		     textcoords= "offset points",# how to position the text
		     color='w', 
		     xytext=(0,-10), # distance from text to points (x,y)
		     ha='center') # horizontal alignment can be left, right or center
        
    plt.savefig(path,
		    bbox_inches = 'tight',
		    pad_inches = 0,
		    transparent=True)
    return True
    
def bar_chart(title,xs,ys,x_label,y_label,bar_colours, y_lim, destination):
    font = {'family' : 'DejaVu Sans',
	    'weight' : 'bold',
	    'size'   : 22}
	    
    params = {"ytick.color" : "w",
	      "xtick.color" : "w",
	      "axes.labelcolor" : "w",
	      "axes.edgecolor" : "w",
	      }

    plt.rcParams.update(params)

    plt.rc('font', **font)   
    
    plt.clf()      
    plt.bar(xs,ys,color=bar_colours)
    plt.xlabel(x_label)    
    plt.ylabel(y_label)
    plt.title(title,color = 'w')
    plt.xticks(xs)
    
    plt.ylim(y_lim)
      
    # zip joins x and y coordinates in pairs
    for x,y in zip(xs,ys):

        label = "{:.2f}".format(y)

        plt.annotate(label, # this is the text
                     (x,y), # this is the point to label
                     textcoords="offset points", # how to position the text
                     xytext=(0,2), # distance from text to points (x,y)
                     ha='center',
                     color = 'w') # horizontal alignment can be left, right or center

        
    plt.savefig(destination,
		    bbox_inches = 'tight',
		    pad_inches = 0,
		    transparent=True)
    #plt.show()
    return True

if __name__ == "__main__":
    # from greenhouse_db import GreenhouseDb
    # from dateutil.tz import tzutc

    # db = GreenhouseDb()  
    # end_date = datetime.utcnow()
    # start_date = datetime(year = (end_date.year-3), month= 1, day = 1, tzinfo=tzutc())
    
    # yearly_sensor_data = db.get_yearly_data(start_date, end_date,'rp3001',2)
    
    # x = []
    # humidity = []
    # moisture = []
    # air_temp = []
    # soil_temp = []

    # #loop through each record	    
    # for record in yearly_sensor_data:
        # d = record['_id']['year']
        # x.append(d)
    
        # humidity.append(record['avgHum'])
        # moisture.append(record['avgMoist'])
        # air_temp.append(record['avgTemp'])
        # soil_temp.append(record['avgSoilTemp'])
    
    # y = humidity
    
    
    xs = ['Monday','Tuesday','Wednesday']
    ys = [12.5,15.8,14.3]
    
    bar_colours = (0.12 , 0.531 , 0.32 , 0.8),(0.12 , 0.331 , 0.22 , 0.8)
    bar_chart('Avg humidity for \nthe last 4 days',xs,ys,'','humidity (%)',bar_colours,'')
    
