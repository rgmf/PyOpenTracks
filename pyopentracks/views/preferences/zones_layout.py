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
from typing import List

from gi.repository import Gtk

from pyopentracks.app_preferences import AppPreferences
from pyopentracks.utils.utils import SensorUtils, ZonesUtils


@Gtk.Template(resource_path="/es/rgmf/pyopentracks/ui/preferences_zones_layout.ui")
class PreferencesZonesLayout(Gtk.Box):
    __gtype_name__ = "PreferencesZonesLayout"

    _title: Gtk.Label = Gtk.Template.Child()
    _help_text: Gtk.Label = Gtk.Template.Child()

    _max_hr_label: Gtk.Label = Gtk.Template.Child()
    _unit_hr_label: Gtk.Label = Gtk.Template.Child()
    _max_hr_entry: Gtk.Entry = Gtk.Template.Child()
    _max_hr_hint_label: Gtk.Label = Gtk.Template.Child()

    _content_box: Gtk.Box = Gtk.Template.Child()

    _zones_grid: Gtk.Grid = Gtk.Template.Child()
    _hr_unit_head_label: Gtk.Label = Gtk.Template.Child()
    _percentage_head_label: Gtk.Label = Gtk.Template.Child()
    _zone1_label: Gtk.Label = Gtk.Template.Child()
    _zone2_label: Gtk.Label = Gtk.Template.Child()
    _zone3_label: Gtk.Label = Gtk.Template.Child()
    _zone4_label: Gtk.Label = Gtk.Template.Child()
    _zone5_label: Gtk.Label = Gtk.Template.Child()
    _zone1_entry: Gtk.Entry = Gtk.Template.Child()
    _zone2_entry: Gtk.Entry = Gtk.Template.Child()
    _zone3_entry: Gtk.Entry = Gtk.Template.Child()
    _zone4_entry: Gtk.Entry = Gtk.Template.Child()
    _zone5_entry: Gtk.Entry = Gtk.Template.Child()
    _zone6_entry: Gtk.Entry = Gtk.Template.Child()
    _bpm1_entry: Gtk.Entry = Gtk.Template.Child()
    _bpm2_entry: Gtk.Entry = Gtk.Template.Child()
    _bpm3_entry: Gtk.Entry = Gtk.Template.Child()
    _bpm4_entry: Gtk.Entry = Gtk.Template.Child()
    _bpm5_entry: Gtk.Entry = Gtk.Template.Child()
    _bpm6_entry: Gtk.Entry = Gtk.Template.Child()

    def __init__(self, dialog):
        super().__init__()

        self._dialog = dialog
        self._hr_max = dialog.get_pref(AppPreferences.HEART_RATE_MAX)
        self._hr_zones: List[int] = dialog.get_pref(AppPreferences.HEART_RATE_ZONES)

        self._title.set_text(_("Training Heart Rate Zones"))
        self._title.get_style_context().add_class("pyot-h3")

        self._help_text.set_text(_("Configure your training heart rate zones"))
        self._help_text.get_style_context().add_class("pyot-prefs-help")

        self._max_hr_label.set_text(_("Max. Heart Rate"))
        self._unit_hr_label.set_text(_("bpm"))
        self._max_hr_entry.set_text(str(self._hr_max))
        self._max_hr_entry.connect("focus-out-event", self._on_hr_max_changed)
        self._max_hr_hint_label.set_text(
            _("* set a heart rate maximum value and click on ok icon or press enter to set zones")
        )
        self._max_hr_hint_label.get_style_context().add_class("pyot-p-danger")
        if self._hr_max and self._hr_max > 0:
            self._max_hr_hint_label.set_visible(False)

        self._content_box.get_style_context().add_class("pyot-stats-bg-color")

        self._set_zones()

    def _set_zones(self):
        if not self._hr_max or self._hr_max < 0:
            self._zones_grid.set_sensitive(False)
        else:
            self._zones_grid.set_sensitive(True)

        self._hr_unit_head_label.set_text(_("bpm"))

        self._zone1_label.set_text(_("Zone 1") + " (" + ZonesUtils.description_hr_zone("Z1") + ")")
        self._zone1_label.get_style_context().add_class("pyot-p-medium")
        self._zone2_label.set_text(_("Zone 2") + " (" + ZonesUtils.description_hr_zone("Z2") + ")")
        self._zone2_label.get_style_context().add_class("pyot-p-medium")
        self._zone3_label.set_text(_("Zone 3") + " (" + ZonesUtils.description_hr_zone("Z3") + ")")
        self._zone3_label.get_style_context().add_class("pyot-p-medium")
        self._zone4_label.set_text(_("Zone 4") + " (" + ZonesUtils.description_hr_zone("Z4") + ")")
        self._zone4_label.get_style_context().add_class("pyot-p-medium")
        self._zone5_label.set_text(_("Zone 5") + " (" + ZonesUtils.description_hr_zone("Z5") + ")")
        self._zone5_label.get_style_context().add_class("pyot-p-medium")

        self._zone1_entry.set_text(str(self._hr_zones[0]))
        self._zone1_entry.connect("focus-out-event", self._on_zone_entry_changed)
        self._zone2_entry.set_text(str(self._hr_zones[1]))
        self._zone2_entry.connect("focus-out-event", self._on_zone_entry_changed)
        self._zone3_entry.set_text(str(self._hr_zones[2]))
        self._zone3_entry.connect("focus-out-event", self._on_zone_entry_changed)
        self._zone4_entry.set_text(str(self._hr_zones[3]))
        self._zone4_entry.connect("focus-out-event", self._on_zone_entry_changed)
        self._zone5_entry.set_text(str(self._hr_zones[4]))
        self._zone5_entry.connect("focus-out-event", self._on_zone_entry_changed)
        self._zone6_entry.set_text(str(self._hr_zones[5]))

        self._bpm1_entry.set_text(str(SensorUtils.round_to_int(self._hr_zones[0] / 100 * self._hr_max)))
        self._bpm1_entry.connect("focus-out-event", self._on_bpm_entry_changed)
        self._bpm2_entry.set_text(str(SensorUtils.round_to_int(self._hr_zones[1] / 100 * self._hr_max)))
        self._bpm2_entry.connect("focus-out-event", self._on_bpm_entry_changed)
        self._bpm3_entry.set_text(str(SensorUtils.round_to_int(self._hr_zones[2] / 100 * self._hr_max)))
        self._bpm3_entry.connect("focus-out-event", self._on_bpm_entry_changed)
        self._bpm4_entry.set_text(str(SensorUtils.round_to_int(self._hr_zones[3] / 100 * self._hr_max)))
        self._bpm4_entry.connect("focus-out-event", self._on_bpm_entry_changed)
        self._bpm5_entry.set_text(str(SensorUtils.round_to_int(self._hr_zones[4] / 100 * self._hr_max)))
        self._bpm5_entry.connect("focus-out-event", self._on_bpm_entry_changed)
        self._bpm6_entry.set_text(str(SensorUtils.round_to_int(self._hr_zones[5] / 100 * self._hr_max)))

        self._zones_grid.show_all()

    def _on_hr_max_changed(self, entry, event):
        try:
            self._hr_max = int(entry.get_text())
            self._max_hr_entry.set_text(str(self._hr_max))
            self._max_hr_hint_label.set_visible(False)
        except Exception as error:
            self._max_hr_entry.set_text("")
            self._max_hr_hint_label.set_visible(True)
            self._zones_grid.set_sensitive(False)
        finally:
            self._dialog.set_pref(AppPreferences.HEART_RATE_MAX, self._hr_max)
            self._set_zones()

    def _on_zone_entry_changed(self, entry, event):
        if entry is self._zone1_entry:
            idx = 0
            bpm_entry = self._bpm1_entry
        elif entry is self._zone2_entry:
            idx = 1
            bpm_entry = self._bpm2_entry
        elif entry is self._zone3_entry:
            idx = 2
            bpm_entry = self._bpm3_entry
        elif entry is self._zone4_entry:
            idx = 3
            bpm_entry = self._bpm4_entry
        elif entry is self._zone5_entry:
            idx = 4
            bpm_entry = self._bpm5_entry
        else:
            return

        try:
            zone_percentage_int_value = int(entry.get_text())
            self._hr_zones[idx] = zone_percentage_int_value
        except Exception as error:
            pass
        finally:
            entry.set_text(str(self._hr_zones[idx]))
            bpm_entry.set_text(str(SensorUtils.round_to_int(self._hr_zones[idx] / 100 * self._hr_max)))
            self._dialog.set_pref(AppPreferences.HEART_RATE_ZONES, self._hr_zones)

    def _on_bpm_entry_changed(self, entry, event):
        if entry is self._bpm1_entry:
            idx = 0
            zone_entry = self._zone1_entry
        elif entry is self._bpm2_entry:
            idx = 1
            zone_entry = self._zone2_entry
        elif entry is self._bpm3_entry:
            idx = 2
            zone_entry = self._zone3_entry
        elif entry is self._bpm4_entry:
            idx = 3
            zone_entry = self._zone4_entry
        elif entry is self._bpm5_entry:
            idx = 4
            zone_entry = self._zone5_entry
        else:
            return

        try:
            bpm_int_value = SensorUtils.round_to_int(int(entry.get_text()))
            int_percentage_value = SensorUtils.round_to_int(bpm_int_value * 100 / self._hr_max)
            self._hr_zones[idx] = int_percentage_value
            zone_entry.set_text(str(int_percentage_value))
        except Exception as error:
            entry.set_text(str(SensorUtils.round_to_int(self._hr_zones[idx] / 100 * self._hr_max)))
        finally:
            self._dialog.set_pref(AppPreferences.HEART_RATE_ZONES, self._hr_zones)
