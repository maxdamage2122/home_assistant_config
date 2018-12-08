import appdaemon.plugins.hass.hassapi as hass
import time

class GoogleSpeakers(hass.Hass):

  groups = {'all_speakers': {'kitchen_speaker','living_room_speaker','bathroom_speaker','upstairs_hall_speaker'},
        'downstairs_speakers': {'kitchen_speaker','living_room_speaker','bathroom_speaker'},
        'upstairs_speakers': {'upstairs_hall_speaker'}}
  
  def initialize(self):
    pass

  def isPlaying(self, entity):
    if self.get_state("media_player."+entity) == 'playing':
      return True
    else:
      for group in self.groups:
        if (entity in self.groups[group]) and (self.get_state("media_player."+group) == 'playing'):
          return True
    return False
  
  def whosPlaying(self):
    playing = []
    for group in self.groups:
      if self.get_state("media_player."+group) == 'playing':
        playing.append(group)
    if "all_speakers" not in playing:
      for speaker in self.groups['all_speakers']:
        if self.get_state("media_player."+speaker) == 'playing':
          playing.append(speaker)
    if len(playing) != 0:
      return playing

  def announce(self, message):
    if self.whosPlaying() == None:
      self.call_service("media_player/turn_on", entity_id = "media_player.all_speakers")
      time.sleep(1)
      self.call_service("tts/google_say", entity_id = "media_player.all_speakers", message = message)
    else:
      self.notify(message, name="broadcast")
    pass

test = "test"