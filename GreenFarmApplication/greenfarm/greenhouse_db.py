from pymongo import MongoClient, errors
from datetime import datetime, timedelta
import random
from dateutil.tz import tzutc
class GreenhouseDb():
    def __init__(self):
        client = MongoClient("mongodb+srv://pi3:1234@cluster0-qbhqv.gcp.mongodb.net/test?retryWrites=true&w=majority")
        self.greenhouse_data = client.GreenhouseDb

#user functions	
    def add_user(self,user_email,user_password, user_name, admin = False):
        db = {}
        db['email'] = user_email
        db['password'] = user_password
        db['name'] = user_name
        db['administrator'] = admin
        db['tmp_password'] = False
        self.greenhouse_data.user.insert_one(db)
        return(self.get_users())
    
    def update_user(self,_id,user_email,user_password, user_name):
        # db = {}
        # db['email'] = user_email
        # db['password'] = user_password
        # db['name'] = user_name
        # db['tmp_password'] = True
        self.greenhouse_data.user.update_one(
	                                              {'_id': _id}, 
						      {
						        "$set": 
							      { 
							         "email": user_email,
                                     "password":user_password,
                                     "name":user_name,
                                     "tmp_password": True
							      }
						      }
						      )
        return(self.get_user_(_id))
	
        #return 

    def get_users(self):
        user_dict = list(self.greenhouse_data.user.find())
        return user_dict

    def get_user(self,email):
        user_dict = self.greenhouse_data.user.find_one({ "email": email })
        return user_dict
        
    def get_user_(self,_id):
        user_dict = self.greenhouse_data.user.find_one({ "_id": _id })
        return user_dict
        
    def remove_user(self,_id):      
        user_greenhouses = self.get_user_greenhouses(_id)
        for greenhouse in user_greenhouses:
            greenhouse_devices = self.get_greenhouse_devices(greenhouse['_id'])
            for device in greenhouse_devices:
                self.remove_device(device['_id'])
            self.remove_greenhouse(greenhouse['_id'])
        
        user_dict = self.greenhouse_data.user.delete_one({ "_id": _id })
        return user_dict
        
       
#greenhouse functions
    def add_greenhouse(self,user_id, greenhouse_nickname, greenhouse_width, greenhouse_length):
        db = {}
        db['user_id'] = user_id
        db['nickname'] = greenhouse_nickname
        db['dimensions'] = {}
        db['dimensions']['length'] = greenhouse_length
        db['dimensions']['width'] = greenhouse_width
        db['pi_ids'] = []
	
        return self.greenhouse_data.greenhouse.insert_one(db)
		
    def get_greenhouses(self):
        greenhouse_dict = list(self.greenhouse_data.greenhouse.find())
        return greenhouse_dict
        
    def get_user_greenhouses(self,user_id):
        greenhouse_dict = list(self.greenhouse_data.greenhouse.find({ "user_id": user_id }))
        return greenhouse_dict

    def get_greenhouse(self,_id):
        greenhouse_dict = self.greenhouse_data.greenhouse.find_one({ "_id": _id })
        return greenhouse_dict
        
    def remove_greenhouse(self,_id):
        greenhouse_dict = self.greenhouse_data.greenhouse.delete_one({ "_id": _id })
        return greenhouse_dict


    def edit_greenhouse(self, greenhouse):
        self.greenhouse_data.greenhouse.update_one(
	                                              {'_id': greenhouse['_id']}, 
						      {
						        "$set": 
							      { 
							         "dimensions": greenhouse['dimensions'],
                                     "nickname":greenhouse['nickname']
							      }
						      }
						      )
        return self.get_greenhouse(greenhouse['_id'])

#device functions
    def add_device(self,pi_id, irrigation_mode, threshold, plant, dt_planted, greenhouse_id):
        db = {}
        db['pi_id'] = pi_id
        db['solenoid_valve'] =  0
        db['plant'] = plant
        db['planted_date'] = dt_planted
        db['irrigation_mode'] = irrigation_mode
        db['threshold'] = threshold
        db['busy'] = None
        db['greenhouse_id'] = greenhouse_id
        #db['timestamps'] = []
	
        return self.greenhouse_data.device.insert_one(db)
		
    def get_devices(self):
        device_dict = list(self.greenhouse_data.device.find())
        return device_dict

    def get_device(self,_id):
        device_dict = self.greenhouse_data.device.find_one({ "_id": _id })
        return device_dict

    def get_greenhouse_devices(self, greenhouse_id):
        device_dict = list(self.greenhouse_data.device.find({ "greenhouse_id": greenhouse_id }))
        return device_dict

    def remove_device(self,_id):
        device_dict = self.greenhouse_data.device.delete_one({ "_id": _id })
        return device_dict

    def edit_device(self, device):
        self.greenhouse_data.device.update_one(
	                                              {'_id': device['_id']}, 
						      {
						        "$set": 
							      { 
							         "plant": device['plant'],
							         "irrigation_mode": device['irrigation_mode'],
							         "threshold": device['threshold'],                                     
							         "date_planted": device['planted_date'],                                     
							      }
						      }
						      )
        return self.get_device(device['_id'])

    def update_irrigation_mode(self, _id, state):
        self.greenhouse_data.device.update_one(
	                                         {'_id': _id}, 
						 {
						  "$set": 
						         { 
                                    "irrigation_mode": state,   
                                    "solenoid_valve": 0
                                 }
						 }
						)
        return self.get_device(_id)		
