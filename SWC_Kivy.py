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

# Create both screens. Please note the root.manager.current: this is how
# you can control the ScreenManager from kv. Each screen has by default a
# property manager that gives you the instance of the ScreenManager used.


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
            
        #TODO Add temp buttons to change screens
        tbutton = Button(text='Favorite',size_hint_x=0.2)
        tbutton.bind(on_press=self.SwitchToFavorite)
        layout.add_widget(tbutton)
        self.add_widget(layout)
        #return self

    def SpeakerGroupToggle(self, event):
        sw.setSpeakerGroupStatus(sw.getSpeakerObject(int(event.id)))
    
    def SpeakerMuteToggle(self, event):
        sw.setSpeakerMute(sw.getSpeakerObject(int(event.id)))
    
    def SpeakerVolume(self, event,second):
        sw.setSpeakerVolume(sw.getSpeakerObject(int(event.id)),int(event.value))

    def SwitchToFavorite(self, event):
        print self.manager.current_screen.x
        self.manager.current = 'FavoriteScreen'
    
    
    
class FavoriteScreen(Screen):
    def __init__(self, **kwargs):
        super(FavoriteScreen, self).__init__(**kwargs)
        layout = GridLayout(cols=3, row_default_height=40)
        layout.add_widget(Label(text='favorite'))
        #TODO Add temp buttons to change screens
        tbutton = Button(text='Speaker')
        tbutton.bind(on_press=self.SwitchToSpeaker)
        layout.add_widget(tbutton)
        self.add_widget(layout)
        
    def SwitchToSpeaker(self, event):
        self.manager.current = 'SpeakerScreen'
    

class SearchScreen(Screen):
    pass



class SWC(App):

    def build(self):
        # Create the screen manager
        sm = ScreenManager()
        sm.add_widget(SpeakerScreen(name='SpeakerScreen'))
        sm.add_widget(FavoriteScreen(name='FavoriteScreen'))
        sm.add_widget(SearchScreen(name='SearchScreen'))
        return sm

if __name__ == '__main__':
    #Window.size = (320,240)
    #Window.fullscreen = True
    SWC().run()