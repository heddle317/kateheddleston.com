import sys

from app.db.galleries import GalleryCategory


if __name__ == "__main__":
    name = sys.argv[1]
    GalleryCategory.create(name=name)
