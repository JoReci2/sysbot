=============
Contributing
=============

Thank you for your interest in contributing to SysBot! This document explains how to contribute effectively to the project.

Table of Contents
=================

* `Code of Conduct`_
* `How to Contribute`_
* `Development Environment Setup`_
* `Code Standards`_
* `Testing`_
* `Pull Request Process`_
* `Bug Reports`_
* `Feature Requests`_

Code of Conduct
===============

By participating in this project, you agree to abide by our code of conduct. Be respectful and constructive in all your interactions.

How to Contribute
=================

There are several ways to contribute:

* Report bugs
* Propose new features
* Improve documentation
* Fix bugs
* Add new features

Development Environment Setup
=============================

1. Fork the repository
2. Clone your fork locally:

   .. code-block:: bash

      git clone https://github.com/your-username/sysbot.git
      cd sysbot

3. Create a virtual environment:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # On macOS/Linux
      # or
      venv\Scripts\activate     # On Windows

4. Install development dependencies:

   .. code-block:: bash

      pip install build ruff bandit radon safety

5. Install the package in development mode:

   .. code-block:: bash

      pip install -e .

Code Standards
==============

Code Style
----------

* Follow PEP 8 for Python style
* Use ``ruff`` for automatic formatting and linting
* Use ``radon`` for code complexity
* Use ``bandit`` for security checks
* Use ``safety`` for dependency checks

Naming Conventions
------------------

* Functions and variables: ``snake_case``
* Classes: ``PascalCase``
* Constants: ``UPPER_CASE``
* Modules: ``lowercase``

Documentation
-------------

* Document all public functions with docstrings
* Use Google format for docstrings
* Include usage examples when appropriate

Docstring example:

.. code-block:: python

   def example_function(param1: str, param2: int) -> bool:
       """Example function with docstring.

       Args:
           param1: Description of first parameter
           param2: Description of second parameter

       Returns:
           Description of return value

       Raises:
           ValueError: Description of when this exception is raised
       """

Testing
=======

* Write tests for any new functionality
* Maintain high test coverage (>80%)
* Use ``robot framework`` or ``unittest`` for testing
* Place tests in the ``tests/`` folder

Running tests:

.. code-block:: bash

   # All tests
   robot -d tests/

   # Specific tests
   robot -d tests/test_specific.robot

Pull Request Process
====================

1. Create a branch for your feature:

   .. code-block:: bash

      git checkout -b feature/feature-name

2. Commit your changes with descriptive messages:

   .. code-block:: bash

      git commit -m "feat: add new feature X"

3. Push your branch:

   .. code-block:: bash

      git push origin feature/feature-name

4. Create a pull request on GitHub

5. Ensure that:

   * All tests pass
   * Code follows standards
   * Documentation is updated if necessary
   * Pull request has a clear description

Commit Convention
-----------------

Use Conventional Commits convention:

* ``feat:``: new feature
* ``fix:``: bug fix
* ``docs:``: documentation
* ``style:``: formatting, missing semicolons, etc.
* ``refactor:``: code refactoring
* ``test:``: adding tests
* ``chore:``: maintenance

Bug Reports
===========

Before reporting a bug:

1. Check it doesn't already exist in issues
2. Make sure you're using the latest version

To report a bug, include:

* Clear description of the problem
* Steps to reproduce
* Expected vs actual behavior
* Python and system version
* Complete error logs

Issue template:

.. code-block:: text

   **Bug Description**
   Clear and concise description of the bug.

   **Reproduction**
   Steps to reproduce:
   1. Go to '...'
   2. Click on '....'
   3. Scroll down to '....'
   4. See error

   **Expected Behavior**
   Clear description of what should happen.

   **Environment**
   - OS: [e.g. macOS 12.0]
   - Python: [e.g. 3.9.0]
   - SysBot: [e.g. 1.0.0]

Feature Requests
================

To propose a new feature:

1. Check it doesn't already exist
2. Describe the problem it solves
3. Propose a solution
4. Give usage examples

Questions and Support
=====================

* For general questions: use GitHub Discussions
* For bugs: create an issue
* For major contributions: contact maintainers first

Acknowledgments
===============

Thanks to all contributors who have helped improve SysBot!

License
=======

By contributing, you agree that your contributions will be licensed under the same license as the project.