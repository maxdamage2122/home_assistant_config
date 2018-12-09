import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime, timedelta
import pytz

class Location(hass.Hass):

  def initialize(self):
    self.speakers = self.get_app("google_speakers")
    
    # someone arrived home
    self.listen_state(self.someone_arrived_home, "group.justin", new="home")
    self.listen_state(self.someone_arrived_home, "group.alex", new="home")
    
    # someone left home
    self.listen_state(self.someone_left_home, "group.justin", old="home")
    self.listen_state(self.someone_left_home, "group.alex", old="home")
    
    # alex left quinn
    self.listen_state(self.alex_left_quinn, "device_tracker.google_maps_103220762903139682628", old="Quinn")
    
    # notification actions
    self.listen_event(self.set_ecobee_away, "html5_notification.clicked", action = "set_ecobee_away")
    self.listen_event(self.set_ecobee_home, "html5_notification.clicked", action = "set_ecobee_home")
  
  def set_ecobee_away(self, event_name, data, kwargs):
    self.call_service("climate/set_away_mode", entity_id="climate.living_room", away_mode="true")
  
  def set_ecobee_home(self, event_name, data, kwargs):
    self.call_service("climate/ecobee_resume_program", entity_id="climate.living_room")
  
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
      domain, name = self.split_entity(entity)
      self.speakers.announce(name+" is home")
      # set thermostat to home
      hold_mode = self.get_state("climate.living_room", attribute="hold_mode")
      if hold_mode != "temp":
        self.call_service("climate/ecobee_resume_program", entity_id="climate.living_room")
      else:
        extra_data = {
          "icon": "https://lh3.googleusercontent.com/JUpoMaUbGEnGJ2x0xiR8cp3GNK76wuh2dcLGZoWXpxG6sWLubetqJTbKExgBSPj39WWz=s180-rw",
          "actions": [{
              "action": "set_ecobee_home",
              "title": "Set to home"}]
        }
        self.call_service("notify/chrome", title="Ecobee", message="Thermostat is holding temperature.", data=extra_data)
  
  def turn_off_callback(self, kwargs):
    self.turn_off(kwargs.get("entity_id"))

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
      hold_mode = self.get_state("climate.living_room", attribute="hold_mode")
      if hold_mode != "temp":
        self.call_service("climate/set_away_mode", entity_id="climate.living_room", away_mode="true")
      else:
        extra_data = {
          "icon": "https://lh3.googleusercontent.com/JUpoMaUbGEnGJ2x0xiR8cp3GNK76wuh2dcLGZoWXpxG6sWLubetqJTbKExgBSPj39WWz=s180-rw",
          "actions": [{
              "action": "set_ecobee_away",
              "title": "Set to away"}]
        }
        self.call_service("notify/chrome", title="Ecobee", message="Thermostat is holding temperature.", data=extra_data)
