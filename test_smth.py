if __name__ == '__main__':
    import json
    with open("locs.json","r") as file:
        data = json.loads(file.read())
        for item in data["subLocs"]:
            print()
