#!/usr/bin/env python3

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.utils import get_color_from_hex

from kivy.uix.behaviors import ButtonBehavior  

import pybase64
import threading

from kivy.uix.popup import Popup
from kivy.uix.label import Label

from kivy.graphics import Color, Rectangle
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.carousel import Carousel
from kivy.uix.scrollview import ScrollView
from kivy.uix.switch import Switch
from kivy.properties import ObjectProperty
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.uix.progressbar import ProgressBar
from kivy.uix.spinner import Spinner

from bson import ObjectId
from kivy.core.window import Window

from kivy.properties import StringProperty, ListProperty

from functools import partial

import re 

from os import listdir, makedirs
from os.path import isfile, join, exists
import shutil

from datetime import datetime, timedelta, date
from dateutil.tz import tzutc

#hashing password 
from passlib.hash import sha256_crypt

#database.py
from greenhouse_db import GreenhouseDb

#graph.py
import greenhouse_graph as GreenhouseGraph

from time import sleep

class ScreenManagement(ScreenManager):
    pass   
class MyGridLayout(GridLayout):
    pass

class OkButton(Button):
    pass
class MyAddAlertButton(Button):
    pass
class MyAddButton(Button):
    pass
class MyRemoveButton(Button):
    pass
class MyValidationLabel(Label):
    pass
class SensorTitle(Label):
    pass
class MyScheduleTitle(Label):
    pass
class MyAlertTitle(Label):
    pass
class MyAlertDescription(Label):
    pass
class MyToggleButton(ToggleButton):
    def on_press(self):
        app = App.get_running_app()        
        if(self.group == 'sensor_alert'):
            app.alert_toggle_pressed = self.text
    pass

class PopupText(Label):
    pass

class ImageButton(ButtonBehavior, Image):
                
    def on_press(self):
        #print(self.id)
        app = App.get_running_app()
        app.imgbtn_pressed = self.id
    pass

class MyCarousel(Carousel):
    def update(self, dt):
        self.load_next()
    pass

class CustomLayoutBrown(BoxLayout):
    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(CustomLayoutBrown, self).__init__(**kwargs)

        with self.canvas.before:
            Color(0.2, 0.631, 0.42, 0.3)  # green; colors range from 0-1 instead of 0-255
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    pass
    
class GreenhouseLayout(BoxLayout):
    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(GreenhouseLayout, self).__init__(**kwargs)

        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 0.5)  # green; colors range from 0-1 instead of 0-255
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    pass
    
class CustomLayoutGreen(BoxLayout):

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(CustomLayoutGreen, self).__init__(**kwargs)

        with self.canvas.before:
            Color(.5, .5, .5, 0.8)  # green; colors range from 0-1 instead of 0-255
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    pass
    
class MyCustomWhiteBox(BoxLayout):
    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(MyCustomWhiteBox, self).__init__(**kwargs)

        with self.canvas.before:
            Color(0.2, 0.631, 0.42, 0.3)  # green; colors range from 0-1 instead of 0-255
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    pass        
        


#Home page: register / login buttons    
class LandingPage(Screen):
    def on_enter(self):
        app = App.get_running_app()
        if(app != None):
            app.current_greenhouse = None
            app.current_user = None
            app.current_device = None	
            
    def login(self):
        app = App.get_running_app()
        
          
        if(app.db is None):
            self.pop = app.please_wait()
            self.pop.open()    
            Clock.schedule_once(app.load_database, 0.5)
            Clock.schedule_once(self.pop.dismiss,0.5)
        else:
            self.pop = app.please_wait('Locating user')
            self.pop.open()    
            Clock.schedule_once(self.handle_login, 0.5)

    def handle_login(self, *args):
        app = App.get_running_app() 
        validation_layout = self.ids.validation_layout
        validation_layout.clear_widgets()
        if(app.db is not None):  
            try:
                app.current_user = app.db.get_user(self.ids.username.text.lower())
            except:
                print('error 203')
                app.db_connection_error('User could not be located') 
            
            self.pop.dismiss()    
            if(app.current_user == None):
                validation_layout.add_widget(
                                                  MyValidationLabel(text = '* Email address not registered. Register an account first.',
                                                                    pos_hint= {'center_y': 0.39, 'center_x': 0.5})
                                        )         
            else:
                app.root.current = 'login_page'
                
    def on_leave(self):
        self.ids.username.text = ''
         
    pass

class LoginPage(Screen):
    def on_pre_enter(self):
        app = App.get_running_app()
        self.ids.username.text = app.current_user['email']
    
    def authenticate_user(self):
        app = App.get_running_app()
        validation_layout = self.ids.validation_layout
        validation_layout.clear_widgets()    

        if(sha256_crypt.verify(self.ids.password.text, app.current_user['password'])):
            if(app.current_user['administrator']):
                app.root.current = 'user_home_page'
            else:
                app.root.current = 'greenhouse_home_page'    
        else:
            validation_layout.add_widget(
                                          MyValidationLabel(text = '* Incorrect password',
                                                            pos_hint= {'center_y': 0.335, 'center_x': 0.5})
                                )    
    pass

#Register page: username, password, register_button    
class RegisterPage(Screen):                     
    def on_enter(self):
        self.app = App.get_running_app()
        self.pop = None
        if(self.app.selected_user is not None):
            self.ids.confirm_password.size_hint = (0,0)
            self.ids.password.hint_text = 'temporary password'
            self.ids.username.text = self.app.selected_user['email']
            self.ids.username.disabled = True
            self.ids.name.text = self.app.selected_user['name']
            self.ids.title.text = 'Update user'
        
    def register_user(self):        
        if(self.app.db is None):
            self.pop = app.please_wait()
            self.pop.open()    
            Clock.schedule_once(self.app.load_database, 0.5)
            Clock.schedule_once(self.pop.dismiss,0.5)
        else:
            self.pop = self.app.please_wait('Registering user')
            self.pop.open()
            if(self.ids.title.text == 'Update user'):
                Clock.schedule_once(self.handle_update,0.5)
            else:
                Clock.schedule_once(self.handle_register, 0.5)

    def handle_update(self,*args):
        validation_layout = self.ids.validation_layout
        validation_layout.clear_widgets()    
        is_valid = True   
        
        password = self.ids.password.text 
        username = self.ids.username.text 
        name = self.ids.name.text 
        
        if(name==''):
            is_valid = False
            validation_layout.add_widget(
                                                  MyValidationLabel(text = '* Type in your name.',
                                                                    pos_hint= {'center_y': 0.665, 'center_x': 0.5})
                                                )
        valid_password = self.validate_password(password)
        if(not valid_password):
            is_valid = False
            validation_layout.add_widget(
                                          MyValidationLabel(text = '* Password must be a length 6 to 12 characters.\nIt should contain at least:\n - 1 lowercase\n- 1 uppercase \n - 1 numeric \n - 1 special character',
                                                        pos_hint= {'center_y': 0.400, 'center_x': 0.5})
                         )                

             
        try:
            self.pop.dismiss() 
            if(is_valid):
                    hash_password =  sha256_crypt.hash(password)
                    self.app.db.update_user(self.app.selected_user['_id'],self.app.selected_user['email'],password,name)
                    self.app.root.current = 'user_home_page'
                    self.pop = self.app.success('User successfully updated', 'User updated in the database')
                    self.pop.open() 
        except:
            self.pop.dismiss()
            print('error 314')
            self.app.db_connection_error('User not registered...') 

    def validate_password(self, password):
        password_regex = '^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})'  #medium strength  #https://www.thepolyglotdeveloper.com/2015/05/use-regex-to-test-password-strength-in-javascript/
        return re.search(password_regex,password) 
            
    def handle_register(self, *args):        
        validation_layout = self.ids.validation_layout
        validation_layout.clear_widgets()    
        is_valid = True   
        
        password = self.ids.password.text 
        username = self.ids.username.text 
        name = self.ids.name.text 
                
        email_regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
        valid_email = re.search(email_regex,username)        
        valid_password = self.validate_password(password)
        
        if(name==''):
            is_valid = False
            validation_layout.add_widget(
                                                  MyValidationLabel(text = '* Type in your name.',
                                                                    pos_hint= {'center_y': 0.665, 'center_x': 0.5})
                                                )
        
        if(valid_email):
            if(valid_password):                 
                if(password != self.ids.confirm_password.text):
                    is_valid = False
                    validation_layout.add_widget(
                                                  MyValidationLabel(text = '* Password does not match.',
                                                                    pos_hint= {'center_y': 0.335, 'center_x': 0.5})
                                                )
            else:
                is_valid = False
                validation_layout.add_widget(
                                          MyValidationLabel(text = '* Password must be a length 6 to 12 characters.\nIt should contain at least: \n - 1 lowercase\n- 1 uppercase \n - 1 numeric \n - 1 special character',
                                                        pos_hint= {'center_y': 0.300, 'center_x': 0.5})
                                         )      
            
        else:
            is_valid = False
            validation_layout.add_widget(
                                            MyValidationLabel(text = '* Invalid email address..',
                                                        pos_hint= {'center_y': 0.555, 'center_x': 0.5})
                                    )   
        
        
        try:
            if(self.app.db.get_user(self.ids.username.text) is not None):
                is_valid = False
                validation_layout.add_widget(
                                             MyValidationLabel(text = '* A user with that email address is already registered',
                                                               pos_hint= {'center_y': 0.555, 'center_x': 0.5})
                                )
        except:
            print('error 301')
            self.app.db_connection_error('Redirecting...')
            self.app.root.current = 'landing_page'
            
        if(is_valid):
            try:
                self.pop.dismiss() 
                email = self.ids.username.text.lower()    
                hash_password =  sha256_crypt.hash(password)
                if(email=='susanhonours2019@gmail.com'):
                    self.app.db.add_user(email,hash_password,name, True)
                else:
                    self.app.db.add_user(email,hash_password,name)
                self.app.root.current = 'landing_page'
                self.pop = self.app.success('Successfull Registration', 'User added to the database')
                self.pop.open() 
            except:
                self.pop.dismiss()
                print('error 345')
                self.app.db_connection_error('User not registered...') 
        self.pop.dismiss()               
                                            
    def on_leave(self):
        self.ids.confirm_password.text = ''
        self.ids.username.text = ''
        self.ids.name.text = ''
        self.ids.password.text = ''  
        self.ids.confirm_password.size_hint = (.3,0.1)
        self.ids.username.disabled = False
        self.ids.title.text = 'User Registration' 
        if(self.pop is not None):     
            self.pop.dismiss()

    pass   

class UserHomePage(Screen):   
    def on_pre_enter(self):
        self.app = App.get_running_app()
        self.app.selected_user = None
        self.app.imgbtn_pressed = None  
           
        self.pop = self.app.please_wait('Getting things ready...')
        self.pop.open()   
         
        Clock.schedule_once(self.load_users, 0.5)

    def load_users(self,*args):
        self.app.previous_screen = self.app.root.current

        users = self.app.db.get_users()
        

        grid = MyGridLayout(cols=2, size_hint=(1, None), height = 500)
        grid.bind(minimum_height=grid.setter('height'))

        scroll = self.ids.scroll
        scroll.clear_widgets()
        if(len(users)>0):
            grid.clear_widgets()
 	
            for user in users:
                self.add_widget_to_grid(grid,user)              
                
        scroll.add_widget(grid)
        
        self.pop.dismiss()
        
    #drawing grid        


    def add_widget_to_grid(self, grid, user):
        big_box = GreenhouseLayout(orientation = 'vertical', size_hint=(1, None), height=230)
        user_id = str(user['_id'])
        
        center_box = BoxLayout(orientation = 'horizontal')
        # left_box = BoxLayout( size_hint=(0.25,1),
                                      # orientation = 'vertical'
                                    # )

        #greenhouse button
        button = ImageButton(source = 'icons/greenhouse.png')
        button.id = user_id
    
        
        right_box = BoxLayout( size_hint=(0.25,1),
                                      orientation = 'vertical'
                                    )        
        #label below greenhouse
        l = Label(size_hint=(1,0.2),text = user['name'])        
              
        #info button left from greenhouse button		
        
        btn_edit = ImageButton(source='icons/edit.png')
        btn_edit.id = user_id
        btn_edit.on_release = self.edit_user      
                      
    
        
        if(user['administrator']):
            btn_admin = ImageButton(source='icons/key.png')
            btn_admin.id = user_id                
            btn_admin.on_release = self.on_admin_press
            right_box.add_widget(btn_admin)
        else:
            btn_remove = ImageButton(source='icons/remove.png')
            btn_remove.id = user_id
            btn_remove.on_release = self.remove_user 
            right_box.add_widget(btn_remove)

        right_box.add_widget(btn_edit)

        #center box
        # center_box.add_widget(left_box)
        center_box.add_widget(button)
        center_box.add_widget(right_box)
        
        
        #big box                
        big_box.add_widget(center_box)
        big_box.add_widget(l)
        
        grid.add_widget(big_box)                   
        
    def get_user(self,redirect_to):
        _id = self.app.imgbtn_pressed
        _id = ObjectId(_id)
        try:
            self.app.selected_user = self.app.db.get_user_(_id)
            self.app.root.current = redirect_to
        except:
            print('error 424')
            self.app.db_connection_error('Could not load user')
            self.app.root.current = 'landing_page'
        self.pop.dismiss()
        return self.app.selected_user 
    
    def on_admin_press(self,*args):
        greenhouse = self.get_user('user_home_page')
        content = BoxLayout(orientation = 'horizontal')
        content.add_widget(Image(source = 'icons/key.png', size_hint = (0.7,0.65),pos_hint= {'center_y': 0.5, 'center_x': 0.5}))
        content.add_widget(PopupText(text= self.app.selected_user['name'] + ' is an administrator'))
        pop = Popup(title='Information for '+ self.app.selected_user['name']+':', 
                    content=content,
                    size_hint=(0.5,0.5))
        pop.open()
        self.app.current_greenhouse = None 
    
    def edit_user(self, *args):
        self.pop = self.app.please_wait('Selecting user...')
        self.pop.open()  
        Clock.schedule_once(lambda x: self.get_user('register_page'), 0.5)
        
        
    def remove_user(self, *args):
        user = self.get_user('user_home_page')
        
        content = BoxLayout(orientation = 'vertical')
        pop = Popup(title='Confirm removal',size_hint=(0.5,0.5))
    
        message_box = BoxLayout(orientation = 'horizontal')
        message_box.add_widget(Image(source = 'icons/remove.png', size_hint = (0.6,0.65),pos_hint= {'center_y': 0.5, 'center_x': 0.5}))
        message_box.add_widget(PopupText(text= 'Are you sure you want to remove ' + user['name'] + '?'))
    
        respond_box = BoxLayout(orientation = 'horizontal', size_hint = (1,0.2),pos_hint= {'center_y': 0.6, 'center_x': 0.5})
        btn_yes = MyAddButton(text = 'Yes', always_release = True,size_hint = (1,1))
        btn_yes.bind(on_press=lambda x: self.confirm_remove(user['_id'],pop))
        respond_box.add_widget(btn_yes)
        btn_no = MyRemoveButton(text = 'No', always_release = True,size_hint = (1,1))
        btn_no.bind(on_press = pop.dismiss)
        respond_box.add_widget(btn_no)
    
        content.add_widget(message_box)
        content.add_widget(respond_box)
        pop.content=content
        pop.open()
    
        self.app.selected_user = None	
         
    def confirm_remove(self,_id,pop1):
        self.pop = self.app.please_wait('Removing user...')
        self.pop.open()                                                 #pop closes in load_greenhouses
        
        Clock.schedule_once(lambda x: self.db_handle_remove(_id), 0.5)
        pop1.dismiss()
        Clock.schedule_once(self.load_users,0.6)
    
    def db_handle_remove(self, _id,*args):
        try:
            self.app.db.remove_user(_id)        ### remove
        except:
            print('error 492')
            self.app.db_connection_error('Could not remove user')
    

    
    def select_help(self):
        message = 'User home page. Remove, view or edit a user.'
        
        self.imgbtn_pressed = None
        icons = {}
        
        icons['info'] = {
                          'source' : 'icons/info.png',
                          'desc'   : 'displays user information'
                        }
        icons['edit'] = {
                          'source' : 'icons/edit.png',
                          'desc'   : 'edit user'
                        }
        icons['remove'] = {
                          'source' : 'icons/remove.png',
                          'desc'   : 'remove user'
                        }
                        
        self.app.select_help(icons,message)                

                   
    pass
  	
