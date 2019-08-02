from netCDF4 import Dataset
import numpy as np


def nc4_get_copy(name_in, name_out):
    din = Dataset(name_in, 'r')
    dout = Dataset(name_out, 'w')

    # Copy dimensions
    for dname, dim in din.dimensions.items():
        dout.createDimension(dname, len(dim) if not dim.isunlimited() else None)

    # Copy variables
    for v_name, in_var in din.variables.items():
        # always create double precision output. Default is single which will not work for perturb.
        #out_var = dout.createVariable(v_name, in_var.datatype, in_var.dimensions)
        out_var = dout.createVariable(v_name, np.float64, in_var.dimensions)

        # Copy variable attributes
        ncdict = {k: in_var.getncattr(k) for k in in_var.ncattrs() if k not in ["_FillValue", "missing_value"]}

        for k in ["_FillValue", "missing_value"]:
            if k in in_var.ncattrs():
                ncdict[k] = np.float64(in_var.getncattr(k))
        out_var.setncatts(ncdict)

        out_var[:] = in_var[:]

    # close the input file
    din.close()
    return dout
