from helpers import os_helpers  # noqa: F401
from observer.browser_observer import BrowserObserver
from user_script import UserObserverScript

if __name__ == '__main__':
    print("Please remember not to abuse usage of this automation. \n"
          "Apply CI test to check if use is fair: \n"
          "what if everyone uses same as yours script under similar circumstances? \n")

    user_observer_script = UserObserverScript(disable_if_maximized=True,
                                              intervals_sec=0.1,
                                              random_intervals_sec=0.3,
                                              proc_filters = ["chrome.exe", "firefox.exe"],
                                              caption_filters = ["Google"]
                                              )
    observer = BrowserObserver(user_observer_script)
    observer.run()
