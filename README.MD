# Script to automatically download the right undetected chromedriver version

## pip install auto-download-undetected-chromedriver

[GitHub - ultrafunkamsterdam/undetected-chromedriver: Custom Selenium Chromedriver | Zero-Config | Passes ALL bot mitigation systems (like Distil / Imperva/ Datadadome / CloudFlare IUAM)](https://github.com/ultrafunkamsterdam/undetected-chromedriver)

```python
How to use:
$pip install auto-download-undetected-chromedriver

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

```
