"""
Copyright (C) 2020 Román Ginés Martínez Ferrández <rgmf@riseup.net>.

This file is part of PyOpenTracks.

PyOpenTracks is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

PyOpenTracks is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyOpenTracks. If not, see <https://www.gnu.org/licenses/>.
"""
from dataclasses import dataclass


@dataclass
class FitSdkProduct:
    # Manufacturer's name
    manufacturer: str
    # Value's name
    value_name: str
    # Value
    value: int
    # Model's description
    model: str
    # Has trusted barometer
    barometer: bool = False

    def has(self, product: any):
        """Return True if product is value_name or value."""
        if type(product) == str:
            return self.value_name == product
        elif type(product) == int:
            return self.value == product
        else:
            return False


@dataclass
class RecordedWith:
    # Unique ID for this recorded option
    id: int
    # Software's name
    software: str
    # Product value (from FIT SDK). It can be str or int
    product: FitSdkProduct = None

    def is_opentracks(self):
        return self.software.lower() == "opentracks"

    def is_unknown(self):
        return self.id == 0

    @staticmethod
    def unknown():
        return RecordedOptions[0]

    @staticmethod
    def from_software(software: str):
        if software is None:
            return RecordedWith.unknown()

        items = list(filter(lambda i: i.software.lower() == software.lower(), RecordedOptions.values()))
        if len(items) > 0:
            return items[0]
        else:
            return RecordedWith.unknown()

    @staticmethod
    def from_device(manufacturer: str, product: any):
        if product is None:
            return RecordedWith.from_software(manufacturer)

        items = list(
            filter(
                lambda i:
                    i.product is not None and \
                    i.product.manufacturer.lower() == manufacturer.lower() and \
                    i.product.has(product),
                RecordedOptions.values()
            )
        )
        if len(items) > 0:
            return items[0]
        else:
            return RecordedWith.unknown()


RecordedOptions = {
    0: RecordedWith(0, "Unknown"),
    1: RecordedWith(1, "OpenTracks"),
    2: RecordedWith(2, "Garmin"),
    3: RecordedWith(3, "Garmin", FitSdkProduct("Garmin", "edge520", 2067, "Edge 520", True)),
    4: RecordedWith(4, "Garmin", FitSdkProduct("Garmin", "edge530", 3121, "Edge 530", True)),
    5: RecordedWith(5, "Garmin", FitSdkProduct("Garmin", "fenix6S", 3288, "Fenix 6s", True)),
    6: RecordedWith(5, "Garmin", FitSdkProduct("Garmin", "fenix6S_sport", 3287, "Fenix 6s", True))
}