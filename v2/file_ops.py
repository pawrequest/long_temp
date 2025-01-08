# import dataclasses
# import os
# import shutil
# from dataclasses import dataclass, field
# from pathlib import Path
#
# from loguru import logger
#
#
# @dataclass
# class RemoveResult:
#     files_removed: set[str] = field(default_factory=set)
#     dirs_removed: set[str] = field(default_factory=set)
#     missing_ignored: set[str] = field(default_factory=set)
#     dirs_ignored: set[str] = field(default_factory=set)
#
#     @property
#     def log_str(self):
#         return (
#             f"Removed {len(self.files_removed)} files and {len(self.dirs_removed)} empty directories, "
#             f"Ignored {len(self.missing_ignored)} Path/s (not found) and {len(self.dirs_ignored)} Directories (not empty)"
#         )
#
# #
# # def do_remove() -> RemoveResult:
# #     rem_res = remove_files()
# #     rem_res = remove_empty_dirs(rem_res)
# #     logger.info(rem_res.log_str)
# #     return rem_res
# #
#
# def remove_files(pathset: set, tgt:Path,  rem_res: RemoveResult = None) -> RemoveResult:
#     rem_res = rem_res or RemoveResult()
#
#     for tgt_path in pathset:
#         dst_path = tgt / tgt_path
#         if not dst_path.exists():
#             rem_res.missing_ignored.add(str(dst_path))
#
#         elif dst_path.is_file():
#             rem_res.files_removed.add(str(dst_path))
#             dst_path.unlink()
#
#     return rem_res
#
#
# def remove_empty_dirs(rem_res: RemoveResult = None) -> RemoveResult:
#     rem_res = rem_res or RemoveResult()
#     empty, not_empty = remove_empty_recurse()
#     rem_res.dirs_removed.update(empty)
#     rem_res.dirs_ignored.update(not_empty)
#     return rem_res
#
#
# def remove_empty_recurse(tgt) -> tuple[set[str], set[str]]:
#     empty = set()
#     r_set = set()
#     for root, dirnames, filenames in os.walk(tgt, topdown=False):
#         r_set.add(root)
#         for dir_ in dirnames:
#             remove_empty_recurse(dir_)
#             if not filenames:
#                 empty.add(root)
#                 shutil.rmtree(root)
#     res = empty, r_set - empty
#     return res
#
#
# def dir_empty(dir_path):
#     try:
#         next(os.scandir(dir_path))
#         return False
#     except StopIteration:
#         return True
#
#
# def dir_tree_empty(tree_root):
#     for dirpath, dirnames, filenames in os.walk(tree_root):
#         if filenames:
#             return False
#         if dirnames:
#             return all([dir_empty(Path(dirpath) / dir_) for dir_ in dirnames])
#     return True
#
#
# def all_sub_paths(folder: Path) -> list[Path]:
#     file_list = []
#     for path in folder.rglob("*"):
#         file_list.append(path.relative_to(folder).as_posix())
#     return file_list
#
#
# def remove_empty_dirs(target: Path) -> tuple[set[str], set[str]]:
#     empty = set()
#     r_set = set()
#     for root, dirnames, filenames in os.walk(target, topdown=False):
#         r_set.add(root)
#         for dir_ in dirnames:
#             remove_empty_dirs(dir_)
#         else:
#             empty.add(root)
#             shutil.rmtree(root)
#     res = empty, r_set - empty
#     return res
#
#
# def coerce_dataclass(coerceable):
#     for field_ in dataclasses.fields(coerceable):
#         value = getattr(coerceable, field_.name)
#         setattr(coerceable, field_.name, field_.type(value))
