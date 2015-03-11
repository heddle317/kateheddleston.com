CREATE TABLE gallery_titles (
    "uuid" uuid NOT NULL,
    "gallery_uuid" uuid NOT NULL,
    "title" varchar(500) NOT NULL,
    "created_at" timestamp(6) NOT NULL
);
