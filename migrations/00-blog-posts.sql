CREATE TABLE blog_posts (
    "uuid" uuid NOT NULL,
    "title" varchar(500) NOT NULL,
    "body" TEXT NOT NULL,
    "image_link" varchar(500),
    "created_at" timestamp(6) NOT NULL
);
