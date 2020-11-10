import discord
import asyncio
import random
from discord.ext import commands
from pyowm.owm import OWM
import string
from datetime import datetime
import os

owm = OWM(os.getenv('OWM_KEY'))

class weather(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def weather(self, ctx, *, location):
        print(f"{ctx.guild.name} - #{ctx.channel.name} - {ctx.author.name} - {ctx.message.content}")
        ' '.join(location)
        mgr = owm.weather_manager()
        observe = mgr.weather_at_place(location)
        loc = observe.location.name
        weather = observe.weather
        if weather.status == "Thunderstorm":
            emoji = ":thunder_cloud_rain:"
        elif weather.status == "Rain" or weather.status == "Drizzle":
            emoji = ":cloud_rain:"
        elif weather.status == "Snow":
            emoji = ":snowflake:"
        elif weather.status == "Clear":
            emoji = ":sunny:"
        elif weather.status == "Tornado":
            emoji = ":cloud_tornado:"
        elif weather.status == "Clouds":
            if weather.detailed_status == "few clouds":
                emoji = ":white_sun_small_cloud:"
            elif weather.detailed_status == "scattered clouds":
                emoji = ":partly_sunny:"
            elif weather.detailed_status == "broken clouds":
                emoji = ":white_sun_cloud:"
            else:
                emoji = ":cloud:"
        else:
            emoji = ":fog:"
        embed = discord.Embed(
            title = f"Weather in {string.capwords(loc)}",
            color = ctx.author.color,
            description = f"{emoji} {weather.detailed_status.capitalize()}"
        )
        temp_dict = weather.temperature(unit = 'fahrenheit')
        embed.add_field(name = "Temperature", value = f"""
            :thermometer: **{round(temp_dict['temp'], 1)} °F**
            :slight_smile: Feels like **{round(temp_dict['feels_like'], 1)} °F**
            :small_red_triangle: **{round(temp_dict['temp_max'], 1)} °F**
            :small_red_triangle_down: **{round(temp_dict['temp_min'], 1)} °F**
        """)
        wind_dict = weather.wind(unit = "miles_hour")
        embed.add_field(name = "Other", value = f"""
            :droplet: Humidity: **{weather.humidity}%**
            :cloud_tornado: Air Pressure: **{weather.pressure['press']} mbar**
            :dash: Wind: **{round(wind_dict['speed'], 1)} mph**
            :compass: Wind Bearing: **{wind_dict['deg']}°**
        """)
        embed.add_field(name = "Sunrise and Sunset", value = f"""
            :sunrise: Sunrise: **{datetime.utcfromtimestamp(weather.sunrise_time(timeformat = 'unix') + weather.utc_offset).strftime('%#I:%M %p')}**
            :city_sunset: Sunset: **{datetime.utcfromtimestamp(weather.sunset_time(timeformat = 'unix') + weather.utc_offset).strftime('%#I:%M %p')}**
        """, inline = False)
        await ctx.send(embed = embed)

    @weather.error
    async def weather_error(self, ctx, error):
        print(error)
        if type(error) == discord.ext.commands.errors.CommandInvokeError:
            await ctx.send("City not found.")
        else:
            await ctx.send("Please follow format: `y.weather {city}`")
        
def setup(client):
    client.add_cog(weather(client))