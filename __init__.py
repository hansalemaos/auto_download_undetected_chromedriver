import os
import platform
import subprocess
import sys
import undetected_chromedriver._compat as uc

def download_undetected_chromedriver(folder_path_for_exe:str, undetected:bool=True) -> str:

    #Based on: https://github.com/MShawon/YouTube-Viewer
    r"""
    How to use:
    path = download_undetected_chromedriver(folder_path_for_exe='f:\\undetectedchromedriver',undetected=True)

        Parameters:
            folder_path_for_exe:str
                folder to save chromedriver.exe
                if it does not exist, it will be created
            undetected:bool
                True - chromedriver will be downloaded and patched: https://github.com/ultrafunkamsterdam/undetected-chromedriver
                False - download regular chromedriver
        Returns:
            executable_path:str

    """
    CHROME = [
        "{8A69D345-D564-463c-AFF1-A69D9E530F96}",
        "{8237E44A-0054-442C-B6B6-EA0509993955}",
        "{401C381F-E0DE-4B85-8BD8-3F3F14FBDA57}",
        "{4ea16ac7-fd5a-47c3-875b-dbf4a2008c20}",
    ]
    oldworkingdict = os.getcwd()
    patchedfolder = folder_path_for_exe
    if not os.path.exists(patchedfolder):
        os.makedirs(patchedfolder)
    osname = platform.system()

    if osname == "Linux":
        osname = "lin"
        exe_name = ""
        with subprocess.Popen(
            ["google-chrome", "--version"], stdout=subprocess.PIPE
        ) as proc:
            version = (
                proc.stdout.read().decode("utf-8").replace("Google Chrome", "").strip()
            )
    elif osname == "Darwin":
        osname = "mac"
        exe_name = ""
        process = subprocess.Popen(
            [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "--version",
            ],
            stdout=subprocess.PIPE,
        )
        version = (
            process.communicate()[0]
            .decode("UTF-8")
            .replace("Google Chrome", "")
            .strip()
        )
    elif osname == "Windows":
        osname = "win"
        exe_name = ".exe"
        version = None
        try:
            process = subprocess.Popen(
                [
                    "reg",
                    "query",
                    "HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon",
                    "/v",
                    "version",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
            )
            version = process.communicate()[0].decode("UTF-8").strip().split()[-1]
        except Exception:
            for i in CHROME:
                for j in ["opv", "pv"]:
                    try:
                        command = [
                            "reg",
                            "query",
                            f"HKEY_LOCAL_MACHINE\\Software\\Google\\Update\\Clients\\{i}",
                            "/v",
                            f"{j}",
                            "/reg:32",
                        ]
                        process = subprocess.Popen(
                            command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL,
                            stdin=subprocess.DEVNULL,
                        )
                        version = (
                            process.communicate()[0].decode("UTF-8").strip().split()[-1]
                        )
                    except Exception:
                        pass

        if not version:
            print(
                "Couldn't find your Google Chrome version automatically!"

            )
            version = input(

                "Please input your google chrome version (ex: 91.0.4472.114) : "

            )
    else:
        input("{} OS is not supported.".format(osname))
        sys.exit()

    try:
        with open("version.txt", "r") as f:
            previous_version = f.read()
    except Exception:
        previous_version = "0"

    with open("version.txt", "w") as f:
        f.write(version)

    if version != previous_version:
        try:
            os.remove(f"chromedriver{exe_name}")
        except Exception:
            pass

    executable_path = os.path.join(patchedfolder, "chromedriver.exe")

    major_version = version.split(".")[0]
    uc.TARGET_VERSION = major_version
    os.chdir(patchedfolder)

    if undetected is False:
        chrommanager = uc.ChromeDriverManager(executable_path=executable_path, target_version=major_version)
        chrommanager.fetch_chromedriver()
    else:
        uc.install(executable_path=executable_path)
    os.chdir(oldworkingdict)
    return executable_path

