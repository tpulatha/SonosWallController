import soco

my_globals = { 'Speakers' : [], 'MainGroup': [] , 'MainGroupUID' : [] , 'RadioFavs' : [], 'somethingChange' : False}

meta_template = """<DIDL-Lite xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/"
    xmlns:r="urn:schemas-rinconnetworks-com:metadata-1-0/"
    xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/">
    <item id="R:0/0/0" parentID="R:0/0" restricted="true">
        <dc:title>{title}</dc:title>
        <upnp:class>object.item.audioItem.audioBroadcast</upnp:class>
        <desc id="cdudn" nameSpace="urn:schemas-rinconnetworks-com:metadata-1-0/">
            {service}
        </desc>
    </item>
</DIDL-Lite>' """

tunein_service = 'SA_RINCON65031_'

def discoverAll():
    if len(my_globals['Speakers']) == 0:
        my_globals['Speakers'] = list(soco.discover())
    elif my_globals['somethingChange'] == True:
        my_globals['somethingChange'] = False
        newList = list(soco.discover())
        print "Rediscover"
        oldList = my_globals['Speakers']
        newNewList = []
        for oldItem in oldList:
            for newItem in newList:
                if newItem == oldItem:
                    newNewList.append(newItem)
        my_globals['Speakers'] = newNewList
    else:
        pass

def getSpeakers():
    return my_globals['Speakers']

def getSpeakerID(SoCo):
    speakers = my_globals['Speakers']
    return speakers.index(SoCo)

def getSpeakerObject(ID):
    speakers = my_globals['Speakers']
    return speakers[ID]

def getGroups():
    discoverAll()
    speakers = my_globals['Speakers']
    return speakers[0].all_groups

def getMainGroup():
    #If already checked, find the right group and return
    if type(my_globals['MainGroupUID']) == str:
        #print "locking into biggest group"
        mainGroupUID = my_globals['MainGroupUID']
        discoverAll()
        speakers = list(my_globals['Speakers'])
        groups = getGroups()
        for group in groups:
            #print 'Searching for in this Group:' + str(group.members)
            if group.uid == mainGroupUID:
                #print 'MainGroup Members: ' + str(group.members)
                return group
            
    #If not already checked, find out
    #print "findind biggest group"
    speakers = list(my_globals['Speakers'])
    groups = getGroups()
    highVal = 0
    for group in groups:
        if len(group.members) > highVal:
            mainGroup = group
            highVal = len(group.members)
    my_globals['MainGroupUID'] = mainGroup.uid
    #print 'MainGroup Members: ' + str(mainGroup.members)
    return mainGroup
        
def getRadioFavorites():
    if len(my_globals['RadioFavs']) == 0:
        group = getMainGroup()
        my_globals['RadioFavs'] = list(group.coordinator.get_favorite_radio_stations( 0, 6)['favorites'])
    
    return my_globals['RadioFavs']

def getRadioFavoriteID(station):
    stations = my_globals['RadioFavs']
    return stations.index(station)

def getRadioFavoriteObject(ID):
    stations = my_globals['RadioFavs']
    return stations[ID]

def play_uri( uri, metadata):
    group = getMainGroup()
    #print '___URI___'
    #print uri
    #print '___METADATA___'
    #print metadata
    #print '___END___'
    group.coordinator.play_uri( uri, metadata)
    
def setSpeakerMute(SoCo, mute=None):
    if type(SoCo) is int:
        speaker = getSpeakerObject(SoCo)
    else:
        speaker = SoCo
    my_globals['somethingChange'] = True
    if mute is int:
        if speaker.mute == mute:
            return False
        else:
            speaker.mute = mute
    elif mute is None:
        if speaker.mute == 1:
            speaker.mute = 0
        else:
            speaker.mute = 1
        return True
        
def getSpeakerMute(SoCo):
    if type(SoCo) is int:
        speaker = getSpeakerObject(SoCo)
    else:
        speaker = SoCo
    return speaker.mute

def setSpeakerVolume(SoCo, newVol):
    if type(SoCo) is int:
        speaker = getSpeakerObject(SoCo)
    else:
        speaker = SoCo
    my_globals['somethingChange'] = True
    if newVol != speaker.volume:
        speaker.volume = newVol
        return True
    return False
    
def getSpeakerVolume(SoCo):
    if type(SoCo) is int:
        speaker = getSpeakerObject(SoCo)
    else:
        speaker = SoCo
    return speaker.volume

def setSpeakerGroupStatus(SoCo, status = None):
    if type(SoCo) is int:
        speaker = getSpeakerObject(SoCo)
    else:
        speaker = SoCo
    mainGroup = getMainGroup()
    my_globals['somethingChange'] = True
    if status is int:
        if status == 0:
            speaker.unjoin()
        elif status == 1:          
            speaker.join(mainGroup.coordinator)
    elif status is None:
        if getSpeakerGroupStatus(speaker) == True:
            speaker.unjoin()
        else:
            speaker.join(mainGroup.coordinator)
        

def getSpeakerGroupStatus(SoCo):
    if type(SoCo) is int:
        speaker = getSpeakerObject(SoCo)
    else:
        speaker = SoCo
    mainGroup = getMainGroup()
    if speaker in mainGroup.members:
        return True
    else:
        return False
    
def playRadio(RadioIn):
    uri = RadioIn['uri']
    # TODO seems at least & needs to be escaped - should move this to play_uri and maybe escape other chars.
    uri = uri.replace('&', '&amp;')
    metadata = meta_template.format(title=RadioIn['title'], service=tunein_service)
    play_uri( uri, metadata)   

def playPause():
    group = getMainGroup()
    my_globals['somethingChange'] = True
    if group.coordinator.get_current_transport_info()['current_transport_state'] == 'PLAYING':
        group.coordinator.stop()
        return 0
    else:
        group.coordinator.play()
        return 1
    

def getPlayPauseState():
    group = getMainGroup()
    if group.coordinator.get_current_transport_info()['current_transport_state'] == 'PLAYING':
        return 1
    else:
        return 0

def skipBack():
    my_globals['somethingChange'] = True
    group = getMainGroup()
    if int(group.coordinator.get_current_track_info()['position'].split(':')[2]) > 5:
        group.coordinator.seek('00:00:00')
    else:
        try:
            group.coordinator.previous()
        except:
            print "error"

def skipForward():
    group = getMainGroup()
    group.coordinator.next()