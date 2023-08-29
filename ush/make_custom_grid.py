#! /usr/bin/env python
'''
This module reads in a custom horizontal and/or vertical grid and writes out a
custom .yaml with the horizontal grid components and .txt file with the vertical
grid specification.
'''

from python_utils import (load_config_file, read_FV3LAM_grid_native,
      calc_grid_lambert_conformal)
from set_gridparams_ESGgrid import set_gridparams_ESGgrid
from set_gridparams_GFDLgrid import set_gridparams_GFDLgrid
from set_namelist import set_namelist
from pathlib import Path
from netCDF4 import Dataset
import sys
import os
import pyproj
import shutil

def HorizGrid(config_fn, stmp):
   '''
   Requires a custom model config.yaml file with either ESG or GFDL grid definitions.
   Also requires a workspace to generate temporary files, specified by stmp.
   
   For ESG grids, the following must be defined:
   ESGgrid_LON_CTR
   ESGgrid_LAT_CTR
   ESGgrid_DELX
   ESGgrid_DELY
   ESGgrid_NX
   ESGgrid_NY
   ESGgrid_WIDE_HALO_WIDTH
   ESGgrid_PAZI

   For GFDL grids, be sure to define the following:
   GFDLgrid_LAT_T6_CTR
   GFDLgrid_NUM_CELLS
   GFDLgrid_STRETCH_FAC
   GFDLgrid_REFINE_RATIO
   GFDLgrid_ISTART_OF_RGNL_DOM_ON_T6G
   GFDLgrid_IEND_OF_RGNL_DOM_ON_T6G
   GFDLgrid_JSTART_OF_RGNL_DOM_ON_T6G
   GFDLgrid_JEND_OF_RGNL_DOM_ON_T6G
   GFDLgrid_USE_NUM_CELLS_IN_FILENAMES

   In both cases, WRTCMP_output_grid must also be set to either
      "lambert_conformal" or "rotated_latlon"
   '''

   expt_config = load_config_file(config_fn)

   # Create the working directory
   work_path = os.path.join(stmp, "custom_grid")

   # Save the CWD
   cwd = os.getcwd()

   # Get the exec directory and verify it exists
   exec_dir=os.path.dirname(os.path.join(cwd,"..","exec","."))
   if not os.path.isdir(exec_dir):
      raise OSError(f"exec directory does not exist!"
         f"Please build the workflow and ensure you are running from ush.")

   try:
      Path(work_path).mkdir(parents=True, exist_ok=True)
   except:
      raise OSError("Cannot create the directory ", work_path)

   constants = load_config_file("constants.yaml")
   constants = constants['constants']
   grid=expt_config["task_make_grid"]
   grid_type = expt_config["workflow"].get("GRID_GEN_METHOD")
   write_grid = expt_config["task_run_fcst"].get("WRTCMP_output_grid")

   if not(write_grid == "lambert_conformal" or write_grid == "rotated_latlon"):
      if write_grid is None:
         raise KeyError("WRTCMP_output_grid not specified in the config file!")

      raise KeyError("Invalid WRTCMP_output_grid specified: " + write_grid)

   # Check for grid types and required variables

   if grid_type is None:
      raise KeyError("No grid type detected in the configuration file " + config_fn)

   elif grid_type == "ESGgrid":
      grid_keys = ["ESGgrid_LON_CTR", "ESGgrid_LAT_CTR", "ESGgrid_DELX",
                    "ESGgrid_DELY", "ESGgrid_NX", "ESGgrid_NY",
                    "ESGgrid_WIDE_HALO_WIDTH", "ESGgrid_PAZI"]
      try:
         grid_info = {grid_key:grid[grid_key] for grid_key in grid_keys}
      except KeyError:
         raise KeyError("At least one ESGgrid parameter is not set in " + config_fn)

      # Run the make_grid application.
      # Start by creating the namelist.

      grid_params = set_gridparams_ESGgrid(grid_info["ESGgrid_LON_CTR"],
            grid_info["ESGgrid_LAT_CTR"],
            grid_info["ESGgrid_NX"],
            grid_info["ESGgrid_NY"],
            grid_info["ESGgrid_WIDE_HALO_WIDTH"],
            grid_info["ESGgrid_DELX"],
            grid_info["ESGgrid_DELY"],
            grid_info["ESGgrid_PAZI"],
            constants)

      # Create a namelists to run the make_grid jobs
      settings = (f"'regional_grid_nml': {{\n"
         f"'plon': {grid_params['LON_CTR']},\n"
         f"'plat': {grid_params['LAT_CTR']},\n"
         f"'delx': {grid_params['DEL_ANGLE_X_SG']},\n"
         f"'dely': {grid_params['DEL_ANGLE_Y_SG']},\n"
         f"'lx': {grid_params['NEG_NX_OF_DOM_WITH_WIDE_HALO']},\n"
         f"'ly': {grid_params['NEG_NY_OF_DOM_WITH_WIDE_HALO']},\n"
         f"'pazi': {grid_params['PAZI']},"
         f"}}")

      os.system("./set_namelist.py -q -u \"" + settings + "\" -o " + 
            os.path.join(work_path, "regional_grid.nml"))

      NH4 = constants["NH4"]
      NHW = grid_info["ESGgrid_WIDE_HALO_WIDTH"]

      # Copy the executables into the working directory
      ex_list = ["regional_esg_grid", "global_equiv_resol", "shave"]
      for exe in ex_list:
         shutil.copy2(os.path.join(exec_dir,exe),os.path.join(work_path, exe))

      # Change directories to the working directory
      os.chdir(work_path)

      # Run the regional grid creation application
      ret_val = os.system("time ./regional_esg_grid " + os.path.join(work_path, "regional_grid.nml"))

      # Check if the executable ran OK
      if (ret_val != 0):
         os.chdir(cwd)
         raise RuntimeError("The regional_esg_grid executable failed!")

      # Run the regional grid creation application; creates regional_grid.nc
      ret_val = os.system("time ./regional_esg_grid " + os.path.join(work_path, "regional_grid.nml"))

      # Run the global equivalent resolution application
      ret_val = os.system("time ./global_equiv_resol regional_grid.nc")

      # Get the CRES equivalent from the regional_grid.nc file
      grid_nc = Dataset("regional_grid.nc")
      CRES = grid_nc.getncattr('RES_equiv')
      CRES = f"C{CRES}"
      grid_nc.close()

      # Rename the regional_grid.nc file
      grid_fn = f"{CRES}_grid.tile7.halo{NHW}.nc"
      shutil.copy2(os.path.join("regional_grid.nc"),
                   os.path.join(grid_fn))

      # Shave the halo from NHW (default 6) to NH4 (always 4)
      # Create the 'shave' namelist file
      halo_NH4_fp = os.path.join(work_path, f"{CRES}_grid.tile7.halo{NH4}.nc")
      shave_nl_fp = os.path.join(work_path, f"shave_{NH4}.in")
      print(shave_nl_fp)
      with open(shave_nl_fp,"w") as sh_fp:
         s = (f'{grid_info["ESGgrid_NX"]} {grid_info["ESGgrid_NY"]} {NH4} '
              f'"{grid_fn}" "{halo_NH4_fp}"')
         sh_fp.write(s)

      # Run shave
      ret_val = os.system(f"time ./shave < {shave_nl_fp}")

      # Read in the native grid
      GTYPE = "regional"
      tiles = [7]
      get_halo_boundaries = True
      remove_regional_halo = True
      native_grid = read_FV3LAM_grid_native(work_path, GTYPE, CRES, tiles,
         get_halo_boundaries, NH4, remove_regional_halo)

      lon_center = native_grid["lon_tile_cntr_all_tiles"][0]
      lat_center = native_grid["lat_tile_cntr_all_tiles"][0]

      lon_corners_face_midpts = native_grid[
            "lon_tile_corners_face_midpts_all_tiles"][0,:]
      lat_corners_face_midpts = native_grid[
            "lat_tile_corners_face_midpts_all_tiles"][0,:]

      nx = native_grid["nx_all_tiles"][0]
      ny = native_grid["ny_all_tiles"][0]

      lon_boundary = native_grid[
         "lon_bdy_all_tiles"][0:2*(nx+ny)]
      lat_boundary = native_grid[
         "lat_bdy_all_tiles"][0:2*(nx+ny)]

      # Change back to the CWD
      os.chdir(cwd)

      wrt_lon_ctr = grid_info["ESGgrid_LON_CTR"]
      wrt_lat_ctr = grid_info["ESGgrid_LAT_CTR"]
      wrt_lat1 = grid_info["ESGgrid_LAT_CTR"]
      wrt_lat2 = grid_info["ESGgrid_LAT_CTR"]

      # Convert corner/face points from lat/lon to Lambert X,Y
      lcc_grid_params = calc_grid_lambert_conformal(wrt_lon_ctr, wrt_lat_ctr,
            lon_corners_face_midpts, lat_corners_face_midpts,
            grid_info["ESGgrid_DELX"], grid_info["ESGgrid_DELY"])

   elif grid_type == "GFDLgrid":

      grid_keys = ["GFDLgrid_LAT_T6_CTR", "GFDLgrid_NUM_CELLS", "GFDLgrid_STRETCH_FAC",
                   "GFDLgrid_REFINE_RATIO", "GFDLgrid_ISTART_OF_RGNL_DOM_ON_T6G",
                   "GFDLgrid_IEND_OF_RGNL_DOM_ON_T6G", "GFDLgrid_JSTART_OF_RGNL_DOM_ON_T6G",
                   "GFDLgrid_JEND_OF_RGNL_DOM_ON_T6G", "GFDLgrid_USE_NUM_CELLS_IN_FILENAMES"]

      try:
         grid_info = {grid_key:grid[grid_key] for grid_key in grid_keys}
      except KeyError:
         raise KeyError("At least one GFDLgrid parameter is not set in " + config_fn)


   # Generate the write grid for ESG grid type
   if grid_type == "ESG":
      print("Nothing yet")

if __name__ == "__main__":
   argv = sys.argv
   HorizGrid(argv[1], argv[2])
