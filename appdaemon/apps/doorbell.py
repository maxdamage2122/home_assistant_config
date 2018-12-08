import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime, timedelta
import pytz

class Doorbell(hass.Hass):

  def initialize(self):
    self.speakers = self.get_app("google_speakers")
    self.listen_state(self.doorbell_pressed, "sensor.doorbell", new="TOGGLE")

  def doorbell_pressed(self, entity, attribute, old, new, kwargs):
    self.speakers.announce("someone's at the kitchen door")
    now = datetime.now(pytz.utc)
    time = now.astimezone(pytz.timezone('US/Eastern'))
    self.notify("@ "+time.strftime('%x %I:%M%p'), title="Someone's at the kitchen door", name="chrome")