from robot.api.deco import keyword, library
import importlib

class Interface:
    """
    A modular data loader for Robot Framework that dynamically delegates 
    to appropriate loader modules.
    """

    ROBOT_LIBRARY_SCOPE = 'SUITE'
    ROBOT_LIBRARY_DOC_FORMAT = 'reST'

    def import_data_from(self, module: str, **kwargs) -> any:
        """
        Loads variables by delegating to a specific loader module.
        
        .. code-block:: robotframework

            *** Settings ***
            Library        Collections
            Library        sysbot_lib_dataloaders.Dataloader

            *** Variables ***

            ${baseline}=    Data Load    yaml    file=/path/to/my/file.yaml
        """
        module = module.lower()

        try:
            module_name = f"sysbot.dataloaders.{module}"
            loader_module = importlib.import_module(module_name)
            result = loader_module.load(**kwargs)
            return result

        except ModuleNotFoundError:
            raise ValueError(f"No loader available for module: {module}")

        except Exception as e:
            raise RuntimeError(f"An error occurred while processing the module: {e}")
