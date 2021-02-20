def get_constants(filename):
    const_list = []
    with open(filename, "r") as f:
        for const in f.readlines():
            const_list.append(const.strip().split(" = ")[1])
    host = const_list[0]
    port = int(const_list[1])
    mode = int(const_list[2])
    return [host, port, mode]
