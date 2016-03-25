from kivy.network.urlrequest import UrlRequest
import json
import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (ObjectProperty, ListProperty, StringProperty,
                             NumericProperty)
from kivy.uix.listview import ListItemButton
from kivy.factory import Factory
from kivy.storage.jsonstore import JsonStore
from kivy.uix.modalview import ModalView
from kivy.clock import Clock, mainthread
from plyer import gps
from kivy.uix.popup import Popup
from random import random


def locations_args_converter(index, data_item):
    city, country = data_item
    return {'location': (city, country), 'deselected_color': [random(), random(), random(), 1]}


def url_request_generator(url_query, **kwargs):
    url = 'http://api.openweathermap.org/data/2.5/' + url_query
    return UrlRequest(url, **kwargs)



class ErrorPopup(Popup):

    def error_occured(self, err_type, err_message):
        self.title = str(err_type)
        self.content.text = str(err_message)
        self.open()
        Clock.schedule_once(lambda d: self.dismiss(), 1.5)


class LocationButton(ListItemButton):
    location = ListProperty()


class AddLocationForm(ModalView):
    search_input = ObjectProperty()
    search_results = ObjectProperty()
    searching_popup = ObjectProperty()

    def search_location(self):
        request = url_request_generator('find?q={}&type=like'.format(self.search_input.text),
                                on_success=self.found_location,
                                on_error=ErrorPopup().error_occured)

    def found_location(self, request, data):
        if 'list' in data.keys() and data['list'] != []:
            data = json.loads(data.decode()) if not isinstance(data, dict) else data
            cities = [(d['name'], d['sys']['country']) for d in data['list']]
            self.search_results.item_strings = cities
            del self.search_results.adapter.data[:]
            self.search_results.adapter.data.extend(cities)
            self.search_results._trigger_reset_populate()
            self.searching_popup.dismiss()
        else:
            ErrorPopup().error_occured('Location Error', 'No data for \'{}\''.format(self.search_input.text))
            self.searching_popup.dismiss()


    def current_location(self):
        try:
            gps.configure(on_location=self.on_location)
            gps.start()
        except NotImplementedError:
            ErrorPopup().error_occured('GPS Error',
                                     'GPS support is not implemented on your platform')

    @mainthread
    def on_location(self, **kwargs):
        search_template = "http://api.openweathermap.org/data/2.5/" + \
                          "weather?lat={}&lon={}"
        search_url = search_template.format(kwargs['lat'], kwargs['lon'])
        data = requests.get(search_url).json()
        location = (data['sys']['country'], data['name'])
        WeatherApp.get_running_app().root.show_current_weather(location)


class CurrentWeather(BoxLayout):
    location = ListProperty(['New York', 'US'])
    conditions = StringProperty()
    conditions_image = StringProperty()
    temp = NumericProperty()
    temp_min = NumericProperty()
    temp_max = NumericProperty()

    def update_weather(self):
        config = WeatherApp.get_running_app().config
        temp_type = config.getdefault("General", "temp_type", "metric").lower()
        url_request_generator('weather?q={},{}&units={}'.format(self.location[0], self.location[1], temp_type),
                              on_success=self.weather_retrieved,
                              on_error=ErrorPopup().error_occured)

        
    def weather_retrieved(self, request, data):
        data = json.loads(data.decode()) if not isinstance(data, dict) else data
        self.conditions = data['weather'][0]['description']
        self.conditions_image = "http://openweathermap.org/img/w/{}.png".format(
            data['weather'][0]['icon'])
        self.temp = data['main']['temp']
        self.temp_min = data['main']['temp_min']
        self.temp_max = data['main']['temp_max']

class Forecast(BoxLayout):
    location = ListProperty(['New York', 'US'])
    forecast_container = ObjectProperty()

    def update_weather(self):
        config = WeatherApp.get_running_app().config
        temp_type = config.getdefault("General", "temp_type", "metric").lower()
        url_request_generator('forecast/daily?q={},{}&units={}&cnt=3'.format(self.location[0],
                                                                             self.location[1],
                                                                             temp_type),
                              on_success=self.weather_retrieved,
                              on_error=ErrorPopup().error_occured)
            
    def weather_retrieved(self, request, data):
        data = json.loads(data.decode()) if not isinstance(data, dict) else data
        self.forecast_container.clear_widgets()
        for day in data['list']:
            label = Factory.ForecastLabel()
            label.date = datetime.datetime.fromtimestamp(day['dt']).strftime(
                "%a %b %d")

            label.conditions = day['weather'][0]['description']
            label.conditions_image = "http://openweathermap.org/img/w/{}.png".format(
                day['weather'][0]['icon'])
            label.temp_min = day['temp']['min']
            label.temp_max = day['temp']['max']
            self.forecast_container.add_widget(label)

class WeatherRoot(BoxLayout):
    current_weather = ObjectProperty()
    locations = ObjectProperty()
    forecast = ObjectProperty()
    carousel = ObjectProperty()
    add_location_form = ObjectProperty()

    def __init__(self, **kwargs):
        super(WeatherRoot, self).__init__(**kwargs)
        self.store = JsonStore("weather_store.json")
        if self.store.exists('locations'):
            locations = self.store.get('locations')
            self.locations.locations_list.adapter.data.extend(locations['locations'])
            current_location = locations["current_location"]
            self.show_current_weather(current_location)
        else:
            Clock.schedule_once(lambda dt: self.show_add_location_form())



    def show_current_weather(self, location):
        if location not in self.locations.locations_list.adapter.data:
            self.locations.locations_list.adapter.data.append(location)
            self.locations.locations_list._trigger_reset_populate()
            self.store.put("locations",
                locations=list(self.locations.locations_list.adapter.data),
                current_location=location)

        self.current_weather.location = location
        self.forecast.location = location
        self.current_weather.update_weather()
        self.forecast.update_weather()

        self.carousel.load_slide(self.current_weather)
        if self.add_location_form is not None:
            self.add_location_form.dismiss()


    def show_add_location_form(self):
        self.add_location_form = AddLocationForm()
        self.add_location_form.open()


class WeatherApp(App):
    def build_config(self, config):
        config.setdefaults('General', {'temp_type': "Metric"})

    def build_settings(self, settings):
        settings.add_json_panel("Weather Settings", self.config, data="""
            [
                {"type": "options",
                    "title": "Temperature System",
                    "section": "General",
                    "key": "temp_type",
                    "options": ["Metric", "Imperial"]
                }
            ]"""
            )

    def on_config_change(self, config, section, key, value):
        if config is self.config and key == "temp_type":
            try:
                self.root.current_weather.update_weather()
                self.root.forecast.update_weather()
            except AttributeError:
                pass

    def on_pause(self):
        return True

if __name__ == '__main__':
	WeatherApp().run()
