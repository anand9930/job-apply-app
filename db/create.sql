CREATE TABLE jobapply.job_postings (
    posting_id      SERIAL        PRIMARY KEY,
    job_id          BIGINT        NOT NULL UNIQUE,          -- 4256343335
    company_name    TEXT       NOT NULL,
    job_title       TEXT          NOT NULL,
    location        TEXT,        NOT NULL                            -- “San Francisco, CA”
    job_link        TEXT          NOT NULL,
    job_description TEXT,   
    job_criteria    TEXT,                         
    posted_date     DATE,
    created_at      TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE jobapply.job_posting_embeddings (
    embedding_id   SERIAL        PRIMARY KEY,
    posting_id     INTEGER       NOT NULL
                               REFERENCES job_postings(posting_id)
                               ON DELETE CASCADE,
    model_name     TEXT          NOT NULL DEFAULT 'text-embedding-ada-002',
    embedding      vector(1536)  NOT NULL,          -- 1536 dims for ada-002
    created_at     TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,

    /* Ensure one active embedding per model per posting */
    UNIQUE (posting_id, model_name)
);