from PmacTestHarness import PmacTestHarness
import trajectory_scan_driver as driver
import unittest
import time

# PMAC_IP = "172.23.243.169"
PMAC_IP = "172.23.253.15"
PROG_NUM = 1


class InitialisationTest(unittest.TestCase):

    def setUp(self):
        self.pmac = PmacTestHarness(PMAC_IP)
        self.pmac.assign_motors()

    def tearDown(self):
        self.pmac.force_abort()
        self.pmac.disconnect()

    def test_given_valid_axes_then_set_axis_values(self):
        self.pmac.set_axes(511)
        self.pmac.run_motion_program(PROG_NUM)

        self.assertEqual(self.pmac.read_variable("M4040"), "511")
        self.assertEqual(self.pmac.read_variable("M4041"), "1")
        self.assertEqual(self.pmac.read_variable("M4042"), "1")
        self.assertEqual(self.pmac.read_variable("M4043"), "1")
        self.assertEqual(self.pmac.read_variable("M4044"), "1")
        self.assertEqual(self.pmac.read_variable("M4045"), "1")
        self.assertEqual(self.pmac.read_variable("M4046"), "1")
        self.assertEqual(self.pmac.read_variable("M4047"), "1")
        self.assertEqual(self.pmac.read_variable("M4048"), "1")
        self.assertEqual(self.pmac.read_variable("M4049"), "1")

    def test_given_axes_too_high_then_error_status_and_abort(self):
        self.pmac.set_axes(550)
        self.pmac.run_motion_program(PROG_NUM)

        self.assertEqual(self.pmac.read_variable("P4001"), "3")
        self.assertEqual(self.pmac.read_variable("P4002"), "1")

    def test_given_axes_too_low_then_error_status_and_abort(self):
        self.pmac.set_axes(0)
        self.pmac.run_motion_program(PROG_NUM)

        self.assertEqual(self.pmac.read_variable("P4001"), "3")
        self.assertEqual(self.pmac.read_variable("P4002"), "1")


class FillBuffersTest(unittest.TestCase):

    def setUp(self):
        self.pmac = PmacTestHarness(PMAC_IP)

    def tearDown(self):
        self.pmac.force_abort()
        self.pmac.disconnect()

    def test_set_buffer_fill_current(self):
        self.pmac.set_buffer_fill(50, current=True)

        self.assertEqual(self.pmac.read_variable("P4011"), "50")

    def test_set_buffer_fill_not_current(self):
        self.pmac.set_buffer_fill(50, current=False)

        self.assertEqual(self.pmac.read_variable("P4012"), "50")


class AbortTests(unittest.TestCase):

    def setUp(self):
        self.pmac = PmacTestHarness(PMAC_IP)
        self.pmac.assign_motors()
        self.pmac.home_motors()
        self.pmac.set_axes(256)

    def tearDown(self):
        self.pmac.force_abort()
        self.pmac.disconnect()

    def test_given_running_and_abort_command_then_abort(self):
        self.pmac.send_points(driver.generate_lin_points(50, 500), current=True)
        self.pmac.set_buffer_fill(50, current=True)
        self.pmac.run_motion_program(PROG_NUM)

        time.sleep(0.1)
        self.assertEqual(self.pmac.read_variable("P4001"), "1")
        self.assertEqual(self.pmac.read_variable("P4002"), "0")

        self.pmac.set_abort()

        time.sleep(0.5)
        self.assertEqual(self.pmac.read_variable("P4001"), "2")
        self.assertEqual(self.pmac.read_variable("P4002"), "1")

    def test_given_time_0_then_abort_and_status_3(self):
        self.pmac.send_points({'time': [0, 0, 0], 'x': [1, 2, 3]}, current=True)
        self.pmac.set_buffer_fill(3, current=True)
        self.pmac.run_motion_program(PROG_NUM)
        time.sleep(0.1)

        self.assertEqual(self.pmac.read_variable("P4001"), "3")
        self.assertEqual(self.pmac.read_variable("P4002"), "1")


