"""Official MAT -> owned raw CSI bytes; no labels or preprocessing."""
import h5py
import numpy as np

def aligned_payload(path):
	with h5py.File(path, 'r') as handle:
		raw = handle['csi_out'][()]
	if raw.shape != (20, 30, 3, 3) or not {'real', 'imag'}.issubset(raw.dtype.names or ()):
		raise ValueError('Unexpected original MAT layout: ' + str(path))
	# HDF5 T/N/A/R -> 对外R/A/T/N，保留复数双精度。
	pairs = np.stack((raw['real'].transpose(3, 2, 0, 1), raw['imag'].transpose(3, 2, 0, 1)), axis=-1).astype('<f8')
	if not np.isfinite(pairs).all():
		raise ValueError('Non-finite raw CSI')
	return pairs.tobytes()
