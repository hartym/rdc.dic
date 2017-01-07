from test.test_functools import TestPartial, capture
from rdc.dic.definition import dereference
from rdc.dic.reference import _partial

class ReferenceTestCase(TestPartial):
    thetype = _partial

    def test_reference(self):
        p = self.thetype(capture)
        self.assertEqual(dereference(self.thetype(p)), ((), {}))
