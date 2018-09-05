import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime, timedelta
import pytz

class Doorbell(hass.Hass):

  def initialize(self):
    self.last_changed = self.convert_utc(self.get_state("sensor.doorbell", attribute="last_changed"))
    self.listen_state(self.doorbell_pressed, "sensor.doorbell", new="ON")

  def doorbell_pressed(self, entity, attribute, old, new, kwargs):
    now = datetime.now(pytz.utc)
    if self.last_changed < (now - timedelta(seconds=10)):
      time = now.astimezone(pytz.timezone('US/Eastern'))
      self.notify("@ "+time.strftime('%x %I:%M%p'), title="Someone's at the kitchen door", name="chrome")
    self.last_changed = now