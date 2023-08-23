import io
import json
import os
import platform
import re
import struct
import subprocess
import sys
import time
import shutil

import requests
from downloadunzip import download_and_extract
from flatten_any_dict_iterable_or_whatsoever import fla_tu
from getfilenuitkapython import get_filepath
from list_files_with_timestats import get_folder_file_complete_path_limit_subdirs
from touchtouch import touch

allsys = ["linux64", "mac-arm64", "mac-x64", "win32", "win64"]
folderhere = os.path.normpath(os.path.dirname(__file__))


def patch_exe(executable_path):
    # from https://github.com/ultrafunkamsterdam/undetected-chromedriver
    if is_binary_patched(executable_path=executable_path):
        return True
    start = time.perf_counter()
    with io.open(executable_path, "r+b") as fh:
        content = fh.read()
        match_injected_codeblock = re.search(rb"\{window\.cdc.*?;\}", content)
        if match_injected_codeblock:
            target_bytes = match_injected_codeblock[0]
            new_target_bytes = b'{console.log("undetected chromedriver 1337!")}'.ljust(
                len(target_bytes), b" "
            )
            new_content = content.replace(target_bytes, new_target_bytes)
            if new_content == content:
                print(
                    "something went wrong patching the driver binary. could not find injection code block"
                )
            else:
                print(
                    "found block:\n%s\nreplacing with:\n%s"
                    % (target_bytes, new_target_bytes)
                )
            fh.seek(0)
            fh.write(new_content)
    print("patching took us {:.2f} seconds".format(time.perf_counter() - start))


def is_binary_patched(executable_path=None):
    try:
        with io.open(executable_path, "rb") as fh:
            return fh.read().find(b"undetected chromedriver") != -1
    except FileNotFoundError:
        return False


