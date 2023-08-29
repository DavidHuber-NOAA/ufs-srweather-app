#
# **********************************************************************
#
# File name: get_rect_grid_bdy.ncl
# Author: Gerard Ketefian
#
# Description:
# ^^^^^^^^^^^
# This function returns two 1-D arrays containing the coordinates (say x
# and y) of the points along the boundary of the logically rectangular 
# grid specified by the given arrays x_coords and y_coords.
#
# If repeat_last_point is set to True, the first point on the boundary 
# is repeated at the end.  This is done so that if a polyline object is
# used to plot the grid boundary, the boundary closes on itself.
#
# If index_order is set to "ij", then we assume the first index in the
# input arrays x_coords and y_coords is the one in the x direction (i.e.
# the i-index) and the second index is the one in the y direction (i.e.
# the j-index).  If index_order is set to "ji", we assume the opposite.
# Note that normal practice in NCL is to use "ji" index ordering.  Thus,
# if index_order is set to "ij", we transpose (the local copies) of the 
# input arrays to obtain "ji" indexing.
#
# **********************************************************************
#

import numpy as np

def get_rect_grid_bdy(
   x_coords, y_coords, repeat_last_point, index_order):

#
# **********************************************************************
#
# Check that index_order has a valid value.
#
# **********************************************************************
#

  if (not index_order == "ij" and not index_order == "ji"):
    msg = (f""
           f"The input argument index_order must be set to either "
           f"\"ji\" or \"ij\":\n"
           f"  index_order = \"{index_order}\"\n")
    raise ValueError(msg)

#
# **********************************************************************
#
# The code below assumes that the coordinate arrays use the index order
# (j,i) [as opposed to (i,j)].  Thus, if the given arrays use the order
# (i,j), transpose them to get back to (j,i) order.
#
# **********************************************************************
#

  x = x_coords
  y = y_coords
  if index_order == "ij":
    x = np.transpose(x)
    y = np.transpose(y)

#
# **********************************************************************
#
# Get the dimensions of the coordinate arrays and check that they are 
# identical.
#
# **********************************************************************
#

  dims_x = np.asarray(x).shape
  dims_y = np.asarray(y).shape

  if not (np.array_equal(dims_x, dims_y)):
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
# For convenience, set nx and ny to the number of grid points in the x
# and y directions, respectively.
#
# **********************************************************************
#

  nx = dims_x[1]
  ny = dims_x[0]

#
# **********************************************************************
#
# Create 1-D arrays to hold the x and y coordinates of the boundary 
# points of the grid.  Note that initially, these arrays will contain 
# only one element; more elements will be appended later below.
#
# **********************************************************************
#

  x_bdy = np.zeros(1)
  y_bdy = np.zeros(1)

#
# **********************************************************************
#
# Copy in the coordinates of the point at (i,j) = (0,0).
#
# **********************************************************************
#

  i = 0
  j = 0
  x_bdy[0] = x[j,i]
  y_bdy[0] = y[j,i]

#
# **********************************************************************
#
# Append the coordinates of the points along the "southern" boundary 
# (j = 0).
#
# **********************************************************************
#

  j = 0
  x_bdy = np.append(x_bdy,x[j,1:])
  y_bdy = np.append(y_bdy,y[j,1:])

#
# **********************************************************************
#
# Append the coordinates of the points along the "eastern" boundary 
# (i = nx).
#
# **********************************************************************
#

  i = nx - 1
  x_bdy = np.append(x_bdy,x[1:,i])
  y_bdy = np.append(y_bdy,y[1:,i])

#
# **********************************************************************
#
# Append the coordinates of the points along the "northern" boundary 
# (j = ny).  Note that in specifying the i-index range [i.e. (nx-1:0)], 
# we do not specify a negative stride, i.e. we do not use (nx-1:0:-1),
# because in NCL, the order of the elements is automatically reversed if
# the starting index is larger than the ending index.
#
# **********************************************************************
#

  j = ny - 1
  x_bdy = np.append(x_bdy, x[j,nx-2::-1])
  y_bdy = np.append(y_bdy, y[j,nx-2::-1])

#
# **********************************************************************
#
# Append the coordinates of the points along the "western" boundary 
# (i = 0).  Note that in specifying the j-index range [i.e. (ny-1:1)],
# we do not specify a negative stride, i.e. we do not use (ny-1:1:-1),
# because in NCL, the order of the elements is automatically reversed if
# the starting index is larger than the ending index.
#
# **********************************************************************
#

  i = 0
  x_bdy = np.append(x_bdy, x[ny-2:1,i])
  y_bdy = np.append(y_bdy, y[ny-2:1,i])

#
# **********************************************************************
#
# If repeat_last_point is set to True, repeat the first point at the 
# end.
#
# **********************************************************************
#

  if repeat_last_point:
    x_bdy = np.append(x_bdy, x_bdy[0])
    y_bdy = np.append(y_bdy, y_bdy[0])

#
# **********************************************************************
#
# Return results as attributes of the logical variable grid_info.
#
# **********************************************************************
#

  grid_info = {"x_bdy" : x_bdy,
               "y_bdy" : y_bdy}

  return(grid_info)