#Greenhouse home page : add_greenhouse button
class GreenhouseHomePage(Screen):   
    def on_pre_enter(self):
        self.app = App.get_running_app()
        self.app.current_greenhouse = None
        self.app.current_device = None
        self.app.imgbtn_pressed = None  
           
        self.pop = self.app.please_wait('Getting things ready...')
        self.pop.open()   
         
        Clock.schedule_once(self.load_greenhouses, 0.5)

    def load_greenhouses(self,*args):
        self.app.previous_screen = self.app.root.current

        greenhouses = self.app.db.get_user_greenhouses(self.app.current_user['_id'])

        grid = MyGridLayout(cols=2, size_hint=(1, None), height = 500)
        grid.bind(minimum_height=grid.setter('height'))

        scroll = self.ids.scroll
        scroll.clear_widgets()
        if(len(greenhouses)>0):
            grid.clear_widgets()
 	
            for greenhouse in greenhouses:
                self.add_widget_to_grid(grid,greenhouse)              
                
        scroll.add_widget(grid)
        
        self.pop.dismiss()
        
    #drawing grid        
    def get_greenhouse_info(self,_id):
        try:
            return self.app.db.get_greenhouse(_id)
        except:
            self.app.db_connection_error('Could not load greenhouse')
    def add_widget_to_grid(self, grid, greenhouse):
        big_box = GreenhouseLayout(orientation = 'vertical', size_hint=(1, None), height=230)
        greenhouse_id = str(greenhouse['_id'])
        
        center_box = BoxLayout(orientation = 'horizontal')
        # left_box = BoxLayout( size_hint=(0.25,1),
                                      # orientation = 'vertical'
                                    # )

        #greenhouse button
        button = ImageButton(source = 'icons/greenhouse.png')
        button.id = greenhouse_id
        button.on_release = self.select_greenhouse       
        
        right_box = BoxLayout( size_hint=(0.25,1),
                                      orientation = 'vertical'
                                    )        
        #label below greenhouse
        l = Label(size_hint=(1,0.2) ,text = greenhouse['nickname'])        
              
        #info button left from greenhouse button		
        btn_info = ImageButton(source='icons/info.png')
        btn_info.id = greenhouse_id
        btn_info.on_release = self.info_greenhouse
        
        btn_edit = ImageButton(source='icons/edit.png')
        btn_edit.id = greenhouse_id
        btn_edit.on_release = self.edit_greenhouse      
                      
        btn_remove = ImageButton(source='icons/remove.png')
        btn_remove.id = greenhouse_id
        btn_remove.on_release = self.remove_greenhouse      
                        

        
        #adding buttons to widgets in order
        
        #left box
        
        
        #right box
        right_box.add_widget(btn_remove)
        right_box.add_widget(btn_edit)
        right_box.add_widget(btn_info)

        #center box
        # center_box.add_widget(left_box)
        center_box.add_widget(button)
        center_box.add_widget(right_box)
        
        
        #big box                
        big_box.add_widget(center_box)
        big_box.add_widget(l)
        
        grid.add_widget(big_box)                   
        
    def get_greenhouse(self,redirect_to):
        _id = self.app.imgbtn_pressed
        _id = ObjectId(_id)
        try:
            self.app.current_greenhouse = self.app.db.get_greenhouse(_id)
            self.app.root.current = redirect_to
        except:
            print('error 424')
            self.app.db_connection_error('Could not load greenhouse')
            self.app.root.current = 'landing_page'
        self.pop.dismiss()
        return self.app.current_greenhouse
    
    def select_greenhouse(self, *args):
        self.pop = self.app.please_wait('Selecting greenhouse...')
        self.pop.open()
        Clock.schedule_once(lambda x: self.get_greenhouse('device_home_page'), 0.5)
    
    def edit_greenhouse(self, *args):
        self.pop = self.app.please_wait('Selecting greenhouse...')
        self.pop.open()  
        Clock.schedule_once(lambda x: self.get_greenhouse('add_greenhouse_page'), 0.5)
        
    def info_greenhouse(self,*args):
        greenhouse = self.get_greenhouse('greenhouse_home_page')
        num_devices = self.get_num_devices()
        
        content = BoxLayout(orientation = 'horizontal')
        content.add_widget(Image(source = 'icons/info.png', size_hint = (0.7,0.65),pos_hint= {'center_y': 0.5, 'center_x': 0.5}))
        content.add_widget(PopupText(text= 'Width:   ' + greenhouse['dimensions']['width'] + '\n'+
                                  'Length:   ' + greenhouse['dimensions']['length']+ '\n'+
                                  'Registered devices:   ' + str(num_devices)))
        pop = Popup(title='Information for '+ greenhouse['nickname']+':', 
                    content=content,
                    size_hint=(0.5,0.5))
        pop.open()
        self.app.current_greenhouse = None	
        
    def get_num_devices(self):
        #_id = ObjectId(_id)
        devices = []
        try:
            devices = self.app.db.get_greenhouse_devices(self.app.current_greenhouse['_id'])
        except:
            self.app.db_connection_error('Could not load the devices')
        return (len(devices))
        
    def remove_greenhouse(self, *args):
        greenhouse = self.get_greenhouse('greenhouse_home_page')
        devices = self.app.db.get_greenhouse_devices(self.app.current_greenhouse['_id'])
        
        if(len(devices)> 0): 	
            pop = Popup(title='Cannot delete '+ greenhouse['nickname'] , 
                        content=PopupText(text='Remove all devices from the greenhouse before attempting to remove it.'),
            size_hint=(0.5,0.5))
            pop.open()
        else:
            content = BoxLayout(orientation = 'vertical')
            pop = Popup(title='Confirm removal',size_hint=(0.5,0.5))
            
            message_box = BoxLayout(orientation = 'horizontal')
            message_box.add_widget(Image(source = 'icons/remove.png', size_hint = (0.6,0.65),pos_hint= {'center_y': 0.5, 'center_x': 0.5}))
            message_box.add_widget(PopupText(text= 'Are you sure you want to remove ' + greenhouse['nickname'] + '?'))
            
            respond_box = BoxLayout(orientation = 'horizontal', size_hint = (1,0.2),pos_hint= {'center_y': 0.6, 'center_x': 0.5})
            btn_yes = MyAddButton(text = 'Yes', always_release = True,size_hint = (1,1))
            btn_yes.bind(on_press=lambda x: self.confirm_remove(greenhouse['_id'],pop))
            respond_box.add_widget(btn_yes)
            btn_no = MyRemoveButton(text = 'No', always_release = True,size_hint = (1,1))
            btn_no.bind(on_press = pop.dismiss)
            respond_box.add_widget(btn_no)
            
            content.add_widget(message_box)
            content.add_widget(respond_box)
            pop.content=content
            pop.open()
            
            self.app.current_greenhouse = None	
         
    def confirm_remove(self,_id,pop1):
        self.pop = self.app.please_wait('Removing greenhouse...')
        self.pop.open()                                                 #pop closes in load_greenhouses
        
        Clock.schedule_once(lambda x: self.db_handle_remove(_id), 0.5)
        pop1.dismiss()
        Clock.schedule_once(self.load_greenhouses,0.6)
    
    def db_handle_remove(self, _id,*args):
        try:
            self.app.db.remove_greenhouse(_id)        ### remove
        except:
            print('error 492')
            self.app.db_connection_error('Could not remove greenhouse')
    
    def select_help(self):
        message = 'Greenhouse home page. Add or view a greenhouse.'
        
        self.imgbtn_pressed = None
        icons = {}
        
        icons['info'] = {
                          'source' : 'icons/info.png',
                          'desc'   : 'displays greenhouse information'
                        }
        icons['edit'] = {
                          'source' : 'icons/edit.png',
                          'desc'   : 'edit greenhouse'
                        }
        icons['remove'] = {
                          'source' : 'icons/remove.png',
                          'desc'   : 'remove greenhouse'
                        }
                        
        self.app.select_help(icons,message)                

                   
    pass
    
#Add Greenhouse page : add_greenhouse button
class AddGreenhousePage(Screen):
    def on_enter(self):
        self.app = App.get_running_app()    
        if(self.app.current_greenhouse is not None):
            
            self.ids.length.text = self.app.current_greenhouse['dimensions']['length']
            self.ids.width.text = self.app.current_greenhouse['dimensions']['width']
            self.ids.greenhouse_nickname.text = self.app.current_greenhouse['nickname']
            
            self.ids.add.text = 'Edit'
            self.ids.lbl_add.text = 'Edit a greenhouse'    
        
    def add_greenhouse(self):
        self.pop = self.app.please_wait('Validating greenhouse...')
        self.pop.open()
        Clock.schedule_once(self.handle_add, 0.5)
          
    def handle_add(self, *args):
        validation_layout = self.ids.validation_layout
        validation_layout.clear_widgets()        
    
        is_valid = True
        
        greenhouse_nickname = self.ids.greenhouse_nickname.text
        text = self.ids.add.text
        width = self.ids.width.text
        length = self.ids.length.text       
        id_regex = '^\w{3,15}'
        
        try:
            float(width)
            if(width==''):
                float('a')  
        except:
            print('error 535')
            is_valid = False
            validation_layout.add_widget(
                                              MyValidationLabel(text = '* Enter a valid width',
                                                            pos_hint= {'center_y': 0.335, 'center_x': 0.5})
                                             )  
        if(greenhouse_nickname == ''):
            is_valid = False
            validation_layout.add_widget(
                                              MyValidationLabel(text = '* Nickname cannot be empty',
                                                            pos_hint= {'center_y': 0.555, 'center_x': 0.5})
                                             )          
        try:
            float(length)  
            if(length==''):
                float('a')  
        except:
            print('error 546')
            is_valid = False
            validation_layout.add_widget(
                                              MyValidationLabel(text = '* Enter a valid length',
                                                            pos_hint= {'center_y': 0.445, 'center_x': 0.5})
                                             )  
           
        if(text == 'Add'):   
            if(is_valid):              
                try:
                    self.app.db.add_greenhouse(self.app.current_user['_id'], greenhouse_nickname, width, length)
                    self.app.root.current = 'greenhouse_home_page' 
                except:
                    print('error 573')
                    self.app.db_connection_error('Could not add greenhouse')
           
        else:   
            if(is_valid ):
                    
                greenhouse = {}
                greenhouse['_id'] = self.app.current_greenhouse['_id']
                greenhouse['user_id'] = self.app.current_user['_id']
                greenhouse['dimensions'] = {}
                greenhouse['dimensions']['width'] = width
                greenhouse['dimensions']['length'] = length
                greenhouse['nickname'] = greenhouse_nickname
                    
                try:
                    self.app.db.edit_greenhouse(greenhouse)
                    self.app.root.current = 'greenhouse_home_page' 
                except:
                    print('error 589')
                    self.app.db_connection_error('Could not edit greenhouse')

    
        self.pop.dismiss()
      
    def on_pre_leave(self):
        self.ids.width.text = ''
        self.ids.length.text = ''	
        self.ids.greenhouse_nickname.text = ''	
        self.ids.lbl_add.text = 'Add a greenhosue'	
        self.ids.add.text = 'Add'	
    pass 
    
