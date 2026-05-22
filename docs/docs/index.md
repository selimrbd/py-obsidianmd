# What is py-obsidianmd ?

py-obsidianmd is a Python library designed to modify your Obsidian notes' metadata in **batch**.
In particular, it enables you to move metadata between the **frontmatter** and **[inline (dataview notation)](https://blacksmithgu.github.io/obsidian-dataview/annotation/add-metadata/#inline-fields)**

Checkout the [examples section](examples.md) for a quickstart on how to use the library, and [reference](reference.md) for method documentation.

!!! warning WARNING
    Consider backing up your vault before using the library, to avoid any risk of data loss.

???+ info For Windows users
    Windows has limitation for maximun length for a path is 256. Starting in Windows 10, version 1607, this limitation have been removed, but you have to opt-in to this new behavior. To do this, open registry, navigate to `Computer\HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem\`, and create a new key with the name `LongPathsEnabled`, type REG_DWORD and value 1. Or you can use this PowerShell command:
    ```PowerShell
    New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
    ```
    Read more about how Windows naming files, paths and namespaces [here](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file#maximum-path-length-limitation) 

# Installation
1. [Download](https://www.python.org/downloads/) and install Python if you haven't
2. Open terminal and use pip:
    ```
    pip install py-obsidianmd
    ```