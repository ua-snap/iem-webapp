"""
Create a multiband raster of means summarized by variable, period, model, scenario, and season, using the following datasets:
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

<<<<<<< HEAD
Write the output arrays to individual rasters in a folder named `ar5_tas_pr_decadal_mean_seasonal_aggregated/` as `<variable>_decadal_mean_<season>_mean_c_<model>_<scenario>_<period>.tif` (folder is created if not found).
=======
Write the output arrays to individual rasters in a folder named `iem_tas_pr_decadal_mean_seasonal_aggregate/` as `<variable>_<period>_<season>_<model>_<scenario>.tiff` (created if not found).
>>>>>>> c02a414fb866f1689fbbc30279df698abc53f62f

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
import rasterio as rio


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

    return arr


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
    models = ["CCSM4", "MRI-CGCM3"]
    scenarios = ["rcp45", "rcp85"]
    seasons = ["DJF", "MAM", "JJA", "SON"]
    variables = ["tas", "pr"]
    units_lu = {"tas": "mean_c", "pr": "total_mm"}
    decades = [
        f"{decade_start}_{decade_start + 9}"
        for decade_start in np.arange(2010, 2091, 10)
    ]
    periods = {
        "2040_2070": decades[3:6],
        "2070_2100": decades[-3:],
    }

    # get metadata from a file (in case write to individual rasters)
    temp_fp = str(in_fp).format(
        variables[0],
        seasons[0],
        units_lu[variables[0]],
        models[0],
        scenarios[0],
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
        itertools.product(periods.keys(), variables, seasons, models, scenarios)
    )

    # append tuple of decades, along with units based on period and variable
    args = []
    for t in modifiers:
        t = list(t)
        run_decades = periods[t[0]]
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
    test_arr = aggr_out[0].copy()
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
    