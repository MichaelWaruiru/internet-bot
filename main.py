from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import psutil
from plyer import notification

class DataUsageMonitor(BoxLayout):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.data_limit_bytes = None
    self.initial_data = None
    self.usage_thresholds = [0.5, 0.75, 0.95] # 50%, 75% and 95%
    self.alerted = set()


  def set_data_limit(self, limit):
        """Set the data limit in bytes."""
        self.data_limit_bytes = float(limit) * (1024 ** 3)  # Convert GB to bytes
        self.initial_data = self.get_data_usage()
        self.ids.status.text = "Monitoring started..."
        Clock.schedule_interval(self.check_usage, 10)  # Check every 10 seconds

  def get_data_usage(self):
      """Retrieve the current total data sent and received."""
      stats = psutil.net_io_counters()
      return stats.bytes_sent + stats.bytes_recv

  def check_usage(self, dt):
      """Check the current usage and notify at thresholds."""
      if self.data_limit_bytes is None or self.initial_data is None:
          return

      current_data = self.get_data_usage() - self.initial_data
      usage_percentage = current_data / self.data_limit_bytes

      for threshold in self.usage_thresholds:
          if usage_percentage >= threshold and threshold not in self.alerted:
              self.alert_user(threshold)
              self.alerted.add(threshold)

  def alert_user(self, threshold):
      """Notify the user when a threshold is crossed."""
      percent = int(threshold * 100)
      message = f"You've used {percent}% of your data limit!"
      self.ids.status.text = message

      # Send a notification
      notification.notify(
          title="Data Usage Alert",
          message=message,
          app_name="Data Monitor",
      )

class DataMonitorApp(App):
    def build(self):
        return DataUsageMonitor()

if __name__ == "__main__":
    DataMonitorApp().run()