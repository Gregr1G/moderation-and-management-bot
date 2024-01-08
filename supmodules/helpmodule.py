import prettytable


def table_former(data, ans):
    a = prettytable.PrettyTable(ans)
    for i in data:
        a.add_row(i)

    return a



