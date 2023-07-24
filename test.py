import pathlib

if __name__ == "__main__":
    path = pathlib.Path.cwd().joinpath("assets", "MainCharacters", "NinjaFrog").glob('**/*')
    images = [f for f in path if f.is_file()]
    print(images[0].name)