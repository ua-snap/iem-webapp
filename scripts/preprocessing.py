"""
Create GeoTIFFs rasters of means summarized by variable, period, model, scenario, and season, using the following datasets:
* [Temperature (`tas`)](http://ckan.snap.uaf.edu/dataset/projected-monthly-and-derived-temperature-products-771m-cmip5-ar5)
* [Precipitation (`pr`)](http://ckan.snap.uaf.edu/dataset/projected-monthly-and-derived-temperature-products-771m-cmip5-ar5)

These data are available on Poseidon under:
* `/workspace/CKAN/CKAN_Data/Base/AK_771m/projected/AR5_CMIP5_models/Projected_Monthy_and_Derived_Temperature_Products_771m_CMIP5_AR5/derived/`
* `/workspace/CKAN/CKAN_Data/Base/AK_771m/projected/AR5_CMIP5_models/Projected_Monthy_and_Derived_Precipitation_Products_771m_CMIP5_AR5/derived/`

makes use of the following env vars:
* BASE_DIR, path to directory containing the derived precip and temp data (subfolder of GeoTIFFs)
* GTIFF_FOLDER, the name of the above subfolder containing the individual GeoTIFFs
* NCORES, number of cores to use  

e.g.,  
`export BASE_DIR=/atlas_scratch/kmredilla/iem-webapp/`  
`export GTIFF_FOLDER=ar5_tas_pr_decadal_seasonal`  
`export NCORES=30`  

Write the output arrays to individual rasters in a folder named `ar5_tas_pr_decadal_mean_seasonal_aggregated/` as `<variable>_decadal_mean_<season>_mean_c_<model>_<scenario>_<period>.tif` (folder is created if not found).

Also create a netCDF file of these data one levels up from the GeoTIFF write dir (`ar5_tas_pr_decadal_seasonal_aggregated.nc`)

Note - this runs in about 10 seconds with 30 cores and ~260GB of RAM.. may be 
substantially slower on less performant hardware
"""


import itertools
import os
import time
import warnings
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio as rio
import xarray as xr
from rasterio.warp import transform


def aggregate_gtiffs(fps, out_fp, meta):
    """Aggregate input geotiffs into a single file
    by taking the mean across axis 0
    """
    data = []
    for fp in fps:
        with rio.open(fp) as src:
            data.append(src.read(1))

    # take mean of arrays
    arr = np.array(data)
    # use nodata value to set nans (to be ignored for aggregation)
    #   (although not necessary if individual pixels are all
    #   NaN or not NaN across all group combinations)
    arr[np.isclose(arr, NODATA)] = np.nan
    with warnings.catch_warnings():
        # ignore warnings for mean of empty slice
        warnings.simplefilter("ignore", category=RuntimeWarning)
        arr = np.nanmean(arr, axis=0)

    # update nodata values
    arr[np.isnan(arr)] = NEW_NODATA
    
    with rio.open(out_fp, "w", **meta) as dst:
        dst.write(arr, 1)
    
    fn_components = out_fp.name.split(".tif")[0].split("_")
    variable, start_year, end_year, season, model, scenario = [
        fn_components[i] for i in [0, -2, -1, 3, -4, -3]
    ]
    period = f"{start_year}_{end_year}"
    
    out_di = {
        "arr": arr,
        "variable": variable,
        "period": period,
        "season": season,
        "model": model,
        "scenario": scenario,
    }

    return out_di


def rm_var(di):
    """Helper to remove the 'variable' key from 
    aggregation output dict
    """
    del di["variable"]
    return di


