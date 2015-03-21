import sys

from app.db.galleries import Category


if __name__ == "__main__":
    name = sys.argv[1]
    Category.create(name=name)
