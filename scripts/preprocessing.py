"""
Create a multiband raster of means summarized by variable, period, model, scenario, and season, using the following datasets:
* [Temperature (`tas`)](http://ckan.snap.uaf.edu/dataset/projected-monthly-and-derived-temperature-products-771m-cmip5-ar5)
* [Precipitation (`pr`)](http://ckan.snap.uaf.edu/dataset/projected-monthly-and-derived-temperature-products-771m-cmip5-ar5)

These data are available on Poseidon under:
* `/workspace/CKAN/CKAN_Data/Base/AK_771m/projected/AR5_CMIP5_models/Projected_Monthy_and_Derived_Temperature_Products_771m_CMIP5_AR5/derived/`
* `/workspace/CKAN/CKAN_Data/Base/AK_771m/projected/AR5_CMIP5_models/Projected_Monthy_and_Derived_Precipitation_Products_771m_CMIP5_AR5/derived/`

makes use of the following env vars:
* $DATA_DIR, path to directory containing the derived precip and temp data
* $NCORES, number of cores to use
(export DATA_DIR=/atlas_scratch/kmredilla/iem-webapp/ar5_tas_pr_annual_seasonal)

Write the output multiband raster to iem_tas_pr_decadal_mean_seasonal_aggregate.tif

Note - this runs in about 30 seconds with 30 cores and ~260GB of RAM.. may be 
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


def aggregate_gtiffs(fps, meta):
    """Aggregate input geotiffs into a single file
    by taking the mean across axis 0
    """
    data = []
    for fp in fps:
        with rio.open(fp) as src:
            print(f"{fp}opened")
            data.append(src.read(1))

    # take mean of arrays
    arr = np.array(data)
    # use nodata value to set nans (to be ignored for aggregation)
    #   (although not necessary if individual pixels are all
    #   NaN or not NaN across all group combinations)
    arr[np.isclose(arr, meta["nodata"])] = np.nan
    with warnings.catch_warnings():
        # ignore warnings for mean of empty slice
        warnings.simplefilter("ignore", category=RuntimeWarning)
        arr = np.nanmean(arr, axis=0)

    # update nodata values
    new_nodata = -9999.0
    arr[np.isnan(arr)] = new_nodata

    return arr


if __name__ == "__main__":
    # get env vars
    in_fp = Path(os.getenv("DATA_DIR")).joinpath("{}_decadal_mean_{}_{}_{}_{}_{}.tif")
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
        args.append((fps, meta))

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
    # set test case arr nodata back to nan
    test_arr = aggr_out[0].copy()
    test_arr[np.isnan(test_arr)] = -9999

    with warnings.catch_warnings():
        # ignore warnings for mean of empty slice
        warnings.simplefilter("ignore", category=RuntimeWarning)
        new_aggr_arr = np.nanmean(new_arr, axis=0)

    new_aggr_arr[np.isnan(new_aggr_arr)] = -9999
    # use np.isclose because result of np.nanmean(should have more
    #   (not true precision but just as artifact of processing)(why though?))
    qc_result = np.all(np.isclose(test_arr, new_aggr_arr))
    print(f"QC complete, {round(time.perf_counter() - tic, 1)}s.")
    print("Test array matches subject array: ", qc_result)

    # write data
    if qc_result:
        print("Writing data to {out_fp}", end="...")
        out_fp = in_fp.parent.joinpath("iem_tas_pr_decadal_mean_seasonal_aggregate.tif")

        tic = time.perf_counter()
        meta.update(
            {"compression": "lzw", "count": 64,}
        )
        with rio.open(out_fp, "w", **meta) as dst:
            dst.write(np.array(aggr_out))

        print(f"done, {round(time.perf_counter() - tic, 2)}")
