from abc import ABC, abstractmethod


class CustomScriptAbstract(ABC):
    @abstractmethod
    def on_initial_window_setup(self, hwnd) -> bool:
        """
        Observer script will try to run this initialization routine
        for each tab ( which pass filters)
        and will repeat for each tab until method finishes with True
        """
        raise NotImplementedError()

    @abstractmethod
    def on_hwnd_filter(self, hwnd) -> bool:
        """
        Second filter to exclude windows which script should ignore
        can sometimes rely just on window titles
        """
        raise NotImplementedError()

    @abstractmethod
    def on_process_module_filter(self, module: str) -> bool:
        """ first filter to exclude processes script should ignore """
        raise NotImplementedError()

    @abstractmethod
    def on_loop_sleep(self) -> bool:
        """
        Set a desired frequency here
        Also you can just simply skip next iteration of observer returning False
         """
        raise NotImplementedError()
