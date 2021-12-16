from importlib.util import module_from_spec, spec_from_file_location
from os import environ as os_environ
from re import findall as re_findall
from typing import Union

from x_rpc.exceptions import LoadFileException


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

    # 2) Load and return module.
    # 获得文件名，去掉后缀，例如：a/b.c -> b
    name = location.split("/")[-1].split(".")[
        0
    ]  # get just the file name without path and .py extension
    # 创建模块
    _mod_spec = spec_from_file_location(name, location, *args, **kwargs)
    module = module_from_spec(_mod_spec)
    # 导入模块
    _mod_spec.loader.exec_module(module)  # type: ignore

    return module
