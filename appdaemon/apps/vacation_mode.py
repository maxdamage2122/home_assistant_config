import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime, timedelta
import pytz

class VacationMode(hass.Hass):

  def initialize(self):
    self.entity_ids = [
        "light.living_room_ceiling_light",
        "light.breezeway_lamp",
        "light.upstairs_hall_light",
        "cover.garage_door",
        "light.kitchen_light",
        "lock.kitchen_door_lock",
        "binary_sensor.living_room_occupancy",
        "binary_sensor.upstairs_occupancy"]
    self.handles = []
    
    if self.get_state("input_boolean.vacation_mode") == "on":
        self.enable(None,None,None,None,None)
    
    self.listen_state(self.enable, "input_boolean.vacation_mode", new="on")
    self.listen_state(self.disable, "input_boolean.vacation_mode", new="off")

  def enable(self, entity, attribute, old, new, kwargs):
    for entity_id in self.entity_ids:
      handle = self.listen_state(self.send_notification, entity_id)
      self.handles.append(handle)

  def send_notification(self, entity, attribute, old, new, kwargs):
    now = datetime.now(pytz.utc)
    time = now.astimezone(pytz.timezone('US/Eastern'))
    self.notify(new+" @ "+time.strftime('%x %I:%M%p'), title=entity, name="chrome")

  def disable(self, entity, attribute, old, new, kwargs):
    for handle in self.handles:
      self.cancel_listen_state(handle)
    self.handles.clear()