#simulation

    def simulate_data(self, pi_id, date):
        db = {}

        timestamp = datetime.timestamp(date)
	# +- 30min	
        random_timestamp = timestamp - random.randint(-3000, 3000)
	
        dt = datetime.fromtimestamp(random_timestamp)
        #dt = datetime.strptime(str(dt), "%Y-%m-%dT%H:%M:%S.000Z")
        #random_timestamp=  dt.strftime("%m/%d/%Y, %H:%M")
	
	
        random_moisture = random.randint(10, 70)*1.05
        random_soil_temp = random.randint(20, 30)*1.05
        random_air_temp = random.randint(10, 30)*1.05	
        random_humidity = random.randint(30, 60)*1.05	
   
        self.add_timestamp(dt,random_soil_temp,random_air_temp,random_humidity,random_moisture,pi_id)	
        return db
#simulation

    def add_timestamp(self,ts,soil_temp,air_temp, humidity, moisture, pi_id):
        db = {}
        db['ts'] = ts
        db['soil_temp'] =  soil_temp
        db['air_temp'] = air_temp
        db['humidity'] = humidity
        db['moisture'] = moisture
        db['pi_id'] = pi_id
	
        return self.greenhouse_data.timestamp.insert_one(db)
#LOOK
#https://github.com/ReinProject/kivy-rein/blob/master/views/SignInScreen.kv

    def get_yearly_data(self, start_date, end_date, pi_id,limit):
	#datetime(2019, 12, 31,tzinfo=tzutc())
        result = self.greenhouse_data.timestamp.aggregate([
	    {
	      '$match': 
		      {
			'$and' :
			    [
				{
				    'ts' : 
				      {
				      
					 '$lt' :   end_date,
					 #'$gte' :   start_date  
				      }
				},
				{
				 'pi_id' : pi_id
				}
			    ]  
		      }	
	    },
	    
	    {
	      "$group": {
                         "_id": {
				  'year' : { "$year": "$ts"}
				  }, 
			  "avgHum": {"$avg": '$humidity'},
			  "avgMoist": {"$avg": '$moisture'},
			  "avgSoilTemp": {"$avg": '$soil_temp'},
			  "avgTemp": {"$avg": '$air_temp'},
			 }
	      
	    },
	    
	    {
	       "$sort" :  {
			    '_id' : -1
			  }
	    },
	    
	    {
	       "$limit" :  limit
	    }
	    
						         ])

        return(list(result))

    def get_monthly_data(self, start_date, end_date, pi_id,limit):
	#datetime(2019, 12, 31,tzinfo=tzutc())
        result = self.greenhouse_data.timestamp.aggregate([
	    {
	      '$match': 
		      {
			'$and' :
			    [
				{
				    'ts' : 
				      {
				      
					 '$lt' :   end_date,
					 '$gte' :   start_date  ,
				      }
				},
				{
				 'pi_id' : pi_id
				}
			    ]  
		      }	
	    },
	    
	    {
	      "$group": {
                         "_id": {
				  'month' : { "$month": "$ts" },
				  'year' : { "$year": "$ts"}
				  }, 
			  "avgHum": {"$avg": '$humidity'},
			  "avgMoist": {"$avg": '$moisture'},
			  "avgSoilTemp": {"$avg": '$soil_temp'},
			  "avgTemp": {"$avg": '$air_temp'},
			 }
	      
	    },
	    
	    {
	       "$sort" :  {
			    '_id' : -1
			  }
	    },
	    
	    {
	       "$limit" :  limit
	    }
	    
						         ])

        return(list(result))

    def get_weekly_data(self, start_date, end_date, pi_id,limit):
	#datetime(2019, 12, 31,tzinfo=tzutc())
        result = self.greenhouse_data.timestamp.aggregate([
	    {
	      '$match': 
		      {
			'$and' :
			    [
                    {
                        'ts' : 
                          {
                          
                         '$lt' :   end_date,
                         '$gte' :   start_date  ,
                          }
                    },
                    {
                        'pi_id' : pi_id
                    }
			    ]  
		      }	
	    },
	    
	    {
	      "$group": {
			  "_id": {
			          'day' : {"$dayOfMonth": "$ts" },
				  'month' : { "$month": "$ts" },
				  'year' : { "$year": "$ts"}
				  }, 
			  "avgHum": {"$avg": '$humidity'},
			  "avgMoist": {"$avg": '$moisture'},
			  "avgSoilTemp": {"$avg": '$soil_temp'},
			  "avgTemp": {"$avg": '$air_temp'},
			 }
	      
	    },
	    
	    {
	       "$sort" :  {
			    '_id' : -1
			  }
	    },
	    
	    {
	       "$limit" :  limit
	    }
	    
						         ])

        return(list(result))

    def get_daily_data(self, start_date, end_date, pi_id,limit):
	#datetime(2019, 12, 31,tzinfo=tzutc())
        result = self.greenhouse_data.timestamp.aggregate([
	    {
	      '$match': 
		      {
			'$and' :
			    [
				{
				    'ts' : 
				      {
				      
					 '$lt' :   end_date,
					 '$gte' :   start_date  ,
				      }
				},
				{
				 'pi_id' : pi_id
				}
			    ]  
		      }	
	    },
	    
	    {
	      "$group": {
			  "_id": {
			          'hour' : {"$hour": "$ts" },
			          'day' : {"$dayOfMonth": "$ts" },
				  'month' : { "$month": "$ts" },
				  'year' : { "$year": "$ts"}
				  }, 
			  "avgHum": {"$avg": '$humidity'},
			  "avgMoist": {"$avg": '$moisture'},
			  "avgSoilTemp": {"$avg": '$soil_temp'},
			  "avgTemp": {"$avg": '$air_temp'},
			 }
	      
	    },
	    
	    {
	       "$sort" :  {
			    '_id' : -1
			  }
	    },
	    
	    {
	       "$limit" :  limit
	    }
	    
						         ])

        return(list(result))

    def get_last_entry(self, pi_id):
        result = self.greenhouse_data.timestamp.aggregate([
	    {
	      '$match': 
		      {
			'pi_id' : pi_id
		      }	
	    },   	    
	    {
	       "$sort" :  {
			    'ts' : -1
			  }
	    },
	    {
	       "$limit" :  1
	    }
	    						         ])
        lst_result = list(result)
        if(len(lst_result) != 0):
            return lst_result[0]                                         #return only the one element
        else:
            return None							 #return None if list is empty


    def get_alerts(self, sensor, pi_id):
        result = self.greenhouse_data.alert.aggregate([
	    {
	      '$match': 
		      {
			'$and' :
			    [
				    {'sensor' : sensor	},
				    {'pi_id' : pi_id }
			    ]  
		      }	
	    }
	                                                  ])

        return(list(result))
    
    def get_alert(self, _id):
        alert_dict= self.greenhouse_data.alert.find_one({"_id": _id})
        return alert_dict
    
    def edit_alert(self, alert):              
        self.greenhouse_data.alert.update_one(   {"_id": alert['_id']}, 
                                                          {
                                                            "$set": 
                                                              { 
                                                                  "recurring": alert['recurring'],                                  
                                                                  "greater_than": alert['greater_than'],                                  
                                                                  "sensor": alert['sensor'],                                  
                                                                  "value": alert['value'],
                                                                  "active": alert['active']
                                                                  
                                                              }
                                                          }
						      )

    # def update_alert_state(self, alert):        
        # self.greenhouse_data.alert.update_one(
	                                         # {'ts': alert['ts']},
                                             # {'pi_id' : alert['pi_id']}, 
						 # {
						  # "$set":                                  
						         # { "active": alert['active']},                                  
						 # }
						# )
        # return self.get_alert(user['email'])


    def add_alert(self, email,pi_id,recurring, greater_than, sensor, value ):
        db = {}
        db['ts'] = datetime.utcnow()
        db['email'] = email
        db['pi_id'] = pi_id        
        db['recurring']= recurring
        db['greater_than'] =  greater_than
        db['sensor'] =  sensor
        db['value'] =  value
        db['active'] = True

	
        return self.greenhouse_data.alert.insert_one(db)

    def add_schedule_item(self, ts, duration, threshold, email, pi_id):
        db = {}
        db['created'] = datetime.utcnow()
        db['ts'] = ts
        db['pi_id'] = pi_id
        db['threshold'] = threshold
        db['duration'] =duration
        db['email'] = email
        db['state'] = 1
        return self.greenhouse_data.schedule_item.insert_one(db)

    def get_schedule(self, pi_id):
        schedule_dict= self.greenhouse_data.schedule_item.find({"pi_id": pi_id}).sort("ts")
        return list(schedule_dict)
    
    def remove_schedule_item(self,_id):
        schedule_dict = self.greenhouse_data.schedule_item.delete_one({"_id": _id})
        return schedule_dict  

 
    def add_schedule_states(self):
        state_list = [
                            {'state_id':1, 'state' : 'normal', 'colour' : (1,1,1,1)},
                            {'state_id':2,'state' : 'terminated', 'colour': (1,0,0,1)},
                            {'state_id':3,'state' : 'busy', 'colour' : (1, .45, 0, 1)},
                            {'state_id':4,'state' : 'missed', 'colour' : (1,0,0,1)},
                            {'state_id':5,'state' : 'completed', 'colour' : (0, 1, 0, 1)}

                     ] 
        self.greenhouse_data.schedule_state.insert_many(state_list)
        
    def get_shcedule_item_states(self):
        state_dict = list(self.greenhouse_data.schedule_state.find())
        return state_dict    
    
    def add_plants(self):
        plant_list = [
                            {'plant_id': 1 , 'plant' : 'onion', 'days' : 138},
                            {'plant_id': 2 , 'plant' :'pumpkin','days': 108},
                            {'plant_id': 3 , 'plant' :'pepper','days':75}, 
                            {'plant_id': 4 , 'plant' :'pea','days': 90}, 
                            {'plant_id': 5 , 'plant' :'patato','days': 70},
                            {'plant_id': 6 , 'plant' :'corn','days': 80}, 
                            {'plant_id': 7 , 'plant' :'tomato','days': 45},
                            {'plant_id': 8 , 'plant' :'brocolli','days': 125},
                            {'plant_id': 9 , 'plant' :'chilli','days': 90}, 
                            {'plant_id': 10 , 'plant' :'lettuce','days': 50}, 
                            {'plant_id': 11 , 'plant' :'carrot','days': 65}, 
                            {'plant_id': 12, 'plant' :'eggplant','days': 110},
                            {'plant_id': 13, 'plant' :'cabbage','days': 130}, 
                            {'plant_id': 14, 'plant' :'spinach', 'days': 49},
                            {'plant_id': 15, 'plant' :'other', 'days': 50}
                     ] 
        self.greenhouse_data.plant.insert_many(plant_list)
        
    def get_plants(self):
        plant_dict = list(self.greenhouse_data.plant.find())
        return plant_dict      
        
  
        
