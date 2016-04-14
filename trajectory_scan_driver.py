import time
from PmacTestHarness import PmacTestHarness
from TrajectoryScanGenerator import TrajectoryScanGenerator as ScanGen

from pkg_resources import require
require('numpy')
import numpy

# IP_ADDRESS = "172.23.243.169"
IP_ADDRESS = "172.23.253.15"


def make_status_message(pmac, start_time, sleep_time):

    time.sleep(sleep_time)

    pmac.update_status_variables()

    if pmac.current_buffer == 0:
        status_message = "Buffer: A"
    else:
        status_message = "Buffer: B"

    scan_time = str(numpy.round(time.time() - start_time, 2))

    status_message += (" - Status: " + str(pmac.status) +
                       " - Error: " + str(pmac.error) +
                       " - Index: " + str(pmac.current_index) +
                       " - Total Points: " + str(pmac.total_points) +
                       " - VelMode: " + pmac.read_variable("M4011") +
                       " - Trigger State: " + pmac.read_variable("M4016") +
                       " - Scan Time: " + scan_time)

    return status_message


def snake_trajectory_scan():

    pmac = PmacTestHarness(IP_ADDRESS)

    pmac.force_abort()
    pmac.assign_motors([(1, "X", 50), (2, "Y", 50)])
    pmac.home_motors()
    pmac.reset_buffers()
    pmac.set_axes(384)

    width = 10
    length = 10
    trajectory = {'move_time': 4000,
                  'width': width,
                  'length': length,
                  'direction': 0}

    snake_scan = ScanGen()
    snake_scan.generate_snake_scan_w_vel(trajectory)
    for axis in snake_scan.point_set.iteritems():
        print(axis)

    snake_scan.check_max_velocity_of_points(pmac.coordinate_system)

    snake_scan.format_point_set()
    for axis in snake_scan.point_set.iteritems():
        print(axis)

    buffer_fill = width * length
    pmac.fill_current_buffer(snake_scan.point_set)
    pmac.set_current_buffer_fill(buffer_fill)

    start_time = time.time()
    pmac.run_motion_program(1)

    time.sleep(3)

    pmac.update_status_variables()
    print("Status: " + str(pmac.status))

    while int(pmac.status) == 1:
        status_message = make_status_message(pmac, start_time, 1)
        print(status_message)


def circle_scan():

    pmac = PmacTestHarness(IP_ADDRESS)

    pmac.force_abort()
    pmac.assign_motors(["100X", "100Y"])
    pmac.home_motors()
    pmac.reset_buffers()
    pmac.set_axes(384)

    circle_points = generate_circle_points(500, 3600)
    print(circle_points)
    print(len(circle_points['time']))
    print(len(circle_points['x']))
    print(len(circle_points['y']))
    circle_points = pmac.convert_points_to_pmac_float(circle_points)

    buffer_length = 1000
    current_start = 0
    current_points, end = grab_buffer_of_points(current_start, buffer_length, circle_points)
    current_start = end + 1

    pmac.fill_current_buffer(current_points)
    pmac.set_current_buffer_fill(buffer_length)
    pmac.prev_buffer_write = 0

    start_time = time.time()
    pmac.run_motion_program(1)
    time.sleep(1)

    pmac.update_status_variables()
    print("Status: " + str(pmac.status))

    while int(pmac.status) == 1:

        if pmac.prev_buffer_write == 1 and int(pmac.current_buffer) == 1:
            current_points, end = grab_buffer_of_points(current_start, 1000, circle_points)
            current_start = end + 1

            pmac.fill_idle_buffer(current_points)
            pmac.set_idle_buffer_fill(buffer_length)
            pmac.prev_buffer_write = 0

        elif pmac.prev_buffer_write == 0 and int(pmac.current_buffer) == 0:
            current_points, end = grab_buffer_of_points(current_start, 1000, circle_points)
            current_start = end + 1

            pmac.fill_idle_buffer(current_points)
            pmac.set_idle_buffer_fill(buffer_length)
            pmac.prev_buffer_write = 1

        status_message = make_status_message(pmac, start_time, 0.1)
        print(status_message)


def main():

    # trajectory_scan()
    snake_trajectory_scan()
    # circle_scan()

if __name__ == "__main__":
    main()