class TrajectoryScanTest(unittest.TestCase):

    def setUp(self):
        self.pmac = PmacTestHarness(PMAC_IP)
        self.pmac.assign_motors()
        self.pmac.home_motors()
        self.pmac.set_axes(384)
        # self.pmac.reset_buffers()
        self.move_time = 250

    def tearDown(self):
        self.pmac.force_abort()
        self.pmac.disconnect()

    def test_given_single_point_then_move(self):

        buffer_fill = 1

        circle_points = driver.generate_circle_points(self.move_time)
        circle_points = self.pmac.convert_points_to_pmac_float(circle_points)
        current_points, _ = driver.grab_buffer_of_points(0, buffer_fill, circle_points)

        self.pmac.fill_current_buffer(current_points)
        self.pmac.set_buffer_fill(buffer_fill, current=True)

        self.pmac.run_motion_program(PROG_NUM)
        scan_time = (self.move_time/4*buffer_fill)/1000
        time.sleep(scan_time + 1)

        self.assertEqual("2", self.pmac.read_variable("P4001"))
        self.assertEqual("0", self.pmac.read_variable("P4002"))
        self.assertEqual(str(buffer_fill), self.pmac.read_variable("P4005"))

    def test_given_one_partial_buffer_then_complete(self):

        buffer_fill = 25

        circle_points = driver.generate_circle_points(self.move_time)
        circle_points = self.pmac.convert_points_to_pmac_float(circle_points)
        current_points, _ = driver.grab_buffer_of_points(0, buffer_fill, circle_points)

        self.pmac.fill_current_buffer(current_points)
        self.pmac.set_buffer_fill(buffer_fill, current=True)

        self.pmac.run_motion_program(PROG_NUM)
        scan_time = (self.move_time/4*buffer_fill)/1000
        time.sleep(scan_time + 2)

        self.assertEqual("2", self.pmac.read_variable("P4001"))
        self.assertEqual("0", self.pmac.read_variable("P4002"))
        self.assertEqual(str(buffer_fill), self.pmac.read_variable("P4005"))

    def test_given_one_full_buffer_then_complete(self):

        buffer_fill = int(self.pmac.buffer_length)

        circle_points = driver.generate_circle_points(self.move_time)
        circle_points = self.pmac.convert_points_to_pmac_float(circle_points)
        current_points, _ = driver.grab_buffer_of_points(0, buffer_fill, circle_points)

        self.pmac.fill_current_buffer(current_points)
        self.pmac.set_buffer_fill(buffer_fill, current=True)

        self.pmac.run_motion_program(PROG_NUM)
        scan_time = (self.move_time/4*buffer_fill)/1000
        time.sleep(scan_time + 1)

        self.assertEqual("2", self.pmac.read_variable("P4001"))
        self.assertEqual("0", self.pmac.read_variable("P4002"))
        self.assertEqual(str(buffer_fill), self.pmac.read_variable("P4005"))

    def test_given_second_partial_buffer_then_complete(self):

        buffer_fill_a = int(self.pmac.buffer_length)
        buffer_fill_b = 25

        circle_points = driver.generate_circle_points(self.move_time)
        circle_points = self.pmac.convert_points_to_pmac_float(circle_points)
        a_points, _ = driver.grab_buffer_of_points(0, buffer_fill_a, circle_points)
        b_points, _ = driver.grab_buffer_of_points(buffer_fill_a, buffer_fill_b, circle_points)

        self.pmac.fill_current_buffer(a_points)
        self.pmac.set_buffer_fill(buffer_fill_a, current=True)

        self.pmac.fill_idle_buffer(b_points)
        self.pmac.set_buffer_fill(buffer_fill_b)

        self.pmac.run_motion_program(PROG_NUM)

        scan_time = (self.move_time/4*buffer_fill_a + self.move_time/4*buffer_fill_b)/1000
        time.sleep(scan_time + 1)

        self.assertEqual("2", self.pmac.read_variable("P4001"))
        self.assertEqual("0", self.pmac.read_variable("P4002"))
        self.assertEqual(str(buffer_fill_a + buffer_fill_b),
                         self.pmac.read_variable("P4005"))

    def test_given_two_full_buffers_then_complete(self):

        buffer_fill_a = int(self.pmac.buffer_length)
        buffer_fill_b = int(self.pmac.buffer_length)

        circle_points = driver.generate_circle_points(self.move_time)
        circle_points = self.pmac.convert_points_to_pmac_float(circle_points)
        a_points, _ = driver.grab_buffer_of_points(0, buffer_fill_a, circle_points)
        b_points, _ = driver.grab_buffer_of_points(buffer_fill_a, buffer_fill_b, circle_points)

        self.pmac.fill_current_buffer(a_points)
        self.pmac.set_buffer_fill(buffer_fill_a, current=True)

        self.pmac.fill_idle_buffer(b_points)
        self.pmac.set_buffer_fill(buffer_fill_b)

        self.pmac.run_motion_program(PROG_NUM)

        scan_time = (self.move_time/4*buffer_fill_a + self.move_time/4*buffer_fill_b)/1000
        time.sleep(scan_time + 1)

        self.assertEqual("2", self.pmac.read_variable("P4001"))
        self.assertEqual("0", self.pmac.read_variable("P4002"))
        self.assertEqual(str(buffer_fill_a + buffer_fill_b), self.pmac.read_variable("P4005"))

    def test_given_five_full_buffers_then_complete(self):

        buffer_fill_a = int(self.pmac.buffer_length)
        buffer_fill_b = buffer_fill_a

        circle_points = driver.generate_circle_points(self.move_time)
        circle_points = self.pmac.convert_points_to_pmac_float(circle_points)
        a_points, end = driver.grab_buffer_of_points(0, buffer_fill_a, circle_points)
        b_points, end = driver.grab_buffer_of_points(end, buffer_fill_b, circle_points)

        self.pmac.fill_current_buffer(a_points)
        self.pmac.set_buffer_fill(buffer_fill_a, current=True)

        self.pmac.fill_idle_buffer(b_points)
        self.pmac.set_buffer_fill(buffer_fill_b)

        self.pmac.run_motion_program(PROG_NUM)

        num_buffers = 1
        self.pmac.prev_buffer_write = 0
        while num_buffers < 5:

            if self.pmac.prev_buffer_write == 1 and int(self.pmac.current_buffer) == 1:
                a_points, end = driver.grab_buffer_of_points(end, buffer_fill_a, circle_points)
                self.pmac.fill_idle_buffer(a_points)
                self.pmac.set_buffer_fill(buffer_fill_a)
                self.pmac.prev_buffer_write = 0
                num_buffers += 1
                print("Filled buffer A")
            elif self.pmac.prev_buffer_write == 0 and int(self.pmac.current_buffer) == 0:
                b_points, end = driver.grab_buffer_of_points(end, buffer_fill_b, circle_points)
                self.pmac.fill_idle_buffer(b_points)
                self.pmac.set_buffer_fill(buffer_fill_b)
                self.pmac.prev_buffer_write = 1
                num_buffers += 1
                print("Filled buffer B")

            time.sleep(self.move_time/4/1000)

            self.pmac.update_status_variables()

        scan_time = (self.move_time/4*buffer_fill_a + self.move_time/4*buffer_fill_b)/1000
        time.sleep(scan_time + 1)

        self.assertEqual("2", self.pmac.read_variable("P4001"))
        self.assertEqual("0", self.pmac.read_variable("P4002"))
        self.assertEqual(str(3*buffer_fill_a + 2*buffer_fill_b),
                         self.pmac.read_variable("P4005"))