class DeviceHomePage(Screen):
    def on_enter(self):
        self.app = App.get_running_app()
        self.app.current_device = None
        self.app.imgbtn_pressed = None     

        if(self.app.current_greenhouse == None or self.app.current_user == None):
            self.app.show_error_message(title='User not authenticated', body = 'Redirecting to home page' )
            self.app.root.current = 'landing_page'           
        else:     
            self.pop = self.app.please_wait('Getting things ready...')
            self.pop.open()      
            self.ids.device_title.text = 'Device home: ' + self.app.current_greenhouse['nickname']
            Clock.schedule_once(self.load_plants, 0.5)
            Clock.schedule_once(self.load_devices, 0.6)
                   
	
        #print('Current greenhouse, device home: '+ app.current_greenhouse['greenhouse_id'])
    def load_plants(self, *args):
        if(self.app.plants is None):
            try:
                self.app.plants = self.app.db.get_plants()
                if(len(self.app.plants) == 0):
                    self.app.db.add_plants()
                    self.app.plants = self.app.db.get_plants()
            except:
                self.app.db_connection_error('Could not load plants')


    def get_last_entry(self, pi_id):
        try:
            return self.app.db.get_last_entry(pi_id)
        except:
            print('error 630')
            self.db_connection_error('Could not load the last entry')
            return None

    def check_connectivity(self, last_entry):
	#if last timestamp more than 3 hours ago
        if(last_entry['ts'] < datetime.utcnow() - timedelta(hours=3)):
            return False
        else:
            return True      
                  
    def load_devices(self, *args):

            
        devices = []
        try:
            devices = self.app.db.get_greenhouse_devices(self.app.current_greenhouse['_id'])
        except:
            self.app.db_connection_error('Could not load the devices')
        grid = MyGridLayout(cols=2, size_hint=(1, None), height = 500)
        grid.bind(minimum_height=grid.setter('height'))
        grid.children[0].text = 'No devices have been added.'                                             
        grid.children[0].size_hint = (1,None)  

        scroll = self.ids.scroll
        scroll.clear_widgets()
        if(len(devices)>0):
            grid.clear_widgets()
 	    
            for device in devices:
                self.add_widget_to_grid(grid, device)      
                
        scroll.add_widget(grid)
        self.pop.dismiss()
                      
    def add_widget_to_grid(self, grid, device):
        big_box = GreenhouseLayout(orientation = 'vertical',size_hint=(1, None), height=230)

        box_top = BoxLayout(size_hint=(1,0.4), orientation = 'horizontal')
        
        label_bottom = Label(text = device['pi_id'],size_hint=(1,0.2))
        
        btn_status= ImageButton(on_release = self.select_connected)
        btn_status.id = str(device['_id'])
        connectivity = None
        last_entry = self.get_last_entry(device['pi_id'])
        if( last_entry != None):
            connectivity = self.check_connectivity(last_entry)	
            if(connectivity):
                btn_status.source = 'icons/connected.png'		
            else:
                btn_status.source = 'icons/disconnected.png'
        else:
            btn_status.source = 'icons/never_connected.png'

        btn_irrigation = ImageButton(source='icons/manual.png', on_release = self.select_irrigation_mode)
        btn_irrigation.id = str(device['_id'])
        if(device['irrigation_mode']):
            btn_irrigation.source ='icons/auto.png'
    
        btn_water = ImageButton(source='icons/irrigation_off.png', on_release = self.select_irrigation_status)
        btn_water.id = str(device['_id'])
        if(device['solenoid_valve']):
            btn_water.source = 'icons/irrigation.png'
        
        btn_busy = None
        if(device['busy'] is not None):
            btn_busy = ImageButton(source='icons/refresh.png', on_release = self.select_irrigation_status)
            btn_busy.id = str(device['_id'])
    
        
        btn_remove = ImageButton(source='icons/remove.png', on_release = self.remove_device)
        btn_remove.id = str(device['_id'])
        
        btn_edit = ImageButton(source='icons/edit.png', on_release = self.edit_device)
        btn_edit.id = str(device['_id'])
        

        box_top.add_widget(btn_status)    
        box_top.add_widget(btn_irrigation)
        box_top.add_widget(btn_water)
        if(btn_busy is not None):
            box_top.add_widget(btn_busy)
        box_top.add_widget(btn_edit)
        box_top.add_widget(btn_remove)	
    
        button = ImageButton(source = 'icons/plants/'+device['plant']+'.png', size_hint = (1,1))
        button.id = str(device['_id'])
        button.on_release = self.select_device
    
        big_box.add_widget(box_top)
        big_box.add_widget(button)
        big_box.add_widget(label_bottom)
    
        grid.add_widget(big_box)               

    def get_device(self, redirect_to):
        _id = ObjectId(self.app.imgbtn_pressed)
        try:
            self.app.current_device = self.app.db.get_device(_id)
            self.app.root.current = redirect_to
        except:
            print('error 722')
            self.app.db_connection_error('Could not load device')
            self.app.root.current = 'landing_page'
        self.pop.dismiss()
        return self.app.current_device

    def select_device(self, *args):
        self.pop = self.app.please_wait('Selecting device...')
        self.pop.open()        
        Clock.schedule_once(lambda x: self.get_device('device_dashboard_page'), 0.5)
    
    def edit_device(self, *args):
        self.pop = self.app.please_wait('Selecting device...')
        self.pop.open()        
        Clock.schedule_once(lambda x: self.get_device('add_device_page'), 0.5)
        
    def remove_device(self, *args):
        device = self.get_device('device_home_page')
        content = BoxLayout(orientation = 'vertical')
        pop = Popup(title='Confirm removal',size_hint=(0.5,0.5))
        
        message_box = BoxLayout(orientation = 'horizontal')
        message_box.add_widget(Image(source = 'icons/remove.png', size_hint = (0.6,0.65),pos_hint= {'center_y': 0.5, 'center_x': 0.5}))
        message_box.add_widget(PopupText(text= 'Are you sure you want to remove ' + device['pi_id'] + '?'))
        
        respond_box = BoxLayout(orientation = 'horizontal', size_hint = (1,0.2),pos_hint= {'center_y': 0.6, 'center_x': 0.5})
        btn_yes = MyAddButton(text = 'Yes', always_release = True,size_hint = (1,1))
        btn_yes.bind(on_press=lambda x: self.confirm_remove(device['_id'],pop))
        respond_box.add_widget(btn_yes)
        btn_no = MyRemoveButton(text = 'No', always_release = True,size_hint = (1,1))
        btn_no.bind(on_press = pop.dismiss)
        respond_box.add_widget(btn_no)
        
        content.add_widget(message_box)
        content.add_widget(respond_box)
        pop.content=content
        pop.open()
        
        self.app.current_device = None	

    def confirm_remove(self,_id,pop):
        self.pop = self.app.please_wait('Removing device...')
        
        Clock.schedule_once(lambda x: self.db_handle_remove(_id), 0.5)
        pop.dismiss()
        Clock.schedule_once(self.load_devices,0.6)        
        
    def db_handle_remove(self, _id,*args):
        try:
            self.app.db.remove_device(_id)        ### remove
        except:
            print('error 773')
            self.app.db_connection_error('Could not remove device')
            
        self.pop.dismiss()
        self.load_devices()

#responsiveness of next three methods
    def select_connected(self, *args):
        device = self.get_device('device_home_page')
        last_entry = self.app.db.get_last_entry(device['pi_id'])
        title = 'Device status: '
        content = BoxLayout(orientation = 'horizontal')
        
        if(last_entry is not None):
            if(self.check_connectivity(last_entry)):
                content.add_widget(Image(source = 'icons/connected.png', size_hint = (0.7,0.65),pos_hint= {'center_y': 0.5, 'center_x': 0.5}))
                content.add_widget(PopupText(text= self.app.current_device['pi_id'] + ' received data within the last three hours'))
                title = title + 'connected'
                ###connected
            else:
                content.add_widget(Image(source = 'icons/disconnected.png', size_hint = (0.7,0.65),pos_hint= {'center_y': 0.5, 'center_x': 0.5}))
                content.add_widget(PopupText(text= self.app.current_device['pi_id'] + ' has not received data within the last three hours'))
                title = title + 'not connected'                ###not_connected
        else:
            content.add_widget(Image(source = 'icons/never_connected.png', size_hint = (0.7,0.65),pos_hint= {'center_y': 0.5, 'center_x': 0.5}))
            content.add_widget(PopupText(text= self.app.current_device['pi_id'] + ' has never received any data'))
            title = title + 'error'#never been
            
        pop = Popup(title= title, 
                    content=content,
                    size_hint=(0.5,0.5))
        pop.open()
        self.app.current_device = None	        

    def select_irrigation_status(self, *args):
        device = self.get_device('device_home_page')
        irrigation_on = self.app.current_device['solenoid_valve']
        title = 'Device Irrigation status: '
        content = BoxLayout(orientation = 'horizontal')
        
        
        if(irrigation_on):
            content.add_widget(Image(source = 'icons/irrigation.png', size_hint = (0.7,0.65),pos_hint= {'center_y': 0.5, 'center_x': 0.5}))
            content.add_widget(PopupText(text= self.app.current_device['pi_id'] + '`s irrigation is currently switched on.'))
            title = title + 'on'
            ###connected
        else:
            content.add_widget(Image(source = 'icons/irrigation_off.png', size_hint = (0.7,0.65),pos_hint= {'center_y': 0.5, 'center_x': 0.5}))
            content.add_widget(PopupText(text= self.app.current_device['pi_id'] + '`s irrigation is currently switched off.'))
            title = title + 'off'                ###not_connected

            
        pop = Popup(title= title, 
                    content=content,
                    size_hint=(0.5,0.5))
        pop.open()
        self.app.current_device = None	          
        
    def select_irrigation_mode(self, *args):
        device = self.get_device('device_home_page')
        irrigation_mode = self.app.current_device['irrigation_mode']
        title = 'Device Irrigation mode: '
        content = BoxLayout(orientation = 'horizontal')
        
        
        if(irrigation_mode):
            content.add_widget(Image(source = 'icons/auto.png', size_hint = (0.7,0.65),pos_hint= {'center_y': 0.5, 'center_x': 0.5}))
            content.add_widget(PopupText(text= self.app.current_device['pi_id'] + '`s irrigation is currently set to automatic.\nThreshold value set at : ' + self.app.current_device['threshold'] +'%'))
            title = title + 'automatic'

        else:
            content.add_widget(Image(source = 'icons/manual.png', size_hint = (0.7,0.65),pos_hint= {'center_y': 0.5, 'center_x': 0.5}))
            content.add_widget(PopupText(text= self.app.current_device['pi_id'] + '`s irrigation is currently set to manual.'))
            title = title + 'manual'               

            
        pop = Popup(title= title, 
                    content=content,
                    size_hint=(0.5,0.5))
        pop.open()
        self.app.current_device = None	          

    def on_leave(self):
        try:
            self.pop.dismiss()
        except:
            print('no pop')
        
    def on_pre_leave(self):
        self.app.previous_screen = self.app.root.current 
        
    def select_help(self):
        message = "Device home page. Add or view devices in your greenhouse."
       
        
        self.imgbtn_pressed = None
        icons = {}
        
        icons['connected'] = {
                          'source' : 'icons/connected.png',
                          'desc'   : 'indicates device connectivity (connected, not connected, never connected)'
                        }
        icons['mode'] = {
                          'source' : 'icons/auto.png',
                          'desc'   : 'indicates irrigation mode (auto, manual)'
                        }
        icons['status'] = {
                          'source' : 'icons/irrigation.png',
                          'desc'   : 'indicates irrigation status (on, off)'
                        }
        icons['edit'] = {
                          'source' : 'icons/edit.png',
                          'desc'   : 'edit device'
                        }
        icons['remove'] = {
                          'source' : 'icons/remove.png',
                          'desc'   : 'remove device'
                        }
                        
        self.app.select_help(icons, message)     
    pass

