"""
Copyright (C) 2020 Román Ginés Martínez Ferrández <rgmf@riseup.net>.

This file is part of fit-segment-encoder.

fit-segment-encoder is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

fit-segment-encoder is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with fit-segment-encoder. If not, see <https://www.gnu.org/licenses/>.
"""
FIT_BASE_TYPES = {
    "enum": 0,
    "sint8": 1,
    "uint8": 2,
    "sint16": 131,
    "uint16": 132,
    "sint32": 133,
    "uint32": 134,
    "string": 7,
    "float32": 136,
    "float64": 137,
    "uint8z": 10,
    "uint16z": 139,
    "uint32z": 140,
    "byte": 13,
    "sint64": 142,
    "uint64": 143,
    "uint64z": 144,
}

MANUFACTURER = {
    "garmin": 1,
}

PRODUCT = {
    "edge_530": 3121,
}

SPORT = {
    "generic": 0,
    "running": 1,
    "cycling": 2,
    "transition": 3,
    "fitness_equipment": 4,
    "swimming": 5,
    "basketball": 6,
    "soccer": 7,
    "tennis": 8,
    "american_football": 9,
    "training": 10,
    "walking": 11,
    "cross_country_skiing": 12,
    "alpine_skiing": 13,
    "snowboarding": 14,
    "rowing": 15,
    "mountaineering": 16,
    "hiking": 17,
    "multisport": 18,
    "paddling": 19,
    "flying": 20,
    "e_biking": 21,
    "motorcycling": 22,
    "boating": 23,
    "driving": 24,
    "golf": 25,
    "hang_gliding": 26,
    "horseback_riding": 27,
    "hunting": 28,
    "fishing": 29,
    "inline_skating": 30,
    "rock_climbing": 31,
    "sailing": 32,
    "ice_skating": 33,
    "sky_diving": 34,
    "snowshoeing": 35,
    "snowmobiling": 36,
    "stand_up_paddleboarding": 37,
    "surfing": 38,
    "wakeboarding": 39,
    "water_skiing": 40,
    "kayaking": 41,
    "rafting": 42,
    "windsurfing": 43,
    "kitesurfing": 44,
    "tactical": 45,
    "jumpmaster": 46,
    "boxing": 47,
    "floor_climbing": 48,
    "diving": 53,
    "all": 254,
}

EVENT = {
    "timer": 0,
    "workout": 3,
    "workout_step": 4,
    "power_down": 5,
    "power_up": 6,
    "off_course": 7,
    "session": 8,
    "lap": 9,
    "course_point": 10,
    "battery": 11,
    "virtual_partner_pace": 12,
    "hr_high_alert": 13,
    "hr_low_alert": 14,
    "speed_high_alert": 15,
    "speed_low_alert": 16,
    "cad_high_alert": 17,
    "cad_low_alert": 18,
    "power_high_alert": 19,
    "power_low_alert": 20,
    "recovery_hr": 21,
    "battery_low": 22,
    "time_duration_alert": 23,
    "distance_duration_alert": 24,
    "calorie_duration_alert": 25,
    "activity": 26,
    "fitness_equpment": 27,
    "length": 28,
    "user_marker": 32,
    "sport_point": 33,
    "calibration": 36,
    "front_gear_change": 42,
    "rear_gear_change": 43,
    "rider_position_change": 44,
    "elev_high_alert": 45,
    "elev_low_alert": 46,
    "comm_timeout": 47,
    "radar_threat_alert": 75,
}

EVENT_TYPE = {
    "start": 0,
    "stop": 1,
    "consecutive_depreciated": 2,
    "marker": 3,
    "stop_all": 4,
    "begin_depreciated": 5,
    "end_depreciated": 6,
    "end_all_depreciated": 7,
    "stop_disable": 8,
    "stop_disable_all": 9,
}

SEGMENT_LEADERBOARD_TYPE = {
    "overall": 0,
    "personal_best": 1,
    "connections": 2,
    "group": 3,
    "challenger": 4,
    "kom": 5,
    "qom": 6,
    "pr": 7,
    "goal": 8,
    "rival": 9,
    "club_leader": 10,
}
