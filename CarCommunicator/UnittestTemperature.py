import unittest
import Temperature

class CarControlAndTemperatureTester(unittest.TestCase):

    def setUp(self):
        self.temp = Temperature.Temperature(20)

    def test_correct_target_temperature(self):
        self.assertEqual(self.temp.target_temp, 20)

    def test_correct_car_control_attributes(self):
        self.assertEqual(self.temp.car_control.AC_target_temperature, 20)
        self.assertTrue(self.temp.car_control.AC_enabled)

    def test_raises_type_exception_if_invalid_argument(self):
        with self.assertRaises(ValueError):
            temp2 = Temperature.Temperature("bug")

    def test_deactivate_works_properly(self):
        self.temp.deactivate()
        self.assertEqual(self.temp.car_control.AC_target_temperature, None)
        self.assertFalse(self.temp.car_control.AC_target_temperature)




if __name__ == "__main__":
    unittest.main()