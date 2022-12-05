# -*- coding: utf-8 -*-
import sqlite3
import argparse
import json


def import_to_database(database_file: str, json_file: str):
    with open(json_file, "r") as fd:
        record_list = json.load(fd)

    try:
        conn = None
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()

        for record in record_list:
            query_str = (
                "select a._id "
                "from activities a, stats s "
                "where a.statsid=s._id and "
                f"s.starttime={record[1]} and "
                f"s.stoptime={record[2]}"
            )
            cursor.execute(query_str)
            result = cursor.fetchone()
            if result:
                print("nombre: " + record[0])
                query_str = (
                    'update activities set '
                    f'name="{record[0]}" '
                    f'where _id={result[0]}'
                )
                cursor.execute(query_str)
                conn.commit()
    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if conn:
            conn.close()


def export_to_file(database_file: str, json_file: str):
    try:
        conn = None
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()

        query_str = "select a.name, s.starttime, s.stoptime from activities a, stats s where a.statsid=s._id;"
        #query_str = "select name, starttime, stoptime from tracks;"
        cursor.execute(query_str)
        record = cursor.fetchall()
        with open(json_file, "w") as fd:
            fd.write(json.dumps(record))
        cursor.close()

    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--database-file", required=True, help="sqlite3 database file")
    parser.add_argument("-j", "--json-file", required=True, help="path to JSON file to read/write")
    parser.add_argument("-e", "--export-to-file", required=False, help="to export data to the JSON file", action="store_true")
    parser.add_argument("-i", "--import-to-database", required=False, help="to update data in the database from JSON file", action="store_true")
    args = parser.parse_args()

    if args.export_to_file or (args.export_to_file is None and args.import_to_database is None):
        export_to_file(args.database_file, args.json_file)
    else:
        import_to_database(args.database_file, args.json_file)
