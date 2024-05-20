from helpers import os  # noqa: F401
from observer.browser_observer import BrowserObserver


if __name__ == '__main__':
    print("Please remember not to abuse usage of this automation. \n"
          "Apply Categorical Imperative to consider moral side: \n"
          "use is only moral if no harm happens when everyone uses same as yours script \n")

    observer = BrowserObserver(proc_name_filter="firefox.exe",
                               disable_if_maximized=True,
                               intervals_sec=0.1,
                               random_interval_extra_sec=0.3)
    observer.run()
