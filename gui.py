'''Setup and running of the GUI, as well as calling to other sub systems

'''

import tkinter as tk
from time import time

from PIL import ImageTk
from goompy import GooMPy

import location
import search

class RoutePlanGUI:
    '''The GUI for the Route Planning System

    All the GUI features are created and run though this class. All expected
    user input will come though this GUI, along with all output to the user

    Attributes:
    root               The Root from which the application is running
        #max_height     Maximium height for the window
        #max_width
    transport_mode     Transport mode setting 
    locations          List of all the current locations
    location_view      Index of what can currently be viewed
    VIEW_SIZE          A limit of how many items can be viewed at one time to ensure they fit on screen
    latitude           The current latitude  of the device running the system
    longitude          The cyrrent longitude of the device running the system
    zoom               The zoom level of the tiles
    map_width          The width  of the displayed map
    map_height         The height of the displayed map
    goompy             A goompy object to act as the API to download the map tiles

    Methods:
    _draw_UI           Creates the UI features and places them in the correct location
    _redraw_map        Redraws the map
    _add_location      Adds a location to the list of locations
    _remove_location   Removes a location from the list of locations
    _move_boxes        Moves the displayed list of locations
    _search            Runs the search algorithm after fetching and passing it data
    '''

    def __init__(self, root):
        self.root = root

        self.max_height = self.root.winfo_screenheight()
        self.max_width  = self.root.winfo_screenwidth()
        self.root.geometry((str(int(self.max_width/2))+"x"+str(int(self.max_height/2))))

##        self.radiogroup = Frame()

##        self.root.bind("<Key>", self.user_input)
##        self.root.bind("<Button>", self.user_input)
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        
        # The user is able to select differnt modes of transportation
        # They are diffined here, as well as the mechanism for storing them
        self.transport_mode  = tk.StringVar()
        self.transport_mode.set("Walking")
        self.transport_modes = ["Walking", "Bicycling", "Driving", "Transit"] 

        # All the locations the user is using, stored in a list
        self.locations = []

        # The index used to calualate which locations are currently visable
        self.location_view = 0

        # Used to limit the system from attempting to display more locations
        # than possible
        self.VIEW_SIZE = 10

        # The coordinates of the current location of the user
        self.latitude  = float(
            location.CURRENT_LOCATION[:location.CURRENT_LOCATION.find(",")]
            )
        self.longitude = float(
            location.CURRENT_LOCATION[location.CURRENT_LOCATION.find(",")+1:]
            )

        # The zoom level on the map
        self.zoom = 15

        # The dimentions of the map
        self.map_width  = 500
        self.map_height = 500

        # GooMPy object to act as an API
        self.goompy = GooMPy(self.map_width, self.map_height, self.latitude, self.longitude, self.zoom, "roadmap")

        self.live = False

        # Starts the system
        self._draw_UI()
        self.root.mainloop()
        

    def _draw_UI(self):
        '''Draw the UI

        '''

        # Backbone of the GUI layout
        self.frame = tk.Frame(self.root)

        # Placement of Radiobuttons with correct control assignment
        for index, mode in enumerate(self.transport_modes):
            tk.Radiobutton(
                self.frame,
                text=mode,
                variable=self.transport_mode,
                value=mode
                ).grid(row=0, column=index)

        # Movement buttons
        self.up_button   = tk.Button(
            self.frame,
            text="  Up   ",
            bg="yellow",
            command=lambda: self._move_boxes(1)
            )
        self.down_button = tk.Button(
            self.frame,
            text="Down",
            bg="yellow",
            command=lambda: self._move_boxes(-1)
            )
        self.showing_movement_buttons = False

        # Start button
        self.go_button = tk.Button(
            self.frame,
            text="Start Search",
            bg="yellow",
            command=lambda: self._search()
            )

        # Entry box for user input, along with an associated button
        self.entry_box = tk.Entry(self.frame)
        self.entry_box.insert("end", "Add Location")
        self.entry_box.bind("<Return>", self._add_location)
        self.entry_button = tk.Button(
            self.frame,
            text="+",
            bg="green",
            command=self._add_location
            )

        # Configureation of the widgets just defined
        self.entry_box.grid(row=2, column=0, columnspan=4, sticky="ew")
        self.entry_button.grid(row=2, column=4)
        self.go_button.grid(row=1, column=3, columnspan=2, sticky="e")

        # Canvas to hold the map
        self.canvas = tk.Canvas(
            self.root,
            width=self.map_width,
            height=self.map_height,
            bg="black"
            )

        # Underlay to configure the tile image
        self.label = tk.Label(self.canvas)

        self.zoom_in_button  = tk.Button(self.canvas, text="+", width=1, command=lambda:self._map_zoom(+1))
        self.zoom_out_button = tk.Button(self.canvas, text="-", width=1, command=lambda:self._map_zoom(-1))

        # Packing of the two layout features
        self.frame.pack(side="left", fill="y")
        self.canvas.pack(side="right", expand=True, fill="both")

        ##        x = int(self.canvas['width']) - 50
##        y = int(self.canvas['height']) - 80
##
##        self.zoom_in_button.place(x=x, y=y)
##        self.zoom_out_button.place(x=x, y=y+30)

        # Load a tile
        self._reload()


        
    def _redraw_map(self):
        '''Fetch a new tile and place that on the map

        '''
