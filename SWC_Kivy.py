from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.slider import Slider
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window

import soco_wrapper as sw

from os import uname

if uname()[4].startswith("arm"):
    raspPi = 1
    import RPi.GPIO as GPIO
else:
    raspPi = 0

print ("RASPPI DETECTION RESULT: " + str(raspPi))

# Declare both screens
class SpeakerScreen(Screen):
    
    #def on_touch_down(self, touch):
     #   print(touch.pos)
        #return super(SpeakerScreen, self).on_touch_down(touch)
    
    def __init__(self, **kwargs):
        super(SpeakerScreen, self).__init__(**kwargs)
        layout = GridLayout(cols=3)
        #Discover all Speakers
        sw.discoverAll()
        #Go trough all speakers and create controls
        for index,speaker in enumerate(sw.getSpeakers()):
            #Add speaker group toggle button
            tbutton = ToggleButton(text=speaker.player_name,id=str(sw.getSpeakerID(speaker)), size_hint_x=0.2, font_size=40)
            if sw.getSpeakerGroupStatus(speaker) == 1:
                tbutton.state='down'
            tbutton.bind(on_press=self.SpeakerGroupToggle)
            layout.add_widget(tbutton)
            #Add Mute button
            tbutton = ToggleButton(text='M', id=str(sw.getSpeakerID(speaker)),size_hint_x=0.1, font_size=40)
            if sw.getSpeakerMute(speaker) == 1:
                tbutton.state='down'
            tbutton.bind(on_press=self.SpeakerMuteToggle)
            layout.add_widget(tbutton)
            #Add Volume Slider
            tbutton = Slider(min=0, max=100, id=str(sw.getSpeakerID(speaker)), value=sw.getSpeakerVolume(speaker), size_hint_x=0.7)
            tbutton.bind(value=self.SpeakerVolume)
            layout.add_widget(tbutton)
            
        self.add_widget(layout)

    def SpeakerGroupToggle(self, event):
        sw.setSpeakerGroupStatus(sw.getSpeakerObject(int(event.id)))
    
    def SpeakerMuteToggle(self, event):
        sw.setSpeakerMute(sw.getSpeakerObject(int(event.id)))
    
    def SpeakerVolume(self, event,second):
        sw.setSpeakerVolume(sw.getSpeakerObject(int(event.id)),int(event.value))
    
    
class FavoriteScreen(Screen):
    def __init__(self, **kwargs):
        super(FavoriteScreen, self).__init__(**kwargs)
        layout = GridLayout(cols=3, size_hint_y=0.2)
        stations = sw.getRadioFavorites()
        for station in stations:
            button = Button(text=station['title'][:10],id=str(sw.getRadioFavoriteID(station)), size_hint_x=0.2, font_size=40)
            button.bind(on_press=self.SetRadioStation)
            layout.add_widget(button)
        layout2 = GridLayout(cols=3, size_hint_y=0.2)
        button = Button(text='<<',id='back', size_hint_x=0.2, font_size=40)
        button.bind(on_press=self.PlayPauseSkip)
        layout2.add_widget(button)
        button = Button(text='>',id='playPause', size_hint_x=0.2, font_size=40)
        button.bind(on_press=self.PlayPauseSkip)
        layout2.add_widget(button)
        button = Button(text='>>',id='forward', size_hint_x=0.2, font_size=40)
        button.bind(on_press=self.PlayPauseSkip)
        layout2.add_widget(button)
        self.add_widget(layout)
        self.add_widget(layout2)

    def SetRadioStation(self, event):
        station = sw.getRadioFavoriteObject(int(event.id))
        sw.playRadio(station)   

    def PlayPauseSkip(self, event):
        pass      
        
class SearchScreen(Screen):
    pass



class SWC(App):
    sm = ScreenManager()
    def build(self):
        # Create the screen manager
        #sm = ScreenManager()
        self.sm.add_widget(SpeakerScreen(name='SpeakerScreen'))
        self.sm.add_widget(FavoriteScreen(name='FavoriteScreen'))
        self.sm.add_widget(SearchScreen(name='SearchScreen'))
        if raspPi == 0:
            #if not on a pi use keyboard
            self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
        #if a pi setup GPIO
        if raspPi == 1:
            GPIO.setmode(GPIO.BCM)
            #input pins for pagescroll
            GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(23, GPIO.FALLING, callback=self.ButtonPress, bouncetime=300)
            GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(22, GPIO.FALLING, callback=self.ButtonPress, bouncetime=300)
            GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(27, GPIO.FALLING, callback=self.ButtonPress, bouncetime=300)
            GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(17, GPIO.FALLING, callback=self.ButtonPress, bouncetime=300)
            #output for backlight
            GPIO.setup(18, GPIO.OUT)
            GPIO.output(18, True)
        return self.sm
    
    def on_stop(self):
        if raspPi == 1:
            GPIO.cleanup()
    

        
    if raspPi == 1:
        def ButtonPress(self, channel):
            if channel == 23:
                self.sm.current = 'SpeakerScreen'
            elif channel == 22:
                self.sm.current = 'FavoriteScreen'
            elif channel == 27:
                self.sm.current = 'SearchScreen'
            #set backlight off/on
            elif channel == 17:
                GPIO.output(18, not GPIO.input(18))
            
        
    
    if raspPi == 0:
        def _keyboard_closed(self):
            print('My keyboard have been closed!')
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)
            self._keyboard = None
            
        def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
            if text == '1':
                self.sm.current = 'SpeakerScreen'
            elif text == '2':
                self.sm.current = 'FavoriteScreen'
            elif text == '3':
                self.sm.current = 'SearchScreen'

    

if __name__ == '__main__':
    #Window.size = (320,240)
    #Window.fullscreen = True
    try:
        SWC().run()
    except KeyboardInterrupt:
        print "Cleaning UP IO"
        GPIO.cleanup()