class AddDevicePage(Screen):
        
    def validate_date(self,day, month, year):
        validation_layout = self.ids.validation_layout
        ts = None
        date_is_valid = True
        isValid = True
        month = self.app.populate_months()[month]['month']
        try:
            day = int(day)
            month = int(month)
            year = int(year)
        except:
            print('error 2234')
            date_is_valid = False
                
        if(date_is_valid):
            ts = datetime(year = year, month = month , day = day)  
            if(ts > datetime.utcnow()):
                isValid = False
                # validation_layout.add_widget(
                                              # MyValidationLabel(text = '*Choose a future date',
                                                                # pos_hint= {'center_y': 0.65, 'center_x': 0.5})
                
                                              # )   
        return [date_is_valid,isValid,ts]
    def on_pre_enter(self):     
        self.app = App.get_running_app()  
        # file_path = 'icons/plants'
        # plant_files = [f for f in listdir(file_path) if isfile(join(file_path, f))]
        # plants_spinner = self.ids.plants
        # plant_names = []
        # for plant in plant_files:
            # plant_names.append(plant[:-4])
        # plant_names.sort()
        # plants_spinner.values = plant_names
        
        plants_spinner = self.ids.plants
        plant_names = []
        for plant in self.app.plants:
            plant_names.append(plant['plant'])
        plant_names.sort()
        
        plants_spinner.values = plant_names
        
        
        self.ids.month.values = list(self.app.populate_months().keys())
        
        #set date to today
        now = datetime.utcnow()
        self.ids.day.text = str(now.day)
        
        self.ids.month.text = self.app.get_monthname(now.month)
        self.ids.year.text = str(now.year)
         
        days = list(range(1,32))
        self.ids.day.values = [str(x) for x in days]
        self.ids.year.values = [str(now.year),str(now.year+1)]
        
        
        if(self.app.current_device is not None):
            self.ids.pi_id.text = self.app.current_device['pi_id']
            self.ids.pi_id.disabled = True
            
            self.ids.threshold.text = self.app.current_device['threshold']
            
            if(self.app.current_device['irrigation_mode']):
                self.ids.auto.state = 'down'
                self.ids.manual.state = 'normal'
            else:
                self.ids.auto.state = 'normal'
                self.ids.manual.state = 'down'
                
            self.ids.plants.text = self.app.current_device['plant']
            
            self.ids.add.text = 'Edit'
            self.ids.lbl_add.text = 'Edit a device'   
               	
    def toggle_state(self, button_text):
        auto_toggle = self.ids.auto
        manual_toggle = self.ids.manual
        if(button_text == 'yes'):
            auto_toggle.state = 'down'
            manual_toggle.state = 'normal'
        else:
            auto_toggle.state = 'normal'
            manual_toggle.state = 'down'
	
    def add_device(self):     
        self.pop = self.app.please_wait('Validating device...')
        self.pop.open()
        Clock.schedule_once(self.handle_add, 0.5)        
        
    def handle_add(self, *args):
        pi_id = self.ids.pi_id.text 
        text = self.ids.add.text
        threshold = self.ids.threshold.text
        mode = self.ids.auto.state == 'down'
        plant = self.ids.plants.text        
        
        validation_layout = self.ids.validation_layout
        validation_layout.clear_widgets()
        is_valid = True
        
        if(plant == 'Choose plant'):
            is_valid = False
            validation_layout.add_widget(
                                         MyValidationLabel( text = '* Choose a plant from the list',
                                                            pos_hint= {'center_y': 0.37, 'center_x': 0.5})
                                             )  
        id_regex = '^\w{3,15}'
        valid_id = re.search(id_regex,pi_id)
        if(valid_id):
            try:
                value = float(threshold)
                if(value<1 or value >99):
                    float('a')
            except:
                print('error 935')
                is_valid = False
                validation_layout.add_widget(
                                                 MyValidationLabel( text = '* Threshold must be between 0 and 100.',
                                                                    pos_hint= {'center_y': 0.605, 'center_x': 0.5})
                                                 )   
            valid_date = self.validate_date(self.ids.day.text, self.ids.month.text, self.ids.year.text)
            if(not valid_date[0]):
                is_valid = False
                validation_layout.add_widget(
                                          MyValidationLabel(text = '*Choose a valid date',
                                                            pos_hint= {'center_y': 0.3, 'center_x': 0.73})
        
                                      )
            elif(not valid_date[1]):
                is_valid = False
                validation_layout.add_widget(
                                          MyValidationLabel(text = '*Future date not allowed',
                                                            pos_hint= {'center_y': 0.3, 'center_x': 0.73})
        
                                      )        
            if(text=='Add' and is_valid):        
                try:
                    if(self.app.db.get_device(pi_id) is not None):        #Add device
                        is_valid = False
                        validation_layout.add_widget(
                                                 MyValidationLabel( text = '* Device id already exists.',
                                                                    pos_hint= {'center_y': 0.715, 'center_x': 0.5})
                                                    )
                    else:
                        try:
                            dt_planted = valid_date[2]
                            self.app.db.add_device(pi_id, mode, threshold, plant,dt_planted,self.app.current_greenhouse['_id'],self.app.current_user['email'],)
                            self.app.root.current = 'device_home_page'                             
                        except:
                            print('error 955')
                            self.app.db_connection_error('Could not add device')    
                except:
                    print('error 958')
                    is_valid - False
                    self.app.db_connection_error('Could not load devices')
            elif(text=='Edit' and is_valid):
                device = {}
                device['_id'] = self.app.current_device['_id']
                device['pi_id'] = pi_id
                device['plant'] = plant
                device['irrigation_mode'] = mode
                device['threshold'] = threshold 
                device['planted_date'] = datetime.utcnow() 
                device['greenhouse_id'] = self.app.current_greenhouse['_id']
                try:
                    self.app.db.edit_device(device)
                    self.app.current_device = None
                    self.app.root.current = 'device_home_page'  
                except:
                    print('error 972')
                    self.app.db_connection_error('Could not edit device')       
        else:
            is_valid = False
            validation_layout.add_widget(
                                             MyValidationLabel( text = '* Device id should contain between 3 and 15 characters..',
                                                                pos_hint= {'center_y': 0.715, 'center_x': 0.5})
                                             )	
        self.pop.dismiss()

    def on_pre_leave(self):
        self.ids.pi_id.text = ''
        self.ids.threshold.text = ''
        self.ids.plants.text = 'Choose plant'
        self.ids.pi_id.disabled = False
        self.ids.add.text = 'Add'
        self.ids.lbl_add.text = 'Add a device'
    
    pass        

class DeviceDashboardPage(Screen):
#general
    def on_pre_enter(self):
        self.app = App.get_running_app()
        self.app.imgbtn_pressed = None   
        
        self.pop = self.app.please_wait('Getting things ready')
        self.pop.open()         
             
        self.app.sensors = ['air temperature', 'soil temperature', 'humidity', 'moisture']           
        sensors = self.app.sensors        
        self.app.alert_toggle_pressed = sensors[0] 
        
        Clock.schedule_once(self.get_last_entry, 0.5)
        Clock.schedule_once(self.get_schedule_states,0.6)
        graphs_path = 'images/graphs/'+self.app.current_device['pi_id']+'/'
        
        if(not exists(graphs_path)):
            makedirs(graphs_path+'year/')
            makedirs(graphs_path+'month/')
            makedirs(graphs_path+'week/')
            makedirs(graphs_path+'day/')
            
    def get_last_entry(self, *args):
        try:
            self.last_entry = self.app.db.get_last_entry(self.app.current_device['pi_id'])
        except:
            print('error 1020')
            self.app.db_connection_error('Could not load entries')   

    def get_schedule_states(self, *args):
        if(self.app.schedule_states is None):
            try:
                self.app.schedule_states = self.app.db.get_shcedule_item_states()
                if(len(self.app.schedule_states) == 0):
                    self.app.db.add_schedule_states()
                    self.app.schedule_states = self.app.db.get_shcedule_item_states()
            except:
                self.app.db_connection_error('Could not load schedule states')

    def set_default_main_navbar(self):
        self.main_navbar =     {                                
                                'current' :    
                                           {   
                                              'disabled' : False ,
                                              'selected' : True,
                                              'on_press' : self.current_view,
                                              'source'   : 'icons/current.png',
                                              'active'   : 'icons/current_selected.png',
                                              'disabled_source': 'icons/current.png'
                                           },
                                'alert' :    
                                           {   
                                              'disabled' : False ,
                                              'selected' : False,
                                              'on_press' : self.alert_view,
                                              'source'   : 'icons/alert.png',
                                              'active'   : 'icons/alert_selected.png',
                                              'disabled_source': 'icons/alert.png'
                                           },
                                'historic' :    
                                           {   
                                              'disabled' : self.last_entry==None,    #if last_entry is None disable historic view
                                              'selected' : False,
                                              'on_press' : self.historic_view,
                                              'source'   : 'icons/analysis.png',
                                              'active'   : 'icons/analysis_selected.png',
                                              'disabled_source': 'icons/analysis_na.png'
                                           },
                                'schedule' :    
                                           {   
                                              'disabled' : self.app.current_device['irrigation_mode']  ,   #if automatic irrigation is enabled disable schedule
                                              'selected' : False,
                                              'on_press' : self.schedule_view,
                                              'source'   : 'icons/schedule.png',
                                              'active'   : 'icons/schedule_selected.png',
                                              'disabled_source': 'icons/schedule_na.png'
                                           }

                                }

    def on_enter(self):
        self.set_default_main_navbar()                                  #can only be called now (otherwise self.last_entry does not exist)
       
        self.historic_navbar = {
                                   'day' :    
                                           {   
                                              'disabled' : True ,
                                              'selected' : False,
                                              'on_press' : self.load_day_view
                                           },
                                   'week' :    
                                           {   
                                              'disabled' : True ,
                                              'selected' : False,
                                              'on_press' : self.load_week_view
                                           },
                                   'month' :    
                                           {   
                                              'disabled' : True ,
                                              'selected' : False,
                                              'on_press' : self.load_month_view
                                           },
                                   'year' :    
                                           {   
                                              'disabled' : True ,
                                              'selected' : False,
                                              'on_press' : self.load_year_view
                                           }
                                }
        
        if(self.last_entry is not None):
            self.ids.last_updated.text = 'last updated : ' +   str(self.last_entry['ts'].strftime("%d/%m/%Y, %H:%M"))
        
        self.ids.dashboard_title.text = self.app.current_device['pi_id']+' dashboard'
        
        self.pop.dismiss()
        Clock.schedule_once(self.get_graph_data, 0.5)
        self.current_view()
        
    def get_graph_data(self, *args):
        end_date = datetime.utcnow()
        #getting for current day only
        start_date = datetime(year = end_date.year, month = end_date.month, day = end_date.day, tzinfo=tzutc())
        self.daily_sensor_data = self.app.db.get_daily_data(start_date,end_date,self.app.current_device['pi_id'],4)
        if(len(self.daily_sensor_data)>0):
            self.historic_navbar['day']['disabled'] = False
        
        #getting data for the last 7 days only
        start_date = end_date - timedelta(days=7)
        self.weekly_sensor_data = self.app.db.get_weekly_data(start_date,end_date,self.app.current_device['pi_id'],4)        
        if(len(self.weekly_sensor_data)>0):
            self.historic_navbar['week']['disabled'] = False
                   
        #getting data for current year only
        start_date = datetime(year = end_date.year, month = end_date.month, day = 1, tzinfo=tzutc())
        self.monthly_sensor_data = self.app.db.get_monthly_data(start_date,end_date,self.app.current_device['pi_id'],4)
        if(len(self.monthly_sensor_data)>0):
            self.historic_navbar['month']['disabled'] = False
 
        #getting data for past 3 years
        start_date = datetime(year = (end_date.year - 3), month = 1, day = 1, tzinfo=tzutc())
        self.yearly_sensor_data = self.app.db.get_yearly_data(start_date,end_date,self.app.current_device['pi_id'],4)
        if(len(self.yearly_sensor_data)>0):
            self.historic_navbar['year']['disabled'] = False
   
    def load_main_navbar(self, selected = None):
        box = BoxLayout(orientation = 'horizontal', size_hint = (0.4,0.2), pos_hint = {'center_y': 0.92, 'center_x': 0.5})    
        
        for key in self.main_navbar.keys():
            btn = ImageButton(on_press =self.main_navbar[key]['on_press'] )
            if (self.main_navbar[key]['selected']):
                btn.source = self.main_navbar[key]['active']
                btn.state = 'down'
            elif (self.main_navbar[key]['disabled']):
                btn.source = self.main_navbar[key]['disabled_source']
                btn.disabled = True
            else:
                btn.source = self.main_navbar[key]['source']
                btn.state = 'normal'
            box.add_widget(btn)        
        
        return box
  
         