##        print("redrawing")
        # Get the tile that goompy has been told to fetch
        self.goompy._fetch_and_update()
        self.image = self.goompy.getImage()

        # Load the image tile onto the map
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.label['image'] = self.image_tk
        self.label.place(
            x=0,
            y=0,
            width=self.map_width,
            height=self.map_height
            )

    def _reload(self):
        self.coords = None
        if self.live:
            self._redraw_map()


    def _add_location(self, event=None):
        '''Make the user's input a Location and add to the list of locations

        '''
        # The details of the new location
        user_input = self.entry_box.get()
        new_location = location.Location(user_input)
        self.locations.append(new_location)
        precise = new_location.location

        # goompy loading a new tile as per the location
        self.goompy.lat = float(precise[:precise.find(",")])
        self.goompy.lon = float(precise[precise.find(",")+1:])
        self._reload()


        # Differnt actions depending on how many locations currently exist
        if len(self.locations) > self.VIEW_SIZE:

            # Configure the movement buttons is not configured
            if not self.showing_movement_buttons:
                self.up_button.grid(row=1, column=0, columnspan=2, sticky="w")
                self.down_button.grid(
                    row=self.VIEW_SIZE+10,
                    column=0,
                    columnspan=2,
                    sticky="w"
                    )
            # Ensures the latest location is displayed at the bottom
            while len(self.locations)-self.location_view > self.VIEW_SIZE:
                self._move_boxes(1)
        else:
            # Move the entry box, and its button, down on space
            self.entry_box.grid_configure(
                row=self.entry_box.grid_info()["row"]+1
                )
            self.entry_button.grid_configure(
                row=self.entry_box.grid_info()["row"]
                )
            
            # The row the the entry box moved from
            row = self.entry_box.grid_info()["row"]-1

            # Create a Label and a Button for the new location
            tk.Label(
                self.frame,
                text=user_input,
                bg="white",
                anchor="w"
                ).grid(row=row, column=0, sticky="ew", columnspan=4)
            tk.Button(
                self.frame,
                text="X",
                bg="red",
                command=lambda: self._remove_location(len(self.locations))
                ).grid(row=row, column=4, sticky="ew")

        # Reset the text in the entry box
        self.entry_box.delete(0, "end")
        self.entry_box.insert("end", "Add Location")

        
    def _remove_location(self, row):
        '''Remove the location selected by the user by visualy and from list

        '''
        # Remove the location from the location list
        self.locations.pop(row+self.location_view-1)

        # Marker to indicate if the locations below should move up
        move = False

        # List of all the locations, as per what is on the Labels
        remaining_locations = [x.user_input for x in self.locations]

        # Index to keep track of where is being investigated
        index = 0

        # Looping though all the slaves and adjusting them as needed
        for slave in self.frame.grid_slaves()[::-1]: # Reversed for simplicity
            
            # Anaylse and configure the Labels
            if type(slave) == tk.Label:
                if self.location_view+index == len(self.locations):
                    slave.grid_forget()
                else:
                    if slave.cget("text") not in remaining_locations:
                        move = True
                    if move:
                        slave.config(
                            text=self.locations[
                                self.location_view+index
                                ].user_input
                            )
                index += 1
            # Ensure that the final button is removed if needed
            if (type(slave) == tk.Button and
                self.location_view+index-1 == len(self.locations)):
                slave.grid_forget()
                
        self.location_view -= 1

    def _move_boxes(self, direction):
        '''Move the visual list of locations in required direction

        '''

        for i in self.locations:
            print(i)

        # Ensure that the given command is valid in the current configuration
        if ((self.location_view == 0 and
            direction == -1) or
            (self.location_view+self.VIEW_SIZE == len(self.locations) and
             direction == 1)):
            return None
        else:
            self.location_view += direction
            
            # Iterate though the Labels and change their values
            for index, slave in enumerate(self.frame.grid_slaves()[::-1]):
                if type(slave) == tk.Label:
                    slave.config(
                        text=self.locations[
                            self.location_view+index
                            ].user_input
                        )


##    def user_input(self, event):
##        if event.char == "a":
##            print(self.transport_mode.get())

    def _search(self):
        '''Calculate and return the most efficent route

        '''
        # Using the Latitude and Longitude, calculate the distance matrix
        precise_locations = [l.location for l in self.locations]
        distance_matrix_info = location.GM.distance_matrix(
            precise_locations, precise_locations,
            mode=self.transport_mode.get().lower()
            )
        self.distance_matrix = []
        for origin in distance_matrix_info["rows"]:
            self.distance_matrix.append(
                [dest["duration"]["value"] for dest in origin["elements"]]
                )

########################################################################################################################
        t = time()
        _time, _route = search.nearest_neighbour(self.distance_matrix)
        print("nn time")
        print(time()-t)
        t2 = time()
        _time2, _route2 = search.brute_force(self.distance_matrix)
        print("bf time")
        print(time()-t2)
        print(_time)
        print(_route)
########################################################################################################################

        # Write message to the user about the best route
        msg = "The best route to visit every location in the minimun amount of time is "
        for loc in _route[:-1]:
            msg += self.locations[loc].user_input
            msg += ", then "
        msg += "and then finally "
        msg += self.locations[_route[-1]].user_input
        
        # Set up the message to tell the user which route is best
        self.route_box = tk.Toplevel(master=self.root)
        self.route_box.title("Best Route")

        # Configure widgets in message box
        tk.Message(self.route_box, text=msg).pack()
        tk.Button(
            self.route_box,
            text="OK",
            command=lambda:self.route_box.destroy()
            ).pack()

if __name__ == "__main__":
    root = tk.Tk()
    RoutePlanGUI(root)
