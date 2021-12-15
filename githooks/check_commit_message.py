import sys

VALID_TYPES = [
    "build",
    "ci",
    "docs",
    "feat",
    "fix",
    "pref",
    "refactor",
    "style",
    "test",
]

HELP_TEXT = """
https://gist.github.com/brianclements/841ea7bffdb01346392c

<type>(<scope>): <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>

type
    * build：对构建系统或者外部依赖项进行了修改
    * ci：对CI配置文件或脚本进行了修改
    * docs：对文档进行了修改
    * feat：增加新的特征
    * fix：修复bug
    * pref：提高性能的代码更改
    * refactor：既不是修复bug也不是添加特征的代码重构
    * style：不影响代码含义的修改，比如空格、格式化、缺失的分号等
    * test：增加确实的测试或者矫正已存在的测试
scope
    说明 commit 影响的范围
subject
    commit 目的的简短描述，不超过50个字符
body
    commit 的详细描述，可以分成多行
footer
    用来关闭issue，例如 Closes #123, #456, #789
"""


def get_commit_message():
    args = sys.argv
    if len(args) <= 1:
        sys.exit(1)
    try:
        with open(args[1], "r", encoding="UTF-8") as fd:
            message = fd.read().strip()
    except Exception as exc_info:
        print(HELP_TEXT)
        print("Commit message error: " + str(exc_info))
        sys.exit(1)
    return message


def main():
    message = get_commit_message()
    ok = False
    for msg_type in VALID_TYPES:
        if message.startswith("{}: ".format(msg_type)):
            ok = True
            break
    else:
        print("Commit Message 不符合规范 Angular 规范")
        print(HELP_TEXT)
    return not ok


if __name__ == "__main__":
    exit(int(main()))
