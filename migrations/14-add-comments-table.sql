CREATE TABLE comments (
    "uuid" uuid NOT NULL,
    "gallery_uuid" uuid NOT NULL,
    "twitter_id" varchar(512) NOT NULL,
    "body" TEXT NOT NULL,
    "created_at" timestamp(6) NOT NULL
);
