CREATE TABLE users (
    "uuid" uuid NOT NULL,
    "email" varchar(120) NOT NULL,
    "role" SMALLINT NOT NULL,
    "password_hash" varchar(60),
    "email_verification_token" varchar(50),
    "created_at" timestamp(6) NOT NULL
);
