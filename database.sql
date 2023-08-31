DROP TABLE IF EXISTS urls CASCADE;

CREATE TABLE urls (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name varchar(255) UNIQUE NOT NULL,
    created_at date NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE url_checks (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url_id bigint REFERENCES urls(id),
    status_code int,
    h1 varchar(255),
    title varchar(255),
    description varchar(255),
    created_at date NOT NULL DEFAULT CURRENT_DATE
);


INSERT INTO urls (name) VALUES ('http://yandex.ru/');
INSERT INTO urls (name) VALUES ('http://google.com/');

