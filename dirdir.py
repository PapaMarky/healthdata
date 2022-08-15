from pathlib import Path
import os
if __name__ == '__main__':
    print(f'USER: {os.getlogin()}')
    directories_on_path = [f.name for f in Path('/Users/mark/Downloads/').iterdir() if not f.is_file()]
    for d in directories_on_path:
        print(d)
