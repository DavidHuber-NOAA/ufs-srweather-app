#
# **********************************************************************
#
# File name: get_rect_grid_corners.ncl
# Author: Gerard Ketefian
#
# Description:
# ^^^^^^^^^^^
# This function returns the coordinates of the four corners of a logi-
# cally rectangular grid whose cell vertex coordinates are specified by
# the 2-D arrays x_verts and y_verts.  We let x and y refere to the co-
# ordinates in the two directions.  If the x coordinate represents lon-
# gitude (which is the case if the logical variable x_is_longitude is
# set to True), this function ensures that the longitudes of the grid
# corners are within the longitude range (-180 deg, 180 deg) or (-pi,
# pi).
#
# **********************************************************************
#

import numpy as np

def get_rect_grid_corners(
      x_verts, y_verts,x_units,y_units,x_is_longitude,opts):

#
# **********************************************************************
#
# Get the dimensions of the coordinate arrays and check that they are
# identical.
#
# **********************************************************************
#
  dims_x = x_verts.shape
  dims_y = y_verts.shape

  if not np.array_equal(dims_x, dims_y):
    dims_x_str = ', '.join(str(x) for x in dims_x)
    dims_y_str = ', '.join(str(y) for y in dims_y)
    print("")
    print("The dimensions of the x-coordinate array do not match those of the y-coordinate array:")
    print(f"  dims_x = ({dims_x_str})")
    print(f"dims_y = ({dims_y_str})")
    raise ValueError()
#
# **********************************************************************
#
# For convenience, set nx and ny to the number of grid cells in the x
# and y directions, respectively.  Note that since we assume that the
# specified coordinates are those of the cell vertices, the number of
# grid cells in each direction is one less than the dimensions of the
# specified arrays.
#
# **********************************************************************
#
  nx = dims_x[1] - 1
  ny = dims_x[0] - 1
#
# **********************************************************************
#
# Find the coordinates of the corners of the grid.
#
# **********************************************************************
#
  corner_i_inds = [ 0, nx, nx, 0 ]
  corner_j_inds = [ 0, 0, ny, ny ]
  num_corners = 4
  x_corners = np.zeros( num_corners )
  y_corners = np.zeros( num_corners )

  for c in range(num_corners):
    x_corners[c] = x_verts[corner_j_inds[c], corner_i_inds[c]]
    y_corners[c] = y_verts[corner_j_inds[c], corner_i_inds[c]]
#
# **********************************************************************
#
# If the x coordinate represents longitude (in which case the logical
# variable x_is_longitude will be True), ensure that the longitudes of
# the corners determined above are all within the valid longitude range.
#
# **********************************************************************
#
  if (x_is_longitude):

    valid_lon_units = [ "deg", "degs", "rad", "rads" ]

    if x_units in valid_lon_units:

      if (x_units == "deg") or (x_units == "degs"):
        max_lon_allowed = 180.0
      elif strcmp_exact(x_units, "rad") or (x_units == "rads"):
        max_lon_allowed = pi_geom
      else:
        print("")
        print("Don't know what the maximum allowed value (max_lon_allowed) should be ")
        print("for these units:")
        print(f"  x_units = '{x_units}'")
        print("Stopping.")

    else:

      valid_vals = ", ".join([f'"{unit}"' for unit in valid_lon_units])

      print("")
      print("Unknown units specified for the longitude (x):")
      print(f'  x_units = "x_units"')
      print("Valid values are:")
      print("   " + valid_vals)
      print("Stopping.")

    lon_range = 2.0*max_lon_allowed

    for c in range(num_corners):
      if x_corners[c] > max_lon_allowed:
        x_corners[c] = x_corners[c] - lon_range

#
# **********************************************************************
#
# Create a (multiline) string containing the coordinates of the grid
# corners.  Then, if opts@verbose exists and is set to True, print this
# string to screen.
#
# **********************************************************************
#

  fmt_str = "%7.2f"
  msg = "\nThe specified grid's corner coordinates are:"
  for c in range(num_corners):
    x_str = f"{x_corners[c]:7.2f}"
    y_str = f"{y_corners[c]:7.2f}"
    msg += "\n"
    msg += f"  Corner {c+1}:  x = {x_str} {x_units};  y = {y_str} {y_units}"

#
# **********************************************************************
#
# Return results as attributes of the logical variable corner_info.
#
# **********************************************************************
#

  corner_info = {"x_corners" : x_corners,
    "y_corners" : y_corners,
    "msg" : msg}

  return(corner_info)
