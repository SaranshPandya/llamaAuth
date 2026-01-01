CREATE TABLE store (
    id SERIAL PRIMARY KEY,

    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,

    password CHAR(64) NOT NULL,
    age INT NOT NULL,

    api_key CHAR(64) UNIQUE, 

    status user_status NOT NULL DEFAULT 'active',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT age_positive CHECK (age >= 0)
);
