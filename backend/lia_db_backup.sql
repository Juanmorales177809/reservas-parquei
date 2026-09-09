--
-- PostgreSQL database cluster dump
--

\restrict hMxyrsbtMkz67AButEdGBpD6DOQDRDJEge2J3ztSmjGqqLVwq1iMYmaxDrjuesJ

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Roles
--

CREATE ROLE postgres;
ALTER ROLE postgres WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS PASSWORD 'md53175bce1d3201d16594cebf9d7eb3f9d';






\unrestrict hMxyrsbtMkz67AButEdGBpD6DOQDRDJEge2J3ztSmjGqqLVwq1iMYmaxDrjuesJ

--
-- Databases
--

--
-- Database "template1" dump
--

\connect template1

--
-- PostgreSQL database dump
--

\restrict 551Vx9xHUhdVYOYKXwgF6L0mK954RUhSjKrXc4qEV4a4vFdGAbcEupVcGk5tWPg

-- Dumped from database version 13.23 (Debian 13.23-1.pgdg13+1)
-- Dumped by pg_dump version 13.23 (Debian 13.23-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- PostgreSQL database dump complete
--

\unrestrict 551Vx9xHUhdVYOYKXwgF6L0mK954RUhSjKrXc4qEV4a4vFdGAbcEupVcGk5tWPg

--
-- Database "lia_db" dump
--

--
-- PostgreSQL database dump
--

\restrict feDrEecNVYTVB1sRoQ8PoUVtT5JYrVKNjHrWwR8jM52FlHCeDJBTRY4nU7m7J9u

-- Dumped from database version 13.23 (Debian 13.23-1.pgdg13+1)
-- Dumped by pg_dump version 13.23 (Debian 13.23-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: lia_db; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE lia_db WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'en_US.utf8';


ALTER DATABASE lia_db OWNER TO postgres;

\unrestrict feDrEecNVYTVB1sRoQ8PoUVtT5JYrVKNjHrWwR8jM52FlHCeDJBTRY4nU7m7J9u
\connect lia_db
\restrict feDrEecNVYTVB1sRoQ8PoUVtT5JYrVKNjHrWwR8jM52FlHCeDJBTRY4nU7m7J9u

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: cargos; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA cargos;


ALTER SCHEMA cargos OWNER TO postgres;

--
-- Name: equipos; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA equipos;


ALTER SCHEMA equipos OWNER TO postgres;

--
-- Name: personal; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA personal;


ALTER SCHEMA personal OWNER TO postgres;

--
-- Name: unidadOrganizacional; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA "unidadOrganizacional";


ALTER SCHEMA "unidadOrganizacional" OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: cargo; Type: TABLE; Schema: cargos; Owner: postgres
--

CREATE TABLE cargos.cargo (
    id_cargo integer NOT NULL,
    nombre_cargo character varying(50) NOT NULL,
    id_unidad integer NOT NULL
);


ALTER TABLE cargos.cargo OWNER TO postgres;

--
-- Name: cargo_id_cargo_seq; Type: SEQUENCE; Schema: cargos; Owner: postgres
--

ALTER TABLE cargos.cargo ALTER COLUMN id_cargo ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME cargos.cargo_id_cargo_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: equipos; Type: TABLE; Schema: equipos; Owner: postgres
--

CREATE TABLE equipos.equipos (
    id_equipo integer NOT NULL,
    id_unidad integer NOT NULL,
    nombre_equipo character varying(50) NOT NULL,
    placa character varying(40),
    serial character varying(50),
    marca character varying(50),
    modelo character varying(50),
    image_path character varying(100),
    manual_operacion character varying(100),
    requiere_calibracion boolean,
    guia_rapida character varying(100),
    instalador character varying(100),
    estado boolean,
    id_categoria integer,
    proxima_fecha_calibracion date,
    proxima_fecha_mantenimiento date,
    frecuencia_calibracion integer,
    frecuencia_mantenimiento integer
);


ALTER TABLE equipos.equipos OWNER TO postgres;

--
-- Name: equipos_id_equipo_seq; Type: SEQUENCE; Schema: equipos; Owner: postgres
--

CREATE SEQUENCE equipos.equipos_id_equipo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE equipos.equipos_id_equipo_seq OWNER TO postgres;

--
-- Name: equipos_id_equipo_seq; Type: SEQUENCE OWNED BY; Schema: equipos; Owner: postgres
--

ALTER SEQUENCE equipos.equipos_id_equipo_seq OWNED BY equipos.equipos.id_equipo;


--
-- Name: personal; Type: TABLE; Schema: personal; Owner: postgres
--

CREATE TABLE personal.personal (
    id_persona integer NOT NULL,
    nombre character varying(50) NOT NULL,
    id_cargo integer NOT NULL,
    documento character varying(20) NOT NULL,
    correo character varying(30) NOT NULL,
    telefono character varying(20) NOT NULL,
    estado boolean
);


ALTER TABLE personal.personal OWNER TO postgres;

--
-- Name: personal_id_persona_seq; Type: SEQUENCE; Schema: personal; Owner: postgres
--

ALTER TABLE personal.personal ALTER COLUMN id_persona ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME personal.personal_id_persona_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: unidad_organizacional; Type: TABLE; Schema: unidadOrganizacional; Owner: postgres
--

CREATE TABLE "unidadOrganizacional".unidad_organizacional (
    id_unidad integer NOT NULL,
    nombre character varying(100) NOT NULL,
    tipo character varying(50) NOT NULL,
    id_unidad_padre integer
);


ALTER TABLE "unidadOrganizacional".unidad_organizacional OWNER TO postgres;

--
-- Name: unidad_organizacional_id_unidad_seq; Type: SEQUENCE; Schema: unidadOrganizacional; Owner: postgres
--

ALTER TABLE "unidadOrganizacional".unidad_organizacional ALTER COLUMN id_unidad ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME "unidadOrganizacional".unidad_organizacional_id_unidad_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: equipos id_equipo; Type: DEFAULT; Schema: equipos; Owner: postgres
--

ALTER TABLE ONLY equipos.equipos ALTER COLUMN id_equipo SET DEFAULT nextval('equipos.equipos_id_equipo_seq'::regclass);


--
-- Data for Name: cargo; Type: TABLE DATA; Schema: cargos; Owner: postgres
--

COPY cargos.cargo (id_cargo, nombre_cargo, id_unidad) FROM stdin;
\.


--
-- Data for Name: equipos; Type: TABLE DATA; Schema: equipos; Owner: postgres
--

COPY equipos.equipos (id_equipo, id_unidad, nombre_equipo, placa, serial, marca, modelo, image_path, manual_operacion, requiere_calibracion, guia_rapida, instalador, estado, id_categoria, proxima_fecha_calibracion, proxima_fecha_mantenimiento, frecuencia_calibracion, frecuencia_mantenimiento) FROM stdin;
\.


--
-- Data for Name: personal; Type: TABLE DATA; Schema: personal; Owner: postgres
--

COPY personal.personal (id_persona, nombre, id_cargo, documento, correo, telefono, estado) FROM stdin;
\.


--
-- Data for Name: unidad_organizacional; Type: TABLE DATA; Schema: unidadOrganizacional; Owner: postgres
--

COPY "unidadOrganizacional".unidad_organizacional (id_unidad, nombre, tipo, id_unidad_padre) FROM stdin;
\.


--
-- Name: cargo_id_cargo_seq; Type: SEQUENCE SET; Schema: cargos; Owner: postgres
--

SELECT pg_catalog.setval('cargos.cargo_id_cargo_seq', 1, false);


--
-- Name: equipos_id_equipo_seq; Type: SEQUENCE SET; Schema: equipos; Owner: postgres
--

SELECT pg_catalog.setval('equipos.equipos_id_equipo_seq', 1, false);


--
-- Name: personal_id_persona_seq; Type: SEQUENCE SET; Schema: personal; Owner: postgres
--

SELECT pg_catalog.setval('personal.personal_id_persona_seq', 1, false);


--
-- Name: unidad_organizacional_id_unidad_seq; Type: SEQUENCE SET; Schema: unidadOrganizacional; Owner: postgres
--

SELECT pg_catalog.setval('"unidadOrganizacional".unidad_organizacional_id_unidad_seq', 1, false);


--
-- Name: cargo pk_cargo; Type: CONSTRAINT; Schema: cargos; Owner: postgres
--

ALTER TABLE ONLY cargos.cargo
    ADD CONSTRAINT pk_cargo PRIMARY KEY (id_cargo);


--
-- Name: equipos pk_equipos; Type: CONSTRAINT; Schema: equipos; Owner: postgres
--

ALTER TABLE ONLY equipos.equipos
    ADD CONSTRAINT pk_equipos PRIMARY KEY (id_equipo);


--
-- Name: equipos uq_equipos_placa; Type: CONSTRAINT; Schema: equipos; Owner: postgres
--

ALTER TABLE ONLY equipos.equipos
    ADD CONSTRAINT uq_equipos_placa UNIQUE (placa);


--
-- Name: equipos uq_equipos_serial; Type: CONSTRAINT; Schema: equipos; Owner: postgres
--

ALTER TABLE ONLY equipos.equipos
    ADD CONSTRAINT uq_equipos_serial UNIQUE (serial);


--
-- Name: personal pk_personal; Type: CONSTRAINT; Schema: personal; Owner: postgres
--

ALTER TABLE ONLY personal.personal
    ADD CONSTRAINT pk_personal PRIMARY KEY (id_persona);


--
-- Name: personal uq_personal_correo; Type: CONSTRAINT; Schema: personal; Owner: postgres
--

ALTER TABLE ONLY personal.personal
    ADD CONSTRAINT uq_personal_correo UNIQUE (correo);


--
-- Name: personal uq_personal_documento; Type: CONSTRAINT; Schema: personal; Owner: postgres
--

ALTER TABLE ONLY personal.personal
    ADD CONSTRAINT uq_personal_documento UNIQUE (documento);


--
-- Name: personal uq_personal_telefono; Type: CONSTRAINT; Schema: personal; Owner: postgres
--

ALTER TABLE ONLY personal.personal
    ADD CONSTRAINT uq_personal_telefono UNIQUE (telefono);


--
-- Name: unidad_organizacional pk_unidad_organizacional; Type: CONSTRAINT; Schema: unidadOrganizacional; Owner: postgres
--

ALTER TABLE ONLY "unidadOrganizacional".unidad_organizacional
    ADD CONSTRAINT pk_unidad_organizacional PRIMARY KEY (id_unidad);


--
-- Name: unidad_organizacional uq_unidad_organizacional_nombre; Type: CONSTRAINT; Schema: unidadOrganizacional; Owner: postgres
--

ALTER TABLE ONLY "unidadOrganizacional".unidad_organizacional
    ADD CONSTRAINT uq_unidad_organizacional_nombre UNIQUE (nombre);


--
-- Name: cargo fk_cargo_unidad; Type: FK CONSTRAINT; Schema: cargos; Owner: postgres
--

ALTER TABLE ONLY cargos.cargo
    ADD CONSTRAINT fk_cargo_unidad FOREIGN KEY (id_unidad) REFERENCES "unidadOrganizacional".unidad_organizacional(id_unidad);


--
-- Name: equipos fk_equipos_unidad; Type: FK CONSTRAINT; Schema: equipos; Owner: postgres
--

ALTER TABLE ONLY equipos.equipos
    ADD CONSTRAINT fk_equipos_unidad FOREIGN KEY (id_unidad) REFERENCES "unidadOrganizacional".unidad_organizacional(id_unidad);


--
-- Name: personal fk_personal_cargo; Type: FK CONSTRAINT; Schema: personal; Owner: postgres
--

ALTER TABLE ONLY personal.personal
    ADD CONSTRAINT fk_personal_cargo FOREIGN KEY (id_cargo) REFERENCES cargos.cargo(id_cargo);


--
-- Name: unidad_organizacional fk_unidad_organizacional_padre; Type: FK CONSTRAINT; Schema: unidadOrganizacional; Owner: postgres
--

ALTER TABLE ONLY "unidadOrganizacional".unidad_organizacional
    ADD CONSTRAINT fk_unidad_organizacional_padre FOREIGN KEY (id_unidad_padre) REFERENCES "unidadOrganizacional".unidad_organizacional(id_unidad);


--
-- PostgreSQL database dump complete
--

\unrestrict feDrEecNVYTVB1sRoQ8PoUVtT5JYrVKNjHrWwR8jM52FlHCeDJBTRY4nU7m7J9u

--
-- Database "postgres" dump
--

\connect postgres

--
-- PostgreSQL database dump
--

\restrict zjiqE7PxyW1l4f8Ivjsfjt2Tgm9jtr45o0Yl8Sg2QeHhwO6wnIBGgLyGje0IfyI

-- Dumped from database version 13.23 (Debian 13.23-1.pgdg13+1)
-- Dumped by pg_dump version 13.23 (Debian 13.23-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- PostgreSQL database dump complete
--

\unrestrict zjiqE7PxyW1l4f8Ivjsfjt2Tgm9jtr45o0Yl8Sg2QeHhwO6wnIBGgLyGje0IfyI

--
-- PostgreSQL database cluster dump complete
--

