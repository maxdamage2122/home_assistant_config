import appdaemon.plugins.hass.hassapi as hass

class HaStartup(hass.Hass):

  def initialize(self):
    self.listen_state(self.ha_started, "script.ha_start")

  def ha_started(self, entity, attribute, old, new, kwargs):
    self.call_service("google_assistant/request_sync")