'''All of the functions needed to standardise the user's input

'''
import math


def grid_ref_to_northing_easting(coord, datum):
    '''Convert a Grid Reference into a Northing and Easting, and return as a string

    Parameters:
    coord              The Grid Reference
    datum              The datum from which to convert
    '''
    # Access data from database
    with open(datum, "r") as file:
        db = [line.split(",") for line in file.readlines()]
        for line in db:
            if line[0] == coord[:2]:
                # Offset the values
                northing = int(line[1])*1000
                easting  = int(line[2])*1000

    # Number component of the Grid Reference
    grid_ref = coord[2:]

    # Calculate the east and north postion of the point
    easting  += int(grid_ref[:int(len(grid_ref)/2)])*10**(5-int(len(grid_ref)/2))
    northing += int(grid_ref[int(len(grid_ref)/2):])*10**(5-int(len(grid_ref)/2))

    return str(easting)+","+str(northing)

def cartesian_shift(x, y, z, datum):
    '''Transform Cartesian coordinates to standard datum and return as list

    Parameters:
    x                  Intial X coordinate
    y                  Intial Y coordinate
    z                  Intial Z coordinate
    datum              The datum from which to convert
    '''

    # Access data from database
    with open(datum+".txt", "r") as file:
        datum_data = [line.split(",") for line in file.readlines()][0]

    # Load and configure database data
    dx = float(datum_data[7])
    dy = float(datum_data[8])
    dz = float(datum_data[9])
    ds = float(datum_data[10])*10**-6
    rx = float(datum_data[11])*math.pi/(180*3600)
    ry = float(datum_data[12])*math.pi/(180*3600)
    rz = float(datum_data[13])*math.pi/(180*3600)

    # Perform cartesian shift based off datum
    fx = dx+(1+ds)*x-rz*y+ry*z
    fy = dy+(1+ds)*y+rz*x-rx*z
    fz = dz+(1+ds)*z-ry*x+rx*y

    return[fx,fy,fz]

def cartesian_to_lat_lon(x, y, z, datum):
    '''Convert Cartesian coordinates to Latituide and Longitudie and reutrn as list

    Parameters:
    x                  Intial X coordinate
    y                  Intial Y coordinate
    z                  Intial Z coordinate
    datum              The datum from which to convert
    '''

    # Access data from database
    with open(datum+".txt", "r") as file:
            datum_data = [line.split(",") for line in file.readlines()][0]

    # Load and configure database data
    semi_major = float(datum_data[0])
    semi_minor = float(datum_data[1])
    e2 = 1-(semi_minor**2)/(semi_major**2)
    p = math.sqrt(x**2+y**2)

    # Set intial values for latituide calculations
    lat  = math.atan2(z, p*(1-e2))
    lat1 = 2*math.pi

    # Perform an interative calculation to get an approximate answer
    while math.fabs(lat-lat1)>= 0.00000000000000001: # Very high level of accuracy
        lat1 = lat
        Rn  = semi_major/math.sqrt(1-e2*math.sin(lat)**2)
        lat = math.atan2(z+e2*Rn*math.sin(lat), p)

    lon = math.atan2(y,x)

    return[lat*180/math.pi, lon*180/math.pi]

def degrees_min_to_degrees_dec(deg_min):
    '''Transform Degrees in minuets to Degrees in decimal and return a string

    Parameters:
    deg_min            The Degrees in minuets
    '''
    # Calculate each componet of the Latitude
    degree_lat = int(deg_min[0:3])
    min_lat = int(deg_min[4:6])
    (1/math.cos(lat)) = int(deg_min[7:9])

    # Calculate each componet of the Longitude
    degree_lon = int(deg_min[-11:-8])
    min_lon = int(deg_min[-7:-5 ])
    sec_lon = int(deg_min[-4:-2 ])

    # Combine all componets together
    degree_lat += min_lat*(1/60)+(1/math.cos(lat))*(1/3600)
    degree_lon += min_lon*(1/60)+sec_lon*(1/3600)

    lat_lon = str(degree_lat)+","+str(degree_lon)

    return lat_lon


def lat_lon_to_cartesian(lat, lon, lat2, datum):
    '''Convert Latitude and Longitude to Cartesian and return a list

    Parameters:
    lat                The Latitude from which to convert
    lon                The Longitude from which to convert 
    lat2               The offset produced by the Latitude
    datum              The datum from which to convert
    '''

    # Access data from database
    with open(datum+".txt", "r") as file:
        datum_data = [line.split(",") for line in file.readlines()][0]

    # Load and configure database data
    semi_major = float(datum_data[0])
    semi_minor = float(datum_data[1])
    SF = float(datum_data[2])
    e2 = 1 - (semi_minor**2)/(semi_major**2)
    Rn = semi_major*SF/math.sqrt(1-e2*math.sin(lat2)**2)
    
    # Convert Latitude and Longitude to Cartesian using the datum
    x = (Rn/SF)*math.cos(lat)*math.cos(lon)
    y = (Rn/SF)*math.cos(lat)*math.sin(lon)
    z = ((1-e2)*(Rn/SF))*math.sin(lat)

    return[x, y, z]

