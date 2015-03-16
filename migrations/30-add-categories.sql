CREATE TABLE gallery_categories (
    "uuid" uuid NOT NULL,
    "name" varchar(500) NOT NULL
);

CREATE TABLE gallery_gallery_categories (
    "uuid" uuid NOT NULL,
    "gallery_uuid" uuid NOT NULL,
    "gallery_category_uuid" uuid NOT NULL
);