if __name__ == "__main__":
    x = GreenhouseDb() 
    x.add_plants()
    x.add_schedule_states() 
       
    #print(plants)
    
    #add 2 weeks
    
    # schedule_item =x.get_schedule('rp3006')[0]
    
    # print(schedule_item['ts'])
    # print('removing')
    # x.remove_schedule_item(schedule_item['ts'],schedule_item['pi_id'])
    
    # created = datetime.utcnow()
    # ts = datetime(year = 2020, month = 2 , day = 16,hour = 12, minute=40, tzinfo=tzutc())
    # duration =45
    # threshold =0
    # email = 'susan0995@gmail.com'
    # pi_id = 'rp3006'
    # x.add_schedule_item(created, ts, duration, threshold, email, pi_id)
    
    
    
    end_date = datetime.utcnow() + timedelta(days=5)
    #50 days
    for i in range(10):
	#24 each day
        for j in range(24):
            x.simulate_data('rp3001', end_date - timedelta(hours=j))
            print(i)
	    
        end_date = end_date - timedelta(days=1)
    
    
    # 
    # print(x.get_weekly_data(start_date, end_date, 'test1',3))
    # lst_pi_ids = []
    # for record in x.get_devices():
        # lst_pi_ids.append(record['pi_id'])
    # print(lst_pi_ids)
    
    # for pi in lst_pi_ids:
	# #simulate 500 records for each pi
        # for i in range(501):
            # x.simulate_data(pi)
    
    #start_date = datetime(2005, 1, 1,tzinfo=tzutc()) 
    #end_date = datetime(2030, 1, 1,tzinfo=tzutc()) 
    #print(x.check_device_timestamps('test'))
    #end_date =  datetime.utcnow()
    #x.get_yearly_data(start_date, end_date, 'test')
    #x.get_monthly_data(start_date, end_date, 'test')
    #x.get_daily_data(start_date, end_date, 'test')
    #x.get_hourly_data(start_date, end_date, 'test')
    #x.get_last_entry( 'test')


    	
    
