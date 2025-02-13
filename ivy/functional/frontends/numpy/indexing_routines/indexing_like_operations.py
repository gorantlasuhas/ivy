import ivy
from ivy.functional.frontends.numpy.func_wrapper import (
    to_ivy_arrays_and_back,
    inputs_to_ivy_arrays,
    handle_numpy_out,
)

@to_ivy_arrays_and_back
def take(a, indices, axis=None, mode='raise', out=None):
    indices = ivy.array(indices)
    shape = ivy.shape(a)
    if ivy.ndim(indices) == 0:
        indices = ivy.expand_dims(indices, axis=0)
    elif ivy.ndim(indices) == 1:
        indices = ivy.expand_dims(indices, axis=axis)
    if axis is None:
        slice_obj = [ivy.newaxis] * ivy.ndim(a)
    else:
        slice_obj = [slice(None)] * axis + [ivy.newaxis] + [slice(None)] * (ivy.ndim(a) - axis - 1)
    if mode == 'raise':
        out_of_bounds = ivy.logical_or(indices < 0, indices >= shape[axis])
        if ivy.any(out_of_bounds):
            raise ValueError('indices are out of bounds')
    elif mode == 'clip':
        indices = ivy.clip(indices, 0, shape[axis] - 1)
    elif mode == 'wrap':
        indices = ivy.mod(indices, shape[axis])
    else:
        raise ValueError('invalid mode')

    slice_obj[axis] = indices
    result = a[tuple(slice_obj)]
    if out is not None:
        ivy.assign(out, result)
        return out
    return result

@to_ivy_arrays_and_back
def take_along_axis(arr, indices, axis):
    return ivy.take_along_axis(arr, indices, axis)


@to_ivy_arrays_and_back
def tril_indices(n, k=0, m=None):
    return ivy.tril_indices(n, m, k)


@to_ivy_arrays_and_back
def indices(dimensions, dtype=int, sparse=False):
    dimensions = tuple(dimensions)
    N = len(dimensions)
    shape = (1,) * N
    if sparse:
        res = tuple()
    else:
        res = ivy.empty((N,) + dimensions, dtype=dtype)
    for i, dim in enumerate(dimensions):
        idx = ivy.arange(dim, dtype=dtype).reshape(shape[:i] + (dim,) + shape[i + 1 :])
        if sparse:
            res = res + (idx,)
        else:
            res[i] = idx
    return res


# unravel_index
@to_ivy_arrays_and_back
def unravel_index(indices, shape, order="C"):
    ret = [x.astype("int64") for x in ivy.unravel_index(indices, shape)]
    return tuple(ret)


@to_ivy_arrays_and_back
def fill_diagonal(a, val, wrap=False):
    if a.ndim < 2:
        raise ValueError("array must be at least 2-d")
    end = None
    if a.ndim == 2:
        # Explicit, fast formula for the common case.  For 2-d arrays, we
        # accept rectangular ones.
        step = a.shape[1] + 1
        # This is needed to don't have tall matrix have the diagonal wrap.
        if not wrap:
            end = a.shape[1] * a.shape[1]
    else:
        # For more than d=2, the strided formula is only valid for arrays with
        # all dimensions equal, so we check first.
        if not ivy.all(ivy.diff(a.shape) == 0):
            raise ValueError("All dimensions of input must be of equal length")
        step = 1 + ivy.sum(ivy.cumprod(a.shape[:-1]))

    # Write the value out into the diagonal.
    shape = a.shape
    a = ivy.reshape(a, a.size)
    a[:end:step] = val
    a = ivy.reshape(a, shape)


@inputs_to_ivy_arrays
def put_along_axis(arr, indices, values, axis):
    ivy.put_along_axis(arr, indices, values, axis)


def diag(v, k=0):
    return ivy.diag(v, k=k)


@to_ivy_arrays_and_back
def diagonal(a, offset, axis1, axis2):
    return ivy.diagonal(a, offset=offset, axis1=axis1, axis2=axis2)


@to_ivy_arrays_and_back
@handle_numpy_out
def compress(condition, a, axis=None, out=None):
    condition_arr = ivy.asarray(condition).astype(bool)
    if condition_arr.ndim != 1:
        raise ivy.utils.exceptions.IvyException("Condition must be a 1D array")
    if axis is None:
        arr = ivy.asarray(a).flatten()
        axis = 0
    else:
        arr = ivy.moveaxis(a, axis, 0)
    if condition_arr.shape[0] > arr.shape[0]:
        raise ivy.utils.exceptions.IvyException(
            "Condition contains entries that are out of bounds"
        )
    arr = arr[: condition_arr.shape[0]]
    return ivy.moveaxis(arr[condition_arr], 0, axis)