#historic view methods      
    #screen  
    def load_hist_navbar(self, selected = None):
        nav_bar = BoxLayout(
                            orientation = 'horizontal',
                            id = 'nav_bar',
                            size_hint= ( 1, 0.1 ),
                            pos_hint = {'center_y': 0.8, 'center_x': 0.5}
		            )
        for key in self.historic_navbar.keys():
            if(not self.historic_navbar[key]['disabled']):
                toggle = MyToggleButton(
                                         text = key,
                                         group= 'time',
                                         state= 'normal',
                                         on_press = self.historic_navbar[key]['on_press']
                                        )
                if(toggle.text == selected):
                    toggle.state = 'down'
                    toggle.disabled = True
                nav_bar.add_widget(toggle)      
        return nav_bar
 
    def set_no_select(self):
        for key in self.historic_navbar.keys():
            self.historic_navbar[key]['selected'] = False 
        
    def historic_view(self,*args):
        self.set_default_main_navbar()
        self.main_navbar['historic']['selected'] = True
        self.main_navbar['current']['selected'] = False
        
        self.ids.dashboard_page_title.text = 'Historic analysis'
         
        self.set_no_select()
        enabled_keys = [key  for (key, value) in self.historic_navbar.items() if not value['disabled']]
        
        if(len(enabled_keys)>0):
            key = enabled_keys[0]
            self.historic_navbar[key]['on_press']()
                  
    #graphs
    def draw_humidity_graph(self,x, y, dt, title,device, x_label = ''):
        graphs_path = 'images/graphs/'+device['pi_id']+'/'+dt +'/'
        bar_colours = (0.12 , 0.531 , 0.32 , 0.8),(0.12 , 0.331 , 0.22 , 0.8)
        GreenhouseGraph.bar_chart(title,x,y,x_label,'Average humidity (%)',bar_colours, [0,100],destination = graphs_path + 'hum.png')    
 
    def draw_moisture_graph(self,x, y, dt, title,device, x_label = ''):
        graphs_path = 'images/graphs/'+device['pi_id']+'/'+dt +'/'
        bar_colours = (0.531 , 0.32 , 0.12 , 0.8),(0.331 , 0.22 , 0.12 , 0.8)
        GreenhouseGraph.bar_chart(title,x,y,x_label,'Average soil moisture (%)',bar_colours, [0,100],destination = graphs_path + 'moisture.png')    
    
    def draw_air_temp_graph(self,x, y, dt, title,device, x_label = ''):
        graphs_path = 'images/graphs/'+device['pi_id']+'/'+dt +'/'
        bar_colours = (0.32 , 0.12 , 0.531 , 0.8),(0.22 , 0.12 , 0.331 , 0.8)
        GreenhouseGraph.bar_chart(title,x,y,x_label,'Average air temp ',bar_colours, [0,35],destination = graphs_path + 'airtemp.png')    
    
    def draw_soil_temp_graph(self,x, y, dt, title,device, x_label = ''):
        graphs_path = 'images/graphs/'+device['pi_id']+'/'+dt +'/'
        bar_colours = (0.45 , 0.45 , 0.45  , 0.8),(0.12 , 0.12 , 0.12, 0.8)
        GreenhouseGraph.bar_chart(title,x,y,x_label,'Average soil temp',bar_colours, [0,35],destination = graphs_path + 'soiltemp.png')    
        
    def handle_draw_graphs(self,data, *args):
        
        x           = data['x']
        humidity    = data['humidity']
        moisture    = data['moisture']
        air_temp    = data['air_temp']   
        soil_temp   = data['soil_temp']    

        time_frame = ''
        x_label = ''
        today = date.today()
        if(self.historic_navbar['day']['selected']):
            time_frame = 'day'
            x_label = 'time (today)'
        elif(self.historic_navbar['week']['selected']):
            time_frame = 'week'
            x_label = 'date ('+str(today.month)+')'
        elif(self.historic_navbar['month']['selected']):
            time_frame = 'month'
            x_label = 'month ('+str(today.year)+')'
        elif(self.historic_navbar['year']['selected']):
            time_frame = 'year'
            x_label = ''
        
        
        self.draw_humidity_graph(x,humidity,time_frame,'',self.app.current_device,x_label)
        self.draw_moisture_graph(x,moisture,time_frame,'',self.app.current_device,x_label)
        self.draw_air_temp_graph(x,air_temp,time_frame,'',self.app.current_device,x_label)
        self.draw_soil_temp_graph(x,soil_temp,time_frame,'',self.app.current_device,x_label)
    
    def handle_load_graphs(self, file_path,grid,container, scroll, *args):
        graph_files = [f for f in listdir(file_path) if isfile(join(file_path, f))]

        for i in range(len(graph_files)):
            img = Image(source = file_path + graph_files[i])
            grid.add_widget(img)                     
       
        scroll.add_widget(grid)
        container.add_widget(scroll) 
        
        self.pop.dismiss()       
        return grid
        
    def load_day_view(self, *args):
        self.pop = self.app.please_wait('Drawing graphs...')
        self.pop.open()      
        
        container = self.ids.container
        container.clear_widgets()        
        container.add_widget(self.load_main_navbar())
        
        self.set_no_select()
        self.historic_navbar['day']['selected'] = True
        
        nav_bar = self.load_hist_navbar(selected = 'day')  
        container.add_widget(nav_bar)     
               
        scroll =ScrollView(
                            pos_hint= {'center_y': 0.38, 'center_x': 0.5},                
                            size_hint= (1, 0.75),
                            do_scroll_x = False	   , 
                            id = 'scroll'
                         )
        grid = MyGridLayout(cols=2, size_hint=(1, None), height = 500)
        grid.clear_widgets() 
    
        x = []
        humidity = []
        moisture = []
        air_temp = []
        soil_temp = []

        #loop through each record	    
        for record in self.daily_sensor_data:
            d = record['_id']['hour']
            #d = str(record['_id']['hour'])+ ':00'

            x.append(d)
                    
            humidity.append(record['avgHum'])
            moisture.append(record['avgMoist'])
            air_temp.append(record['avgTemp'])
            soil_temp.append(record['avgSoilTemp'])
        
        data = { 
                'x' : x,
                'humidity' : humidity,
                'moisture' : moisture,
                'air_temp' : air_temp,
                'soil_temp' : soil_temp
                }
        Clock.schedule_once(lambda x: self.handle_draw_graphs(data), 0.5)

        file_path = 'images/graphs/'+self.app.current_device['pi_id']+'/day/'       
        Clock.schedule_once(lambda x: self.handle_load_graphs(file_path,grid, container, scroll), 0.6)  
        
    def load_week_view(self, *args):
        self.pop = self.app.please_wait('Drawing graphs...')
        self.pop.open()  
        
        container = self.ids.container
        container.clear_widgets()
        container.add_widget(self.load_main_navbar())
        
        self.set_no_select()
        self.historic_navbar['week']['selected'] = True
        
        nav_bar = self.load_hist_navbar(selected = 'week')  
        container.add_widget(nav_bar)  

        scroll =ScrollView(
                            pos_hint= {'center_y': 0.38, 'center_x': 0.5},                
                            size_hint= (1, 0.75),
                            do_scroll_x = False	   , 
                            id = 'scroll'
                         )
                            
        grid = MyGridLayout(cols=2, size_hint=(1, None), height = 500)
        grid.clear_widgets() 

        x = []
        humidity = []
        moisture = []
        air_temp = []
        soil_temp = []

        #loop through each record	    
        for record in self.weekly_sensor_data:
            d = record['_id']['day']
            x.append(d)
                    
            humidity.append(record['avgHum'])
            moisture.append(record['avgMoist'])
            air_temp.append(record['avgTemp'])
            soil_temp.append(record['avgSoilTemp'])
                
        data = { 
                'x' : x,
                'humidity' : humidity,
                'moisture' : moisture,
                'air_temp' : air_temp,
                'soil_temp' : soil_temp
                }
        Clock.schedule_once(lambda x: self.handle_draw_graphs(data), 0.5)

        file_path = 'images/graphs/'+self.app.current_device['pi_id']+'/week/'       
        Clock.schedule_once(lambda x: self.handle_load_graphs(file_path,grid, container, scroll), 0.6)  
        
    def load_month_view(self, *args):
        self.pop = self.app.please_wait('Drawing graphs...')
        self.pop.open()      
        
        container = self.ids.container
        container.clear_widgets()
        container.add_widget(self.load_main_navbar())
        
        self.set_no_select()
        self.historic_navbar['month']['selected'] = True
             
        nav_bar = self.load_hist_navbar(selected = 'month')  
        container.add_widget(nav_bar)                  
       
        scroll =ScrollView(
                            pos_hint= {'center_y': 0.38, 'center_x': 0.5},                
                            size_hint= (1, 0.75),
                            do_scroll_x = False	   , 
                            id = 'scroll'
                         )
                            
        grid = MyGridLayout(cols=2, size_hint=(1, None), height = 500)
        grid.clear_widgets() 
        
        x = []
        humidity = []
        moisture = []
        air_temp = []
        soil_temp = []

        #loop through each record	    
        for record in self.monthly_sensor_data:
            d = record['_id']['month']
            x.append(d)
                    
            humidity.append(record['avgHum'])
            moisture.append(record['avgMoist'])
            air_temp.append(record['avgTemp'])
            soil_temp.append(record['avgSoilTemp'])
                
        data = { 
                'x' : x,
                'humidity' : humidity,
                'moisture' : moisture,
                'air_temp' : air_temp,
                'soil_temp' : soil_temp
                }
        Clock.schedule_once(lambda x: self.handle_draw_graphs(data), 0.5)

        file_path = 'images/graphs/'+self.app.current_device['pi_id']+'/month/'       
        Clock.schedule_once(lambda x: self.handle_load_graphs(file_path,grid, container, scroll), 0.6)  
        
    def load_year_view(self, *args):
        self.pop = self.app.please_wait('Drawing graphs...')
        self.pop.open()      
        
        
        container = self.ids.container
        container.clear_widgets()
        container.add_widget(self.load_main_navbar())
        
        self.set_no_select()
        self.historic_navbar['year']['selected'] = True
             
        nav_bar = self.load_hist_navbar(selected = 'year')  
        container.add_widget(nav_bar)  
                        
        scroll =ScrollView(
                            pos_hint= {'center_y': 0.38, 'center_x': 0.5},                
                            size_hint= (1, 0.75),
                            do_scroll_x = False	   , 
                            id = 'scroll'
                         )
                            
        grid = MyGridLayout(cols=2, size_hint=(1, None), height = 500)
        grid.clear_widgets() 
        

        x = []
        humidity = []
        moisture = []
        air_temp = []
        soil_temp = []

        #loop through each record	    
        for record in self.yearly_sensor_data:
            d = record['_id']['year']
            x.append(d)
                    
            humidity.append(record['avgHum'])
            moisture.append(record['avgMoist'])
            air_temp.append(record['avgTemp'])
            soil_temp.append(record['avgSoilTemp'])
                   
        data = { 
                'x' : x,
                'humidity' : humidity,
                'moisture' : moisture,
                'air_temp' : air_temp,
                'soil_temp' : soil_temp
                }
        Clock.schedule_once(lambda x: self.handle_draw_graphs(data), 0.5)

        file_path = 'images/graphs/'+self.app.current_device['pi_id']+'/year/'       
        Clock.schedule_once(lambda x: self.handle_load_graphs(file_path,grid, container, scroll), 0.6)  


