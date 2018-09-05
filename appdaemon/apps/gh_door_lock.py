import appdaemon.plugins.hass.hassapi as hass

class GhDoorLock(hass.Hass):

  def initialize(self):
    self.listen_state(self.lock_door, "script.kitchen_door_lock")

  def lock_door(self, entity, attribute, old, new, kwargs):
    self.call_service("lock/lock", entity_id="lock.kitchen_door_lock")