def make_arr_from_aggr(aggr, dimnames):
    """Make the array structured according to the various axes
    to create an xarray.DataArray from
    
    We need an array shaped exactly according to the dimensions 
      to be used in the xarray.DataArrays/.DataSet
    Not sure the best way to do this, but here we start with an 
      empty array of correct shape will populate
    """
    # 
    # create empty array
    ny, nx = aggr[0]["arr"].shape
    arr_shape = (
        len(PERIODS), len(SEASONS), len(MODELS), len(SCENARIOS), ny, nx
    )
    out_arr = np.empty(arr_shape, dtype=np.float32)
    
    # restructure data for indexing by dimension names
    df = pd.DataFrame(aggr).set_index(dimnames).sort_index()
        
    # run nested loop to correctly populate empty array
    for period, pn in zip(PERIODS, range(arr_shape[0])):
        for season, sn in zip(SEASONS, range(arr_shape[1])):
            for model, mn in zip(MODELS, range(arr_shape[2])):
                for scenario, cn in zip(SCENARIOS, range(arr_shape[3])):
                    out_arr[pn, sn, mn, cn] = df.loc[(period, season, model, scenario)]["arr"]
                    
    return out_arr



if __name__ == "__main__":
    # get env vars
    base_dir = Path(os.getenv("BASE_DIR"))
    in_fn = os.getenv("GTIFF_FOLDER")
    in_dir = base_dir.joinpath(in_fn)
    in_fp = in_dir.joinpath("{}_decadal_mean_{}_{}_{}_{}_{}.tif")
    out_dir = base_dir.joinpath(f"{in_fn}_aggregated")
    out_dir.mkdir(exist_ok=True)

    ncores = int(os.getenv("NCORES"))
    # Specify all group combinations to generate file paths,
    #   and run the aggregation in parallel.
    decades = [
        f"{decade_start}_{decade_start + 9}"
        for decade_start in np.arange(2010, 2091, 10)
    ]
    PERIODS = ["2040_2070", "2070_2100"]
    periods_lu = {
        PERIODS[0]: decades[3:6],
        PERIODS[1]: decades[-3:],
    }
    MODELS = ["CCSM4", "MRI-CGCM3"]
    SCENARIOS = ["rcp45", "rcp85"]
    SEASONS = ["DJF", "MAM", "JJA", "SON"]
    variables = ["tas", "pr"]
    units_lu = {variables[0]: "mean_c", variables[1]: "total_mm"}

    # get metadata from a file (in case write to individual rasters)
    temp_fp = str(in_fp).format(
        variables[0],
        SEASONS[0],
        units_lu[variables[0]],
        MODELS[0],
        SCENARIOS[0],
        decades[0],
    )
    with rio.open(temp_fp) as src:
        meta = src.meta

    # will set nodata to -9999 instead of current, 
    # need to save current nodata though 
    NODATA = meta["nodata"]
    # set new nodata value of -9999 for later use
    NEW_NODATA = -9999.0
    # and update meta dict
    meta.update(
        {"compress": "lzw", "nodata": NEW_NODATA}
    )

    # doing the same thing for all above variables! easy pool-ing..right??
    modifiers = list(
        itertools.product(PERIODS, variables, SEASONS, MODELS, SCENARIOS)
    )

    # append tuple of decades, along with units based on period and variable
    args = []
    for t in modifiers:
        t = list(t)
        run_decades = periods_lu[t[0]]
        fps = [
            str(in_fp).format(t[1], t[2], units_lu[t[1]], t[3], t[4], decade)
            for decade in run_decades
        ]
        # build output filepath from first input filepath
        first_year, suffix = fps[0].split("_")[-2:]
        out_fp = out_dir.joinpath(
            Path(fps[0]).name.replace(suffix, f"{int(first_year) + 30}.tif")
        )
        args.append((fps, out_fp, meta))

    print(f"Aggregating decadal means using {ncores} cores", sep="...")
    
    tic = time.perf_counter()
    with Pool(ncores) as p:
        aggr_out = p.starmap(aggregate_gtiffs, args)

    print(f"done, {round(time.perf_counter() - tic, 1)}s")
    
    # Do a quick quality control check that output for
    #   a single variable-period-model-scenario-season
    #   matches mean of expected input rasters
    print("Conducting a brief QC on the aggregates", sep="...")
    
    tic = time.perf_counter()
    test_fps = args[0][0]
    first_fp = test_fps[0]
    fp_tags = first_fp.split(".")[-2].split("_")
    # assumes ...<firstyear>_<lastyear>.tif
    first_year = int(fp_tags[-2])
    last_year = first_year + 29

    new_arr = np.zeros((3, meta["height"], meta["width"]))
    for i in np.arange(3):
        with rio.open(test_fps[i]) as src:
            new_arr[i] = src.read(1)
    # "top left" pixel shoudl be nodata
    new_arr[new_arr == new_arr[0, 0, 0]] = np.nan
    # set test case arr nodata back to -9999 for comparison
    test_arr = aggr_out[0]["arr"].copy()
    test_arr[np.isnan(test_arr)] = NEW_NODATA

    with warnings.catch_warnings():
        # ignore warnings for mean of empty slice
        warnings.simplefilter("ignore", category=RuntimeWarning)
        new_aggr_arr = np.nanmean(new_arr, axis=0)

    new_aggr_arr[np.isnan(new_aggr_arr)] = -9999.0
    # use np.isclose because result of np.nanmean(should have more
    #   (not true precision but just as artifact of processing)(why though?))
    qc_result = np.all(np.isclose(test_arr, new_aggr_arr))
    print(f"QC complete, {round(time.perf_counter() - tic, 1)}s.")
    print("Test array matches subject array: ", qc_result)

    print("Creating xarray.DataSet from aggregated arrays")
    tic = time.perf_counter()

    # first, break aggr_out by variable
    tas_aggr = [rm_var(di.copy()) for di in aggr_out if di["variable"] == "tas"]
    pr_aggr = [rm_var(di.copy()) for di in aggr_out if di["variable"] == "pr" ]

    dimnames = ["period", "season", "model", "scenario"]
    tas_arr = make_arr_from_aggr(tas_aggr, dimnames)
    pr_arr = make_arr_from_aggr(pr_aggr, dimnames)

    # generate the lat and lon grids
    print("Generating lat/lon grids..", sep="...")
    
    with xr.open_rasterio(temp_fp) as da:
        # Compute the lon/lat coordinates with rasterio.warp.transform
        ny, nx = len(da["y"]), len(da["x"])
        x, y = np.meshgrid(da["x"], da["y"])

        # Rasterio works with 1D arrays
        lon, lat = transform(
            da.crs, {'init': 'EPSG:4326'}, x.flatten(), y.flatten()
        )
        lon = np.asarray(lon, dtype=np.float32).reshape((ny, nx))
        lat = np.asarray(lat, dtype=np.float32).reshape((ny, nx))

    print(f"done, {round(time.perf_counter() - tic, 1)}s.")
    tic = time.perf_counter()

    xy_dimnames = ["y", "x"]
    dimnames.extend(xy_dimnames)
    ds = xr.Dataset(
        data_vars={
            "tas": (dimnames, tas_arr),
            "pr": (dimnames, pr_arr)
        },
        coords={
            "period": PERIODS,
            "season": SEASONS,
            "model": MODELS,
            "scenario": SCENARIOS,
            "lon": (xy_dimnames, lon),
            "lat": (xy_dimnames, lat)
        },
        attrs={},
    )

    print("Writing to netCDF", sep="...")
    tic = time.perf_counter()
    
    # specify encoding to try to compress?
    encoding = {
        "tas": {'zlib': True, "complevel": 9},
        "pr": {'zlib': True, "complevel": 9},
    }
    nc_fp = out_fp.parent.parent.joinpath("ar5_tas_pr_decadal_seasonal_aggregated.nc")
    ds.to_netcdf(nc_fp, encoding=encoding)

    print(f"NetCDF created, written to {nc_fp}, {round(time.perf_counter() - tic, 1)}s.")
