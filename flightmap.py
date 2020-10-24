import json

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import pandas as pd

data_crs = ccrs.PlateCarree()


class FlightMap:
    def __init__(self, data_file, projection = "ortho", colordata = None):
        with open(data_file, "r") as infile:
            data_dict = json.load(infile)

        for key, item in data_dict.items():
            data_dict[key] = np.array(item)

        self._data_dict = data_dict

        self._latitude = data_dict["PLANE_LATITUDE"]
        self._longitude = data_dict["PLANE_LONGITUDE"]

        self._mid_long = (min(self._longitude) + max(self._longitude)) / 2
        self._mid_lat = (min(self._latitude) + max(self._latitude)) / 2

        if projection == "ortho":
            self.projection = ccrs.Orthographic(central_longitude = self._mid_long,
                                                central_latitude = self._mid_lat)

        if colordata is not None:
            self.cdata = data_dict[colordata]
            self._colordata = colordata
        else:
            self.cdata = "black"

        self.airport_data = pd.read_csv("airport_data/airports.dat")

    def make_plot(self, figsize = (12, 12)):
        self.fig = plt.figure(figsize = (12,12))
        self.ax = plt.axes(projection=self.projection)
        fig = self.fig
        ax = self.ax

        states_provinces = cfeature.NaturalEarthFeature(category='cultural',
                                                        name='admin_0_countries',
                                                        scale='10m',
                                                        facecolor='none')

        ax.add_feature(cfeature.LAND)
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(states_provinces, edgecolor='gray')

        cs = plt.scatter(self._longitude, self._latitude, s = 0.5,
                         c = self.cdata, cmap = "gnuplot", transform = data_crs)
        
        if hasattr(self, "_colordata"):
            cbar = fig.colorbar(cs, label = self._colordata)

        extents = list(ax.get_extent(data_crs))
        extents_x_diff = extents[1] - extents[0]
        extents_y_diff = extents[3] - extents[2]

        diff = extents_x_diff - extents_y_diff
        if diff < 0:
            extents[0] += diff/2
            extents[1] -= diff/2
        else:
            extents[2] -= diff/2
            extents[3] += diff/2

        ax.set_extent(extents)

    def plot_airport(self, icao, ax_ = None):
        if ax_ is None:
            ax_ = self.ax

        try:
            airport = self.airport_data[self.airport_data["ICAO"] == icao]
            longitude = float(airport["LON"])
            latitude = float(airport["LAT"])

            ax_.plot(longitude, latitude, "x", color = "red", transform = data_crs)
        except Exception as e:
            print("Couldn't plot airport:", e)

    def show_plot(self):
        plt.show()


if __name__ == "__main__":
    flightmap = FlightMap("engm_ekch_201023.json",
                          projection="ortho",
                          colordata = "PLANE_ALTITUDE")

    flightmap.make_plot()
    flightmap.plot_airport("ENGM")
    flightmap.plot_airport("EKCH")
    flightmap.show_plot()