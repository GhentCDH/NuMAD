from src.data import get_data
from src.db import engine

def main():
    print(engine)

    reader = get_data()
    for i, row in enumerate(reader):
        print(row)

        if i == 5:
            break



if __name__ == "__main__":
    main()