#current view
    def current_view(self, *args):
        self.set_default_main_navbar()
        
        self.ids.dashboard_page_title.text = 'Current View'
         
        container = self.ids.container
        container.clear_widgets()
        container.add_widget(self.load_main_navbar())    
        #air
        air_temp_float = FloatLayout(size_hint = (0.25,0.33), pos_hint= {'center_y': 0.65, 'center_x': 0.11})
        air_temp_float.add_widget(Image(source = 'icons/blank_left.png',pos_hint = {'center_y': 0.5, 'center_x': 0.5}))
        #humidity
        hum_float = FloatLayout(size_hint = (0.25,0.33), pos_hint= {'center_y': 0.7, 'center_x': 0.32})
        hum_float.add_widget(Image(source = 'icons/blank_left.png',pos_hint = {'center_y': 0.5, 'center_x': 0.5}))        
        #moisture
        moisture_float = FloatLayout(size_hint = (0.25,0.33), pos_hint= {'center_y': 0.7, 'center_x': 0.68})
        moisture_float.add_widget(Image(source = 'icons/blank_right.png',pos_hint = {'center_y': 0.5, 'center_x': 0.5}))
        #soil
        soil_temp_float = FloatLayout(size_hint = (0.25,0.33), pos_hint= {'center_y': 0.65, 'center_x': 0.89})
        soil_temp_float.add_widget(Image(source = 'icons/blank_right.png',pos_hint = {'center_y': 0.5, 'center_x': 0.5}))                

        
        solenoid_valve = self.app.current_device['solenoid_valve']
        if(solenoid_valve):
            container.add_widget(Image(source = 'icons/irrigation_active.png', size_hint = (0.2,0.2),pos_hint= {'center_y': 0.4, 'center_x': 0.5}))

        else:
            container.add_widget(Image(source = 'icons/irrigation_not_active.png', size_hint = (0.2,0.2),pos_hint= {'center_y': 0.4, 'center_x': 0.5}))    
                
        irrigation_mode = self.app.current_device['irrigation_mode']
        switch = Switch(active = irrigation_mode,pos_hint= {'center_y': 0.53, 'center_x': 0.5}, size_hint = (0.2,0.2))
        if(irrigation_mode):
            irrigation_mode = 'Auto'
            container.add_widget(Image(source = 'icons/auto.png', size_hint = (0.2,0.2),pos_hint= {'center_y': 0.65, 'center_x': 0.5}))
        else:
            irrigation_mode = 'Manual'
            container.add_widget(Image(source = 'icons/manual.png', size_hint = (0.2,0.2),pos_hint= {'center_y': 0.65, 'center_x': 0.5}))
            
        
        switch.bind(active=self.irrigation_switch) 
        container.add_widget(switch)                
            
            
        container.add_widget(Image(source = 'icons/plants/'+self.app.current_device['plant']+'.png', size_hint = (0.2,0.2),pos_hint= {'center_y': 0.2, 'center_x': 0.5}))


        
         #titles
        air_temp_title = SensorTitle(text = 'NA', pos_hint = {'center_y': 0.5, 'center_x': 0.5}) 
        humidity_title = SensorTitle(text = 'NA', pos_hint = {'center_y': 0.5, 'center_x': 0.5}) 
        moisture_title =SensorTitle(text = 'NA', pos_hint = {'center_y': 0.5, 'center_x': 0.5})
        soil_temp_title= SensorTitle(text = 'NA', pos_hint = {'center_y': 0.5, 'center_x': 0.5})       

        btn_remove =  ImageButton(source = 'icons/remove.png', size_hint = (0.2,0.2),pos_hint= {'center_y': 0.35, 'center_x': 0.92}, on_press = self.remove_device)
        btn_edit =  ImageButton(source = 'icons/edit.png', size_hint = (0.2,0.2),pos_hint= {'center_y': 0.35, 'center_x': 0.75}, on_press = self.edit_device)
        container.add_widget(btn_edit)
        container.add_widget(btn_remove)
        

        plant_days = 0
        for plant in self.app.plants:
            if(plant['plant']==self.app.current_device['plant']):
                plant_days = plant['days']
                
        progress = ProgressBar(max = plant_days, size_hint = (0.5,0.1),pos_hint= {'center_y': 0.08, 'center_x': 0.5} )
        
        plant_time = (datetime.utcnow() - self.app.current_device['planted_date']).days
        progress.value = plant_time
        if((plant_days - plant_time)>0):
            text = 'Harvest in {} days'.format((plant_days - plant_time))
        else:
            text = 'Ready to harvest'
        container.add_widget(Label(text = text,pos_hint= {'center_y': 0.05, 'center_x': 0.5} )) 
        
        #progress.value = 15                        
        container.add_widget(progress)
        
        planted_date = self.app.current_device['planted_date']
        harvest_date = planted_date + timedelta(days = plant_days)
        planted_date = datetime.fromisoformat(str(planted_date))
        harvest_date = datetime.fromisoformat(str(harvest_date))
        
        container.add_widget(Image(source = 'icons/planted.png', size_hint = (0.2,0.2),pos_hint= {'center_y': 0.16, 'center_x': 0.1}))     
        container.add_widget(Label(text = planted_date.strftime("%d-%m-%Y"),pos_hint= {'center_y': 0.03, 'center_x': 0.1} ))                            
        
        container.add_widget(Image(source = 'icons/harvest.png', size_hint = (0.2,0.2),pos_hint= {'center_y': 0.16, 'center_x': 0.9}))  
        container.add_widget(Label(text = harvest_date.strftime("%d-%m-%Y"),pos_hint= {'center_y': 0.03, 'center_x': 0.9} ))                            
           
        if(self.last_entry is not None):
            air_temp = self.last_entry['air_temp']
            soil_temp = self.last_entry['soil_temp']
            humidity = self.last_entry['humidity']
            moisture = self.last_entry['moisture']
            
            temp_string_format = '{0:.1f}\u00b0C'
            hum_string_format = '{0:.1f}%'
            
            air_temp_title.text= temp_string_format.format(air_temp)
            humidity_title.text= hum_string_format.format(humidity)            
            moisture_title.text= hum_string_format.format(moisture)        
            soil_temp_title.text= temp_string_format.format(soil_temp)
                     
            if(self.check_connectivity()):
                connectivity =  Image(source = 'icons/connected.png', size_hint = (0.2,0.2),pos_hint= {'center_y': 0.35, 'center_x': 0.08})
                container.add_widget(connectivity)                                
                container.add_widget(SensorTitle(text= 'Data received within the last 3 hours' ,
                                                 pos_hint = {'center_y': 0.35, 'center_x': 0.3},
                                                 size_hint = (0.25,0.2)))
                ###connected
            
            else:
                connectivity =  Image(source = 'icons/disconnected.png', size_hint = (0.2,0.2),pos_hint= {'center_y': 0.35, 'center_x': 0.08})
                container.add_widget(connectivity)                                
                container.add_widget(SensorTitle(text= 'Data not received within the last 3 hours' ,
                                                 pos_hint = {'center_y': 0.35, 'center_x': 0.3},
                                                 size_hint = (0.25,0.2)))
        else:
            connectivity =  Image(source = 'icons/never_connected.png', size_hint = (0.2,0.2),pos_hint= {'center_y': 0.35, 'center_x': 0.08})
            container.add_widget(connectivity)                                
            container.add_widget(SensorTitle(text= 'No data has been received' ,
                                             pos_hint = {'center_y': 0.35, 'center_x': 0.3},
                                             size_hint = (0.25,0.2)))    
             

        air_temp_float.add_widget(air_temp_title)
        container.add_widget(air_temp_float)
        
        hum_float.add_widget(humidity_title)
        container.add_widget(hum_float)
        
        moisture_float.add_widget(moisture_title)
        container.add_widget(moisture_float)
        
        soil_temp_float.add_widget(soil_temp_title)         
        container.add_widget(soil_temp_float)         
        
        container.add_widget(SensorTitle(text= 'Air Temperature' ,
                                         pos_hint = {'center_y': 0.75, 'center_x': 0.11},
                                         size_hint = (0.25,0.2)))
        container.add_widget(SensorTitle(text= 'Humidity' ,
                                         pos_hint = {'center_y': 0.8, 'center_x': 0.32},
                                         size_hint = (0.25,0.2)))
        container.add_widget(SensorTitle(text= irrigation_mode ,
                                         pos_hint = {'center_y': 0.75, 'center_x': 0.5},
                                         size_hint = (0.25,0.2)))
        container.add_widget(SensorTitle(text= 'Moisture' ,
                                         pos_hint = {'center_y': 0.8, 'center_x': 0.68},
                                         size_hint = (0.25,0.2)))
        container.add_widget(SensorTitle(text= 'Soil Temperature' ,
                                         pos_hint = {'center_y': 0.75, 'center_x': 0.89},
                                         size_hint = (0.25,0.2)))     
        
    def irrigation_switch(self,instance, value):
        content = BoxLayout(orientation = 'vertical')
        pop = Popup(title='Confirm switch',size_hint=(0.5,0.5))
        
        message_box = BoxLayout(orientation = 'horizontal')
        message_box.add_widget(Image(source = 'icons/help.png', size_hint = (0.6,0.65),pos_hint= {'center_y': 0.5, 'center_x': 0.5}))
        btn_yes = MyAddButton(text = 'Yes', always_release = True,size_hint = (1,1))
        if(value):
            btn_yes.bind(on_press=lambda x: self.confirm_irrigation_switch(self.app.current_device['_id'],1,pop))
            message_box.add_widget(PopupText(text= 'Are you sure you want to enable auomatic irrigation for ' + self.app.current_device['pi_id'] +'?'))               
        else:
            btn_yes.bind(on_press=lambda x: self.confirm_irrigation_switch(self.app.current_device['_id'],0,pop))
            message_box.add_widget(PopupText(text= 'Are you sure you want to enable manual irrigation for ' + self.app.current_device['pi_id'] +'?'))               
        
                
        respond_box = BoxLayout(orientation = 'horizontal', size_hint = (1,0.2),pos_hint= {'center_y': 0.6, 'center_x': 0.5})
        respond_box.add_widget(btn_yes)

        btn_no = MyRemoveButton(text = 'No', always_release = True,size_hint = (1,1))
        btn_no.bind(on_press=lambda x: self.leave_irrigation(pop))
        respond_box.add_widget(btn_no)
        
        content.add_widget(message_box)
        content.add_widget(respond_box)
        pop.content=content
        pop.open()    
            
    def confirm_irrigation_switch(self, _id, state, pop):
        try:
            self.app.current_device = self.app.db.update_irrigation_mode(_id,state)
            self.current_view()
            pop.dismiss()
        except:
            print('error 1608')
            self.app.db_connection_error('Could not change the irrigation mode')
            
    def leave_irrigation(self, pop):
        pop.dismiss()
        self.current_view()  
    
    def check_connectivity(self):
	#if last timestamp more than 3 hours ago
        if(self.last_entry['ts'] < datetime.utcnow() - timedelta(hours=3)):
            return False
        else:
            return True  

    def edit_device(self, *args):
        self.app.previous_screen = self.app.root.current
        self.app.root.current = 'add_device_page'
        
    def remove_device(self,*args):
        content = BoxLayout(orientation = 'vertical')
        pop = Popup(title='Confirm removal',size_hint=(0.5,0.5))
        
        message_box = BoxLayout(orientation = 'horizontal')
        message_box.add_widget(Image(source = 'icons/remove.png', size_hint = (0.6,0.65),pos_hint= {'center_y': 0.5, 'center_x': 0.5}))
        message_box.add_widget(PopupText(text= 'Are you sure you want to remove ' + self.app.current_device['pi_id'] + '?'))
        
        respond_box = BoxLayout(orientation = 'horizontal', size_hint = (1,0.2),pos_hint= {'center_y': 0.6, 'center_x': 0.5})
        btn_yes = MyAddButton(text = 'Yes', always_release = True,size_hint = (1,1))
        btn_yes.bind(on_press=lambda x: self.confirm_remove(pop))
        respond_box.add_widget(btn_yes)
        btn_no = MyRemoveButton(text = 'No', always_release = True,size_hint = (1,1))
        btn_no.bind(on_press = pop.dismiss)
        respond_box.add_widget(btn_no)
        
        content.add_widget(message_box)
        content.add_widget(respond_box)
        pop.content=content
        pop.open()
        
    def confirm_remove(self,pop):

        self.pop = self.app.please_wait('Removing device...')
        
        Clock.schedule_once(lambda x: self.db_handle_remove(self.app.current_device['_id']), 0.5)
        pop.dismiss()
        
    def db_handle_remove(self, _id,*args):
        try:
            self.app.db.remove_device(_id)        ### remove
            self.app.root.current = 'device_home_page'
        except:
            print('error 1857')
            self.app.db_connection_error('Could not remove device')
            
        self.pop.dismiss()



#schedule view                        

    def btn_add_item_press(self, *args):
        self.app.root.current = 'add_schedule_item_page'

    def schedule_view(self,*args):       
        self.set_default_main_navbar()
        self.main_navbar['schedule']['selected'] = True
        self.main_navbar['current']['selected'] = False
        
        self.ids.dashboard_page_title.text = 'Schedule'

        container = self.ids.container
        container.clear_widgets()
        container.add_widget(self.load_main_navbar())
        main_layout = self.ids.float
        
        scroll =ScrollView(
                            pos_hint= {'center_y': 0.47, 'center_x': 0.5},                
                            size_hint= (1, 0.77),
                            do_scroll_x = False
                         )

        nav_bar = BoxLayout(
                                orientation = 'horizontal',
                                size_hint= ( 1, 0.1 ),
                                pos_hint = {'center_y': 0.79, 'center_x': 0.5}
		            )
        
        grid = MyGridLayout(cols=1, size_hint=(1, None), height = 500)
                            
        grid.children[0].text = 'No schedule items have been added.'                                             
        grid.children[0].size_hint = (1,None)                                              


        schedule_items = self.app.db.get_schedule(self.app.current_device['_id'])
        
        num_items = len(schedule_items)
        if(num_items==0):
            alerts = None
        elif(num_items>3):
            grid.height = num_items*150
        

        if(schedule_items is not None ):
            grid.clear_widgets()
            grid.cols = 1           
            for item in schedule_items:
                _id =    str(item['_id'])
                ts = datetime.fromisoformat(str(item['ts']))
                created = datetime.fromisoformat(str(item['created']))
                duration = int(item['duration'])
                threshold = float(item['threshold'])
                status = item['state']
                colour = None
                

                    
                label_desc = 'Created on ' + created.strftime("%d-%m-%Y at %H:%M")
                
                ts_scheduled = 'Scheduled for ' + ts.strftime("%d-%m-%Y at %H:%M")
                temp_string_format = '{0:.1f}\u00b0C'
                hum_string_format = '{0:.1f}%'           
                     
                big_box= MyCustomWhiteBox(orientation = 'horizontal', size_hint=(1, None))
                
                float_box = FloatLayout(size_hint = (1,0.6))      
                if(threshold>0):
                    big_box.add_widget(Image(source= 'icons/moisture.png',size_hint = (0.2,1)))
                    float_box.add_widget(MyScheduleTitle(text = hum_string_format.format(threshold),pos_hint = {'center_y': 0.95, 'center_x': 0.3}, size_hint = (0.5,0.2)))
                else:
                    big_box.add_widget(Image(source= 'icons/clock.png',size_hint = (0.2,1)))
                    float_box.add_widget(MyScheduleTitle(text = str(duration) + ' min',pos_hint = {'center_y': 0.95, 'center_x': 0.3}, size_hint = (0.5,0.2)))

                float_box.add_widget(MyScheduleTitle ( text = ts_scheduled,pos_hint = {'center_y': 0.8, 'center_x': 0.5}, size_hint = (0.3,0.18)))
                
                for state in self.app.schedule_states:
                    if(status==state['state_id']):
                        status = state['state']
                        colour = state['colour']

                float_box.add_widget(MyScheduleTitle ( text = status, color = colour,pos_hint = {'center_y': 0.8, 'center_x': 0.95}, size_hint = (0.4,0.2)))                
                
                
                float_box.add_widget(MyScheduleTitle ( text = label_desc,pos_hint = {'center_y': 0.3, 'center_x': 0.18}, size_hint = (0.3,0.18)))
                
                big_box.add_widget(float_box)
                big_box.add_widget(ImageButton(source= 'icons/remove.png',size_hint = (0.2,1), id = _id, on_release = self.remove_schedule_item))
                                
                              
                grid.add_widget(big_box)    

        float_layout = BoxLayout(size_hint=(1,None))
        float_layout.add_widget(MyAddAlertButton(text='Add item', on_press = self.btn_add_item_press,size_hint=(0.3,None),pos_hint = {'center_y': 0.5, 'center_x': 0.5}))

        grid.add_widget(float_layout)
        scroll.add_widget(grid)
        container.add_widget(scroll)
        container.add_widget(nav_bar)   
        
    def remove_schedule_item(self, *args):


        _id = ObjectId(self.app.imgbtn_pressed)
        
        content = BoxLayout(orientation = 'vertical')
        pop = Popup(title='Confirm removal',size_hint=(0.5,0.5))
        
        message_box = BoxLayout(orientation = 'horizontal')
        message_box.add_widget(Image(source = 'icons/remove.png', size_hint = (0.6,0.65),pos_hint= {'center_y': 0.5, 'center_x': 0.5}))
        message_box.add_widget(PopupText(text= 'Are you sure you want to remove the schedule item?'))
        
        respond_box = BoxLayout(orientation = 'horizontal', size_hint = (1,0.2),pos_hint= {'center_y': 0.6, 'center_x': 0.5})
        btn_yes = MyAddButton(text = 'Yes', always_release = True,size_hint = (1,1))
        
        btn_yes.bind(on_press=lambda x: self.confirm_remove_item(_id,pop))
        respond_box.add_widget(btn_yes)
        btn_no = MyRemoveButton(text = 'No', always_release = True,size_hint = (1,1))
        btn_no.bind(on_press = pop.dismiss)
        respond_box.add_widget(btn_no)
        
        content.add_widget(message_box)
        content.add_widget(respond_box)
        pop.content=content
        pop.open()
        
        self.app.current_greenhouse = None	
         
    def confirm_remove_item(self,_id,pop1):
        self.pop = self.app.please_wait('Removing schedule item...')
        self.pop.open()                                                 
        
        Clock.schedule_once(lambda x: self.db_handle_remove_item(_id), 0.5)
        pop1.dismiss()
        Clock.schedule_once(self.schedule_view,0.6)
    
    def db_handle_remove_item(self, _id,*args):
        try:
            self.app.db.remove_schedule_item(_id)        ### remove
            self.pop.dismiss()
            self.schedule_view()
            
        except:
            print('error 1937')
            self.pop = self.app.db_connection_error('Could not remove schedule item')

