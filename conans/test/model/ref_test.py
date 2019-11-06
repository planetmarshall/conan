import unittest
from conans.model.ref import ConanFileReference, ConanName, InvalidNameException, check_valid_ref
from conans.errors import ConanException


class RefTest(unittest.TestCase):
    def basic_test(self):
        ref = ConanFileReference.loads("opencv/2.4.10 @ lasote/testing")
        self.assertEqual(ref.name, "opencv")
        self.assertEqual(ref.version, "2.4.10")
        self.assertEqual(ref.user, "lasote")
        self.assertEqual(ref.channel, "testing")
        self.assertEqual(str(ref), "opencv/2.4.10@lasote/testing")

        ref = ConanFileReference.loads("opencv_lite/2.4.10@phil_lewis/testing")
        self.assertEqual(ref.name, "opencv_lite")
        self.assertEqual(ref.version, "2.4.10")
        self.assertEqual(ref.user, "phil_lewis")
        self.assertEqual(ref.channel, "testing")
        self.assertEqual(str(ref), "opencv_lite/2.4.10@phil_lewis/testing")

        ref = ConanFileReference.loads("opencv/2.4.10@3rd-party/testing")
        self.assertEqual(ref.name, "opencv")
        self.assertEqual(ref.version, "2.4.10")
        self.assertEqual(ref.user, "3rd-party")
        self.assertEqual(ref.channel, "testing")
        self.assertEqual(str(ref), "opencv/2.4.10@3rd-party/testing")

    def errors_test(self):
        self.assertRaises(ConanException, ConanFileReference.loads, "")
        self.assertRaises(ConanException, ConanFileReference.loads, "opencv/2.4.10")
        self.assertRaises(ConanException, ConanFileReference.loads, "opencv/2.4.10 @ lasote")
        self.assertRaises(ConanException, ConanFileReference.loads, "opencv??/2.4.10@laso/testing")
        self.assertRaises(ConanException, ConanFileReference.loads, ".opencv/2.4.10@lasote/testing")
        self.assertRaises(ConanException, ConanFileReference.loads, "o/2.4.10 @ lasote/testing")
        self.assertRaises(ConanException, ConanFileReference.loads, "lib/1.0@user&surname/channel")
        self.assertRaises(ConanException, ConanFileReference.loads,
                          "opencv%s/2.4.10@laso/testing" % "A" * 40)
        self.assertRaises(ConanException, ConanFileReference.loads,
                          "opencv/2.4.10%s@laso/testing" % "A" * 40)
        self.assertRaises(ConanException, ConanFileReference.loads,
                          "opencv/2.4.10@laso%s/testing" % "A" * 40)
        self.assertRaises(ConanException, ConanFileReference.loads,
                          "opencv/2.4.10@laso/testing%s" % "A" * 40)

    def check_with_revision_test(self):
        _br = ConanFileReference.loads
        ref = _br("opencv/2.4.10@3rd-party/testing")
        self.assertTrue(ref.matches_with_ref(ref))

        self.assertFalse(ref.matches_with_ref(_br("opencv/2.4.10@3rd-party/testing#Revision")))
        self.assertTrue(_br("opencv/2.4.10@3rd-party/testing#Revision").matches_with_ref(ref))

        self.assertTrue(_br("opencv/2.4.10@3rd-party/"
                            "testing#Revision").matches_with_ref(_br("opencv/2.4.10@3rd-party/"
                                                                     "testing#Revision")))

        self.assertFalse(_br("opencv/2.4.10@3rd-party/"
                             "testing#Revision2").matches_with_ref(_br("opencv/2.4.10@3rd-party/"
                                                                       "testing#Revision1")))


class ConanNameTestCase(unittest.TestCase):

    def _check_invalid_format(self, value, *args):
        with self.assertRaisesRegexp(InvalidNameException, "Valid names"):
            ConanName.validate_name(value, *args)

    def _check_invalid_type(self, value):
        with self.assertRaisesRegexp(InvalidNameException, "is not a string"):
            ConanName.validate_name(value)

    def validate_name_test(self):
        self.assertIsNone(ConanName.validate_name("string.dot.under-score.123"))
        self.assertIsNone(ConanName.validate_name("_underscore+123"))
        self.assertIsNone(ConanName.validate_name("*"))
        self.assertIsNone(ConanName.validate_name("a" * ConanName._min_chars))
        self.assertIsNone(ConanName.validate_name("a" * ConanName._max_chars))
        self.assertIsNone(ConanName.validate_name("a" * 50))  # Regression test

    def validate_name_test_invalid_format(self):
        self._check_invalid_format("-no.dash.start")
        self._check_invalid_format("a" * (ConanName._min_chars - 1))
        self._check_invalid_format("a" * (ConanName._max_chars + 1))

    def validate_name_test_invalid_type(self):
        self._check_invalid_type(123.34)
        self._check_invalid_type(("item1", "item2",))

    def validate_name_version_test(self):
        self.assertIsNone(ConanName.validate_name("[vvvv]", version=True))

    def validate_name_version_test_invalid(self):
        self._check_invalid_format("[no.close.bracket", True)
        self._check_invalid_format("no.open.bracket]", True)


class CheckValidRefTest(unittest.TestCase):

    def test_string(self):
        self.assertTrue(check_valid_ref("package/1.0@user/channel", allow_pattern=False))
        self.assertTrue(check_valid_ref("package/1.0@user/channel", allow_pattern=True))

        self.assertFalse(check_valid_ref("package/*@user/channel", allow_pattern=False))
        self.assertTrue(check_valid_ref("package/1.0@user/channel", allow_pattern=True))

    def test_conanfileref(self):
        ref = ConanFileReference.loads("package/1.0@user/channel")
        self.assertTrue(check_valid_ref(ref, allow_pattern=False))
        self.assertTrue(check_valid_ref(ref, allow_pattern=True))

        ref_pattern = ConanFileReference.loads("package/*@user/channel")
        self.assertFalse(check_valid_ref(ref_pattern, allow_pattern=False))
        self.assertTrue(check_valid_ref(ref_pattern, allow_pattern=True))