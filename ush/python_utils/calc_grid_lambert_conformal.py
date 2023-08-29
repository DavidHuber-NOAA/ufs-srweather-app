#
# **********************************************************************
#
# Calculate the write grid parameters for a lambert conformal projection
# Inputs:
# lon_ctr_native: Native grid center longitude in degrees
# lat_ctr_native: Native grid center latitude in degrees
# lon_tile_corners_face_midpts_native: Native grid longitudes (degrees)
#     of the corners and center points of the the perimiter (len 8)
# lat_tile_corners_face_midpts_native: Native grid latitudes (degrees)
#     of the corners and center points of the the perimiter (len 8)
# dx_native: Native grid dx (meters)
# dy_native: Native grid dy (meters)
#
# **********************************************************************
#
def calc_grid_lambert_conformal( 
      lon_ctr_native, lat_ctr_native,
      lon_tile_corners_face_midpts_native,
      lat_tile_corners_face_midpts_native,
      dx_native, dy_native):

  import pyproj
  import numpy as np

# **********************************************************************
#
# Calculate the Lambert coordinates of the southwest corner of the na-
# tive grid from its spherical coordinates.
#
# **********************************************************************
#

  lat0 = lat_ctr_native
  lat1 = lat_ctr_native
  lat2 = lat_ctr_native
  lat_ctr = lat_ctr_native
  lon0 = lon_ctr_native
  lon_ctr = lon_ctr_native

  lcc_def = (f"+proj=lcc +lat_0={lat0} +lon_0={lon0} "
             f"lat_1={lat1} +lat_2={lat2} +y_0=0 "
             f"+datum=WGS84 +R=6371000 +units=m +no_defs")

  lcc_proj=pyproj.Proj(lcc_def)

  x_tile_corners_face_midpts_native = np.zeros(
      len(lon_tile_corners_face_midpts_native))
  y_tile_corners_face_midpts_native = np.zeros(
      len(lon_tile_corners_face_midpts_native))
  for i in range(len(lon_tile_corners_face_midpts_native)):
    (x_tile_corners_face_midpts_native[i], y_tile_corners_face_midpts_native[i]) = (
         lcc_proj(lon_tile_corners_face_midpts_native[i],
                  lat_tile_corners_face_midpts_native[i]))

  i = 0
  x_SW_native = x_tile_corners_face_midpts_native[i]
  y_SW_native = y_tile_corners_face_midpts_native[i]

  i = i + 1
  x_S_native = x_tile_corners_face_midpts_native[i]
  y_S_native = y_tile_corners_face_midpts_native[i]

  i = i + 1
  x_SE_native = x_tile_corners_face_midpts_native[i]
  y_SE_native = y_tile_corners_face_midpts_native[i]

  i = i + 1
  x_E_native = x_tile_corners_face_midpts_native[i]
  y_E_native = y_tile_corners_face_midpts_native[i]
  
  i = i + 1
  x_NE_native = x_tile_corners_face_midpts_native[i]
  y_NE_native = y_tile_corners_face_midpts_native[i]

  i = i + 1
  x_N_native = x_tile_corners_face_midpts_native[i]
  y_N_native = y_tile_corners_face_midpts_native[i]

  i = i + 1
  x_NW_native = x_tile_corners_face_midpts_native[i]
  y_NW_native = y_tile_corners_face_midpts_native[i]

  i = i + 1
  x_W_native = x_tile_corners_face_midpts_native[i]
  y_W_native = y_tile_corners_face_midpts_native[i]
#
# **********************************************************************
#
#
#
# **********************************************************************
#
  dx = dx_native 
  dy = dy_native 
  num_margin_cells = 1
#
# **********************************************************************
#
# Reduce the extent of the write-component grid in both the positive and
# negative x directions until the latitude of the center of the west 
# face of the write-component grid is greater than that of the native 
# grid, and the latitude of the center of the east face of the write-
# component grid is less than that of the native grid (i.e. the write-
# component grid lies within the native grid in the x direction).  Then,
# as an extra safety measure, reduce each of these extents by a further
# nc_reduce_extra_max cells of size dx.
#
# **********************************************************************
#
  x_W_native_max = max([x_SW_native, x_W_native, x_NW_native])
  x_E_native_min = min([x_SE_native, x_E_native, x_NE_native])

  x_W = x_W_native_max + num_margin_cells*dx
  x_E = x_E_native_min - num_margin_cells*dx

  Lx = x_E - x_W
  Lx_ovr_dx = Lx/dx
  nx = int(Lx_ovr_dx)
  frac_x = Lx_ovr_dx - nx
  x_adj = (0.5*frac_x)*dx
  x_W = x_W + x_adj
  x_E = x_E - x_adj
#
# **********************************************************************
#
#
#
# **********************************************************************
#
  y_S_native_max = max([y_SW_native, y_S_native, y_SE_native])
  y_N_native_min = min([y_NW_native, y_N_native, y_NE_native])

  y_S = y_S_native_max + num_margin_cells*dy
  y_N = y_N_native_min - num_margin_cells*dy

  y_S = -min([abs(y_S), abs(y_N)])
  y_N = -y_S

  Ly = y_N - y_S
  Ly_ovr_dy = Ly/dy
  ny = int(Ly_ovr_dy)
  frac_y = Ly_ovr_dy - ny
  y_adj = (0.5*frac_y)*dy
  y_S = y_S + y_adj
  y_N = y_N - y_adj
#
# **********************************************************************
#
# Calculate the spherical coordinates of the southwest corner of the 
# native grid from its Lambert coordinates.  
#
# Note that the coordinates that the write-component takes as input are 
# those of the center of the grid cell at the lower-left corner of the 
# grid.  However, the Lambert coordinates (x_W, y_S) caluclated above 
# are those of the lower-left vertex (not center) of that cell.  Thus, 
# we first add half a grid distance in the x and y directions to the 
# Lambert coordinates of the vertex to obtain the Lambert coordinates of 
# the cell center.  We then convert the result to spherical coordinates.
#
# **********************************************************************
#
  xctr_ll_cell = x_W + 0.5*dx
  yctr_ll_cell = y_S + 0.5*dy

  (lonctr_ll_cell, latctr_ll_cell) = lcc_proj(
        xctr_ll_cell, yctr_ll_cell, inverse=True)
#
# **********************************************************************
#
# Create a string array containing the names of the Lambert conformal
# output grid parameters that appear in the NEMS model_configure file.
#
# **********************************************************************
#
  out_grid_params = { 
        "output_grid" : "lambert_conformal", 
        "cen_lon" : lon_ctr,
        "cen_lat" : lat_ctr,
        "stdlat1" : lat1,
        "stdlat2" : lat2,
        "nx" : nx,
        "ny" : ny,
        "lon1" : lonctr_ll_cell,
        "lat1" : latctr_ll_cell,
        "dx" : dx,
        "dy" : dy}

  for param, val in out_grid_params.items():
     print(f"{param}: {val}")

  return out_grid_params