#alert view 
    def btn_add_alert_press(self,args):
        self.app.root.current = 'add_alert_page'	                

    def btn_edit_alert_press(self,args):
            
        _id = self.app.imgbtn_pressed
        _id = ObjectId(_id)

        self.app.current_alert = self.app.db.get_alert(_id)
        self.app.root.current = 'add_alert_page'      
              
    def toggle_btn_sensor_press(self,args):
        sensor = self.app.alert_toggle_pressed
        self.alert_view(sensor)
        
    def active_switch(self,instance, value):
        _id = ObjectId(instance.id)
        alert = self.app.db.get_alert(_id)
        
        
        alert['active'] = value
        self.app.db.edit_alert(alert)

    def alert_view(self, sensor = None ):
        self.set_default_main_navbar()
        self.main_navbar['alert']['selected'] = True
        self.main_navbar['current']['selected'] = False
        
        self.ids.dashboard_page_title.text = 'Alerts'

        container = self.ids.container
        container.clear_widgets()
        container.add_widget(self.load_main_navbar())
        main_layout = self.ids.float
        if( sensor is None or isinstance(sensor,str)==False):
            if(self.app.alert_toggle_pressed is not None):
                sensor = self.app.alert_toggle_pressed 
            else:
                sensor = self.app.sensors[0]

                
        scroll =ScrollView(
                            pos_hint= {'center_y': 0.38, 'center_x': 0.5},                
                            size_hint= (1, 0.75),
                            do_scroll_x = False
                         )

        nav_bar = BoxLayout(
                                orientation = 'horizontal',
                                size_hint= ( 1, 0.1 ),
                                pos_hint = {'center_y': 0.79, 'center_x': 0.5}
		            )
        
        grid = MyGridLayout(cols=1, size_hint=(1, None), height = 500)
                            
        grid.children[0].text = 'No alerts have been added.'                                             
        grid.children[0].size_hint = (1,None)                                              


        alerts = self.app.db.get_alerts( sensor , self.app.current_device['_id'])
        
        
        
        num_alerts = len(alerts)
        if(num_alerts==0):
            alerts = None
        elif(num_alerts>3):
            grid.height = num_alerts*150
        

        if(alerts is not None ):
            grid.clear_widgets()
            grid.cols = 1           
            str_fmt = '{0:.1f}\u00b0C'
            if(sensor == 'humidity' or sensor == 'moisture'):
                str_fmt = '{0:.1f}%'
            for alert in alerts:        
                greater_than = alert['greater_than']
                recurring = alert['recurring']
                value = alert['value']
                active = alert['active']

                
                big_box= MyCustomWhiteBox(orientation = 'horizontal', size_hint=(1, None))
 
                img_box = BoxLayout(orientation = 'horizontal', size_hint = (0.4,1),padding = (6,0))
                left_box =     BoxLayout(orientation = 'vertical')
                right_box =     BoxLayout(orientation = 'vertical')
                edit_box = BoxLayout(orientation = 'horizontal', size_hint = (0.4,1),padding = (6,0))
                     
                left_box.add_widget(MyAlertTitle (size_hint = (0.6,0.05),pos_hint = {'center_y': 0.5, 'center_x': 0.4}, text = str_fmt.format(value)))
                label_desc = ''
                
                if(recurring):
                   label_desc = 'Always -> '                 
                else:
                   label_desc = 'Once -> '                 
                if(greater_than):
                    img_box.add_widget(ImageButton(source= 'icons/greater.png'))                    
                    label_desc = label_desc +'greater than'
                else:
                    img_box.add_widget(ImageButton(source= 'icons/less.png'))                    
                    label_desc = label_desc +'less than'
    


                switch = Switch(size_hint = (0.2,1),pos_hint = {'center_y': 0.5, 'center_x': 0.6}, active = active, id = str(alert['_id']))   
                switch.bind(active=self.active_switch) 

                left_box.add_widget(MyAlertDescription (size_hint = (0.8,0.1),pos_hint = {'center_y': 0.2, 'center_x': 0.4},text = label_desc))       
                right_box.add_widget(switch)
                
                #
                edit_box.add_widget(ImageButton(source = 'icons/edit.png', id = str(alert['_id']), on_release = self.btn_edit_alert_press))
                                                
                big_box.add_widget(img_box)
                big_box.add_widget(left_box)
                big_box.add_widget(right_box)   
                big_box.add_widget(edit_box)   

              
                grid.add_widget(big_box)    

                
                

        alert_navbar = self.load_alert_navbar(sensor)
        
        for toggle_btn in alert_navbar:
            nav_bar.add_widget(toggle_btn)
        float_layout = BoxLayout(size_hint=(1,None))
        float_layout.add_widget(MyAddAlertButton(text='Add alert', on_press = self.btn_add_alert_press,size_hint=(0.3,None),pos_hint = {'center_y': 0.5, 'center_x': 0.5}))

        grid.add_widget(float_layout)
        scroll.add_widget(grid)
        container.add_widget(scroll)
        container.add_widget(nav_bar)   
                    
    def load_alert_navbar(self,active):
        sensor_buttons = []
        i = 0
        for sensor in self.app.sensors:
            sensor_toggle = MyToggleButton(
                                    text = sensor,
                                    group= 'sensor_alert',
                                    on_release = self.toggle_btn_sensor_press
                                    )
            if(active == sensor_toggle.text):
                sensor_toggle.state = 'down'
            sensor_buttons.append(sensor_toggle)
        return sensor_buttons
    def select_help(self):
        message = "Device dashboard page. View dashboard, alerts, schedule or history."
       
        
        self.imgbtn_pressed = None
        icons = {}
        
        icons['alerts'] = {
                          'source' : 'icons/alert.png',
                          'desc'   : 'view device alerts'
                        }        
        icons['schedule'] = {
                          'source' : 'icons/schedule.png',
                          'desc'   : 'view device irrigation schedule'
                        }        
        icons['history'] = {
                          'source' : 'icons/analysis.png',
                          'desc'   : 'view device history'
                        }        
        icons['current'] = {
                          'source' : 'icons/current.png',
                          'desc'   : 'view latest sensor information'
                        }        
        icons['connected'] = {
                          'source' : 'icons/connected.png',
                          'desc'   : 'indicates device connectivity (connected, not connected, never connected)'
                        }
        icons['mode'] = {
                          'source' : 'icons/auto.png',
                          'desc'   : 'indicates irrigation mode (auto, manual)'
                        }
        icons['status'] = {
                          'source' : 'icons/irrigation_active.png',
                          'desc'   : 'indicates irrigation status (on, off)'
                        }
        icons['edit'] = {
                          'source' : 'icons/edit.png',
                          'desc'   : 'edit device'
                        }
        icons['remove'] = {
                          'source' : 'icons/remove.png',
                          'desc'   : 'remove device'
                        }
                        
        self.app.select_help(icons, message)  
    pass    
    
class AddEditAlertPage(Screen):
    def toggle_state(self, button_text):
        once_off_toggle = self.ids.once
        recurring_toggle = self.ids.recurring
        less_than_toggle = self.ids.less
        more_than_toggle = self.ids.more
        
        if(button_text == 'Once-off'):
            once_off_toggle.state = 'down'
            recurring_toggle.state = 'normal'
            
        elif(button_text == 'Every time'):
            once_off_toggle.state = 'normal'
            recurring_toggle.state = 'down' 
            
        elif(button_text =="Less than"):
            less_than_toggle.state = 'down'
            more_than_toggle.state = 'normal'
            
        else:
            less_than_toggle.state = 'normal'
            more_than_toggle.state = 'down'
    
    def on_leave(self):
        self.ids.recurring.state = 'normal'
        self.ids.once.state = 'down'
        self.ids.more.state = 'normal'
        self.ids.less.state = 'down'
                
        self.ids.value.text = ''
        self.ids.sensor.text = 'Choose sensor'
        
        self.imgbtn_pressed = None
        self.current_alert = None

    def get_sensors(self):
        if(self.app is None):
            return []
        else:
            return self.app.sensors

    def on_enter(self):
        self.app = App.get_running_app()
        self.app.previous_screen = self.app.root.current
        alert = self.app.current_alert
        self.ids.sensor.values = self.get_sensors()    
        
        main_layout = self.ids.main_layout
        
        if(alert is not None):
            if(alert['recurring']):
                self.ids.recurring.state = 'down'
                self.ids.once.state = 'normal'
            if(alert['greater_than']):
                self.ids.more.state = 'down'
                self.ids.more.state = 'normal'
            self.ids.add.text = 'Edit'
                
            self.ids.value.text = str(alert['value'])
            self.ids.sensor.text = alert['sensor']
                        
            btn_no = MyRemoveButton(text = 'Remove', on_press = self.remove_alert ,pos_hint= {'center_y': 0.115, 'center_x': 0.5})
            main_layout.add_widget(btn_no)

    def remove_alert(self, *args):
        content = BoxLayout(orientation = 'vertical')
        pop = Popup(title='Confirm removal',size_hint=(0.5,0.5))
        
        message_box = BoxLayout(orientation = 'horizontal')
        message_box.add_widget(Image(source = 'icons/remove.png', size_hint = (0.6,0.65),pos_hint= {'center_y': 0.5, 'center_x': 0.5}))
        message_box.add_widget(PopupText(text= 'Are you sure you want to remove the alert?'))
        
        respond_box = BoxLayout(orientation = 'horizontal', size_hint = (1,0.2),pos_hint= {'center_y': 0.6, 'center_x': 0.5})
        btn_yes = MyAddButton(text = 'Yes', always_release = True,size_hint = (1,1))
        btn_yes.bind(on_press=lambda x: self.confirm_remove(self.app.current_alert['_id'],pop))
        respond_box.add_widget(btn_yes)
        btn_no = MyRemoveButton(text = 'No', always_release = True,size_hint = (1,1))
        btn_no.bind(on_press = pop.dismiss)
        respond_box.add_widget(btn_no)
        
        content.add_widget(message_box)
        content.add_widget(respond_box)
        pop.content=content
        pop.open()
        

    def confirm_remove(self,_id,pop):
        self.pop = self.app.please_wait('Removing alert...')
        
        Clock.schedule_once(lambda x: self.db_handle_remove(_id), 0.5)
        pop.dismiss()
                
        
    def db_handle_remove(self, _id,*args):
 
        try:
            self.app.db.remove_alert(_id)        ### remove
            pop = self.app.success('Successfull', 'Alert successfully removed')
            pop.open() 
            self.app.root.current = 'device_dashboard_page' 
        except:
            print('error 2536')
            self.app.db_connection_error('Could not remove alert')
            
        self.pop.dismiss()
        
    def add_alert(self):
        self.pop = self.app.please_wait('Validating alert...')
        self.pop.open()
        Clock.schedule_once(self.handle_add, 0.5)     
         
    def handle_add(self,*args):
        #create validation layout
        validation_layout = self.ids.validation_layout
        validation_layout.clear_widgets()
        
        text = self.ids.add.text
        recurring = self.ids.recurring.state == 'down'
        greater_than = self.ids.more.state == 'down'
        value = self.ids.value.text
        sensor = self.ids.sensor.text
        
        is_edit = text == 'Edit'   
               
        isValid = True
        if(sensor == 'Choose sensor'):
            isValid = False
            validation_layout.add_widget(
                                          MyValidationLabel(text = 'Choose a sensor from the list',
                                                            pos_hint= {'center_y': 0.72, 'center_x': 0.5})
                                        )
        try:
            value = float(value)
            if(value<-1 or value>100):
                isValid = False
                validation_layout.add_widget(
                                          MyValidationLabel(text = 'Type in the correct sensor value',
                                                            pos_hint= {'center_y': 0.335, 'center_x': 0.5})
                                        ) 
        except:
            print('error 1882')
            isValid = False
            validation_layout.add_widget(
                                          MyValidationLabel(text = 'Type in the correct sensor value',
                                                            pos_hint= {'center_y': 0.335, 'center_x': 0.5})
                                         )
        
        if(isValid):
            
            if(is_edit):
                alert = self.app.current_alert
                alert['recurring'] = recurring
                alert['greater_than'] = greater_than
                alert['sensor'] = sensor.lower()
                alert['value'] = value
                alert['active'] = True
                
                try:
                    self.app.db.edit_alert(alert)
                    pop = self.app.success('Alert edited', 'Alert was successfully edited')
                    pop.open() 
                    self.app.root.current = 'device_dashboard_page' 
                except:
                    print('error 1905')
                    self.app.db_connection_error('Alert not updated.')

            else:
                
                try:
                    self.app.db.add_alert(self.app.current_user['email'],self.app.current_device['_id'],recurring, greater_than, sensor.lower(), value)
                    pop = self.app.success('Successfull', 'Alert was successfully added to the database. \nAlerts will be sent to user email adress: '+ self.app.current_user['email'])
                    pop.open() 
                    self.app.root.current = 'device_dashboard_page' 
                except:
                    print('error 1918')
                    self.app.db_connection_error('Alert not added.')
        self.pop.dismiss()
    pass
    
