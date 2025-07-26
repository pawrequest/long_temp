# long_temp

**long_temp** is a naive file manager for Python, designed to help you track, compare, and synchronize files and folders. It provides utilities for scanning directories, managing file manifests, logging file operations, and redeploying files from archives (including WinRAR support).

## Features

- **Manifest Tracking**: Record the state of directories and their files, compare differences, and merge or subtract file sets.
- **Itinery Management**: Group multiple manifests, track file operations, and update file states.
- **File Operations**: Copy, remove, and redeploy files and folders, including support for cleaning up empty directories.
- **Archive Handling**: Unpack and redeploy files from various archive formats (zip, tar, rar, 7z) using WinRAR.
- **Logging**: Track and log file operations for auditing and debugging.

## Class Descriptions

- **Manifest**: Represents a snapshot of a directory, storing its root path and a set of relative file paths. Supports scanning, comparison, merging, and subtraction of file sets.
- **Itinery**: Manages a collection of manifests for a target directory, allowing batch file operations (copy, remove, redeploy) and tracking results of these operations.
- **FileTracker**: Handles persistent storage and management of multiple `Itinery` objects, providing JSON-based logging and merging of file operation histories.

## Installation

Clone the repository:

```sh
git clone https://github.com/pawrequest/long_temp.git
cd long_temp
```

Install dependencies:

```sh
pip install -r requirements.txt
```

## Usage

### Scanning a Directory

```python
from long_temporary.mainfest import Manifest
manifest = Manifest.from_scan(Path("/path/to/source"))
print(manifest.paths_relative)
```

### Comparing Directories

```python
src = Path("/path/to/source")
tgt = Path("/path/to/target")
diff_manifest = Manifest.tgt_sub_src(src, tgt)
```

### Managing Itineries

```python
from long_temporary.itinery import Itinery
itin = Itinery.from_manifests(manifest, name="example")
itin.copy_files(Path("/path/to/target"))
```

### Redeploying Archives (with WinRAR)

```python
from long_temporary.main import redeploy_archives
redeploy_archives(Path("/path/to/archives"), Path("/path/to/target"))
```

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements or bug fixes.

## License

See `LICENSE` for details.

## Acknowledgements

- Uses [pydantic](https://docs.pydantic.dev/) for data validation.
- Logging via [loguru](https://github.com/Delgan/loguru).
- Archive extraction via [WinRAR](https://www.win-rar.com/) (Windows only).

---

For more details, see the source code and docstrings in the `src/long_temporary` directory.
