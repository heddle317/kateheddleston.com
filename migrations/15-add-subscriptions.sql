CREATE TABLE subscriptions (
    "uuid" uuid NOT NULL,
    "name" varchar(500) NOT NULL,
    "email" varchar(500) NOT NULL,
    "verified" BOOLEAN NOT NULL DEFAULT false,
    "email_verification_token" varchar(50),
    "dead" BOOLEAN NOT NULL DEFAULT false,
    "created_at" timestamp(6) NOT NULL
);