class AddScheduleItemPage(Screen):
    def on_spinner_select(self, text):
        self.ids.option_value.disabled = False
        if(text == 'duration'):
            #self.ids.option.hint_text = 'min'
            self.ids.option_lbl.text = 'min'
        else:
            #self.ids.option.hint_text = '%'
            self.ids.option_lbl.text = '%'

    def get_monthname(self, month_int):
        months = self.populate_months()
        for key in months.keys():
            if(months[key]['month']==month_int):
                return key

            
    def populate_months(self):
        month_dict = {}
        month_dict['January']   =   {'month': 1 , 'days' : 31}
        month_dict['February']  =   {'month': 2 , 'days' : 29}
        month_dict['March']     =   {'month': 3 , 'days' : 31}
        month_dict['April']     =   {'month': 4 , 'days' : 30}
        month_dict['May']       =   {'month': 5 , 'days' : 31}
        month_dict['June']      =   {'month': 6 , 'days' : 30}
        month_dict['July']      =   {'month': 7 , 'days' : 31}
        month_dict['August']    =   {'month': 8 , 'days' : 31}
        month_dict['September'] =   {'month': 9 , 'days' : 30}
        month_dict['October']   =   {'month': 10 , 'days' : 31}
        month_dict['November']  =   {'month': 11, 'days' : 30}
        month_dict['December']  =   {'month': 12, 'days' : 31}
        return month_dict

    def on_enter(self):
        self.app = App.get_running_app()
        self.app.previous_screen = self.app.root.current
        self.ids.month.values = list(self.populate_months().keys())
        
        #set date to today
        now = datetime.utcnow()
        self.ids.day.text = str(now.day)
        
        self.ids.month.text = self.get_monthname(now.month)
        self.ids.year.text = str(now.year)
         
        days = list(range(1,32))
        self.ids.day.values = [str(x) for x in days]
        self.ids.year.values = [str(now.year),str(now.year+1)]
        
    def add_schedule_item(self):
        validation_layout = self.ids.validation_layout
        validation_layout.clear_widgets()
        
        day = self.ids.day.text
        month = self.ids.month.text
        year = self.ids.year.text
        
        hour = self.ids.hour.text
        minute = self.ids.minute.text
        period = self.ids.period.text
        
        option_spinner = self.ids.option_spinner.text
        option_value = self.ids.option_value.text
        
        duration = 0
        threshold = 0
        
        is_valid = True
        
        date_is_valid = True
        month = self.populate_months()[month]['month']
        try:
            day = int(day)
            month = int(month)
            year = int(year)
        except:
            print('error 2234')
            date_is_valid = False
                
        if(not date_is_valid):
            is_valid = False
            validation_layout.add_widget(
                                          MyValidationLabel(text = '*Choose a valid date',
                                                            pos_hint= {'center_y': 0.65, 'center_x': 0.5})
        
                                      )
            
        time_is_valid = True  
        try:
            hour = int(hour)
            if(hour<0 or hour>12):
                time_is_valid = False  
        except:
            print('error 1994')
            time_is_valid = False  

        try:
            minute = int(minute)
            if(minute<0 or minute>59):
                is_valid = False
        except:
            print('error 2003')
            time_is_valid = False
        
        if(not time_is_valid):
            is_valid = False
            validation_layout.add_widget(
                                          MyValidationLabel(text = '*Select a valid time',
                                                            pos_hint= {'center_y': 0.5, 'center_x': 0.5})
                                        )
        
        
        if(option_spinner == 'choose'):
            is_valid = False
            validation_layout.add_widget(
                                          MyValidationLabel(text = '*Choose an option',
                                                            pos_hint= {'center_y': 0.35, 'center_x': 0.5})
                                        ) 
        else:
            if(option_spinner == 'duration'):
                try:
                    option_value = int(option_value)
                    if(option_value < 0):
                        is_valid = False
                        validation_layout.add_widget(
                                          MyValidationLabel(text = '*Miniumum duration of 10min required',
                                                            pos_hint= {'center_y': 0.35, 'center_x': 0.5})
                                        )
                    else:
                        duration = option_value
                except:
                    print('error 2033')
                    is_valid = False
                    validation_layout.add_widget(
                                          MyValidationLabel(text = '*Type in the correct amount of minutes',
                                                            pos_hint= {'center_y': 0.35, 'center_x': 0.5})
                                        )
            else:
                try:
                    option_value = float(option_value)
                    if(option_value < 15):
                        is_valid = False
                        validation_layout.add_widget(
                                          MyValidationLabel(text = '*Miniumum moisture of 15% required',
                                                            pos_hint= {'center_y': 0.35, 'center_x': 0.5})
                                        )
                    else:
                        threshold = option_value
                except:
                    print('error 2051')
                    is_valid = False
                    validation_layout.add_widget(
                                          MyValidationLabel(text = '*Type in the correct moisture',
                                                            pos_hint= {'center_y': 0.35, 'center_x': 0.5})
                                        )
                                        
        ts = None                                
        if(time_is_valid and date_is_valid):
            if(period == 'am' and hour == 12):
                hour = 00
            elif(period == 'pm' and hour < 12):
                hour = hour + 12
            try:
                ts = datetime(year = year, month = month , day = day,hour = hour, minute=minute)  
                if(ts < datetime.utcnow()):
                    is_valid = False
                    validation_layout.add_widget(
                                                  MyValidationLabel(text = '*Choose a future date',
                                                                    pos_hint= {'center_y': 0.65, 'center_x': 0.5})
                
                                              ) 
            except:
                is_valid = False
                validation_layout.add_widget(
                                                  MyValidationLabel(text = '*Choose a valid date',
                                                                    pos_hint= {'center_y': 0.65, 'center_x': 0.5})
                
                                              ) 
                
        if(is_valid):
            try:
                print(is_valid)
                self.app.db.add_schedule_item(ts, duration, threshold,self.app.current_user['email'],self.app.current_device['_id'])
                pop = self.app.success('Successfull', 'Schedule item successfully added to the database.')
                pop.open() 
                self.app.root.current = 'device_dashboard_page' 
            except:
                print('error 2073')
                self.app.db_connection_error('Could not add item to the schedule')
    def on_leave(self):
        self.ids.option_spinner.text = 'choose'
        self.ids.option_value.text  = ''
        self.ids.hour.text = ''
        self.ids.minute.text = ''
        self.ids.option_value.disabled = True

        

        
    pass
 
class TestPage(Screen):                                                                        
    pass


class GreenFarmApp(App):
    def db_connection_error(self, title='Error'):
        content = BoxLayout(orientation = 'horizontal')
        content.add_widget(Image(source = 'icons/error.png', size_hint = (0.7,0.65),pos_hint= {'center_y': 0.5, 'center_x': 0.5}))
        content.add_widget(PopupText(text = 'Unable to establish database connection. \nMake sure you have an active internet connection.'))
        pop = Popup(title=title, 
                content=content,
                size_hint=(0.5,0.5))
        pop.open()

    def please_wait(self, title='Establising database connection'):
        content = BoxLayout(orientation = 'horizontal')
        content.add_widget(Image(source = 'icons/info.png', size_hint = (0.7,0.65),pos_hint= {'center_y': 0.5, 'center_x': 0.5}))
        content.add_widget(PopupText(text = 'Please wait... This might take a few seconds...'))
        pop = Popup(   title=title, 
                            content=content,
                            size_hint=(0.5,0.5),
                            auto_dismiss = False)
        return pop
        
    def success(self, title='Successfull', body = 'Successfully added'):
        content = BoxLayout(orientation = 'horizontal')
        content.add_widget(Image(source = 'icons/success.png', size_hint = (0.7,0.65),pos_hint= {'center_y': 0.5, 'center_x': 0.5}))
        content.add_widget(PopupText(text = body))
        pop = Popup(   title=title, 
                            content=content,
                            size_hint=(0.5,0.5))
        return pop

    def show_error_message(self, title='Error', body = 'Logging out'):
        content = BoxLayout(orientation = 'horizontal')
        content.add_widget(Image(source = 'icons/error.png', size_hint = (0.7,0.65),pos_hint= {'center_y': 0.5, 'center_x': 0.5}))
        content.add_widget(PopupText(text = body))
        pop = Popup(title=title, 
                content=content,
                size_hint=(0.5,0.5))
        pop.open()
                  
    def show_log_out(self):
        
        content = BoxLayout(orientation = 'vertical')

        pop = Popup(title='Log out',size_hint=(0.5,0.5))
    
        message_box = BoxLayout(orientation = 'horizontal')
        message_box.add_widget(Image(source = 'icons/logout.png', size_hint = (0.6,0.65),pos_hint= {'center_y': 0.5, 'center_x': 0.5}))
        message_box.add_widget(PopupText(text= 'Are you sure you want to log out?'))
    
        respond_box = BoxLayout(orientation = 'horizontal', size_hint = (1,0.2),pos_hint= {'center_y': 0.6, 'center_x': 0.5})
        btn_yes = MyAddButton(text = 'Yes', always_release = True,size_hint = (1,1))
        btn_yes.bind(on_press=lambda x: self.confirm_logout(pop))
        respond_box.add_widget(btn_yes)
        btn_no = MyRemoveButton(text = 'No', always_release = True,size_hint = (1,1))
        btn_no.bind(on_press = pop.dismiss)
        respond_box.add_widget(btn_no)
    
        content.add_widget(message_box)
        content.add_widget(respond_box)
        pop.content=content
        pop.open()
        
    
    def confirm_logout(self, pop):
        self.current_user = None	    
        self.current_greenhouse = None	    
        self.current_device = None	    
        self.current_alert = None	 
        pop.dismiss()   
        self.root.current = 'landing_page'        
            
    def load_database(self,*args):
        try:
            self.db = GreenhouseDb()
            return True
        except:
            print('error 2143')
            self.db_connection_error('Database could not be loaded') 
  
    def select_help(self,icons,message = '',*args):
        content = BoxLayout(orientation = 'vertical')
        
        
        pop = Popup(title='Help', size_hint=(0.5,0.8))
        
        btn_ok = OkButton(text = 'OK')
        btn_ok.bind(on_press = pop.dismiss)
        
        scroll =ScrollView(
                            pos_hint= {'center_y': 0.38, 'center_x': 0.5},                
                            size_hint= (1, 0.75),
                            do_scroll_x = False)
                         
        grid = MyGridLayout(cols=2, size_hint=(1, None), height = 180)
        grid.clear_widgets()
        if( message is not ''):
            content.add_widget(PopupText(text = message, size_hint = (0.7,0.3)))
        
        num_icons = len(icons)
        if(num_icons>2):
            grid.height = num_icons*110
        
        
        for item in icons:
            grid.add_widget(Image(source = icons[item]['source'], size_hint = (0.3,None)))
            grid.add_widget(PopupText(text = icons[item]['desc'], size_hint = (0.7,1)))
            
            
        
        scroll.add_widget(grid)
        content.add_widget(scroll)
        content.add_widget(btn_ok)
        
       
        pop.content = content
                
        pop.open()  

    def get_monthname(self, month_int):
        months = self.populate_months()
        for key in months.keys():
            if(months[key]['month']==month_int):
                return key

    def populate_months(self):
        month_dict = {}
        month_dict['January']   =   {'month': 1 , 'days' : 31}
        month_dict['February']  =   {'month': 2 , 'days' : 29}
        month_dict['March']     =   {'month': 3 , 'days' : 31}
        month_dict['April']     =   {'month': 4 , 'days' : 30}
        month_dict['May']       =   {'month': 5 , 'days' : 31}
        month_dict['June']      =   {'month': 6 , 'days' : 30}
        month_dict['July']      =   {'month': 7 , 'days' : 31}
        month_dict['August']    =   {'month': 8 , 'days' : 31}
        month_dict['September'] =   {'month': 9 , 'days' : 30}
        month_dict['October']   =   {'month': 10 , 'days' : 31}
        month_dict['November']  =   {'month': 11, 'days' : 30}
        month_dict['December']  =   {'month': 12, 'days' : 31}
        return month_dict

        
    def build(self):
        self.current_user = None
        self.current_alert = None
        self.current_pass = None
        self.imgbtn_pressed = None
        self.db = None
        self.sensors = None
        alert_toggle_pressed = None
        self.previous_screen = 'landing_page'     
        self.current_greenhouse = None     
        self.current_device = None 
        self.plants = None   
        self.schedule_states = None   
        self.selected_user = None   
               
        Clock.schedule_once(self.load_database, 0.5)
         
        return kv_file
        
if __name__ == '__main__':
	kv_file = Builder.load_file("greenhouse_app.kv")
	GreenFarmApp().run()
#cheatsheat

#please_wait
# self.pop = app.please_wait()
# self.pop.open()    
# Clock.schedule_once(self.method, 0.5)

# lambda x: self.confirm_remove(arg1, arg2)
