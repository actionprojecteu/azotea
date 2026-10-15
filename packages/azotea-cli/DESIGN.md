# Design
A brief summary of the new azotea design.

The new azotea version has been redesigned following the principles of hexagonal architecture (aka "ports and adapters").
The main focus have been the abstraction of the database as the storage service and the image reading and metadata capture.
The image reader now has a cleaner interface to load and manipulate metadata from  FITS and EXIF Raw images.
This allows a much cleaner design of the use cases, with no details of the actual packages used.

The project is structured along major use cases:
* `provision`: creation/update of major entities (Camera, Observer, Location, Roi, etc)
* `operation`: the main focus of the tool, registering and computing raw image statistics in a given ROI
* `reports`: extract data from the storage and export to varios formats (i.e. CSV)
To keep the use cases self-contained as much as possible, 
every folder contains an `adapters` sub-package with the actual implementations.

The `infra` folder contains the CLI code and the database infrastucture framweork (i.e. sqlalchemy) stuff.
The CLI tools `azotool` and `azotea` create all the infrastructure-dependant objects and inject them into the use cases.

Since this is a CLI tool for the time being, it does not require asyncio.
