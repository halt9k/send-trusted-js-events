from helpers import os_helpers  # noqa: F401
from helpers.winapi.windows import MissingWindowFocusException
from observer.browser_observer import BrowserObserver
from custom_script import UserObserverScript


if __name__ == '__main__':
    print("Please remember not to abuse usage of this automation. \n"
          "Apply CI test to check if use is fair: \n"
          "what if everyone uses same as yours script under similar circumstances? \n")

    user_observer_script = UserObserverScript(disable_if_maximized=True,
                                              intervals_sec=0.1,
                                              proc_filters=["chrome.exe", "firefox.exe"])
    observer = BrowserObserver(user_observer_script,
                               ignore_exceptions=[MissingWindowFocusException],
                               ignore_pywin_exceptions=['Invalid window handle.'])
    observer.run()
