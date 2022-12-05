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


class PreferencesZonesLayout(Gtk.Box):
    def __init__(self, dialog):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        self._dialog = dialog
        self._hr_max = dialog.get_pref(AppPreferences.HEART_RATE_MAX)
        self._hr_zones: List[int] = dialog.get_pref(AppPreferences.HEART_RATE_ZONES)

        self._title = Gtk.Label.new(_("Training Heart Rate Zones"))
        self._title.get_style_context().add_class("pyot-h3")
        self._title.set_margin_top(20)

        self._help_text = Gtk.Label.new(_("Configure your training heart rate zones"))
        self._help_text.get_style_context().add_class("pyot-prefs-help")
        self._help_text.set_margin_bottom(20)

        self._content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self._content_box.set_hexpand(False)
        self._content_box.set_halign(Gtk.Align.CENTER)

        box_max_hr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self._max_hr_label = Gtk.Label.new(_("Max. Heart Rate"))
        box_entry_unit = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self._max_hr_entry = Gtk.Entry()
        self._max_hr_entry.set_text(str(self._hr_max))
        focus_controller = Gtk.EventControllerFocus()
        focus_controller.connect("leave", self._on_hr_max_changed)
        self._max_hr_entry.add_controller(focus_controller)

        self._unit_hr_label = Gtk.Label.new(_("bpm"))
        box_entry_unit.append(self._max_hr_entry)
        box_entry_unit.append(self._unit_hr_label)
        box_max_hr.append(self._max_hr_label)
        box_max_hr.append(box_entry_unit)

        self._max_hr_hint_label = Gtk.Label.new(
            _("* set a heart rate maximum value and click on ok icon or press enter to set zones")
        )
        self._max_hr_hint_label.get_style_context().add_class("pyot-p-danger")
        if self._hr_max and self._hr_max > 0:
            self._max_hr_hint_label.set_visible(False)

        self._zones_grid = Gtk.Grid()
        self._zones_grid.set_row_spacing(10)
        self._zones_grid.set_column_spacing(10)
        self._zones_grid.attach(Gtk.Label.new("bpm"), 0, 0, 1, 1)
        self._zones_grid.attach(Gtk.Label.new("%"), 1, 0, 1, 1)

        self._bpm1_entry = Gtk.Entry()
        self._zones_grid.attach(self._bpm1_entry, 0, 1, 1, 2)
        self._bpm2_entry = Gtk.Entry()
        self._zones_grid.attach(self._bpm2_entry, 0, 4, 1, 2)
        self._bpm3_entry = Gtk.Entry()
        self._zones_grid.attach(self._bpm3_entry, 0, 7, 1, 2)
        self._bpm4_entry = Gtk.Entry()
        self._zones_grid.attach(self._bpm4_entry, 0, 10, 1, 2)
        self._bpm5_entry = Gtk.Entry()
        self._zones_grid.attach(self._bpm5_entry, 0, 13, 1, 2)
        self._bpm6_entry = Gtk.Entry()
        self._zones_grid.attach(self._bpm6_entry, 0, 16, 1, 2)

        self._zone1_entry = Gtk.Entry()
        self._zones_grid.attach(self._zone1_entry, 1, 1, 1, 2)
        self._zone2_entry = Gtk.Entry()
        self._zones_grid.attach(self._zone2_entry, 1, 4, 1, 2)
        self._zone3_entry = Gtk.Entry()
        self._zones_grid.attach(self._zone3_entry, 1, 7, 1, 2)
        self._zone4_entry = Gtk.Entry()
        self._zones_grid.attach(self._zone4_entry, 1, 10, 1, 2)
        self._zone5_entry = Gtk.Entry()
        self._zones_grid.attach(self._zone5_entry, 1, 13, 1, 2)
        self._zone6_entry = Gtk.Entry()
        self._zones_grid.attach(self._zone6_entry, 1, 16, 1, 2)

        self._zone1_label = Gtk.Label()
        self._zones_grid.attach(self._zone1_label, 2, 2, 1, 3)
        self._zone2_label = Gtk.Label()
        self._zones_grid.attach(self._zone2_label, 2, 5, 1, 3)
        self._zone3_label = Gtk.Label()
        self._zones_grid.attach(self._zone3_label, 2, 8, 1, 3)
        self._zone4_label = Gtk.Label()
        self._zones_grid.attach(self._zone4_label, 2, 11, 1, 3)
        self._zone5_label = Gtk.Label()
        self._zones_grid.attach(self._zone5_label, 2, 14, 1, 3)

        self._content_box.append(box_max_hr)
        self._content_box.append(self._max_hr_hint_label)
        self._content_box.append(self._zones_grid)

        self.append(self._title)
        self.append(self._help_text)
        self.append(self._content_box)

        self._set_zones()

    def _set_zones(self):
        if not self._hr_max or self._hr_max < 0:
            self._zones_grid.set_sensitive(False)
        else:
            self._zones_grid.set_sensitive(True)

        self._zone1_label.set_text(_("Zone 1") + " (" + ZonesUtils.description_hr_zone("Z1") + ")")
        self._zone1_label.get_style_context().add_class("pyot-p-medium")
        self._zone1_label.set_xalign(0.0)
        self._zone2_label.set_text(_("Zone 2") + " (" + ZonesUtils.description_hr_zone("Z2") + ")")
        self._zone2_label.get_style_context().add_class("pyot-p-medium")
        self._zone2_label.set_xalign(0.0)
        self._zone3_label.set_text(_("Zone 3") + " (" + ZonesUtils.description_hr_zone("Z3") + ")")
        self._zone3_label.get_style_context().add_class("pyot-p-medium")
        self._zone3_label.set_xalign(0.0)
        self._zone4_label.set_text(_("Zone 4") + " (" + ZonesUtils.description_hr_zone("Z4") + ")")
        self._zone4_label.get_style_context().add_class("pyot-p-medium")
        self._zone4_label.set_xalign(0.0)
        self._zone5_label.set_text(_("Zone 5") + " (" + ZonesUtils.description_hr_zone("Z5") + ")")
        self._zone5_label.get_style_context().add_class("pyot-p-medium")
        self._zone5_label.set_xalign(0.0)

        self._zone1_entry.set_text(str(self._hr_zones[0]))
        controller = Gtk.EventControllerFocus()
        controller.connect("leave", self._on_zone_entry_changed)
        self._zone1_entry.add_controller(controller)

        self._zone2_entry.set_text(str(self._hr_zones[1]))
        controller = Gtk.EventControllerFocus()
        controller.connect("leave", self._on_zone_entry_changed)
        self._zone2_entry.add_controller(controller)

        self._zone3_entry.set_text(str(self._hr_zones[2]))
        controller = Gtk.EventControllerFocus()
        controller.connect("leave", self._on_zone_entry_changed)
        self._zone3_entry.add_controller(controller)

        self._zone4_entry.set_text(str(self._hr_zones[3]))
        controller = Gtk.EventControllerFocus()
        controller.connect("leave", self._on_zone_entry_changed)
        self._zone4_entry.add_controller(controller)

        self._zone5_entry.set_text(str(self._hr_zones[4]))
        controller = Gtk.EventControllerFocus()
        controller.connect("leave", self._on_zone_entry_changed)
        self._zone5_entry.add_controller(controller)

        self._zone6_entry.set_text(str(self._hr_zones[5]))

        self._bpm1_entry.set_text(str(SensorUtils.round_to_int(self._hr_zones[0] / 100 * self._hr_max)))
        controller = Gtk.EventControllerFocus()
        controller.connect("leave", self._on_bpm_entry_changed)
        self._bpm1_entry.add_controller(controller)

        self._bpm2_entry.set_text(str(SensorUtils.round_to_int(self._hr_zones[1] / 100 * self._hr_max)))
        controller = Gtk.EventControllerFocus()
        controller.connect("leave", self._on_bpm_entry_changed)
        self._bpm2_entry.add_controller(controller)

        self._bpm3_entry.set_text(str(SensorUtils.round_to_int(self._hr_zones[2] / 100 * self._hr_max)))
        controller = Gtk.EventControllerFocus()
        controller.connect("leave", self._on_bpm_entry_changed)
        self._bpm3_entry.add_controller(controller)

        self._bpm4_entry.set_text(str(SensorUtils.round_to_int(self._hr_zones[3] / 100 * self._hr_max)))
        controller = Gtk.EventControllerFocus()
        controller.connect("leave", self._on_bpm_entry_changed)
        self._bpm4_entry.add_controller(controller)

        self._bpm5_entry.set_text(str(SensorUtils.round_to_int(self._hr_zones[4] / 100 * self._hr_max)))
        controller = Gtk.EventControllerFocus()
        controller.connect("leave", self._on_bpm_entry_changed)
        self._bpm5_entry.add_controller(controller)

        self._bpm6_entry.set_text(str(SensorUtils.round_to_int(self._hr_zones[5] / 100 * self._hr_max)))

    def _on_hr_max_changed(self, controller: Gtk.EventControllerFocus):
        try:
            entry = controller.get_widget()
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

    def _on_zone_entry_changed(self, controller: Gtk.EventControllerFocus):
        entry = controller.get_widget()
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

    def _on_bpm_entry_changed(self, controller: Gtk.EventControllerFocus):
        entry = controller.get_widget()
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
