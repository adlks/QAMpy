import numpy as np
import numpy.testing as npt

from dsp import filter


class TestMovingAvg(object):
    def test_lengths(self):
        for i in range(100, 131):
            x = np.arange(i)
            for j in range(5, 30):
                assert len(filter.moving_average(x, j)) == i-j+1

    def test_numbers1(self):
        npt.assert_allclose(np.array([6,9,12])/3, filter.moving_average(np.arange(1,6), 3))

    def test_numbers2(self):
        npt.assert_allclose(np.array([1.,1., 1.]), filter.moving_average(np.ones(5), 3))

    def test_numbers3(self):
        npt.assert_allclose(np.array([6,9,12,15])/3, filter.moving_average(np.arange(1,7), 3))

