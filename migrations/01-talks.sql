CREATE TABLE talks (
    "uuid" uuid NOT NULL,
    "title" varchar(500) NOT NULL,
    "description" TEXT NOT NULL,
    "slides_link" varchar(500),
    "video_link" varchar(500),
    "created_at" timestamp(6) NOT NULL
);
