import yaml


class SettingsManager:
    """
    A class for managing application settings stored in a YAML file.

    This class provides methods to load, save, retrieve, and update settings from a YAML file.
    The settings are stored as a dictionary and can be accessed using dot notation (e.g., "api.key").

    Attributes:
        settings_file (str): The path to the YAML file containing the settings.
        settings (dict): The loaded settings dictionary.

    Methods:
        load_settings(): Loads the settings from the YAML file and returns them as a dictionary.
        save_settings(): Saves the current settings dictionary to the YAML file.
        get(key: str): Retrieves the value associated with the specified key using dot notation.
        set(key: str, value: Any): Sets the value for the specified key using dot notation and saves the settings.
    """

    def __init__(self, settings_file: str) -> None:
        self.settings_file = settings_file
        self.settings = self.load_settings()

    def load_settings(self):
        with open(self.settings_file, "r") as file:
            settings = yaml.safe_load(file)
        return settings

    def save_settings(self):
        with open(self.settings_file, "w") as file:
            yaml.dump(self.settings, file)

    def get(self, key: str):
        keys = key.split(".")
        value = self.settings
        for k in keys:
            value = value.get(k)
            if value is None:
                break
        return value

    def set(self, key, value):
        keys = key.split(".")
        settings = self.settings
        for k in keys[:-1]:
            if k not in settings:
                settings[k] = {}
            settings = settings[k]
        settings[keys[-1]] = value
        self.save_settings()
