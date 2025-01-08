from pathlib import Path

X_DATA = Path(r"D:\Games\mods\manual\x_data")
# DESTINATION_PATH = Path(r"D:\GAMES\Starfield\Data")
OG_DATA = Path(r"D:\Games\mods\manual\data2")
REFERENCE_FILE = "../game_mods/file_references.json"


def create_symlinks(src, dst):
    for item in src.iterdir():
        symlink_path = dst / item.name
        if symlink_path.exists():
            if symlink_path.is_symlink():
                symlink_path.unlink()  # Remove existing symlink
            elif symlink_path.is_dir():
                continue  # Skip existing directories
        symlink_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure parent directories exist
        symlink_path.symlink_to(item, target_is_directory=item.is_dir())
        print(f"Created symlink: {symlink_path} -> {item}")


def remove_symlinks(src, dst):
    for item in src.iterdir():
        symlink_path = dst / item.name
        if symlink_path.exists() and symlink_path.is_symlink():
            symlink_path.unlink()
            print(f"Removed symlink: {symlink_path}")
        else:
            print(f"Symlink does not exist: {symlink_path}")


if __name__ == "__main__":
    create_symlinks(X_DATA, OG_DATA)
    # To remove the symlinks, uncomment the following line:
    # remove_symlinks(SOURCE_PATH, DESTINATION_PATH)
