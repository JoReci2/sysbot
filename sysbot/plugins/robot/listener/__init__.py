"""
Robot Framework Listener Package

This package previously provided listener implementations for storing Robot Framework
test execution results in various database systems. These listeners have been removed
as Robot Framework provides native xUnit output support via the --xunit option.

Use Robot Framework's built-in xUnit output instead:
    robot --xunit xunit_output.xml tests/
"""