class WriteTest(unittest.TestCase):

    def setUp(self):
        self.pmac = PmacTestHarness(PMAC_IP)
        self.pmac.assign_motors()
        self.pmac.home_motors()
        self.pmac.set_axes(384)
        self.pmac.reset_buffers()

    def tearDown(self):
        self.pmac.force_abort()
        self.pmac.disconnect()

    def test_message_length(self):
        values = ""
        num_values = 16
        pmac_10 = self.pmac.double_to_pmac_float(10)

        for _ in range(0, num_values - 1):
            values += pmac_10 + ","
        values += pmac_10
        buffer_set = "P4011=1000"

        command = "WL$30000," + values + buffer_set

        print(command)
        print(len(command))

        self.pmac.sendCommand(command)
        points = self.pmac.read_points(num_values)

        print(points)

    def test_message_speed(self):
        values = ""
        num_values = 16

        for _ in range(0, num_values - 1):
            values += self.pmac.double_to_pmac_float(10)
        values += "$500000000803"
        buffer_set = "P4011=1000"

        command1 = "WL$30000," + values + buffer_set
        print(len(command1))

        times = []
        for i in range(0, 20):
            start_time = time.time()
            for j in range(0, 100):
                self.pmac.sendCommand(command1)
                # print(j)
            times.append(time.time() - start_time)

        print(times)

    def test_buffer_fill_time_one_axis(self):
        time_values = ""
        x_values = ""
        num_values = 8
        buffer_length = 1000
        buffer_fill = 0
        time_address = "30000"
        x_address = self.pmac.add_dechex("30000", buffer_length)
        pmac_10 = self.pmac.double_to_pmac_float(10)

        for _ in range(0, num_values - 1):
            time_values += pmac_10 + ","
        time_values += pmac_10
        for _ in range(0, num_values - 1):
            x_values += pmac_10 + ","
        x_values += pmac_10

        start_time = time.time()
        while buffer_length - buffer_fill >= num_values:
            buffer_fill += num_values
            buffer_set = "P4011=" + str(buffer_fill)
            command = "WL$" + time_address + "," + time_values + \
                      "WL$" + x_address + "," + x_values + buffer_set
            self.pmac.sendCommand(command)
            time_address = self.pmac.add_dechex(time_address, num_values)
            x_address = self.pmac.add_dechex(x_address, num_values)

        print(command)
        print(len(command))

        time_values = ""
        x_values = ""
        num_values = buffer_fill - buffer_length

        for _ in range(0, num_values - 1):
            time_values += "100,"
        time_values += "100"
        for _ in range(0, num_values - 1):
            x_values += pmac_10 + ","
        x_values += pmac_10

        buffer_set = "P4011=1000"
        command = "WL$" + time_address + "," + time_values + "WL$" + x_address + "," + x_values
        self.pmac.sendCommand(command + " " + buffer_set)

        print(time.time() - start_time)
        self.pmac.buffer_length = 1000
        points = self.pmac.read_points(1000)
        print(points)

    def test_buffer_fill_time_nine_axes(self):
        num_values = 1
        buffer_length = 1000
        buffer_fill = 0

        time_values = ""
        values = ""
        pmac_10 = self.pmac.double_to_pmac_float(10)

        time_address = "30000"
        x_address = self.pmac.add_dechex("30000", buffer_length)
        y_address = self.pmac.add_dechex("30000", 2*buffer_length)
        z_address = self.pmac.add_dechex("30000", 3*buffer_length)
        u_address = self.pmac.add_dechex("30000", 4*buffer_length)
        v_address = self.pmac.add_dechex("30000", 5*buffer_length)
        w_address = self.pmac.add_dechex("30000", 6*buffer_length)
        a_address = self.pmac.add_dechex("30000", 7*buffer_length)
        b_address = self.pmac.add_dechex("30000", 8*buffer_length)
        c_address = self.pmac.add_dechex("30000", 9*buffer_length)

        for _ in range(0, num_values - 1):
            time_values += "100,"
        time_values += "100"
        for _ in range(0, num_values - 1):
            values += pmac_10 + ","
        values += pmac_10

        start_time = time.time()
        while buffer_length - buffer_fill >= num_values:
            buffer_fill += num_values
            buffer_set = "P4011=" + str(buffer_fill)
            command = "WL$" + time_address + "," + time_values + "WL$" + x_address + "," + values + \
                      "WL$" + y_address + "," + values + "WL$" + z_address + "," + values + \
                      "WL$" + u_address + "," + values + "WL$" + v_address + "," + values + \
                      "WL$" + w_address + "," + values + "WL$" + a_address + "," + values + \
                      "WL$" + b_address + "," + values + "WL$" + c_address + "," + values + buffer_set

            self.pmac.sendCommand(command + buffer_set)
            time_address = self.pmac.add_dechex(time_address, num_values)
            x_address = self.pmac.add_dechex(x_address, num_values)
            y_address = self.pmac.add_dechex(y_address, num_values)
            z_address = self.pmac.add_dechex(z_address, num_values)
            u_address = self.pmac.add_dechex(u_address, num_values)
            v_address = self.pmac.add_dechex(v_address, num_values)
            w_address = self.pmac.add_dechex(w_address, num_values)
            a_address = self.pmac.add_dechex(a_address, num_values)
            b_address = self.pmac.add_dechex(b_address, num_values)
            c_address = self.pmac.add_dechex(c_address, num_values)

        print(command)
        print(len(command))
        print(time.time() - start_time)
        self.pmac.buffer_length = 1000
        # points = self.pmac.read_points(1000, num_axes=9)
        # print(points)
        # print(len(points))

    def test_float_parsing(self):
        self.pmac.sendCommand("M4500->L:$30000,0,48")

        value = 10
        pmac_float = self.pmac.double_to_pmac_float(value)
        print(str(value) + ' : ' + str(pmac_float))
        self.pmac.write_to_address("L", "30000", pmac_float)
        self.assertAlmostEqual(value, float(self.pmac.read_variable("M4500")), places=5)

