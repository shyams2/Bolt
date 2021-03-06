#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This test ensures that the implementation of time-steppers is accurate
For this, we consider the test problem df/dt = f
We integrate till t = 1 and compare the results with the expected
analytic solution f = e^t
"""

import numpy as np

from bolt.lib.linear_solver.integrators \
    import RK2, RK4, RK5

class test(object):
    def __init__(self):
        self.f = np.array([1.0])

    def _source(self, f):
        return (f)

# This test ensures that the RK2 implementation is 2nd order in time
def test_RK2():
    number_of_time_step = 10**np.arange(4)
    time_step_sizes = 1 / number_of_time_step
    error = np.zeros(time_step_sizes.size)

    for i in range(time_step_sizes.size):
        test_obj = test()
        for j in range(number_of_time_step[i]):
            test_obj.f = RK2(test_obj._source, test_obj.f, time_step_sizes[i])
        error[i] = abs(test_obj.f - np.exp(1))

    poly = np.polyfit(np.log10(number_of_time_step), np.log10(error), 1)
    assert (abs(poly[0] + 2) < 0.2)

# This test ensures that the RK4 implementation is 4th order in time
def test_RK4():
    number_of_time_step = 10**np.arange(4)
    time_step_sizes = 1 / number_of_time_step
    error = np.zeros(time_step_sizes.size)

    for i in range(time_step_sizes.size):
        test_obj = test()
        for j in range(number_of_time_step[i]):
            test_obj.f = RK4(test_obj._source, test_obj.f, time_step_sizes[i])
        error[i] = abs(test_obj.f - np.exp(1))

    poly = np.polyfit(np.log10(number_of_time_step), np.log10(error), 1)
    assert (abs(poly[0] + 4) < 0.2)

# This test ensures that the RK5 implementation is 5th order in time
def test_RK5():
    number_of_time_step = 10**np.arange(3)
    time_step_sizes = 1 / number_of_time_step
    error = np.zeros(time_step_sizes.size)

    for i in range(time_step_sizes.size):
        test_obj = test()
        for j in range(number_of_time_step[i]):
            test_obj.f = RK5(test_obj._source, test_obj.f, time_step_sizes[i])
        error[i] = abs(test_obj.f - np.exp(1))

    poly = np.polyfit(np.log10(number_of_time_step), np.log10(error), 1)
    assert (abs(poly[0] + 5) < 0.2)
