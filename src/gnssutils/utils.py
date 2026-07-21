# ipp_utils.py
# Utilities for calculating ionospheric pierce points

import numpy as np
import datetime as dt
import pymap3d as pm


def gps2utc(wnc, tow):
    # THIS FUNCTION DOES NOT HANDLE LEAP SECONDS CORRECTLY
    # There is a way to do this with spacepy, but it is extremely slow and will sometimes crash because it runs out of memory
    # Until this is solved, output will be off by ~18 seconds
    gps_tstmp = (np.array(wnc)*7*24*60*60*1000+np.array(tow))
    gps_epoch = np.datetime64('1980-01-06').astype('datetime64[ms]').astype(int)
    time = (gps_epoch + gps_tstmp).astype('datetime64[ms]')
    return time


def calc_ipp(site, satellite, satcoords='azel', height=300.):
    '''
    Calculate the ionospheric pierce point (IPP) based on receiver and satellite coordinates.
    Satellite coordinates can be provided as azel, ecef, or geodetic.

    Input
    -----
    site: ground receiver site coordinates as a 3 element list/array [geodetic latitude, geodetic longitude, geodetic altitude]
    satellite: position of the GNSS satellite in one of three coordinates
        - azimuth/elevation: [azimuth, elevation] in degrees (note that only two coordinates are required for this option
        - Earth-Cenetered Earth Fixed: [X, Y, Z] in meters
        - geodetic: [geodetic latitude, geodetic longitude geodetic altitude] - altitude in meters
    satcoords: keyword to indicate what coordinates the satellite postion is provided  in (default='azel')
        - azimuth/elevation: 'azel'
        - Earth-Cenered Earth-Fixed: 'ecef'
        - geodetic: 'geo'

    Returns
    -------
    lat: geodetic latitude of the IPP
    lon: geodetic longitude of the IPP
    '''

    # Get site coordinate in ECEF
    lat0, lon0, alt0 = site
    x, y, z = pm.geodetic2ecef(lat0, lon0, alt0)

    # Calcualte vector from site to satellite
    #   Note that this does not actually have to be normalized
    if satcoords == 'azel':
        e, n, u = pm.aer2enu(*satellite, 1.)
        vx, vy, vz = pm.enu2uvw(e, n, u, lat0, lon0)

    elif satcoords == 'ecef':
        vx = satellite[0] - x
        vy = satellite[1] - y
        vz = satellite[2] - z

    elif satcoords == 'geo':
        sx, sy, sz = pm.geodetic2ecef(*satellite)
        vx = sx - x
        vy = sy - y
        vz = sz - z

    else:
        raise ValueError(f'satcoords={satcoords} is not a valid coordinate option')

    earth = pm.Ellipsoid.from_name('wgs84')
    a2 = (earth.semimajor_axis + height*1000.)**2
    b2 = (earth.semimajor_axis + height*1000.)**2
    c2 = (earth.semiminor_axis + height*1000.)**2

    A = vx**2/a2 + vy**2/b2 + vz**2/c2
    B = x*vx/a2 + y*vy/b2 + z*vz/c2
    C = x**2/a2 + y**2/b2 + z**2/c2 -1

    alpha = (np.sqrt(B**2-A*C)-B)/A

    lat, lon, alt = pm.ecef2geodetic(x + alpha*vx, y + alpha*vy, z + alpha*vz)

    return lat, lon



# Add method for converting between PRN, SVN, NORAD_ID, COSPAR_ID, ect
# Most of the reference tables to do this are contained within this file, which is presumably updated as needed
# https://files.igs.org/pub/station/general/igs_satellite_metadata.snx?_gl=1*1mnhzza*_ga*MTE5MzExNzMyOC4xNzQwNDU4ODE0*_ga_Z5RH7R682C*MTc0MDQ1ODgxNC4xLjEuMTc0MDQ2MDA5OS40NC4wLjA.&_ga=2.10007349.1451599704.1740458815-1193117328.1740458814
# This is the IGS satellite metadata file, which can be downloaded from this website:
# https://igs.org/mgex/metadata/
# This method would either have to pull from the file over the web or keep a local downloaded version that woudl periodically have to be updated
# Updates should only be necessary when satellites are reassigned or swaped out of the GPS constellation, which should only happen once every couple of years




#def gaussiran_method(site, az, el, height=300.):
#
#    lat0, lon0, alt0 = site
#    phi0 = lat0*np.pi/180.
#    lam0 = lon0*np.pi/180.
#    az = az*np.pi/180.
#    el = el*np.pi/180.
#    RE = 6371.
#
#    p = np.pi/2-el-np.arcsin(RE*np.cos(el)/(RE+height))
#
#    phi = np.arcsin(np.sin(phi0)*np.cos(p)+np.cos(phi0)*np.sin(p)*np.cos(az))
#    lam = lam0 + np.arcsin(np.sin(p)*np.sin(az)/np.cos(phi0))
#
#    return phi*180./np.pi, lam*180./np.pi
#
#
#
#def parse_sp3(filename):
#    sat_ephem = {}
#    time = []
#
#    with open(filename,'r') as sp3file:
#        lines = sp3file.readlines()
#        num_sat = int(lines[2].split()[1])
#
#        for s in range(num_sat):
#            sat_ephem['{:02}'.format(s+1)] = []
#
#        for j in range(22,len(lines)-1,num_sat+1):
#
#            t = lines[j][2:-6]
#            time.append(dt.datetime.strptime(t, ' %Y %m %d %H %M %S.%f'))
#
#            for i in range(num_sat):
#                s = lines[j+i+1].split()
#                sat_ephem[s[0][2:]].append([float(s[1]),float(s[2]),float(s[3])])
#
#    for sat in sat_ephem:
#        sat_ephem[sat] = np.array(sat_ephem[sat]).T*1000.
#
#    return sat_ephem, np.array(time)
