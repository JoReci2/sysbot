"""
Polarion Plugin for Robot Framework Integration

This module provides utilities for integrating Robot Framework test results
with Siemens Polarion ALM/QA. It includes:
- xUnit post-processor for Polarion-compatible output using rebot
- Test case ID mapping utilities for linking RF tests to Polarion STD
- Metadata extraction and formatting for Polarion requirements

Usage:
    from sysbot.plugins.polarion import PolarionExporter
    
    exporter = PolarionExporter()
    exporter.generate_xunit(
        output_xml='output.xml',
        xunit_file='polarion_results.xml',
        project_id='MY_PROJECT',
        test_run_id='TEST_RUN_001'
    )

Polarion Test Case Linking:
    Robot Framework tests can be linked to Polarion test cases using tags:
    
    *** Test Cases ***
    My Test Case
        [Documentation]    This test validates login functionality
        [Tags]    polarion-id:TEST-123    polarion-title:Login Test
        # Test steps...

Requirements:
    - robotframework package must be installed
"""

import os
import xml.etree.ElementTree as ET
from typing import Optional, Dict, List


class PolarionExporter:
    """
    Polarion exporter for Robot Framework test results.
    
    This class provides methods to convert Robot Framework output.xml files
    into Polarion-compatible xUnit XML format with proper test case mapping.
    """
    
    def __init__(self):
        """Initialize the Polarion exporter."""
        self.project_id = None
        self.test_run_id = None
        self.custom_properties = {}
    
    @staticmethod
    def extract_polarion_id(tags: List[str]) -> Optional[str]:
        """
        Extract Polarion test case ID from Robot Framework tags.
        
        Args:
            tags: List of tags from a Robot Framework test case
            
        Returns:
            Polarion test case ID if found, None otherwise
            
        Example:
            tags = ['smoke', 'polarion-id:TEST-123', 'regression']
            extract_polarion_id(tags)  # Returns 'TEST-123'
        """
        for tag in tags:
            if tag.startswith('polarion-id:'):
                return tag.split(':', 1)[1]
        return None
    
    @staticmethod
    def extract_polarion_title(tags: List[str]) -> Optional[str]:
        """
        Extract Polarion test case title from Robot Framework tags.
        
        Args:
            tags: List of tags from a Robot Framework test case
            
        Returns:
            Polarion test case title if found, None otherwise
        """
        for tag in tags:
            if tag.startswith('polarion-title:'):
                return tag.split(':', 1)[1]
        return None
    
    @staticmethod
    def extract_polarion_properties(tags: List[str]) -> Dict[str, str]:
        """
        Extract all Polarion custom properties from tags.
        
        Args:
            tags: List of tags from a Robot Framework test case
            
        Returns:
            Dictionary of custom properties for Polarion
            
        Example:
            tags = ['polarion-testEnvironment:prod', 'polarion-assignee:jdoe']
            # Returns {'testEnvironment': 'prod', 'assignee': 'jdoe'}
        """
        properties = {}
        for tag in tags:
            if tag.startswith('polarion-') and ':' in tag:
                # Extract property name and value
                tag_content = tag[9:]  # Remove 'polarion-' prefix
                if tag_content.startswith('id:') or tag_content.startswith('title:'):
                    continue  # Skip id and title as they're handled separately
                if ':' in tag_content:
                    key, value = tag_content.split(':', 1)
                    properties[key] = value
        return properties
    
    def generate_xunit(
        self,
        output_xml: str,
        xunit_file: str,
        project_id: Optional[str] = None,
        test_run_id: Optional[str] = None,
        custom_properties: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Generate Polarion-compatible xUnit XML from Robot Framework output.
        
        This method uses rebot to generate a base xUnit file, then enhances it
        with Polarion-specific metadata and test case ID mappings.
        
        Args:
            output_xml: Path to Robot Framework output.xml file
            xunit_file: Path where xUnit XML file should be saved
            project_id: Polarion project ID (optional)
            test_run_id: Polarion test run ID (optional)
            custom_properties: Additional custom properties for all tests
            
        Returns:
            Path to generated xUnit file
            
        Raises:
            FileNotFoundError: If output_xml doesn't exist
            RuntimeError: If rebot command fails
        """
        if not os.path.exists(output_xml):
            raise FileNotFoundError(f"Output file not found: {output_xml}")
        
        # Store configuration
        self.project_id = project_id
        self.test_run_id = test_run_id
        self.custom_properties = custom_properties or {}
        
        # Generate base xUnit file using rebot
        self._run_rebot(output_xml, xunit_file)
        
        # Enhance xUnit with Polarion metadata
        self._enhance_xunit(output_xml, xunit_file)
        
        return xunit_file
    
    def _run_rebot(self, output_xml: str, xunit_file: str) -> None:
        """
        Run rebot to generate xUnit XML using Robot Framework API.
        
        Args:
            output_xml: Path to Robot Framework output.xml
            xunit_file: Path for xUnit output
            
        Raises:
            RuntimeError: If rebot command fails
        """
        try:
            from robot.api import ResultWriter
        except ImportError:
            raise ImportError(
                "Robot Framework is required. Install it with: pip install robotframework"
            )
        
        try:
            # Use Robot Framework ResultWriter API to generate xUnit
            result = ResultWriter(output_xml)
            result.write_results(
                xunit=xunit_file,
                report=None,
                log=None
            )
            
            # Check if xUnit file was created
            if not os.path.exists(xunit_file):
                raise RuntimeError(f"Failed to create xUnit file: {xunit_file}")
                
        except Exception as e:
            if isinstance(e, (ImportError, RuntimeError)):
                raise
            raise RuntimeError(f"Failed to generate xUnit: {e}") from e
    
    def _enhance_xunit(self, output_xml: str, xunit_file: str) -> None:
        """
        Enhance xUnit XML with Polarion-specific metadata.
        
        This method parses the Robot Framework output.xml to extract tags
        and metadata, then updates the xUnit file with Polarion-compatible
        properties and test case IDs.
        
        Args:
            output_xml: Path to Robot Framework output.xml
            xunit_file: Path to xUnit XML file to enhance
        """
        # Parse original Robot Framework output to get tags and metadata
        rf_tree = ET.parse(output_xml)
        rf_root = rf_tree.getroot()
        
        # Parse xUnit file
        xunit_tree = ET.parse(xunit_file)
        xunit_root = xunit_tree.getroot()
        
        # Get test case mapping from Robot Framework output
        test_mapping = self._build_test_mapping(rf_root)
        
        # Add global properties to root (if root is testsuite) or first testsuite
        self._add_global_properties(xunit_root)
        
        # Enhance each test case - handle both testsuite as root and testsuites wrapper
        testcases = []
        if xunit_root.tag == 'testsuite':
            # Root is testsuite, get testcases directly
            testcases = xunit_root.findall('testcase')
        else:
            # Root is testsuites, get testcases from all testsuites
            testcases = xunit_root.findall('.//testcase')
        
        for testcase in testcases:
            test_name = testcase.get('name')
            classname = testcase.get('classname', '')
            
            # Find corresponding RF test
            test_key = f"{classname}.{test_name}" if classname else test_name
            rf_test_info = test_mapping.get(test_key)
            
            if rf_test_info:
                self._enhance_testcase(testcase, rf_test_info)
        
        # Write enhanced xUnit file
        xunit_tree.write(xunit_file, encoding='utf-8', xml_declaration=True)
    
    def _build_test_mapping(self, rf_root: ET.Element) -> Dict[str, Dict]:
        """
        Build a mapping of test cases from Robot Framework output.
        
        Args:
            rf_root: Root element of Robot Framework output.xml
            
        Returns:
            Dictionary mapping test names to their metadata
        """
        test_mapping = {}
        
        for suite in rf_root.findall('.//suite'):
            suite_name = suite.get('name', '')
            
            for test in suite.findall('.//test'):
                test_name = test.get('name', '')
                
                # Get tags
                tags = []
                for tag in test.findall('.//tag'):
                    if tag.text:
                        tags.append(tag.text)
                
                # Get documentation
                doc_elem = test.find('doc')
                documentation = doc_elem.text if doc_elem is not None and doc_elem.text else ''
                
                # Build test key
                test_key = f"{suite_name}.{test_name}" if suite_name else test_name
                
                test_mapping[test_key] = {
                    'name': test_name,
                    'suite': suite_name,
                    'tags': tags,
                    'documentation': documentation
                }
        
        return test_mapping
    
    def _add_global_properties(self, xunit_root: ET.Element) -> None:
        """
        Add global Polarion properties to xUnit root.
        
        Args:
            xunit_root: Root element of xUnit XML
        """
        # Determine the testsuite element
        if xunit_root.tag == 'testsuite':
            testsuite = xunit_root
        else:
            testsuite = xunit_root.find('testsuite')
        
        if testsuite is None:
            return
        
        properties = testsuite.find('properties')
        if properties is None:
            # Insert properties at the beginning of testsuite
            properties = ET.Element('properties')
            testsuite.insert(0, properties)
        
        # Add project ID
        if self.project_id:
            prop = ET.SubElement(properties, 'property')
            prop.set('name', 'polarion-project-id')
            prop.set('value', self.project_id)
        
        # Add test run ID
        if self.test_run_id:
            prop = ET.SubElement(properties, 'property')
            prop.set('name', 'polarion-testrun-id')
            prop.set('value', self.test_run_id)
        
        # Add custom properties
        for key, value in self.custom_properties.items():
            prop = ET.SubElement(properties, 'property')
            prop.set('name', f'polarion-custom-{key}')
            prop.set('value', str(value))
    
    def _enhance_testcase(self, testcase: ET.Element, rf_test_info: Dict) -> None:
        """
        Enhance a single test case with Polarion metadata.
        
        Args:
            testcase: xUnit testcase element
            rf_test_info: Test information from Robot Framework
        """
        tags = rf_test_info.get('tags', [])
        
        # Extract Polarion ID and title
        polarion_id = self.extract_polarion_id(tags)
        polarion_title = self.extract_polarion_title(tags)
        polarion_props = self.extract_polarion_properties(tags)
        
        # Add properties to test case
        properties = testcase.find('properties')
        if properties is None:
            properties = ET.SubElement(testcase, 'properties')
        
        # Add Polarion test case ID
        if polarion_id:
            prop = ET.SubElement(properties, 'property')
            prop.set('name', 'polarion-testcase-id')
            prop.set('value', polarion_id)
        
        # Add Polarion test case title
        if polarion_title:
            prop = ET.SubElement(properties, 'property')
            prop.set('name', 'polarion-testcase-title')
            prop.set('value', polarion_title)
        
        # Add custom properties from tags
        for key, value in polarion_props.items():
            prop = ET.SubElement(properties, 'property')
            prop.set('name', f'polarion-custom-{key}')
            prop.set('value', value)


def generate_polarion_xunit(
    output_xml: str,
    xunit_file: str = 'polarion_results.xml',
    project_id: Optional[str] = None,
    test_run_id: Optional[str] = None,
    custom_properties: Optional[Dict[str, str]] = None
) -> str:
    """
    Convenience function to generate Polarion-compatible xUnit XML.
    
    Args:
        output_xml: Path to Robot Framework output.xml file
        xunit_file: Path where xUnit XML file should be saved (default: polarion_results.xml)
        project_id: Polarion project ID (optional)
        test_run_id: Polarion test run ID (optional)
        custom_properties: Additional custom properties for all tests
        
    Returns:
        Path to generated xUnit file
        
    Example:
        generate_polarion_xunit(
            'output.xml',
            'polarion_results.xml',
            project_id='MYPROJECT',
            test_run_id='RUN-001'
        )
    """
    exporter = PolarionExporter()
    return exporter.generate_xunit(
        output_xml=output_xml,
        xunit_file=xunit_file,
        project_id=project_id,
        test_run_id=test_run_id,
        custom_properties=custom_properties
    )
