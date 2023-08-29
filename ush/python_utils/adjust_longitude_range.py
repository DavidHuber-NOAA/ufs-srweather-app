# **********************************************************************
#
# File name: adjust_longitude_range.ncl
# Author: Gerard Ketefian
#
# Description:
# ^^^^^^^^^^^
# This function adjust the given array of longitude values such that all
# values in the returned array lon_out are in the range 
# 
#   -lon_min <= lon_out < lon_max,
#
# Here, lon_min is the given minimum longitude value and lon_max is ei-
# ther lon_min plus 360 deg (if the units of lon and lon_min are in de-
# grees) or lon_min plus 2*pi (if the units are in radians).  lon and 
# lon_min must have the same units (degrees or radians).  These units
# are specified by the input string degs_or_rads.  This string should be
# set either to "degs" for degrees or to "rads" for radians.
#                                                                      *
# **********************************************************************

import numpy as np

def adjust_longitude_range(lon, lon_min, degs_or_rads):

#
# **********************************************************************
#                                                                      *
# Set the size of the longitude domain.  This is either 360 deg (if the
# given longitudes are in degrees) or 2*pi (if the given longitudes are
# in radians).
#                                                                      *
# **********************************************************************
#
  if degs_or_rads == "degs":
    lon_domain_size = 360.0
  elif degs_or_rads == "rads":
    pi = 4.0*atan(1.0)
    lon_domain_size = 2.0*pi
  else:
    print("")
    print("Disallowed value specified for input argument degs_or_rads:")
    print("  degs_or_rads = \"" + degs_or_rads + "\"")
    print("Allowed values are \"degs\" and \"rads\".")
    print("Stopping.")
    raise ValueError
#
# **********************************************************************
#                                                                      *
# Add the longitude domain size calculated above to the given minimum 
# longitude to obtain the maximum longitude.
#                                                                      *
# **********************************************************************
#
  lon_max = lon_min + lon_domain_size
#
# **********************************************************************
#                                                                      *
# Create a new longitude array (lon_out) that will serve as the output
# of this function.  Then adjust longitudes to ensure that all elements
# of lon_out are in the range lon_min <= lon_out < lon_max.
#                                                                      *
# **********************************************************************
#
  lon_out = np.asarray(lon)
  lon_out = np.where(lon_out < lon_min, lon_out + lon_domain_size, lon_out)
  lon_out = np.where(lon_out > lon_max, lon_out - lon_domain_size, lon_out)
#
# **********************************************************************
#                                                                      *
# Return the adjusted longitude array lon_out.
#                                                                      *
# **********************************************************************
#
  return(lon_out)
