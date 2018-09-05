import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime, timedelta
import pytz

class Location(hass.Hass):

  def initialize(self):
    # someone arrived home
    self.listen_state(self.someone_arrived_home, "group.justin", new="home")
    self.listen_state(self.someone_arrived_home, "group.alex", new="home")
    
    # someone left home
    self.listen_state(self.someone_left_home, "group.justin", old="home")
    self.listen_state(self.someone_left_home, "group.alex", old="home")
    
    # alex left quinn
    self.listen_state(self.alex_left_quinn, "device_tracker.google_maps_103220762903139682628", old="Quinn")

  def alex_left_quinn(self, entity, attribute, old, new, kwargs):
    # notify justin
    if new != "Quinn":
      self.notify("Alex left Quinn.", name = "chrome")

  def someone_arrived_home(self, entity, attribute, old, new, kwargs):
    # if someone didn't arrive in last 5 minutes
    if entity == "group.justin":
      last_changed = self.get_state("group.alex", attribute="last_changed")
    elif entity == "group.alex":
      last_changed = self.get_state("group.justin", attribute="last_changed")
    last_changed = self.convert_utc(last_changed)
    now = datetime.now(pytz.utc)
    if last_changed < (now - timedelta(minutes=5)):
      # turn on breezeway lamp for 10 minutes if after sunset and not already on
      breezeway_lamp_state = self.get_state("light.breezeway_lamp")
      if self.sun_down() and (breezeway_lamp_state == "off"):
        self.turn_on("light.breezeway_lamp")
        self.run_in(self.turn_off_callback, 10*60, entity_id="light.breezeway_lamp")
      # unlock door
      self.call_service("lock/unlock", entity_id="lock.kitchen_door_lock")
      # set speaker volume and announce who arrived
      self.volume = self.get_state("media_player.living_room_speaker", attribute="volume_level")
      if self.volume != 0.5:
        self.call_service("media_player/volume_set", entity_id="media_player.living_room_speaker", volume_level="0.5")
        self.speaker_handle = self.listen_state(self.speaker_done_playing, "media_player.living_room_speaker", old="playing", new="idle")
      domain, name = self.split_entity(entity)
      self.call_service("tts/google_say", entity_id="media_player.living_room_speaker", message=name+" is home")
      # set thermostat to home
      self.call_service("climate/set_hold_mode", entity_id="climate.living_room", hold_mode="home")

  def speaker_done_playing(self, entity, attribute, old, new, kwargs):
    # restore speaker volume
    self.call_service("media_player/volume_set", entity_id="media_player.living_room_speaker", volume_level=str(self.volume))
    # cancel speaker listen state
    self.cancel_listen_state(self.speaker_handle)
    
  def someone_left_home(self, entity, attribute, old, new, kwargs):
    if self.noone_home():
      # lock doors
      self.call_service("lock/lock", entity_id="group.all_locks")
      # turn off lights
      self.turn_off("group.all_lights")
      # turn off harmony
      self.call_service("remote/turn_off", entity_id="remote.harmony_hub")
      # set thermostat to away
      self.call_service("climate/set_hold_mode", entity_id="climate.living_room", hold_mode="away")