def NE_to_local_lat_lon(easting, northing, datum):
    '''Convert Northing and Easting to a locally based Latituide and Longitude
       and return a list with both and the required offset

       Parameters:
       easting            The Easting from which to convert
       northing           The Northing from which ton convert
       datum              The datum from which to convert
       '''

    # Access data from database
    with open(datum+".txt", "r") as file:
        datum_data = [line.split(",") for line in file.readlines()][0]

    # Load and configure database data
    semi_major = float(datum_data[0])
    semi_minor = float(datum_data[1])
    SF  = float(datum_data[2])
    la = math.radians(float(datum_data[3]))
    lo = math.radians(float(datum_data[4]))
    north_origin  = float(datum_data[5])
    east_origin   = float(datum_data[6])
    e2 = 1-(semi_minor**2)/(semi_major**2)
    n  = (semi_major-semi_minor)/(semi_major+semi_minor)

    # Intial points
    lat = la
    meridian = 0

    # Perform an interative calculation to get an approximate answer
    while (northing-north_origin-meridian) >= 0.00000000000000001: # Very high level of accuracy
        lat = (northing-north_origin-meridian)/(semi_major*SF) + lat
        M1  = (1+n+(5/4)*n**2+(5/4)*n**3)*(lat-la)
        M2  = (3*n+3*n**2+(21./8)*n**3)*math.sin(lat-la)*math.cos(lat+la)
        M3  = (
            (
            (15/8)
            *n**2
            +(15/8)
            *n**3
            )
            *math.sin(2*(lat-la))
            *math.cos(2*(lat+la))
            )
        M4  = (35/24)*n**3*math.sin(3*(lat-la))*math.cos(3*(lat+la))

        meridian = semi_minor*SF*(M1-M2+M3-M4)

    # Calculate location values
    Rn   = semi_major*SF/math.sqrt(1-e2*math.sin(lat)**2)
    Rm   = semi_major*SF*(1-e2)*(1-e2*math.sin(lat)**2)**(-1.5)
    eta2 = Rn/Rm-1

    # Calculate intermedate values
    interm_1 = math.tan(lat)/(2*Rm*Rn)
    interm_2 = (
        math.tan(lat)
        /(24*Rm*Rn**3)
        *(
        5
        +3*math.tan(lat)**2
        +eta2
        -9*math.tan(lat)**2
        *eta2
        )
        )
    interm_3 = (
        math.tan(lat)
        /(720*Rm*Rn**5)
        *(
        61
        +90*math.tan(lat)**2
        +45*math.tan(lat)**4
        )
        )
    interm_4 = (1/math.cos(lat))/Rn
    interm_5 = (1/math.cos(lat))/(6*Rn**3)*(Rn/Rm+2*math.tan(lat)**2)
    interm_6 = (
        (1/math.cos(lat))
        /(120*Rn**5)
        *(
        5
        +28*math.tan(lat)**2
        +24*math.tan(lat)**4)
        )
    interm_7 = (
        (1/math.cos(lat))
        /(5040*Rn**7)
        *(
        61
        +662*math.tan(lat)**2
        +1320*math.tan(lat)**4
        +720*math.tan(lat)**6
        )
        )

    # Change in easting
    deltaE = easting-east_origin

    # The local Latitude and Longitude
    local_lat = lat-interm_1*deltaE**2+interm_2*deltaE**4-interm_3*deltaE**6
    local_lon = lo+interm_4*deltaE-interm_5*deltaE**3+interm_6*deltaE**5-interm_7*deltaE**7


    return [local_lat, local_lon, lat]



def northing_easting_to_degrees(no_ea, datum):
    '''Convert a Northing Easting to Degrees and return as a string

    Parameters:
    no_ea              The Northing and Easting to be converted
    datum              The datum from which to convert
    '''
    # Split the input into Easting and Northing
    E, N = no_ea.split(",")

    # Pass value to chain of functions to calualte Latitude and Longitude
    local_ll = NE_to_local_lat_lon(int(E), int(N), datum)
    local_cart = lat_lon_to_cartesian(
        local_ll[0], local_ll[1], local_ll[2], datum
        )
    global_cart = cartesian_shift(
        local_cart[0], local_cart[1], local_cart[2], datum
        )
    global_ll = cartesian_to_lat_lon(
        global_cart[0], global_cart[1], global_cart[2], "WGS84"
        )
    string = str(global_ll[0])+","+str(global_ll[1])
    return string


def map_ref_convert(grid_ref, datum):
    '''Convert a Grid Reference to Degrees and return as single value

    Parameters:
    grid_ref           The Grid Reference from which to convert
    datum              The datum from which to convert
    '''
    no_ea = grid_ref_to_northing_easting(grid_ref.lower().replace(" ", ""), datum+".txt")
    return northing_easting_to_degrees(no_ea, datum)
