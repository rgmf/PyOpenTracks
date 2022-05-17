import fitparse

from definitions import SPORT, SEGMENT_LEADERBOARD_TYPE
from fit_encoder import SegmentPoint, FitSegmentEncoder, SegmentLeader

if __name__ == '__main__':
    file_name = "segment.fit"
    segment_points = [
        SegmentPoint(0, 456184344, -10688374, int(0.0), int(194.79), int(0.0), int(0.0)),
        SegmentPoint(1, 456188506, -10691639, int(45.54), int(195.39), int(7.328), int(7.328)),
        SegmentPoint(2, 456195291, -10698303, int(125.44), int(197.6), int(19.021), int(19.021)),
        SegmentPoint(3, 456202077, -10704968, int(205.34), int(203.2), int(30.756), int(30.756)),
    ]

    # Generate FIT segment file.
    with open(file_name, "wb") as fd:
        encoder = FitSegmentEncoder(
            name="Nombre",
            sport=SPORT["cycling"],
            segment_points=segment_points
        )
        encoder.add_leader(
            SegmentLeader(
                type=SEGMENT_LEADERBOARD_TYPE["personal_best"],
                segment_time=10 * 60,
                activity_id_string="12345"
            )
        )
        encoder.add_leader(
            SegmentLeader(
                type=SEGMENT_LEADERBOARD_TYPE["pr"],
                segment_time=10 * 60,
                activity_id_string="54321"
            )
        )
        fd.write(encoder.end_and_get())

    # HERE python-fitparse is used TO SHOW THE CONTENTS OF THE JUST CREATED FIT SEGMENT FILE.

    # Read and print information about FIT segment file using python-fitparse Python library.
    fitfile = fitparse.FitFile(file_name)
    for file_id in fitfile.get_messages("file_id"):
        fields = [field_data for field_data in file_id.fields]
        if not list(filter(lambda field_data: field_data.field and field_data.field.def_num == 0 and field_data.value == "segment", fields)):
            print("It's not a segment file")
            exit()
        else:
            print("It's a segment file")

        print()
        for mesg in fitfile.messages:
            print(mesg.name, mesg.get_values())
