CREATE TABLE galleries (
    "uuid" uuid NOT NULL,
    "name" varchar(500) NOT NULL,
    "dead" BOOLEAN NOT NULL DEFAULT false,
    "published" BOOLEAN NOT NULL DEFAULT false,
    "created_at" timestamp(6) NOT NULL
);

CREATE TABLE gallery_items (
    "uuid" uuid NOT NULL,
    "gallery_uuid" uuid NOT NULL,
    "title" varchar(500) NOT NULL,
    "body" TEXT NOT NULL,
    "image_link" varchar(500),
    "position" integer NOT NULL
);
