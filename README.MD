### Script to automatically download the right undetected chromedriver version

[GitHub - ultrafunkamsterdam/undetected-chromedriver: Custom Selenium Chromedriver | Zero-Config | Passes ALL bot mitigation systems (like Distil / Imperva/ Datadadome / CloudFlare IUAM)](https://github.com/ultrafunkamsterdam/undetected-chromedriver)

```python
How to use:
$pip install auto-download-undetected-chromedriver
from auto_download_undetected_chromedriver import download_undetected_chromedriver
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
```
