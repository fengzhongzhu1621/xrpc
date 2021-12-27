from inspect import isclass


def parse_config_from_object(config):
    if not isinstance(config, dict):
        cfg = {}
        if not isclass(config):
            # 获得对象/模块的所有属性
            cfg.update(
                {
                    key: getattr(config, key)
                    for key in config.__class__.__dict__.keys()
                }
            )

        # 获得类中的所有属性
        config = dict(config.__dict__)
        config.update(cfg)

    # 只保留大写的属性
    config = dict(filter(lambda i: i[0].isupper(), config.items()))
    return config
