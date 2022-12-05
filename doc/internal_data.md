# Data source
PyOpenTracks offers three possibilities of adding tracks:
- By importing a file.
- By importing a folder (it imports all supported track files).
- By sync a folder (it imports every supported track file in there and it'll maintain sync this folder so every new supported track file will be imported).

Also, PyOpenTracks offer the possiblity of open a track file so the user can see it withouth importing anything.

## Open a track
User can open a supported track file and see all its stats.

When a file is opened then a parser is executed and `TrackStats` is used to compute stats.

At the end of the parser process a `Track` object is built from `TrackStats` (including the list of `TrackPoint`.

Database and internal storage isn't touch. So it's an option that user can use only for see stats from a supported track file.

## Importing a file
User can import a supported track file.

In this case a parser is executed and it uses `TrackStats` to compute the stats and creates a `Track` object.

Now, PyOpenTracks looks for a `Track` like this in the database. If `Track` is a new one then PyOpenTracks will save it into the database and it will move the track file to internal storage.

PyOpenTracks check for a duplication `Track` in this way:
- Checks that there is not a track with the same UUID (if any).
- Checks that there is not a track between starttime and endtime. 

# Internal data
All imported files by whatever method will be moved to the internal storage.

Also, PyOpenTracks uses a sqlite database where all tracks are saved with its stats.

# Binary files (deprecated)
PyOpenTracks save all the data from track files into binary files with this fields (in this order):

## Track ID (32 bytes - 32 characters - "=32s"

128 bits UUID that OpenTracks use to identify all tracks.

The code used to write the UUID to a binary file and recover it again from a binary file is showed here:

```python
from uuid import UUID
from struct import pack, unpack

# Creates a UUID object from the UUID read from track file.
my_uuid = UUID("618af835-1b8f-4417-a446-0ebf62bfe1b8")

# Pack the uuid to save it to a binary file.
packed_uuid = pack("=32s", my_uuid.hex.encode())

# Recover UUID from binary file: unpack and recreate UUID.
uuid_frombin = unpack("=32s", packed_uuid)
my_uuid_recovered = uuid_frombin[0].decode("utf-8")
```

## Start timestamp in milliseconds (4 bytes - 1 long - "l")
Then binary file contains the start time in a timestamp unix format. Here it shows the python code that pack and unpack the a timestamp:

```python
from struct import pack, unpack
import time

# Pack now time.
now = int(time.time() * 1000)
packed_timestamp = pack("l", now)

# Unpack the time.
unpacked_timestamp = unpack("l", packed_timestamp)[0]

```

## End timestamp in milliseconds (4 bytes - 1 long - "l")
Then the end timestamp is saved into binary file (the last timestamp in the track file).

## Activity type (2 bytes - 1 short - "h")
The activity type is a short number representing the activity type. So it's needed to link every number to a string like: road biking, mtb biking, road biking, running, trail running...

This is the code in python to pack and unpack a short number:

```python
from struct import pack, unpack

# Pack activity type.
activity_type = 1
packed = pack("h", activity_type)

# Unpack activity type.
unpacked = unpack("h", packed)[0]
```

