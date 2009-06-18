import unittest
import datetime

from DateTime import DateTime

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from Products.PloneTestCase.ptc import PloneTestCase
from example.conference.tests.layer import Layer

from example.conference.program import start_default_value
from example.conference.program import end_default_value
from example.conference.program import IProgram
from example.conference.program import StartBeforeEnd

class MockProgram(object):
    pass

class TestProgramUnit(unittest.TestCase):
    
    def test_start_defaults(self):
        data = MockProgram()
        default_value = start_default_value(data)
        today = datetime.datetime.today()
        delta = default_value - today
        self.assertEquals(6, delta.days)

    def test_end_default(self):
        data = MockProgram()
        default_value = end_default_value(data)
        today = datetime.datetime.today()
        delta = default_value - today
        self.assertEquals(9, delta.days)
    
    def test_validate_invariants_ok(self):
        data = MockProgram()
        data.start = datetime.datetime(2009, 1, 1)
        data.end = datetime.datetime(2009, 1, 2)
        
        try:
            IProgram.validateInvariants(data)
        except:
            self.fail()
    
    def test_validate_invariants_fail(self):
        data = MockProgram()
        data.start = datetime.datetime(2009, 1, 2)
        data.end = datetime.datetime(2009, 1, 1)
        
        try:
            IProgram.validateInvariants(data)
            self.fail()
        except StartBeforeEnd:
            pass
    
    def test_validate_invariants_edge(self):
        data = MockProgram()
        data.start = datetime.datetime(2009, 1, 2)
        data.end = datetime.datetime(2009, 1, 2)
        
        try:
            IProgram.validateInvariants(data)
        except:
            self.fail()

class TestProgramIntegration(PloneTestCase):
    
    layer = Layer
    
    def test_adding(self):
        self.folder.invokeFactory('example.conference.program', 'program1')
        p1 = self.folder['program1']
        self.failUnless(IProgram.providedBy(p1))
    
    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='example.conference.program')
        self.assertNotEquals(None, fti)
    
    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='example.conference.program')
        schema = fti.lookup_schema()
        self.assertEquals(IProgram, schema)
    
    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='example.conference.program')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IProgram.providedBy(new_object))
    
    def test_view(self):
        self.folder.invokeFactory('example.conference.program', 'program1')
        p1 = self.folder['program1']
        view = p1.restrictedTraverse('@@view')
        sessions = view.sessions()
        self.assertEquals(0, len(sessions))
    
    def test_start_end_dates_indexed(self):
        self.folder.invokeFactory('example.conference.program', 'program1')
        p1 = self.folder['program1']
        p1.start = datetime.datetime(2009, 1, 1, 14, 01)
        p1.end = datetime.datetime(2009, 1, 2, 15, 02)
        p1.reindexObject()
        
        result = self.portal.portal_catalog(path='/'.join(p1.getPhysicalPath()))
        
        self.assertEquals(1, len(result))
        self.assertEquals(result[0].start, DateTime('2009-01-01T14:01:00'))
        self.assertEquals(result[0].end, DateTime('2009-01-02T15:02:00'))
    
    def test_tracks_indexed(self):
        self.folder.invokeFactory('example.conference.program', 'program1')
        p1 = self.folder['program1']
        p1.tracks = ['Track 1', 'Track 2']
        p1.reindexObject()
        
        result = self.portal.portal_catalog(Subject='Track 2')
        
        self.assertEquals(1, len(result))
        self.assertEquals(result[0].getURL(), p1.absolute_url())
    
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)