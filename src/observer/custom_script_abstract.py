from abc import ABC, abstractmethod


class CustomScriptAbstract(ABC):
    @abstractmethod
    def on_initial_window_setup(self, hwnd) -> bool:
        """
        Observer script will try to run this initialization routine
        for each tab ( which pass filters)
        and will repeat for each tab until method finishes with True
        n: total amount of currently tracked windows not including new one
        """
        raise NotImplementedError()

    @abstractmethod
    def on_custom_processing(self, hwnd, n, msg_count) -> bool:
        """
        Custom processing for all tracked windows each iteration.
        For example, you can auto move them to 2nd desktop here.
        """
        raise NotImplementedError()

    @abstractmethod
    def on_hwnd_filter(self, hwnd) -> bool:
        """
        Second filter to exclude windows which script should ignore
        can sometimes rely just on window titles
        Filter is not applied if window caption contains command
        """
        raise NotImplementedError()

    @abstractmethod
    def on_process_module_filter(self, module: str) -> bool:
        """ First filter to exclude processes script should ignore """
        raise NotImplementedError()

    @abstractmethod
    def on_loop_sleep(self) -> bool:
        """
        Set a desired frequency here
        Also you can just simply skip next iteration of observer returning False
         """
        raise NotImplementedError()
