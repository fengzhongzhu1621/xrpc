import types
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from inspect import ismodule
from os import environ as os_environ
from pathlib import Path
from re import findall as re_findall
from typing import Union

from x_rpc.exceptions import LoadFileException, PyFileException


def import_string(module_name, package=None):
    """按模块字符串加载
    import a module or class by string path.

    :module_name: str with path of module or path to import and
    instantiate a class
    :returns: a module object or one instance from class if
    module_name is a valid path to class

    """
    module, klass = module_name.rsplit(".", 1)
    module = import_module(module, package=package)
    obj = getattr(module, klass)
    if ismodule(obj):
        return obj
    return obj()


def load_module_from_path(location: Union[bytes, str], encoding: str = "utf8", *args, **kwargs):
    # 1) Parse location.
    # 文件路径转换为str类型
    if isinstance(location, bytes):
        location = location.decode(encoding)

    if not isinstance(location, Path):
        # A) Check if location contains any environment variables
        #    in format ${some_env_var}.
        # 获得路径中的参数
        env_vars_in_location = set(re_findall(r"\${(.+?)}", location))

        # B) Check these variables exists in environment.
        # 判断是否所有的变量是否在环境变量中定义
        not_defined_env_vars = env_vars_in_location.difference(os_environ.keys())
        if not_defined_env_vars:
            raise LoadFileException(
                "The following environment variables are not set: "
                f"{', '.join(not_defined_env_vars)}"
            )

        # C) Substitute them in location.
        # 使用环境变量替换参数值
        for env_var in env_vars_in_location:
            location = location.replace("${" + env_var + "}", os_environ[env_var])

    location = str(location)
    if ".py" in location:
        # 获得文件名，去掉后缀，例如：a / b.c -> b
        name = location.split("/")[-1].split(".")[
            0
        ]  # get just the file name without path and .py extension
        # 创建模块
        _mod_spec = spec_from_file_location(
            name, location, *args, **kwargs
        )
        assert _mod_spec is not None  # type assertion for mypy
        module = module_from_spec(_mod_spec)
        # 导入模块
        _mod_spec.loader.exec_module(module)  # type: ignore
    else:
        module = types.ModuleType("config")
        module.__file__ = str(location)
        try:
            with open(location) as config_file:
                exec(  # nosec
                    compile(config_file.read(), location, "exec"),
                    module.__dict__,
                )
        except IOError as e:
            e.strerror = "Unable to load configuration file (e.strerror)"
            raise
        except Exception as e:
            raise PyFileException(location) from e

    return module


def load_module_from_file_location(
    location: Union[bytes, str], encoding: str = "utf8", *args, **kwargs
):
    """Returns loaded module provided as a file path.

    :param location:
        Coresponds to importlib.util.spec_from_file_location location
        parameters,but with this differences:
        - It has to be of a string or bytes type.
        - You can also use here environment variables
          in format ${some_env_var}.
          Mark that $some_env_var will not be resolved as environment variable.
    :param encoding:
        If location parameter is of a bytes type, then use this encoding
        to decode it into string.
    :param args:
        Coresponds to the rest of importlib.util.spec_from_file_location
        parameters.
    :param kwargs:
        Coresponds to the rest of importlib.util.spec_from_file_location
        parameters.

    For example You can:

        some_module = load_module_from_file_location(
            "some_module_name",
            "/some/path/${some_env_var}"
        )
    """

    # 1) Parse location.
    # 文件路径转换为str类型
    if isinstance(location, bytes):
        location = location.decode(encoding)

    if isinstance(location, Path) or "/" in location or "$" in location:
        module = load_module_from_path(location, *args, **kwargs)
        return module
    else:
        try:
            # 按模块字符串加载
            return import_string(location)
        except ValueError:
            raise IOError("Unable to load configuration %s" % str(location))
