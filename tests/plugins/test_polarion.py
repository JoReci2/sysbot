"""
Unit tests for Polarion plugin functionality
"""

import os
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

# Import the polarion module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sysbot.plugins.polarion import PolarionExporter, generate_polarion_xunit


class TestPolarionExporter(unittest.TestCase):
    """Test cases for PolarionExporter class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.exporter = PolarionExporter()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up temp files
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_extract_polarion_id(self):
        """Test extraction of Polarion test case ID from tags"""
        tags = ['smoke', 'polarion-id:TEST-123', 'regression']
        result = PolarionExporter.extract_polarion_id(tags)
        self.assertEqual(result, 'TEST-123')
    
    def test_extract_polarion_id_not_found(self):
        """Test when no Polarion ID is present"""
        tags = ['smoke', 'regression']
        result = PolarionExporter.extract_polarion_id(tags)
        self.assertIsNone(result)
    
    def test_extract_polarion_title(self):
        """Test extraction of Polarion test case title from tags"""
        tags = ['polarion-title:Login Test', 'smoke']
        result = PolarionExporter.extract_polarion_title(tags)
        self.assertEqual(result, 'Login Test')
    
    def test_extract_polarion_title_not_found(self):
        """Test when no Polarion title is present"""
        tags = ['smoke', 'regression']
        result = PolarionExporter.extract_polarion_title(tags)
        self.assertIsNone(result)
    
    def test_extract_polarion_properties(self):
        """Test extraction of custom properties from tags"""
        tags = [
            'polarion-testEnvironment:prod',
            'polarion-assignee:jdoe',
            'polarion-id:TEST-001',  # Should be skipped
            'smoke'
        ]
        result = PolarionExporter.extract_polarion_properties(tags)
        self.assertEqual(result, {
            'testEnvironment': 'prod',
            'assignee': 'jdoe'
        })
    
    def test_extract_polarion_properties_empty(self):
        """Test when no custom properties are present"""
        tags = ['smoke', 'regression']
        result = PolarionExporter.extract_polarion_properties(tags)
        self.assertEqual(result, {})
    
    def test_build_test_mapping(self):
        """Test building test mapping from Robot Framework output"""
        # Create a minimal Robot Framework output XML
        rf_xml = """<?xml version="1.0" encoding="UTF-8"?>
<robot>
    <suite name="TestSuite">
        <test name="Test 1">
            <doc>Test documentation</doc>
            <tag>polarion-id:TEST-001</tag>
            <tag>smoke</tag>
            <status status="PASS"/>
        </test>
    </suite>
</robot>
"""
        rf_root = ET.fromstring(rf_xml)
        test_mapping = self.exporter._build_test_mapping(rf_root)
        
        self.assertIn('TestSuite.Test 1', test_mapping)
        test_info = test_mapping['TestSuite.Test 1']
        self.assertEqual(test_info['name'], 'Test 1')
        self.assertEqual(test_info['suite'], 'TestSuite')
        self.assertIn('polarion-id:TEST-001', test_info['tags'])
        self.assertIn('smoke', test_info['tags'])
        self.assertEqual(test_info['documentation'], 'Test documentation')
    
    def test_polarion_id_with_special_characters(self):
        """Test Polarion ID with special characters"""
        tags = ['polarion-id:TEST-001-ABC_123']
        result = PolarionExporter.extract_polarion_id(tags)
        self.assertEqual(result, 'TEST-001-ABC_123')
    
    def test_polarion_title_with_spaces(self):
        """Test Polarion title with multiple words"""
        tags = ['polarion-title:This is a test with spaces']
        result = PolarionExporter.extract_polarion_title(tags)
        self.assertEqual(result, 'This is a test with spaces')
    
    def test_multiple_polarion_ids(self):
        """Test that first Polarion ID is used when multiple are present"""
        tags = ['polarion-id:TEST-001', 'polarion-id:TEST-002']
        result = PolarionExporter.extract_polarion_id(tags)
        self.assertEqual(result, 'TEST-001')
    
    def test_exporter_initialization(self):
        """Test PolarionExporter initialization"""
        self.assertIsNone(self.exporter.project_id)
        self.assertIsNone(self.exporter.test_run_id)
        self.assertEqual(self.exporter.custom_properties, {})
    
    def test_add_global_properties(self):
        """Test adding global properties to xUnit XML"""
        # Create a minimal xUnit XML
        xunit_xml = """<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
    <testsuite name="TestSuite" tests="1">
        <testcase name="Test 1" classname="TestSuite"/>
    </testsuite>
</testsuites>
"""
        xunit_root = ET.fromstring(xunit_xml)
        
        # Set properties
        self.exporter.project_id = 'PROJ-001'
        self.exporter.test_run_id = 'RUN-001'
        self.exporter.custom_properties = {'environment': 'test'}
        
        # Add global properties
        self.exporter._add_global_properties(xunit_root)
        
        # Verify properties were added
        properties = xunit_root.find('.//properties')
        self.assertIsNotNone(properties)
        
        # Check property values
        prop_dict = {prop.get('name'): prop.get('value') 
                     for prop in properties.findall('property')}
        self.assertEqual(prop_dict['polarion-project-id'], 'PROJ-001')
        self.assertEqual(prop_dict['polarion-testrun-id'], 'RUN-001')
        self.assertEqual(prop_dict['polarion-custom-environment'], 'test')


class TestConvenienceFunction(unittest.TestCase):
    """Test the convenience function"""
    
    def test_generate_polarion_xunit_invalid_file(self):
        """Test that FileNotFoundError is raised for missing output.xml"""
        with self.assertRaises(FileNotFoundError):
            generate_polarion_xunit('nonexistent.xml')


if __name__ == '__main__':
    unittest.main()
