from test.test_functools import TestPartial, capture
from rdc.dic.reference import Reference

class ReferenceTestCase(TestPartial):
    thetype = Reference

    def test_reference(self):
        p = self.thetype(capture)
        self.assertEqual(self.thetype.dereference(p), ((), {}))
