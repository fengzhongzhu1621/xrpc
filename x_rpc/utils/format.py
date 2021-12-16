def str_to_bool(val: str) -> bool:
    """将字符串转换为bool类型 ."""
    val = val.lower()
    if val in {
        "y",
        "yes",
        "yep",
        "yup",
        "t",
        "true",
        "on",
        "enable",
        "enabled",
        "1",
    }:
        return True
    elif val in {"n", "no", "f", "false", "off", "disable", "disabled", "0"}:
        return False
    else:
        raise ValueError(f"Invalid truth value {val}")
