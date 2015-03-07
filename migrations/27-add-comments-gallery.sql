CREATE TABLE gallery_item_comments (
    "uuid" uuid NOT NULL,
    "gallery_item_uuid" uuid NOT NULL,
    "body" TEXT NOT NULL,
    "resolved" boolean,
    "created_at" timestamp(6) NOT NULL
);
