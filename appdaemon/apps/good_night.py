import appdaemon.plugins.hass.hassapi as hass

class GoodNight(hass.Hass):

  def initialize(self):
    self.listen_state(self.good_night, "script.good_night")

  def good_night(self, entity, attribute, old, new, kwargs):
    # turn off lights
    self.turn_off("group.all_lights")
    # locks doors
    self.call_service("lock/lock", entity_id="group.all_locks")
    # turn off harmony
    self.call_service("remote/turn_off", entity_id="remote.harmony_hub")
    # set thermostat to sleep
    self.call_service("climate/set_hold_mode", entity_id="climate.living_room", hold_mode="sleep")