def download_undetected_chromedriver(
        folder_path_for_exe: str,
        undetected: bool = True,
        arm: bool = False,
        force_update: bool = True,
        dowloadurl: bool = r"https://googlechromelabs.github.io/chrome-for-testing/latest-patch-versions-per-build-with-downloads.json",
) -> str:
    r"""
    Args:
        folder_path_for_exe (str): The path to the folder where the ChromeDriver executable will be saved.
        undetected (bool, optional): Apply the undetected patch to the downloaded ChromeDriver binary. Defaults to True.
        arm (bool, optional): If True, download the ARM architecture version of ChromeDriver for Mac. Defaults to False.
        force_update (bool, optional): Force the update of the ChromeDriver binary, even if it's already present. Defaults to True.
        dowloadurl (str, optional): URL to the JSON file containing download links for ChromeDriver versions.
            Defaults to the official repository URL (https://googlechromelabs.github.io/chrome-for-testing/latest-patch-versions-per-build-with-downloads.json).

    Returns:
        str: The path to the downloaded and possibly patched ChromeDriver executable.

    Note:
    - The function detects the operating system and Chrome version to download the appropriate ChromeDriver version.
    - If 'undetected' is True, the function patches the ChromeDriver binary with an additional console log message to make it harder to detect.
    - Use the returned executable path to start ChromeDriver with the provided options.

    Example:
        from auto_download_undetected_chromedriver import download_undetected_chromedriver
        folder_path = "c:\\download2thisfolder"
        chromedriver_path = download_undetected_chromedriver(folder_path, undetected=True, arm=False, force_update=True)
    """
    # Based on: https://github.com/MShawon/YouTube-Viewer

    CHROME = [
        "{8A69D345-D564-463c-AFF1-A69D9E530F96}",
        "{8237E44A-0054-442C-B6B6-EA0509993955}",
        "{401C381F-E0DE-4B85-8BD8-3F3F14FBDA57}",
        "{4ea16ac7-fd5a-47c3-875b-dbf4a2008c20}",
    ]
    # patchedfolder = folder_path_for_exe
    folder_path_for_exe = os.path.normpath(folder_path_for_exe)
    if not os.path.exists(folder_path_for_exe):
        os.makedirs(folder_path_for_exe)
    osname = platform.system()

    if osname == "Linux":
        for_download = "linux64"
        osname = "lin"
        exe_name = ""
        with subprocess.Popen(
                ["google-chrome", "--version"], stdout=subprocess.PIPE
        ) as proc:
            version = (
                proc.stdout.read().decode("utf-8").replace("Google Chrome", "").strip()
            )
    elif osname == "Darwin":
        if arm:
            for_download = "mac-arm64"
        else:
            for_download = "mac-x64"
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
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        creationflags = subprocess.CREATE_NO_WINDOW
        invisibledict = {
            "startupinfo": startupinfo,
            "creationflags": creationflags,
            "start_new_session": True,
        }
        if struct.calcsize("P") == 8:
            for_download = "win64"
        else:
            for_download = "win32"
        osname = "win"
        exe_name = ".exe"
        version = None
        try:
            process = subprocess.Popen(
                [
                    "reg.exe",
                    "query",
                    "HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon",
                    "/v",
                    "version",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                **invisibledict,
            )
            version = process.communicate()[0].decode("UTF-8").strip().split()[-1]
        except Exception:
            for i in CHROME:
                for j in ["opv", "pv"]:
                    try:
                        command = [
                            "reg.exe",
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
                            **invisibledict,
                        )
                        version = (
                            process.communicate()[0].decode("UTF-8").strip().split()[-1]
                        )
                    except Exception:
                        pass

        if not version:
            print("Couldn't find your Google Chrome version automatically!")
            version = input(
                "Please input your google chrome version (ex: 91.0.4472.114) : "
            )
    else:
        input("{} OS is not supported.".format(osname))
        sys.exit()

    versionfile = os.path.normpath(
        os.path.join(folderhere, "versionCHROMEDRIVERBACKUP.txt")
    )
    touch(versionfile)
    try:
        with open(versionfile, "r", encoding="utf-8") as f:
            previous_version = f.read()
    except Exception:
        try:
            versionfile = get_filepath("versionCHROMEDRIVERBACKUP.txt")
            with open(versionfile, "r", encoding="utf-8") as f:
                previous_version = f.read()
        except Exception:
            previous_version = "0"
    if not previous_version:
        previous_version = "0"
    with open(versionfile, "w", encoding="utf-8") as f:
        f.write(version)

    # On OSX we need to work on a copy of system's Chrome binary, it's in a protected location.
    #   otherwise you get error: PermissionError: [Errno 1] Operation not permitted:
    #   'chromedriver-mac-x64/chromedriver' -> '/Applications/Google Chrome.app/Contents/MacOS/Google\\ Chrome'
    if platform.system() == "Darwin":
        source_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        destination_path = os.path.expanduser("~") + "/Desktop/Google Chrome"
        source_path = source_path.replace('\\', '')
        shutil.copy(source_path, destination_path)
        executable_path = destination_path
    else:
        executable_path = os.path.join(folder_path_for_exe, "chromedriver.exe")

    if (
            version != previous_version
            or force_update
            or not os.path.exists(executable_path)
    ):
        major_version = version.split(".")[0]
        print(f"version: {version} | major_version: {major_version}")
        print(f"downloading: {dowloadurl}")
        with requests.get(dowloadurl) as res:
            rs = res
        lookingfor = "chromedriver"
        jsonfi = list(fla_tu(json.loads(rs.content)))
        downloadlink = ""
        print(f"system: {for_download}")
        for q in range(len(version)):
            _version = "".join(list(reversed("".join(reversed(list(version)))[q:])))

            try:
                downloadlink = [
                    x[0]
                    for x in jsonfi
                    if "https" in (g := str(x[0]).lower())
                       and _version in x[0]
                       and for_download in g.split("/")  # [-1]
                       and lookingfor in g
                ]  # [0]
                print(downloadlink)
                downloadlink = downloadlink[0]
                break
            except Exception as fe:
                print(f"{_version} could not be found")

        print(f"downloading: {downloadlink}")
        download_and_extract(
            url=downloadlink,
            folder=folder_path_for_exe,
        )
        if for_download in ["win32", "win64"]:
            # lookingfor="chromedriver.exe"
            fo = sorted(
                [
                    q
                    for q in get_folder_file_complete_path_limit_subdirs(
                    folder_path_for_exe, maxsubdirs=1, withdate=True
                )
                    if "chrome" in q.file.lower() and q.ext.lower() == ".exe"
                ],
                key=lambda x: x.created_ts,
                reverse=True,
            )[0].path
        else:
            fo = sorted(
                [
                    q
                    for q in get_folder_file_complete_path_limit_subdirs(
                    folder_path_for_exe, maxsubdirs=1, withdate=True
                )
                    if "chrome" == q.file.lower() or "chromedriver" == q.file.lower()
                ],
                key=lambda x: x.created_ts,
                reverse=True,
            )[0].path
        if os.path.exists(executable_path):
            try:
                os.remove(executable_path)
            except Exception:
                pass
        os.rename(fo, executable_path)

    if undetected:
        worked = is_binary_patched(executable_path)

        if not worked:
            print(f"not patched yet")
            patch_exe(executable_path)

        print(
            f"To start chromedriver: uc.Chrome(driver_executable_path={executable_path})"
        )

        # Need this on OSX
        if osname == "Darwin":
            os.chmod(executable_path, 0o755)

        return executable_path
    return executable_path
