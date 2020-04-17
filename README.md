### Try #1: ###
```
pip install -r requirements.txt
```

### Try #2: ###
```
pip install flask opencv-python
```
If it gets any error, probably with `opencv-python` try to install them manually.

## Running ##
To start the service `cd` to project folder and type `python server.py` or `python3 server.py`

*It only runs on python3*

#### Command line arguments
- FP = String specifying the path to a static file path. This is very useful for debugging and allows you to design with a static image


#### Example
- python server.py -FP "images/markers.jpg"

Once done navigate to the ip of the server and access the port `5000`.

http://localhost:5000

### Change camera source ###
To change the camera source of opencv you can go to the beginning of file `server.py` and add a `video_source=1` it can be 0,1,2... as many video inputs the device has in the declaration of object `Camera`. Or you can change the default video source on `camera.py` `Camera` class `__init__` method.

