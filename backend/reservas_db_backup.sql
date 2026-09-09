--
-- PostgreSQL database cluster dump
--

\restrict NqF6Yt5WLKhAEJ6Dh9P2geX7sK7elncIP8OZ44isdf4Elv9zLXfyStSMYfebbQv

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Roles
--

CREATE ROLE postgres;
ALTER ROLE postgres WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS PASSWORD 'md53175bce1d3201d16594cebf9d7eb3f9d';






\unrestrict NqF6Yt5WLKhAEJ6Dh9P2geX7sK7elncIP8OZ44isdf4Elv9zLXfyStSMYfebbQv

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

\restrict 03sKNJUyHFD38WplJfwGQM8uJfnpaw8nVWpzgRwDD5fiuea4sdln8ejFWwC2OWx

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

\unrestrict 03sKNJUyHFD38WplJfwGQM8uJfnpaw8nVWpzgRwDD5fiuea4sdln8ejFWwC2OWx

--
-- Database "postgres" dump
--

\connect postgres

--
-- PostgreSQL database dump
--

\restrict 5zGFxaDE22qT6oMxGT4we3GApgc7Iff09Fuvv5eOALg83liise1E6Qnx7VEPucL

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

\unrestrict 5zGFxaDE22qT6oMxGT4we3GApgc7Iff09Fuvv5eOALg83liise1E6Qnx7VEPucL

--
-- Database "reservas_db" dump
--

--
-- PostgreSQL database dump
--

\restrict 3Iaej6gMlEaVAESqsfUpXYpr2w6fEcfVbSlFYWW6DwS4NsKGN46NYZvBYnyG8tr

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
-- Name: reservas_db; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE reservas_db WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'en_US.utf8';


ALTER DATABASE reservas_db OWNER TO postgres;

\unrestrict 3Iaej6gMlEaVAESqsfUpXYpr2w6fEcfVbSlFYWW6DwS4NsKGN46NYZvBYnyG8tr
\connect reservas_db
\restrict 3Iaej6gMlEaVAESqsfUpXYpr2w6fEcfVbSlFYWW6DwS4NsKGN46NYZvBYnyG8tr

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
-- Name: btree_gist; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS btree_gist WITH SCHEMA public;


--
-- Name: EXTENSION btree_gist; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION btree_gist IS 'support for indexing common datatypes in GiST';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: control_cambios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.control_cambios (
    id integer NOT NULL,
    usuario_id integer,
    accion character varying(20) NOT NULL,
    entidad character varying(40) NOT NULL,
    entidad_id integer,
    descripcion text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    personal_id integer,
    CONSTRAINT ck_control_cambios_actor_unico CHECK (((usuario_id IS NULL) OR (personal_id IS NULL)))
);


ALTER TABLE public.control_cambios OWNER TO postgres;

--
-- Name: control_cambios_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.control_cambios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.control_cambios_id_seq OWNER TO postgres;

--
-- Name: control_cambios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.control_cambios_id_seq OWNED BY public.control_cambios.id;


--
-- Name: correo_saliente; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.correo_saliente (
    id integer NOT NULL,
    destinatario character varying(255) NOT NULL,
    asunto character varying(255) NOT NULL,
    cuerpo text NOT NULL,
    estado character varying(20) NOT NULL,
    intentos integer NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    enviado_en timestamp with time zone,
    es_html boolean DEFAULT false NOT NULL,
    adjunto_nombre character varying(255),
    adjunto_content_type character varying(100),
    adjunto_contenido text,
    CONSTRAINT correo_saliente_estado_check CHECK (((estado)::text = ANY ((ARRAY['pendiente'::character varying, 'enviado'::character varying, 'fallido'::character varying])::text[])))
);


ALTER TABLE public.correo_saliente OWNER TO postgres;

--
-- Name: correo_saliente_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.correo_saliente_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.correo_saliente_id_seq OWNER TO postgres;

--
-- Name: correo_saliente_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.correo_saliente_id_seq OWNED BY public.correo_saliente.id;


--
-- Name: ensayos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ensayos (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    zona_id integer NOT NULL,
    estado character varying(20) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by integer,
    updated_by integer,
    CONSTRAINT ck_ensayos_estado CHECK (((estado)::text = ANY ((ARRAY['activo'::character varying, 'inactivo'::character varying, 'mantenimiento'::character varying])::text[])))
);


ALTER TABLE public.ensayos OWNER TO postgres;

--
-- Name: ensayos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ensayos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ensayos_id_seq OWNER TO postgres;

--
-- Name: ensayos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ensayos_id_seq OWNED BY public.ensayos.id;


--
-- Name: espacio_recursos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.espacio_recursos (
    id integer NOT NULL,
    espacio_id integer NOT NULL,
    recurso_id integer NOT NULL
);


ALTER TABLE public.espacio_recursos OWNER TO postgres;

--
-- Name: espacios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.espacios (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    laboratorio_id integer NOT NULL,
    descripcion text,
    capacidad integer,
    estado character varying(20) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by integer,
    updated_by integer,
    CONSTRAINT ck_espacios_estado CHECK (((estado)::text = ANY ((ARRAY['activo'::character varying, 'inactivo'::character varying, 'mantenimiento'::character varying])::text[])))
);


ALTER TABLE public.espacios OWNER TO postgres;

--
-- Name: laboratorios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.laboratorios (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    ubicacion character varying(200) NOT NULL,
    capacidad integer NOT NULL,
    estado character varying(20) NOT NULL,
    descripcion text,
    dias_atencion json DEFAULT '[0, 1, 2, 3, 4, 5]'::jsonb NOT NULL,
    hora_apertura time without time zone DEFAULT '07:00:00'::time without time zone NOT NULL,
    hora_cierre time without time zone DEFAULT '20:00:00'::time without time zone NOT NULL,
    horario_atencion json DEFAULT '{}'::jsonb NOT NULL,
    horas_antelacion integer DEFAULT 24 NOT NULL,
    aprobacion_automatica boolean DEFAULT false NOT NULL,
    modalidad_reserva character varying(20) DEFAULT 'equipos'::character varying NOT NULL,
    correo character varying(255),
    create_at timestamp with time zone,
    updated_at timestamp with time zone,
    created_by integer,
    updated_by integer,
    notificar_por_correo boolean DEFAULT true NOT NULL,
    CONSTRAINT ck_espacios_modalidad_reserva CHECK (((modalidad_reserva)::text = ANY ((ARRAY['equipos'::character varying, 'zonas'::character varying, 'mixto'::character varying])::text[]))),
    CONSTRAINT ck_laboratorios_horario_atencion CHECK ((hora_apertura < hora_cierre)),
    CONSTRAINT ck_laboratorios_horas_antelacion CHECK ((horas_antelacion >= 0))
);


ALTER TABLE public.laboratorios OWNER TO postgres;

--
-- Name: espacios_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.espacios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.espacios_id_seq OWNER TO postgres;

--
-- Name: espacios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.espacios_id_seq OWNED BY public.laboratorios.id;


--
-- Name: evento_calendario_saliente; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.evento_calendario_saliente (
    id integer NOT NULL,
    reserva_id integer,
    accion character varying(20) NOT NULL,
    estado character varying(20) NOT NULL,
    intentos integer NOT NULL,
    graph_event_id character varying(255),
    asunto character varying(255),
    cuerpo text,
    ubicacion character varying(255),
    inicio timestamp with time zone,
    fin timestamp with time zone,
    asistentes json,
    comentario text,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    procesado_en timestamp with time zone,
    CONSTRAINT ck_evento_calendario_saliente_accion CHECK (((accion)::text = ANY ((ARRAY['crear'::character varying, 'actualizar'::character varying, 'cancelar'::character varying])::text[]))),
    CONSTRAINT ck_evento_calendario_saliente_estado CHECK (((estado)::text = ANY ((ARRAY['pendiente'::character varying, 'enviado'::character varying, 'fallido'::character varying])::text[])))
);


ALTER TABLE public.evento_calendario_saliente OWNER TO postgres;

--
-- Name: evento_calendario_saliente_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.evento_calendario_saliente_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.evento_calendario_saliente_id_seq OWNER TO postgres;

--
-- Name: evento_calendario_saliente_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.evento_calendario_saliente_id_seq OWNED BY public.evento_calendario_saliente.id;


--
-- Name: lista_espera; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lista_espera (
    id integer NOT NULL,
    usuario_id integer,
    personal_id integer,
    recurso_id integer NOT NULL,
    fecha date NOT NULL,
    hora_inicio time without time zone NOT NULL,
    hora_fin time without time zone NOT NULL,
    estado character varying(20) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    notificada_en timestamp with time zone,
    CONSTRAINT ck_lista_espera_actor_unico CHECK (((usuario_id IS NOT NULL) <> (personal_id IS NOT NULL))),
    CONSTRAINT ck_lista_espera_estado CHECK (((estado)::text = ANY ((ARRAY['activa'::character varying, 'notificada'::character varying, 'cancelada'::character varying, 'expirada'::character varying])::text[]))),
    CONSTRAINT ck_lista_espera_horario_valido CHECK ((hora_inicio < hora_fin))
);


ALTER TABLE public.lista_espera OWNER TO postgres;

--
-- Name: lista_espera_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.lista_espera_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lista_espera_id_seq OWNER TO postgres;

--
-- Name: lista_espera_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.lista_espera_id_seq OWNED BY public.lista_espera.id;


--
-- Name: motivos_solicitud; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.motivos_solicitud (
    id integer NOT NULL,
    laboratorio_id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    codigo character varying(30) NOT NULL,
    estado character varying(20) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by integer,
    updated_by integer,
    CONSTRAINT ck_motivos_solicitud_codigo CHECK (((codigo)::text = ANY ((ARRAY['reserva_en_laboratorio'::character varying, 'reserva_fuera_laboratorio'::character varying, 'orden_salida'::character varying])::text[]))),
    CONSTRAINT ck_motivos_solicitud_estado CHECK (((estado)::text = ANY ((ARRAY['activo'::character varying, 'inactivo'::character varying])::text[])))
);


ALTER TABLE public.motivos_solicitud OWNER TO postgres;

--
-- Name: motivos_solicitud_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.motivos_solicitud_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.motivos_solicitud_id_seq OWNER TO postgres;

--
-- Name: motivos_solicitud_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.motivos_solicitud_id_seq OWNED BY public.motivos_solicitud.id;


--
-- Name: notificaciones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notificaciones (
    id integer NOT NULL,
    usuario_id integer,
    reserva_id integer,
    tipo character varying(20) NOT NULL,
    leida boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    personal_id integer,
    CONSTRAINT ck_notificaciones_actor_unico CHECK (((usuario_id IS NOT NULL) <> (personal_id IS NOT NULL))),
    CONSTRAINT notificaciones_tipo_check CHECK (((tipo)::text = ANY ((ARRAY['Pendiente'::character varying, 'Aprobada'::character varying, 'Rechazada'::character varying, 'Cancelada'::character varying, 'Actualizada'::character varying])::text[])))
);


ALTER TABLE public.notificaciones OWNER TO postgres;

--
-- Name: notificaciones_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notificaciones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.notificaciones_id_seq OWNER TO postgres;

--
-- Name: notificaciones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notificaciones_id_seq OWNED BY public.notificaciones.id;


--
-- Name: personal; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.personal (
    id integer NOT NULL,
    username character varying(80) NOT NULL,
    email character varying(255) NOT NULL,
    supabase_id uuid,
    rol character varying(20) NOT NULL,
    documento_identificacion character varying(30),
    telefono character varying(30),
    institucion character varying(120),
    vinculacion character varying(30),
    dependencia character varying(150),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    recibir_correos boolean DEFAULT true NOT NULL,
    CONSTRAINT ck_personal_rol CHECK (((rol)::text = ANY ((ARRAY['admin'::character varying, 'gestor'::character varying])::text[]))),
    CONSTRAINT ck_personal_vinculacion CHECK (((vinculacion IS NULL) OR ((vinculacion)::text = ANY ((ARRAY['docente'::character varying, 'estudiante'::character varying, 'contratista_empleado'::character varying, 'extension'::character varying, 'otra'::character varying])::text[]))))
);


ALTER TABLE public.personal OWNER TO postgres;

--
-- Name: personal_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.personal_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.personal_id_seq OWNER TO postgres;

--
-- Name: personal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.personal_id_seq OWNED BY public.personal.id;


--
-- Name: recursos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recursos (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    laboratorio_id integer NOT NULL,
    tipo_recurso_id integer NOT NULL,
    descripcion text,
    capacidad integer NOT NULL,
    estado character varying(30) NOT NULL,
    es_prestacion_servicio boolean DEFAULT false NOT NULL,
    create_at timestamp with time zone DEFAULT now() NOT NULL,
    update_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by integer,
    update_by integer,
    placa character varying(50),
    requiere_apoyo_auxiliar boolean DEFAULT false NOT NULL
);


ALTER TABLE public.recursos OWNER TO postgres;

--
-- Name: recursos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.recursos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.recursos_id_seq OWNER TO postgres;

--
-- Name: recursos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.recursos_id_seq OWNED BY public.recursos.id;


--
-- Name: reserva_acompanantes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reserva_acompanantes (
    id integer NOT NULL,
    reserva_id integer NOT NULL,
    nombre character varying(150) NOT NULL,
    correo character varying(255) NOT NULL
);


ALTER TABLE public.reserva_acompanantes OWNER TO postgres;

--
-- Name: reserva_acompanantes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reserva_acompanantes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.reserva_acompanantes_id_seq OWNER TO postgres;

--
-- Name: reserva_acompanantes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reserva_acompanantes_id_seq OWNED BY public.reserva_acompanantes.id;


--
-- Name: reserva_ensayos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reserva_ensayos (
    id integer NOT NULL,
    reserva_id integer NOT NULL,
    ensayo_id integer NOT NULL
);


ALTER TABLE public.reserva_ensayos OWNER TO postgres;

--
-- Name: reserva_ensayos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reserva_ensayos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.reserva_ensayos_id_seq OWNER TO postgres;

--
-- Name: reserva_ensayos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reserva_ensayos_id_seq OWNED BY public.reserva_ensayos.id;


--
-- Name: reserva_espacios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reserva_espacios (
    id integer NOT NULL,
    reserva_id integer NOT NULL,
    espacio_id integer NOT NULL,
    fecha date NOT NULL,
    hora_inicio time without time zone NOT NULL,
    hora_fin time without time zone NOT NULL,
    estado character varying(20) NOT NULL
);


ALTER TABLE public.reserva_espacios OWNER TO postgres;

--
-- Name: reserva_recursos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reserva_recursos (
    id integer NOT NULL,
    reserva_id integer NOT NULL,
    recurso_id integer NOT NULL,
    fecha date NOT NULL,
    hora_inicio time without time zone NOT NULL,
    hora_fin time without time zone NOT NULL,
    estado character varying(20) NOT NULL
);


ALTER TABLE public.reserva_recursos OWNER TO postgres;

--
-- Name: reserva_recursos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reserva_recursos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.reserva_recursos_id_seq OWNER TO postgres;

--
-- Name: reserva_recursos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reserva_recursos_id_seq OWNED BY public.reserva_recursos.id;


--
-- Name: reserva_zonas_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reserva_zonas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.reserva_zonas_id_seq OWNER TO postgres;

--
-- Name: reserva_zonas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reserva_zonas_id_seq OWNED BY public.reserva_espacios.id;


--
-- Name: reservas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reservas (
    id integer NOT NULL,
    usuario_id integer,
    laboratorio_id integer NOT NULL,
    recurso_id integer NOT NULL,
    fecha date NOT NULL,
    hora_inicio time without time zone NOT NULL,
    hora_fin time without time zone NOT NULL,
    estado character varying(20) NOT NULL,
    asistentes integer NOT NULL,
    tipo character varying(30),
    asistio boolean,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    motivo_rechazo text,
    descripcion text,
    tipo_solicitud character varying(30) DEFAULT 'reserva_en_laboratorio'::character varying NOT NULL,
    ubicacion_uso character varying(200),
    requiere_apoyo_auxiliar boolean DEFAULT false NOT NULL,
    personal_id integer,
    recordatorio_enviado_en timestamp with time zone,
    serie_id uuid,
    tipo_reserva_id integer,
    propuesta_motivo text,
    propuesta_horarios text,
    propuesta_por character varying(20),
    propuesta_en timestamp with time zone,
    motivo_solicitud_id integer,
    grupo_id uuid,
    graph_event_id character varying(255),
    calendario_secuencia integer DEFAULT 0 NOT NULL,
    CONSTRAINT ck_reservas_actor_unico CHECK (((usuario_id IS NOT NULL) <> (personal_id IS NOT NULL))),
    CONSTRAINT ck_reservas_asistentes_positivos CHECK ((asistentes > 0)),
    CONSTRAINT ck_reservas_estado CHECK (((estado)::text = ANY ((ARRAY['esperando'::character varying, 'aprobada'::character varying, 'rechazada'::character varying, 'cancelada'::character varying])::text[]))),
    CONSTRAINT ck_reservas_horario_valido CHECK ((hora_inicio < hora_fin)),
    CONSTRAINT ck_reservas_propuesta_por CHECK (((propuesta_por IS NULL) OR ((propuesta_por)::text = ANY ((ARRAY['tecnico'::character varying, 'usuario'::character varying])::text[])))),
    CONSTRAINT ck_reservas_tipo CHECK (((tipo)::text = ANY ((ARRAY['trabajo_investigacion'::character varying, 'trabajo_grado'::character varying, 'servicio_de_ensayo'::character varying])::text[]))),
    CONSTRAINT ck_reservas_tipo_solicitud CHECK (((tipo_solicitud)::text = ANY ((ARRAY['reserva_en_laboratorio'::character varying, 'reserva_fuera_laboratorio'::character varying])::text[])))
);


ALTER TABLE public.reservas OWNER TO postgres;

--
-- Name: reservas_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reservas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.reservas_id_seq OWNER TO postgres;

--
-- Name: reservas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reservas_id_seq OWNED BY public.reservas.id;


--
-- Name: tipos_recursos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tipos_recursos (
    id integer NOT NULL,
    nombre character varying(80) NOT NULL,
    descripcion text NOT NULL,
    activo character varying(50) NOT NULL
);


ALTER TABLE public.tipos_recursos OWNER TO postgres;

--
-- Name: tipos_recursos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tipos_recursos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tipos_recursos_id_seq OWNER TO postgres;

--
-- Name: tipos_recursos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tipos_recursos_id_seq OWNED BY public.tipos_recursos.id;


--
-- Name: tipos_reserva; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tipos_reserva (
    id integer NOT NULL,
    laboratorio_id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    estado character varying(20) DEFAULT 'activo'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by integer,
    updated_by integer,
    CONSTRAINT ck_tipos_reserva_estado CHECK (((estado)::text = ANY ((ARRAY['activo'::character varying, 'inactivo'::character varying])::text[])))
);


ALTER TABLE public.tipos_reserva OWNER TO postgres;

--
-- Name: tipos_reserva_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tipos_reserva_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tipos_reserva_id_seq OWNER TO postgres;

--
-- Name: tipos_reserva_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tipos_reserva_id_seq OWNED BY public.tipos_reserva.id;


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuarios (
    id integer NOT NULL,
    username character varying(80) NOT NULL,
    email character varying(255) NOT NULL,
    hashed_password character varying(255) NOT NULL,
    rol character varying(20) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    debe_cambiar_password boolean DEFAULT false NOT NULL,
    supabase_id uuid,
    documento_identificacion character varying(30),
    telefono character varying(30),
    institucion character varying(120),
    vinculacion character varying(30),
    dependencia character varying(150),
    recibir_correos boolean DEFAULT true NOT NULL,
    CONSTRAINT ck_usuarios_vinculacion CHECK (((vinculacion IS NULL) OR ((vinculacion)::text = ANY ((ARRAY['docente'::character varying, 'estudiante'::character varying, 'contratista_empleado'::character varying, 'extension'::character varying, 'otra'::character varying])::text[]))))
);


ALTER TABLE public.usuarios OWNER TO postgres;

--
-- Name: usuarios_laboratorios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuarios_laboratorios (
    id integer NOT NULL,
    usuario_id integer NOT NULL,
    laboratorio_id integer NOT NULL
);


ALTER TABLE public.usuarios_laboratorios OWNER TO postgres;

--
-- Name: usuarios_espacios_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usuarios_espacios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.usuarios_espacios_id_seq OWNER TO postgres;

--
-- Name: usuarios_espacios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuarios_espacios_id_seq OWNED BY public.usuarios_laboratorios.id;


--
-- Name: usuarios_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.usuarios_id_seq OWNER TO postgres;

--
-- Name: usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuarios_id_seq OWNED BY public.usuarios.id;


--
-- Name: zona_recursos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.zona_recursos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.zona_recursos_id_seq OWNER TO postgres;

--
-- Name: zona_recursos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.zona_recursos_id_seq OWNED BY public.espacio_recursos.id;


--
-- Name: zonas_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.zonas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.zonas_id_seq OWNER TO postgres;

--
-- Name: zonas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.zonas_id_seq OWNED BY public.espacios.id;


--
-- Name: control_cambios id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.control_cambios ALTER COLUMN id SET DEFAULT nextval('public.control_cambios_id_seq'::regclass);


--
-- Name: correo_saliente id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.correo_saliente ALTER COLUMN id SET DEFAULT nextval('public.correo_saliente_id_seq'::regclass);


--
-- Name: ensayos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ensayos ALTER COLUMN id SET DEFAULT nextval('public.ensayos_id_seq'::regclass);


--
-- Name: espacio_recursos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.espacio_recursos ALTER COLUMN id SET DEFAULT nextval('public.zona_recursos_id_seq'::regclass);


--
-- Name: espacios id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.espacios ALTER COLUMN id SET DEFAULT nextval('public.zonas_id_seq'::regclass);


--
-- Name: evento_calendario_saliente id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evento_calendario_saliente ALTER COLUMN id SET DEFAULT nextval('public.evento_calendario_saliente_id_seq'::regclass);


--
-- Name: laboratorios id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.laboratorios ALTER COLUMN id SET DEFAULT nextval('public.espacios_id_seq'::regclass);


--
-- Name: lista_espera id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lista_espera ALTER COLUMN id SET DEFAULT nextval('public.lista_espera_id_seq'::regclass);


--
-- Name: motivos_solicitud id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.motivos_solicitud ALTER COLUMN id SET DEFAULT nextval('public.motivos_solicitud_id_seq'::regclass);


--
-- Name: notificaciones id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notificaciones ALTER COLUMN id SET DEFAULT nextval('public.notificaciones_id_seq'::regclass);


--
-- Name: personal id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personal ALTER COLUMN id SET DEFAULT nextval('public.personal_id_seq'::regclass);


--
-- Name: recursos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recursos ALTER COLUMN id SET DEFAULT nextval('public.recursos_id_seq'::regclass);


--
-- Name: reserva_acompanantes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_acompanantes ALTER COLUMN id SET DEFAULT nextval('public.reserva_acompanantes_id_seq'::regclass);


--
-- Name: reserva_ensayos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_ensayos ALTER COLUMN id SET DEFAULT nextval('public.reserva_ensayos_id_seq'::regclass);


--
-- Name: reserva_espacios id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_espacios ALTER COLUMN id SET DEFAULT nextval('public.reserva_zonas_id_seq'::regclass);


--
-- Name: reserva_recursos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_recursos ALTER COLUMN id SET DEFAULT nextval('public.reserva_recursos_id_seq'::regclass);


--
-- Name: reservas id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservas ALTER COLUMN id SET DEFAULT nextval('public.reservas_id_seq'::regclass);


--
-- Name: tipos_recursos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipos_recursos ALTER COLUMN id SET DEFAULT nextval('public.tipos_recursos_id_seq'::regclass);


--
-- Name: tipos_reserva id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipos_reserva ALTER COLUMN id SET DEFAULT nextval('public.tipos_reserva_id_seq'::regclass);


--
-- Name: usuarios id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id SET DEFAULT nextval('public.usuarios_id_seq'::regclass);


--
-- Name: usuarios_laboratorios id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios_laboratorios ALTER COLUMN id SET DEFAULT nextval('public.usuarios_espacios_id_seq'::regclass);


--
-- Data for Name: control_cambios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.control_cambios (id, usuario_id, accion, entidad, entidad_id, descripcion, created_at, personal_id) FROM stdin;
8	\N	crear	reserva	1	Creó una reserva de los recursos Prueba con estado esperando	2026-08-19 16:27:02.324294+00	\N
1	\N	crear	usuario	2	Creó el usuario Santi con rol gestor	2026-08-19 16:21:26.823154+00	1
2	\N	crear	usuario	3	Creó el usuario reserva con rol usuario	2026-08-19 16:21:51.432834+00	1
4	\N	actualizar	espacio	5	Actualizó el espacio Auditorio Pequeño	2026-08-19 16:24:19.596526+00	1
5	\N	actualizar	espacio	5	Actualizó el espacio Auditorio Pequeño	2026-08-19 16:24:21.641706+00	1
6	\N	actualizar	espacio	5	Actualizó el espacio Auditorio Pequeño	2026-08-19 16:26:20.534216+00	1
7	\N	actualizar	recurso	1	Actualizó el recurso Prueba	2026-08-19 16:26:31.107812+00	1
9	\N	actualizar	usuario	2	Actualizó el usuario Santi	2026-08-24 17:32:31.112219+00	1
10	\N	actualizar	usuario	2	Actualizó el usuario Santi	2026-08-24 17:33:35.264579+00	1
12	\N	actualizar	usuario	3	Actualizó el usuario reserva	2026-08-25 19:29:52.815668+00	1
13	\N	actualizar	usuario	2	Actualizó el usuario Santi	2026-08-25 19:31:34.184359+00	1
14	\N	actualizar	usuario	3	Actualizó el usuario reserva	2026-08-25 20:11:20.95154+00	1
15	\N	actualizar	usuario	2	Actualizó el usuario Santi	2026-08-25 20:11:35.308208+00	1
16	\N	crear	usuario	4	Creó el usuario Santiago con rol usuario	2026-08-27 04:10:22.07539+00	1
17	\N	eliminar	usuario	4	Eliminó el usuario Santiago	2026-08-27 04:36:08.63269+00	1
18	\N	crear	usuario	5	Creó el usuario Santiago con rol usuario	2026-08-27 04:37:40.749606+00	1
19	\N	eliminar	usuario	3	Eliminó el usuario reserva	2026-08-27 19:16:29.470707+00	1
20	\N	actualizar	usuario	2	Actualizó el usuario Santi	2026-08-27 19:16:40.907196+00	1
21	\N	crear	usuario	6	Creó el usuario Prueba con rol gestor	2026-08-27 19:23:51.554579+00	1
22	\N	actualizar	usuario	6	Actualizó el usuario Prueba	2026-08-27 19:25:10.788987+00	1
23	\N	eliminar	usuario	5	Eliminó el usuario Santiago	2026-08-27 19:26:02.005291+00	1
24	\N	reenviar_invitacion	usuario	6	Reenvió la invitación a Prueba	2026-08-27 19:26:06.617535+00	1
25	\N	reenviar_invitacion	usuario	6	Reenvió la invitación a Prueba	2026-08-28 03:03:42.209897+00	1
26	\N	reenviar_invitacion	usuario	6	Reenvió la invitación a Prueba	2026-08-28 03:04:10.112317+00	1
27	\N	eliminar	usuario	6	Eliminó el usuario Prueba	2026-08-28 03:04:53.944605+00	1
28	\N	crear	usuario	7	Creó el usuario Prueba con rol usuario	2026-08-28 03:06:10.769259+00	1
29	\N	crear	usuario	8	Creó el usuario Lia con rol usuario	2026-08-28 17:47:45.767969+00	1
3	\N	crear	recurso	1	Creó el recurso Prueba	2026-08-19 16:23:13.425952+00	2
11	\N	configurar	espacio	5	Actualizó las reglas de reserva de Auditorio Pequeño	2026-08-24 21:15:03.367696+00	2
30	\N	eliminar	usuario	8	Eliminó el usuario Lia	2026-08-28 19:18:45.782753+00	1
31	\N	eliminar	usuario	7	Eliminó el usuario Prueba	2026-08-28 19:18:53.214798+00	1
32	\N	crear	usuario	9	Creó el usuario Prueba con rol usuario	2026-08-28 19:43:30.115211+00	1
33	\N	reenviar_invitacion	usuario	9	Reenvió la invitación a Prueba	2026-08-28 19:45:46.751928+00	1
34	\N	reenviar_invitacion	usuario	9	Reenvió la invitación a Prueba	2026-08-28 19:48:04.345592+00	1
35	\N	reenviar_invitacion	usuario	9	Reenvió la invitación a Prueba	2026-08-28 19:57:26.428192+00	1
36	\N	eliminar	usuario	9	Eliminó el usuario Prueba	2026-08-28 20:02:28.132248+00	1
37	\N	crear	usuario	10	Creó el usuario prueba con rol usuario	2026-08-28 22:38:38.59738+00	1
38	\N	crear	espacio	7	Creó el espacio Laboratorio de Sistemas de Control y Robotica	2026-09-01 16:27:07.907001+00	1
39	\N	crear	personal	2	Creó el personal juandorado con rol gestor	2026-09-01 16:27:50.117431+00	1
40	\N	eliminar	espacio	1	Eliminó el espacio Auditorio Principal	2026-09-01 16:38:40.416129+00	1
41	\N	eliminar	espacio	4	Eliminó el espacio Sala de Conferencias	2026-09-01 16:38:45.964517+00	1
42	\N	eliminar	espacio	6	Eliminó el espacio Sala de Estudio Grupales	2026-09-01 16:38:54.312077+00	1
43	\N	eliminar	espacio	3	Eliminó el espacio Laboratorio de Informática	2026-09-01 16:39:01.328845+00	1
44	\N	eliminar	espacio	2	Eliminó el espacio Sala de Juntas Ejecutiva	2026-09-01 16:39:04.375154+00	1
45	\N	eliminar	recurso	1	Eliminó el recurso Prueba	2026-09-01 16:39:22.628377+00	1
49	\N	crear	personal	3	Creó el personal Juan Carlos Morales con rol gestor	2026-09-01 16:40:45.285223+00	1
50	\N	eliminar	personal	3	Eliminó el personal Juan Carlos Morales	2026-09-01 16:42:11.998049+00	1
51	\N	crear	personal	4	Creó el personal Juan Carlos Morales con rol gestor	2026-09-01 16:42:38.917752+00	1
52	\N	crear	recurso	2	Creó el recurso Mesa 1	2026-09-01 18:14:55.641113+00	4
53	\N	configurar	espacio	7	Actualizó las reglas de reserva de Laboratorio de Sistemas de Control y Robotica	2026-09-01 18:15:27.938004+00	4
55	\N	actualizar	reserva	2	Actualizó la reserva #2	2026-09-01 18:19:43.569571+00	4
56	\N	cambiar estado	reserva	2	Cambió la reserva #2 de esperando a aprobada	2026-09-01 18:20:35.320716+00	4
57	\N	eliminar	reserva	2	Eliminó la reserva #2	2026-09-01 18:24:36.648445+00	4
58	\N	crear	reserva	3	Creó una reserva de los recursos Mesa 1 con estado aprobada	2026-09-01 18:28:17.443299+00	4
59	\N	crear	recurso	3	Creó el recurso Impresora 3D	2026-09-01 18:29:05.473118+00	4
60	\N	actualizar	reserva	3	Actualizó la reserva #3	2026-09-01 18:29:18.061294+00	4
61	\N	crear	reserva	4	Creó una reserva de los recursos Impresora 3D, Mesa 1 con estado aprobada	2026-09-01 18:47:45.191681+00	4
62	\N	crear	reserva	5	Creó una reserva de los recursos Impresora 3D con estado aprobada	2026-09-01 18:48:53.9029+00	4
63	\N	configurar	laboratorio	7	Actualizó las reglas de reserva de Laboratorio de Sistemas de Control y Robotica	2026-09-02 20:58:28.661774+00	4
64	\N	crear	reserva	6	Creó una reserva de los recursos Impresora 3D con estado aprobada	2026-09-02 21:01:03.076395+00	4
54	\N	crear	reserva	2	Creó una reserva de los recursos Mesa 1 con estado esperando	2026-09-01 18:15:54.401169+00	\N
65	\N	eliminar	usuario	11	Eliminó el usuario Santiago	2026-09-06 00:30:47.182081+00	1
66	\N	crear	personal	5	Creó el personal Santiago con rol gestor	2026-09-06 00:31:02.9237+00	1
\.


--
-- Data for Name: correo_saliente; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.correo_saliente (id, destinatario, asunto, cuerpo, estado, intentos, creado_en, enviado_en, es_html, adjunto_nombre, adjunto_content_type, adjunto_contenido) FROM stdin;
1	santiago32296@gmail.com	Invitación a Reservas Parque i	Hola Prueba,\n\nTe reenviamos el link para completar tu cuenta en Reservas Parque i:\n\nhttps://ijktwqnkknemjrokwcdn.supabase.co/auth/v1/verify?token=9e24f0a042a1069497006c0c52e5f5ac3388169aad086728ff8a3b1b&type=invite&redirect_to=http://172.20.10.18:8091/completar-cuenta\n\nSi no esperabas este correo, podés ignorarlo.	enviado	0	2026-08-27 19:26:06.617535+00	2026-08-28 19:57:18.024833+00	f	\N	\N	\N
2	santiago32296@gmail.com	Invitación a Reservas Parque i	Hola Prueba,\n\nTe reenviamos el link para completar tu cuenta en Reservas Parque i:\n\nhttps://ijktwqnkknemjrokwcdn.supabase.co/auth/v1/verify?token=f6d909dd195475d389c30c5b6648af2fc5fa8d1954c8ee7c01e80238&type=invite&redirect_to=http://172.20.10.18:8091/completar-cuenta\n\nSi no esperabas este correo, podés ignorarlo.	enviado	0	2026-08-28 03:03:42.209897+00	2026-08-28 19:57:19.325991+00	f	\N	\N	\N
3	santiago32296@gmail.com	Invitación a Reservas Parque i	Hola Prueba,\n\nTe reenviamos el link para completar tu cuenta en Reservas Parque i:\n\nhttps://ijktwqnkknemjrokwcdn.supabase.co/auth/v1/verify?token=9eb8ec58fc62dcad449fdf1d79f1ff237002bf7ce2dcab26d467ac8a&type=invite&redirect_to=http://172.20.10.18:8091/completar-cuenta\n\nSi no esperabas este correo, podés ignorarlo.	enviado	0	2026-08-28 03:04:10.112317+00	2026-08-28 19:57:20.462405+00	f	\N	\N	\N
4	sgc-lia@itm.edu.co	Invitación a Reservas Parque i	<!DOCTYPE html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i</title>\n</head>\n<body style="margin:0;padding:0;background-color:#f1f5f9;font-family:Arial,Helvetica,sans-serif;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f1f5f9;padding:32px 16px;">\n<tr>\n<td align="center">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:520px;background-color:#ffffff;border-radius:16px;overflow:hidden;border:1px solid #e2e8f0;">\n<tr>\n<td style="background-image:linear-gradient(135deg,#1e3a8a,#10b981);background-color:#1e3a8a;padding:28px 32px;">\n<span style="display:block;font-size:11px;letter-spacing:1px;text-transform:uppercase;color:#dbeafe;font-weight:700;">Instituto Tecnologico Metropolitano</span>\n<span style="display:block;font-size:20px;font-weight:800;color:#ffffff;margin-top:4px;">Reservas Parque i</span>\n</td>\n</tr>\n<tr>\n<td style="padding:32px;">\n<p style="margin:0 0 16px;font-size:16px;line-height:1.5;color:#0f172a;">Hola Prueba,</p>\n<p style="margin:0 0 24px;font-size:15px;line-height:1.6;color:#334155;">\nTe invitaron a crear tu cuenta en el <strong>Sistema de Reservas de Laboratorios</strong> del Parque i.\nCon ella vas a poder reservar espacios y equipos, y hacer seguimiento a tus solicitudes.\n</p>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 0 24px;">\n<tr>\n<td style="border-radius:10px;background-color:#1e3a8a;">\n<a href="https://ijktwqnkknemjrokwcdn.supabase.co/auth/v1/verify?token=b395c274f96a3da729f2dbd731f4d1c1f024a713c1c0e745c4e75bfd&amp;type=invite&amp;redirect_to=http://172.20.10.18:8091/completar-cuenta" style="display:inline-block;padding:14px 28px;font-size:15px;font-weight:700;color:#ffffff;text-decoration:none;border-radius:10px;">Crear mi cuenta</a>\n</td>\n</tr>\n</table>\n<p style="margin:0 0 8px;font-size:13px;line-height:1.5;color:#64748b;">Si el boton no funciona, copia y pega este link en tu navegador:</p>\n<p style="margin:0 0 24px;font-size:13px;line-height:1.5;word-break:break-all;"><a href="https://ijktwqnkknemjrokwcdn.supabase.co/auth/v1/verify?token=b395c274f96a3da729f2dbd731f4d1c1f024a713c1c0e745c4e75bfd&amp;type=invite&amp;redirect_to=http://172.20.10.18:8091/completar-cuenta" style="color:#1e3a8a;">https://ijktwqnkknemjrokwcdn.supabase.co/auth/v1/verify?token=b395c274f96a3da729f2dbd731f4d1c1f024a713c1c0e745c4e75bfd&amp;type=invite&amp;redirect_to=http://172.20.10.18:8091/completar-cuenta</a></p>\n<p style="margin:0;font-size:13px;line-height:1.5;color:#94a3b8;">Si vos no solicitaste esta cuenta, podes ignorar este correo.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:20px 32px;background-color:#f8fafc;border-top:1px solid #e2e8f0;">\n<p style="margin:0;font-size:12px;color:#94a3b8;">Este es un mensaje automatico del Sistema de Reservas de Laboratorios - Parque i, ITM. No respondas a este correo.</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-08-28 19:45:46.751928+00	2026-08-28 19:57:21.639009+00	t	\N	\N	\N
5	sgc-lia@itm.edu.co	Invitación a Reservas Parque i	<!DOCTYPE html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i</title>\n</head>\n<body style="margin:0;padding:0;background-color:#f1f5f9;font-family:Arial,Helvetica,sans-serif;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f1f5f9;padding:32px 16px;">\n<tr>\n<td align="center">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:520px;background-color:#ffffff;border-radius:16px;overflow:hidden;border:1px solid #e2e8f0;">\n<tr>\n<td style="background-image:linear-gradient(135deg,#1e3a8a,#10b981);background-color:#1e3a8a;padding:28px 32px;">\n<span style="display:block;font-size:11px;letter-spacing:1px;text-transform:uppercase;color:#dbeafe;font-weight:700;">Instituto Tecnologico Metropolitano</span>\n<span style="display:block;font-size:20px;font-weight:800;color:#ffffff;margin-top:4px;">Reservas Parque i</span>\n</td>\n</tr>\n<tr>\n<td style="padding:32px;">\n<p style="margin:0 0 16px;font-size:16px;line-height:1.5;color:#0f172a;">Hola Prueba,</p>\n<p style="margin:0 0 24px;font-size:15px;line-height:1.6;color:#334155;">\nTe invitaron a crear tu cuenta en el <strong>Sistema de Reservas de Laboratorios</strong> del Parque i.\nCon ella vas a poder reservar espacios y equipos, y hacer seguimiento a tus solicitudes.\n</p>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 0 24px;">\n<tr>\n<td style="border-radius:10px;background-color:#1e3a8a;">\n<a href="https://ijktwqnkknemjrokwcdn.supabase.co/auth/v1/verify?token=41b6d8bd1fb9371a7b3e8a7da10363a4781199b3d556ccf856ea20c8&amp;type=invite&amp;redirect_to=http://172.20.10.18:8091/completar-cuenta" style="display:inline-block;padding:14px 28px;font-size:15px;font-weight:700;color:#ffffff;text-decoration:none;border-radius:10px;">Crear mi cuenta</a>\n</td>\n</tr>\n</table>\n<p style="margin:0 0 8px;font-size:13px;line-height:1.5;color:#64748b;">Si el boton no funciona, copia y pega este link en tu navegador:</p>\n<p style="margin:0 0 24px;font-size:13px;line-height:1.5;word-break:break-all;"><a href="https://ijktwqnkknemjrokwcdn.supabase.co/auth/v1/verify?token=41b6d8bd1fb9371a7b3e8a7da10363a4781199b3d556ccf856ea20c8&amp;type=invite&amp;redirect_to=http://172.20.10.18:8091/completar-cuenta" style="color:#1e3a8a;">https://ijktwqnkknemjrokwcdn.supabase.co/auth/v1/verify?token=41b6d8bd1fb9371a7b3e8a7da10363a4781199b3d556ccf856ea20c8&amp;type=invite&amp;redirect_to=http://172.20.10.18:8091/completar-cuenta</a></p>\n<p style="margin:0;font-size:13px;line-height:1.5;color:#94a3b8;">Si vos no solicitaste esta cuenta, podes ignorar este correo.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:20px 32px;background-color:#f8fafc;border-top:1px solid #e2e8f0;">\n<p style="margin:0;font-size:12px;color:#94a3b8;">Este es un mensaje automatico del Sistema de Reservas de Laboratorios - Parque i, ITM. No respondas a este correo.</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-08-28 19:48:04.345592+00	2026-08-28 19:57:22.716631+00	t	\N	\N	\N
6	sgc-lia@itm.edu.co	Invitación a Reservas Parque i	<!DOCTYPE html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i</title>\n</head>\n<body style="margin:0;padding:0;background-color:#f1f5f9;font-family:Arial,Helvetica,sans-serif;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f1f5f9;padding:32px 16px;">\n<tr>\n<td align="center">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:520px;background-color:#ffffff;border-radius:16px;overflow:hidden;border:1px solid #e2e8f0;">\n<tr>\n<td style="background-image:linear-gradient(135deg,#1e3a8a,#10b981);background-color:#1e3a8a;padding:28px 32px;">\n<span style="display:block;font-size:11px;letter-spacing:1px;text-transform:uppercase;color:#dbeafe;font-weight:700;">Instituto Tecnologico Metropolitano</span>\n<span style="display:block;font-size:20px;font-weight:800;color:#ffffff;margin-top:4px;">Reservas Parque i</span>\n</td>\n</tr>\n<tr>\n<td style="padding:32px;">\n<p style="margin:0 0 16px;font-size:16px;line-height:1.5;color:#0f172a;">Hola Prueba,</p>\n<p style="margin:0 0 24px;font-size:15px;line-height:1.6;color:#334155;">\nTe invitaron a crear tu cuenta en el <strong>Sistema de Reservas de Laboratorios</strong> del Parque i.\nCon ella vas a poder reservar espacios y equipos, y hacer seguimiento a tus solicitudes.\n</p>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 0 24px;">\n<tr>\n<td style="border-radius:10px;background-color:#1e3a8a;">\n<a href="https://ijktwqnkknemjrokwcdn.supabase.co/auth/v1/verify?token=d81325d3c660f3d65dcc8b0669421536b7b725d8f7ea61735b493020&amp;type=invite&amp;redirect_to=http://172.20.10.18:8091/completar-cuenta" style="display:inline-block;padding:14px 28px;font-size:15px;font-weight:700;color:#ffffff;text-decoration:none;border-radius:10px;">Crear mi cuenta</a>\n</td>\n</tr>\n</table>\n<p style="margin:0 0 8px;font-size:13px;line-height:1.5;color:#64748b;">Si el boton no funciona, copia y pega este link en tu navegador:</p>\n<p style="margin:0 0 24px;font-size:13px;line-height:1.5;word-break:break-all;"><a href="https://ijktwqnkknemjrokwcdn.supabase.co/auth/v1/verify?token=d81325d3c660f3d65dcc8b0669421536b7b725d8f7ea61735b493020&amp;type=invite&amp;redirect_to=http://172.20.10.18:8091/completar-cuenta" style="color:#1e3a8a;">https://ijktwqnkknemjrokwcdn.supabase.co/auth/v1/verify?token=d81325d3c660f3d65dcc8b0669421536b7b725d8f7ea61735b493020&amp;type=invite&amp;redirect_to=http://172.20.10.18:8091/completar-cuenta</a></p>\n<p style="margin:0;font-size:13px;line-height:1.5;color:#94a3b8;">Si vos no solicitaste esta cuenta, podes ignorar este correo.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:20px 32px;background-color:#f8fafc;border-top:1px solid #e2e8f0;">\n<p style="margin:0;font-size:12px;color:#94a3b8;">Este es un mensaje automatico del Sistema de Reservas de Laboratorios - Parque i, ITM. No respondas a este correo.</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-08-28 19:57:26.428192+00	2026-08-28 19:57:27.903423+00	t	\N	\N	\N
7	sgc-lia@itm.edu.co	Invitación a Reservas Parque i	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">¡Bienvenida/o! Ya podés crear tu cuenta en Reservas Parque i, Institución Universitaria ITM.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="data:image/png;base64,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" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" width="56%" valign="top">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">prueba</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:29px;line-height:1.28;color:#102d69;font-weight:800;">¡Bienvenida/o!<br>Ya podés crear tu cuenta</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n<td class="stack-col" width="6%">&nbsp;</td>\n<td class="stack-col" width="38%" valign="top">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-radius:12px;overflow:hidden;background-color:#fbfcfe;border:1px solid #edf1f6;">\n<tr>\n<td align="center" valign="middle" style="padding:14px;">\n<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQQAAADqCAMAAABz78t+AAAAwFBMVEVZmrDH0N+Vo8cemqQhR3osssVmo8hRaqIgPYRDVHo7aJ0IIF+s7vOAjrgABD76+/0XPIPa5vp5wdGUwueQvuWExtUbQIjk6vcUNnau2OgHKW14vc0Spba2xdfM2ecqSYgLmq0uqbtyh6w2VI0qRnequM+OutWqyeaGl7UAGFVOZ5PZ8/eVqMWs1dxFW42O0txme6YJJVrDzNoAHGQiO3QvrcCQo7uu4uhUd6eY2eNkd5p8kbRYc5kUqMEACFJwmcu/YIcWAAAAQHRSTlP/////////////////////////////////////////////////////////////////////////////////////73leyQAAD3JJREFUeNrtnQt/oroSwNF22909916IigmhgPLwge/Hqa1td7//t7qTgIoIvoqa7mZ+Z7tWcSH/zExmkkmOokpRFYlAQpAQJAQJQUKQECQECUFCkBAkBAlBQpAQJAQJQUKQECSELwIBr+SvgwBtRnkiCg/lwj2PDsvtSSi3BSCGSijXNgEROSgXIIDOlVtxUIQhcEMMhUL4JIGbcVCuqQWrOEE0DMrFEeR6vD048JeEgPN7/nAQeXMMygURfC6mwF8KAi6iIzMwXM81KMUzOPfhdzngrwIBF9l/OxzwV4CAi1bhNAYsPISL6G/aS2KxIaQZFPZQ11YGpTAGhT4rvuowoQjaXds2gcWEcHm7vSIFRVQG16SgiPx8+EoUFKH76EoUlKs9Wg/11i61d45/xCJBOIsBGj08VBas8YuKokSvTsWAxYFwFoNX5enj6alhqqrefHp6at4pvTPuh0WBcBaD/ygNDqFh6s1G44lhqJwVMogB4SwGvQpr91PjqXHX5K8+vj3dIVUYXfgEhOO/NLiLIHAd4AJvjFRhKChnx8onfMuA5nMCMYWPj9MgJChcJI9QztUDfBqERkINmHs4DYJ62SFCuQIDDuFpWxqNkSoMBeUKDFSkpBl8NO4WqjAUlLMcwqnP8Z9mI8WgcXygcHkKylWeovcAzvDjIwGhuVBVYSgolx0cNwbx9O0joQpN/VPTODeD8LlHWDQb36JQgTnJu4r6qcQN3wjCZ59g1OQMosFSQZ/MrG8D4fO9YNw1VhBOdoo7T4FvC+H82y/u+BDRuKv01E/P7uIbQCikCwwWLjSao14RU003gFDMvYHCXfNVLWRdBl8dQlG3RoqyUAtanbodBPXmguziVUG5oVMWRhVOgyAAg0s8zEnmIEZNOr4RBCwQg3jmFePrxwkYCbRVo+inkdt/JAQJQUK4EQS77z4Oh6Hbb/+tEHrPYeg5GojjDcOO/TdCCFyHUq3ugNQ1Qp33Pv7rIARzShzQg3okDhAp238ZhPKEfGeWUF+LppFh6Y+AcGwg3aGUgBHErQcW9wR+knB6XJXP5fM25ey03jDa7bZh2AcfsT+nda4FWsQgkjoh44NfRYYx0kejwcBA4kFAdrtWq1WrVfjZPoDBdqiTaPxaHOJ0DtxloLfMCohp6rotGgS73aqupdZq76OAXUfLYsAoeHtbZugtvaJzARAtCwkFwaimxd6nCGRtBRuvwH7WNcfd41QsPUJQicXUkUAQbCvNoLZHF/oEIDiJkUHbENH2qMIg1oJK5fIUToeAAn1HE6q5kbDNrKHurBloWxDmpXxb0PUUBN3Ue4JAQO0MBtVWXpdaw6j3U2oQQyDlvLvwxqcoVExDEAh2q1o9gUKwCQ+0pEOIf3NzNNwwdQ6hkqAALy5kECdDaOdAyOmkPq1vjw1rdeC2kRMwIdb6WBNWGNiLliEEBNSuZUKotbPttZyGsD1QDK1sr1jZgrC2DVMMCHY1R3IGiA6HUM+D4GVDGEVmoFfWIKIXlVFPBAhGi4WJWRSMXHP4vuMUtfp+TRhxRdiGEOmGLQqE6ikQ2CRC5tDAR4dxdqNgNNz4wzUE9mcgDITq8RCCNYJtDDGEnLmVCMJmmFwj+ZoQ7EdHy6WgzbOtQYXBobXxjYlIQRAIJzpG/EyyITAhHtoHIa0FlUsFCiePDu08CDl+25onIQCF7ysCdeK/5bTJSg2RK59gDgSJE7LtoZY3gqNxyh6+c1sghGh0iHIzhxwIYsQJeU4hP5YrzWFSpa5tGQS4RGCwZ1JlYFbSwRK3CFuQBMqyMgPGfGN9I8RJTrOuzIHumV4zkiPDxjMOREmlbat9EgNVdamWnmtmw2No7ZmPGqRsIVIEJMykyq4q1Kp7bdUeMw+gbbuG+dDaq3C6nqZgXih9Om96rX0aA2jR25zUE0GT4xDyfsC8UQqBXmldyBjOg9DbziRbLaN30JG8ELYGFQlbcwgOujiUgAB/TP1SenDmbDMy+PRSm6lETT9qTcDouCGhXIjndo5ZfUKLwcobmGZlgIRbfIFVEb74wtZfjv1OsBwyCZfP+OiRaK0NA1UVchmOLUKhnnpZ6S0Gl7+L+JUqGMtyHfVPO7waCVUT+mkIPVgxt5kcuW6OkW2VOy7Im9vpB/aRJOAuzAMb6LJeQTlvTVpvtVo1Lq1W++DqvN1yvTlhovGfZO6MD1aqoMVI54OjaZpwN30g0IJsj8cItYSwgGEPB9wPWYAE8UEUPAMHChMtjhf287/UG+icAEj8V4uNk2LkDqAEECHygHE151xjq/PVvGINuzP2CKvZqqdyKHjTe8mpYgMElaj9idUn9o4+MG4PARmMQMwg1oMYRmb9AArGhGpOVpEGzDAAh5e+nVWcEbU/AWEdOZqL3o0hGIwAN4CkMaxziJ18Go0J2Z1ZXM8wMumGaPcueiVXQBsWt4SArG1fsI2AfZZalW378+TiYxYDEKe/U5iwR0A7is+klFNWIbfsYBcDjBSJ58MdSJhzlGAD4R4qO90Eu56lV/Sk+ps7RmEWnkgoJ63E6lkQYhDReGlsGMDcoqPtEcJBgHOYbyj0LDPlA8xdEGbRMwvKSavReoYqbPSBY0ArBvHM4mEBCmO8GhbMLDeQhBC5zMUtIHBbqOnVTWvXJXxbRlFbLcLwUqUjGdQ1P67g4gzMTes5gUrGSFGsd1SOLc1YjYfxjxwIqwWIIIqLjlSFOpmX8XqOOaUG2Q5Sv/4OWSND+7eGylQ9nzWk3OYPN3+1DOHDtGtPNyvHSqFrUcdBqGZ7gMx4oQaVbGNaP0oVNqVsNCxBodIJEPRr74tEtd1ur+VGTW277xwJYTNQ1LtLldXwHo3BbF0XArZqUb+3kuNiLSdwqrXbHmSLGjkWQ3QZ9VonQkBXhYDi6pStFmd7CZZY1B60U7RAW+XXHmTNx0OoHJ7oLxSCvcoXj4AA5d417yQGcfCoUfJwAgJGAV0RAmon0oM82XzYftgbLeeH0Pcv5kkUilunV06qYc3xAzGE6EVNOVUR1nnEQ9XMCBez06jbQcjShTWE2C3+drTzhBDlWAixJvSuCKG2D0I1BcF4IOdD2JlLMfdAKC5qVI4JFw9AqNWqSQj0TAha/eeDvjd5EgVCNRtCIl5Uzoageb+rJ5hDpWLcCkJ1J49MzLmykfPlfE24V6o7OdMeCOZVISQy5WxJjBIPHjkbAlFesydYhdKEPAgJ/fh9PgSNcE3IgZChEjc2h1wIVYBAPgkhd4o1LQMRITBNYRDImUPkXgi7UEwhNYHJ2ZoADOhLOlrKnmn9ChDOIpAN4TqzSxeAoJ0LQQMIFVEhtKqp2DjlDYvRBDax8pPPMurZg0O8QLkxjetCaF/aHGJfSt/1I2SzLQhdc1LFOEH6w09owosBRyUcktHo1YDrCjxTQSm60CwISVzAm9z8tE828+9dF+qAVPXrF26hlxk9W55V9c+oXguctXixOHsl/tjz/bH9x5Tw2UFgBdY5guXZa6o8gE5CkBAkBAlBQpAQJAQJQUL4kyHYxSQ+eJqcIcA2EhqCvcp4ose0loWkf7gTdnDybNu3qcgQlEmXy4RveMbLLu0XoU9k5iTOYnPrpCMyBJfSGYNAyZw9p/u/iVUEhPmvYUKjXE1sCFC87XX6z88v2q+hyva3WIU8y7RcSp7oSYSHEDLrtb1/2MYVvHKMNkym2LGPA3ueWsGUe7hpafX5dOVSosvQ1FZxaf2leKMgtoIAMQhv8b9lWVMsLATV4wpc9rka4+DdJ34YsE+CH0M78Mg8bLG9YD+W/Gsl139kl4Vw2XvAzx8Kl/3OcO6/W9y3eB3Ez7H0CVmWx1oEYep69/6wI9xBtZ054VuXAucXg1HuEqhnxm9kwg4GIKxsvzwjjx7bBOjD3Ony1z1vgvudjLlDgasogQYj6G1/wn5j9d3IoS9wnf0+IfAvEVjTdOFLLZ9XttGwLRoEX/Ncdww9ys32N4fQnnd9N+j7XQca1JlB89yOTyicJzX+RdjYh7zuI1I793TeaUP186TP7J7+43dcn7L6buTMGIQlQHH776zlAKEPLMblsrf3GJrbQHDYtkbanUFBMvuVQbBD6jAVNx4paEeHwmEZGFveDPoY7IL1tOXDuoI6nP1kum+RX2OMXa17b2H0DLulglgTbO+X07fhPVAWuPy967O9tJZHnY5wELz38ctLCJ0F/fP2CyAEVPM6QT8IXii11bcu5VXo7sx5xrjT7fZB9+vkGdo4+xnAZX1CwZG4ZDZmXuAlgjB7tNWOR0OwLVVl/7hqeN0wuqU3C0UzB8fl+2Ggf8ADrCBQCJ+6XVBji0GwIgg+nJsRdKmr2j7r6ABKPSmdMO8BB1KOKXW5K+QQ/Floq8u6tmQQ8Ns97ahlhzsGeOORj8YCQXh2nGj0CkDdkep2Iwh1Zzj0fsB/JbCQJISpR/0gmMwC5kupEw5hoQV8awk0YQeCW9dcrgk8YoRthS9CQ4AHbXl0voJAtJ8BRAwIs9ME/rsFAT7sur8paIiKh7OX+NQBCBHGWgRBYRBsvxuuzAFkyMwh8KjH79RxxDOH72MbGgyLryxgeOsSg50oFe11tVig4DIIeA0B+V3Pi07xD6nHLsPlAIbIFIQZKEfJ6/rP8FGflTCpOOzev0WOkXSEixOcpTJ+92jXhxZxCKrlUDIOymM6eWYQZkkImB0vRLhuPPszOu73wy4MkbCXOgEBSLETjJcTNkQuCYcAcRnbVf4c0tkFFyrPS6AgeJkw50YmLBYsd+8Nlgn70dKyD6rgdicRBKDEIsi+T8k9Zu+wZvEM1A9YsLTyCXMGYQKaoJbCCZnAx159Ag+HGAVI1ejQUgXzCT/uff/+3veWAd8I6kdb31nYDCFSicXDc3/KTdkf8kvU5fzHSp2DIZlM/KXNufnsXdQZgg7g0Of7hW2Isch70A/5ZzzKJr4rXNiMptZ0ag+saZz4xAkQez9OdVC8xGxbJbzKndYRXwkSpOgrKM6kUImlWKX4EhwlWHb8K8u3BEyg5ByjhCAhSAgSgoQgIUgIEoKEICFICOpnDpWF/63hKN6VMHqF168gIy45exdGo62P+Y6PxZeGULn79u3bv00u/36L5N/49+a/SWG/NpuJT5pJqXxlCMrdU6MAubvrfWVNSHZnunuPlzvla/sEA3xAerfO6+a9BRMj64LEt14XPTk6yCFSQpAQJAQJQUKQECQECUFCkBAkBAlBQpAQJAQJQUKQECQECUFCkBAkBAlBQpAQJAQJQUKQECQECUFCkBAkhD9c/g83DiFJ9CQ1+AAAAABJRU5ErkJggg==" alt="" style="display:block;width:150px;max-width:100%;height:auto;margin:0 auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 6px 40px;">\n<p style="margin:0 0 16px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Te invitaron a crear tu cuenta en el sistema de reservas de los Laboratorios de Investigación del Parque i.</p>\n<p style="margin:0 0 30px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Con ella vas a poder reservar espacios y equipos, y hacer seguimiento a tus solicitudes.</p>\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:0 40px 30px 40px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="width:100%;">\n<tr>\n<td align="center" style="border-radius:8px;background-color:#102d69;">\n<a href="https://ijktwqnkknemjrokwcdn.supabase.co/auth/v1/verify?token=80f2db11003fb1f80c0cb4ef067b6c51d55a766583152abdc1f50dac&amp;type=invite&amp;redirect_to=http://172.20.10.18:8091/completar-cuenta" target="_blank" style="display:block;padding:16px 24px;font-family:'Montserrat',Arial,sans-serif;font-size:15px;font-weight:800;letter-spacing:0.6px;color:#ffffff;text-align:center;text-transform:uppercase;">Ingresá aquí</a>\n</td>\n</tr>\n</table>\n\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático. Si no solicitaste este acceso,<br>podés ignorar este mensaje.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-08-28 22:38:38.59738+00	2026-08-28 22:38:40.930397+00	t	\N	\N	\N
8	juandorado@itm.edu.co	Invitación a Reservas Parque i	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">¡Bienvenida/o! Ya podés crear tu cuenta en Reservas Parque i, Institución Universitaria ITM.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="data:image/png;base64,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" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" width="56%" valign="top">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">juandorado</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:29px;line-height:1.28;color:#102d69;font-weight:800;">¡Bienvenida/o!<br>Ya podés crear tu cuenta</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n<td class="stack-col" width="6%">&nbsp;</td>\n<td class="stack-col" width="38%" valign="top">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-radius:12px;overflow:hidden;background-color:#fbfcfe;border:1px solid #edf1f6;">\n<tr>\n<td align="center" valign="middle" style="padding:14px;">\n<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQQAAADqCAMAAABz78t+AAAAwFBMVEVZmrDH0N+Vo8cemqQhR3osssVmo8hRaqIgPYRDVHo7aJ0IIF+s7vOAjrgABD76+/0XPIPa5vp5wdGUwueQvuWExtUbQIjk6vcUNnau2OgHKW14vc0Spba2xdfM2ecqSYgLmq0uqbtyh6w2VI0qRnequM+OutWqyeaGl7UAGFVOZ5PZ8/eVqMWs1dxFW42O0txme6YJJVrDzNoAHGQiO3QvrcCQo7uu4uhUd6eY2eNkd5p8kbRYc5kUqMEACFJwmcu/YIcWAAAAQHRSTlP/////////////////////////////////////////////////////////////////////////////////////73leyQAAD3JJREFUeNrtnQt/oroSwNF22909916IigmhgPLwge/Hqa1td7//t7qTgIoIvoqa7mZ+Z7tWcSH/zExmkkmOokpRFYlAQpAQJAQJQUKQECQECUFCkBAkBAlBQpAQJAQJQUKQECSELwIBr+SvgwBtRnkiCg/lwj2PDsvtSSi3BSCGSijXNgEROSgXIIDOlVtxUIQhcEMMhUL4JIGbcVCuqQWrOEE0DMrFEeR6vD048JeEgPN7/nAQeXMMygURfC6mwF8KAi6iIzMwXM81KMUzOPfhdzngrwIBF9l/OxzwV4CAi1bhNAYsPISL6G/aS2KxIaQZFPZQ11YGpTAGhT4rvuowoQjaXds2gcWEcHm7vSIFRVQG16SgiPx8+EoUFKH76EoUlKs9Wg/11i61d45/xCJBOIsBGj08VBas8YuKokSvTsWAxYFwFoNX5enj6alhqqrefHp6at4pvTPuh0WBcBaD/ygNDqFh6s1G44lhqJwVMogB4SwGvQpr91PjqXHX5K8+vj3dIVUYXfgEhOO/NLiLIHAd4AJvjFRhKChnx8onfMuA5nMCMYWPj9MgJChcJI9QztUDfBqERkINmHs4DYJ62SFCuQIDDuFpWxqNkSoMBeUKDFSkpBl8NO4WqjAUlLMcwqnP8Z9mI8WgcXygcHkKylWeovcAzvDjIwGhuVBVYSgolx0cNwbx9O0joQpN/VPTODeD8LlHWDQb36JQgTnJu4r6qcQN3wjCZ59g1OQMosFSQZ/MrG8D4fO9YNw1VhBOdoo7T4Fv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" alt="" style="display:block;width:150px;max-width:100%;height:auto;margin:0 auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 6px 40px;">\n<p style="margin:0 0 16px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Te invitaron a crear tu cuenta en el sistema de reservas de los Laboratorios de Investigación del Parque i.</p>\n<p style="margin:0 0 30px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Con ella vas a poder reservar espacios y equipos, y hacer seguimiento a tus solicitudes.</p>\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:0 40px 30px 40px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="width:100%;">\n<tr>\n<td align="center" style="border-radius:8px;background-color:#102d69;">\n<a href="https://ijktwqnkknemjrokwcdn.supabase.co/auth/v1/verify?token=453a3eff7a7d026317072ef9b008f18577ba4debc192423484ec7407&amp;type=invite&amp;redirect_to=http://172.20.10.18:8091/completar-cuenta" target="_blank" style="display:block;padding:16px 24px;font-family:'Montserrat',Arial,sans-serif;font-size:15px;font-weight:800;letter-spacing:0.6px;color:#ffffff;text-align:center;text-transform:uppercase;">Ingresá aquí</a>\n</td>\n</tr>\n</table>\n\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático. Si no solicitaste este acceso,<br>podés ignorar este mensaje.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-01 16:27:50.117431+00	2026-09-01 16:27:52.279786+00	t	\N	\N	\N
9	juanmorales@itm.edu.co	Invitación a Reservas Parque i	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">¡Bienvenida/o! Ya podés crear tu cuenta en Reservas Parque i, Institución Universitaria ITM.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="data:image/png;base64,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" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" width="56%" valign="top">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Juan Carlos Morales</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:29px;line-height:1.28;color:#102d69;font-weight:800;">¡Bienvenida/o!<br>Ya podés crear tu cuenta</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n<td class="stack-col" width="6%">&nbsp;</td>\n<td class="stack-col" width="38%" valign="top">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-radius:12px;overflow:hidden;background-color:#fbfcfe;border:1px solid #edf1f6;">\n<tr>\n<td align="center" valign="middle" style="padding:14px;">\n<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQQAAADqCAMAAABz78t+AAAAwFBMVEVZmrDH0N+Vo8cemqQhR3osssVmo8hRaqIgPYRDVHo7aJ0IIF+s7vOAjrgABD76+/0XPIPa5vp5wdGUwueQvuWExtUbQIjk6vcUNnau2OgHKW14vc0Spba2xdfM2ecqSYgLmq0uqbtyh6w2VI0qRnequM+OutWqyeaGl7UAGFVOZ5PZ8/eVqMWs1dxFW42O0txme6YJJVrDzNoAHGQiO3QvrcCQo7uu4uhUd6eY2eNkd5p8kbRYc5kUqMEACFJwmcu/YIcWAAAAQHRSTlP/////////////////////////////////////////////////////////////////////////////////////73leyQAAD3JJREFUeNrtnQt/oroSwNF22909916IigmhgPLwge/Hqa1td7//t7qTgIoIvoqa7mZ+Z7tWcSH/zExmkkmOokpRFYlAQpAQJAQJQUKQECQECUFCkBAkBAlBQpAQJAQJQUKQECSELwIBr+SvgwBtRnkiCg/lwj2PDsvtSSi3BSCGSijXNgEROSgXIIDOlVtxUIQhcEMMhUL4JIGbcVCuqQWrOEE0DMrFEeR6vD048JeEgPN7/nAQeXMMygURfC6mwF8KAi6iIzMwXM81KMUzOPfhdzngrwIBF9l/OxzwV4CAi1bhNAYsPISL6G/aS2KxIaQZFPZQ11YGpTAGhT4rvuowoQjaXds2gcWEcHm7vSIFRVQG16SgiPx8+EoUFKH76EoUlKs9Wg/11i61d45/xCJBOIsBGj08VBas8YuKokSvTsWAxYFwFoNX5enj6alhqqrefHp6at4pvTPuh0WBcBaD/ygNDqFh6s1G44lhqJwVMogB4SwGvQpr91PjqXHX5K8+vj3dIVUYXfgEhOO/NLiLIHAd4AJvjFRhKChnx8onfMuA5nMCMYWPj9MgJChcJI9QztUDfBqERkINmHs4DYJ62SFCuQIDDuFpWxqNkSoMBeUKDFSkpBl8NO4WqjAUlLMcwqnP8Z9mI8WgcXygcHkKylWeovcAzvDjIwGhuVBVYSgolx0cNwbx9O0joQpN/VPTODeD8LlHWDQb36JQgTnJu4r6qcQN3wjCZ59g1OQMosFSQZ/MrG8D4fO9YNw1VhBOdoo7T4Fv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" alt="" style="display:block;width:150px;max-width:100%;height:auto;margin:0 auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 6px 40px;">\n<p style="margin:0 0 16px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Te invitaron a crear tu cuenta en el sistema de reservas de los Laboratorios de Investigación del Parque i.</p>\n<p style="margin:0 0 30px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Con ella vas a poder reservar espacios y equipos, y hacer seguimiento a tus solicitudes.</p>\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:0 40px 30px 40px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="width:100%;">\n<tr>\n<td align="center" style="border-radius:8px;background-color:#102d69;">\n<a href="https://ijktwqnkknemjrokwcdn.supabase.co/auth/v1/verify?token=a05f7d2cc508723fb0ba873d06ec4e25169e3e1bf635bf5e342e7b11&amp;type=invite&amp;redirect_to=http://172.20.10.18:8091/completar-cuenta" target="_blank" style="display:block;padding:16px 24px;font-family:'Montserrat',Arial,sans-serif;font-size:15px;font-weight:800;letter-spacing:0.6px;color:#ffffff;text-align:center;text-transform:uppercase;">Ingresá aquí</a>\n</td>\n</tr>\n</table>\n\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático. Si no solicitaste este acceso,<br>podés ignorar este mensaje.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-01 16:40:45.285223+00	2026-09-01 16:40:47.299865+00	t	\N	\N	\N
10	juanmorales@itm.edu.co	Invitación a Reservas Parque i	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">¡Bienvenida/o! Ya podés crear tu cuenta en Reservas Parque i, Institución Universitaria ITM.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="data:image/png;base64,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" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" width="56%" valign="top">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Juan Carlos Morales</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:29px;line-height:1.28;color:#102d69;font-weight:800;">¡Bienvenida/o!<br>Ya podés crear tu cuenta</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n<td class="stack-col" width="6%">&nbsp;</td>\n<td class="stack-col" width="38%" valign="top">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-radius:12px;overflow:hidden;background-color:#fbfcfe;border:1px solid #edf1f6;">\n<tr>\n<td align="center" valign="middle" style="padding:14px;">\n<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQQAAADqCAMAAABz78t+AAAAwFBMVEVZmrDH0N+Vo8cemqQhR3osssVmo8hRaqIgPYRDVHo7aJ0IIF+s7vOAjrgABD76+/0XPIPa5vp5wdGUwueQvuWExtUbQIjk6vcUNnau2OgHKW14vc0Spba2xdfM2ecqSYgLmq0uqbtyh6w2VI0qRnequM+OutWqyeaGl7UAGFVOZ5PZ8/eVqMWs1dxFW42O0txme6YJJVrDzNoAHGQiO3QvrcCQo7uu4uhUd6eY2eNkd5p8kbRYc5kUqMEACFJwmcu/YIcWAAAAQHRSTlP/////////////////////////////////////////////////////////////////////////////////////73leyQAAD3JJREFUeNrtnQt/oroSwNF22909916IigmhgPLwge/Hqa1td7//t7qTgIoIvoqa7mZ+Z7tWcSH/zExmkkmOokpRFYlAQpAQJAQJQUKQECQECUFCkBAkBAlBQpAQJAQJQUKQECSELwIBr+SvgwBtRnkiCg/lwj2PDsvtSSi3BSCGSijXNgEROSgXIIDOlVtxUIQhcEMMhUL4JIGbcVCuqQWrOEE0DMrFEeR6vD048JeEgPN7/nAQeXMMygURfC6mwF8KAi6iIzMwXM81KMUzOPfhdzngrwIBF9l/OxzwV4CAi1bhNAYsPISL6G/aS2KxIaQZFPZQ11YGpTAGhT4rvuowoQjaXds2gcWEcHm7vSIFRVQG16SgiPx8+EoUFKH76EoUlKs9Wg/11i61d45/xCJBOIsBGj08VBas8YuKokSvTsWAxYFwFoNX5enj6alhqqrefHp6at4pvTPuh0WBcBaD/ygNDqFh6s1G44lhqJwVMogB4SwGvQpr91PjqXHX5K8+vj3dIVUYXfgEhOO/NLiLIHAd4AJvjFRhKChnx8onfMuA5nMCMYWPj9MgJChcJI9QztUDfBqERkINmHs4DYJ62SFCuQIDDuFpWxqNkSoMBeUKDFSkpBl8NO4WqjAUlLMcwqnP8Z9mI8WgcXygcHkKylWeovcAzvDjIwGhuVBVYSgolx0cNwbx9O0joQpN/VPTODeD8LlHWDQb36JQgTnJu4r6qcQN3wjCZ59g1OQMosFSQZ/MrG8D4fO9YNw1VhBOdoo7T4Fv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" alt="" style="display:block;width:150px;max-width:100%;height:auto;margin:0 auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 6px 40px;">\n<p style="margin:0 0 16px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Te invitaron a crear tu cuenta en el sistema de reservas de los Laboratorios de Investigación del Parque i.</p>\n<p style="margin:0 0 30px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Con ella vas a poder reservar espacios y equipos, y hacer seguimiento a tus solicitudes.</p>\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:0 40px 30px 40px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="width:100%;">\n<tr>\n<td align="center" style="border-radius:8px;background-color:#102d69;">\n<a href="https://ijktwqnkknemjrokwcdn.supabase.co/auth/v1/verify?token=8f57620c939e2821aa7a77bc57bf9b435617df228fab84c273c4f984&amp;type=invite&amp;redirect_to=http://172.20.10.18:8091/completar-cuenta" target="_blank" style="display:block;padding:16px 24px;font-family:'Montserrat',Arial,sans-serif;font-size:15px;font-weight:800;letter-spacing:0.6px;color:#ffffff;text-align:center;text-transform:uppercase;">Ingresá aquí</a>\n</td>\n</tr>\n</table>\n\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático. Si no solicitaste este acceso,<br>podés ignorar este mensaje.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-01 16:42:38.917752+00	2026-09-01 16:42:40.534151+00	t	\N	\N	\N
11	juanmorales@itm.edu.co	Tu contraseña fue actualizada — Reservas Parque i	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">Tu contraseña en Reservas Parque i fue actualizada.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="data:image/png;base64,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" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Juan Carlos Morales</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:26px;line-height:1.3;color:#102d69;font-weight:800;">Tu contraseña fue<br>actualizada</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 30px 40px;">\n<p style="margin:0 0 20px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">La contraseña de tu cuenta en Reservas Parque i se actualizó correctamente.</p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;line-height:1.7;color:#4a4f58;">Si no hiciste este cambio vos, contactá a soporte de inmediato.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático de seguridad. Si no reconocés este cambio,<br>contactá a soporte de inmediato.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-01 16:43:04.929687+00	2026-09-01 16:43:06.424241+00	t	\N	\N	\N
12	santiagosuarez1136374@correo.itm.edu.co	Bienvenida/o a Reservas Parque i	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">Tu cuenta en Reservas Parque i ya está lista.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="data:image/png;base64,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" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Santiago</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:26px;line-height:1.3;color:#102d69;font-weight:800;">¡Bienvenida/o a<br>Reservas Parque i!</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 30px 40px;">\n<p style="margin:0 0 20px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Tu cuenta en el sistema de reservas de los Laboratorios de Investigación del Parque i ya está lista para usarse.</p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;line-height:1.7;color:#4a4f58;">Ingresá al sistema para completar tu perfil y empezar a reservar espacios y equipos.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático. Si no creaste esta cuenta,<br>contactá a soporte de inmediato.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-01 18:13:06.975184+00	2026-09-01 18:13:09.011846+00	t	\N	\N	\N
13	juandorado@itm.edu.co	Nueva reserva pendiente de aprobación	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">Nueva reserva pendiente de tu aprobación en Laboratorio de Sistemas de Control y Robotica.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="data:image/png;base64,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" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">juandorado</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:26px;line-height:1.3;color:#102d69;font-weight:800;">Tenés una reserva<br>por aprobar</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 30px 40px;">\n<p style="margin:0 0 20px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Hay una nueva reserva pendiente de tu aprobación:</p>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 22px;background-color:#fef3c7;border-left:4px solid #d97706;border-radius:8px;">\n<tr>\n<td style="padding:14px 18px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:800;color:#92400e;">Laboratorio de Sistemas de Control y Robotica</p>\n<p style="margin:6px 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;color:#4a4f58;">2026-09-01 &middot; 14:00:00&ndash;15:00:00</p>\n</td>\n</tr>\n</table>\n\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;line-height:1.7;color:#4a4f58;">Ingresá al sistema de reservas para aprobarla o rechazarla.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático del Sistema de Reservas de Laboratorios.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-01 18:15:54.401169+00	2026-09-01 18:15:55.819211+00	t	\N	\N	\N
14	juanmorales@itm.edu.co	Nueva reserva pendiente de aprobación	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">Nueva reserva pendiente de tu aprobación en Laboratorio de Sistemas de Control y Robotica.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="data:image/png;base64,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" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Juan Carlos Morales</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:26px;line-height:1.3;color:#102d69;font-weight:800;">Tenés una reserva<br>por aprobar</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 30px 40px;">\n<p style="margin:0 0 20px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Hay una nueva reserva pendiente de tu aprobación:</p>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 22px;background-color:#fef3c7;border-left:4px solid #d97706;border-radius:8px;">\n<tr>\n<td style="padding:14px 18px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:800;color:#92400e;">Laboratorio de Sistemas de Control y Robotica</p>\n<p style="margin:6px 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;color:#4a4f58;">2026-09-01 &middot; 14:00:00&ndash;15:00:00</p>\n</td>\n</tr>\n</table>\n\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;line-height:1.7;color:#4a4f58;">Ingresá al sistema de reservas para aprobarla o rechazarla.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático del Sistema de Reservas de Laboratorios.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-01 18:15:54.401169+00	2026-09-01 18:15:57.134596+00	t	\N	\N	\N
15	santiagosuarez1136374@correo.itm.edu.co	Recibimos tu solicitud de reserva	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">Recibimos tu solicitud de reserva en Laboratorio de Sistemas de Control y Robotica, pendiente de aprobación.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="data:image/png;base64,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" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Santiago</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:26px;line-height:1.3;color:#102d69;font-weight:800;">Recibimos tu<br>solicitud</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 30px 40px;">\n<p style="margin:0 0 20px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Recibimos tu solicitud de reserva y quedó pendiente de aprobación:</p>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 22px;background-color:#fef3c7;border-left:4px solid #d97706;border-radius:8px;">\n<tr>\n<td style="padding:14px 18px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:800;color:#92400e;">Laboratorio de Sistemas de Control y Robotica</p>\n<p style="margin:6px 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;color:#4a4f58;">2026-09-01 &middot; 14:00:00&ndash;15:00:00</p>\n</td>\n</tr>\n</table>\n\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;line-height:1.7;color:#4a4f58;">Te vamos a avisar por correo apenas el gestor la apruebe o la rechace.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático del Sistema de Reservas de Laboratorios.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-01 18:15:54.401169+00	2026-09-01 18:15:58.365592+00	t	\N	\N	\N
16	santiagosuarez1136374@correo.itm.edu.co	Tu reserva fue aprobada	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">Tu reserva #2 de Laboratorio de Sistemas de Control y Robotica fue aprobada.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAUAAAADUCAMAAADazgp5AAAAYFBMVEUAAAABGl4DCWYPJmYYLmwZVnFWZpMAAP/29/iZn7Q4T4QvQ3p4jKpoanGmrdFIWYktQXk7ToIA//+y1dfy8rOifKf/AAAAAKr//wC06bTloeX/f3///3//v79/AH9VAABpFBxlAAAAIHRSTlMA+wmgYRgWAQULJU8SBQlIi1MBBwUHAQMBBQQCAgQCAxc68EwAABimSURBVHja7V2JcuM4zqYBXpJsd2e7e2Z3/2Pf/y1XPAWekmwnkROzpqY6FsXjEwCCIAgw9tlFMaY5nmzhksGOV0EALPW1lMDngnM51QqeEOfnAHIIDYBiz15mADiZJLBNUwKCnBTConbaUQySIH1TT46fTGc+rtCgEiJUGEaD3On2gh7EJ6ZDYCKfVAdACNhpARzvgY6CKJ6YDIFBMSNZZWIQkeweBR3B0NCheEoEx3I6ophKkHcDPBy7iCE8IxUqJitz+cEuFfDkfdJuA4SCMXg6Bq5hAnEeXuRdx3fGLkAonww/USXAk/SLLbjV4mPA82rocxFhnQBxWTHkR4LnOv/zVAjq2hyEE3pywo9GzyJ4TiTw0VXoBgGykX8GeD0t6ll0wNPpfPlE8OwX1PDMADq+nTe23O77k/ITfXnvlQSeRQs8F4OfZgk4rMtOfQYJE99tQthWxLMgWK7CnNha2iVDU47AH7pDwedZiWW+F5jhUVtkuFIwa9mCgqmNMRC/2TqSmGJu1WINlowYB++nxqeRgvM4z55oULB7dwFqoUhjdbiLh59hCTHSTJoJSykv2sg9YUEUplxC2SAKw9/uPWNu9eaH6VYUkT23kfoRoiHacG7C8BlUmHEyJVX0RjN184/pRyjrq7E0lDzORZ7nImV8FEywN5gjnkH48brsGXaK+rpBIh6seJsOfjkA2b9OVUtgFdeOslHfDhpdeG3L+NwysDEnvYdW7CxB46ltU6xqm18EQKybM3fMdTKfoUWxeq2vFeEgnmsLspDNDg6+ztsR9mdViMGeNp9lM9xcQvS+JaQJzsKDsJ+BZ4PW8XdyDQ4Wu6hENcGhAOLX28lB7TTYcjDu2m21wYkA3sLAp4E962GS3EUl0CZY3v9Ui+X2SU0JQ0N126UEQoc7PQaK/V+nSqu3y2FNB94HqsFWe5VA0ZGYXg/pMbBoSVzxvEqg2KMEdpcHR4HQa9Foild8GiXab/91W7HYpwQObOxV9xatob/ZqO4cj2iNjhs31MGj1BS8x47AQK5pwl0NJtAoX3UNOxLPplskzCCZtgM4rugnxtNadGtAXUoecgVe9F3pARTWgJxtzHbaEboqj17dgizWBn54ARi/MhLxkvHXbiWwCzeubkGwygl4PehxXMLB4FYUmfGkU3Tm85H5UKPKe/HgA4TsKMhRyeEbDVbEInY+uBt5ssDxzjEYdjYXW3a4qyxOpfGiT8JBNRgGzqPFQ+DPP0p0DIGZczhRV3OWozcBKyojX7Uh0MU21JXP4NjWdEpV67au7TZSo+X0pei5sG0gHHgHspyhtdCBdQ4W222kUD9yaYkMNfeIlyc5C9b1jZlYs3UlJHNdVRP5qiKeqgnz+gvP5wxTO8Fo2rpgh5FejjsPPaR+mms2uGqAG1ZNJLJyDTNFG1csf+NT0Js3IEgqB8UaOm1bV6/GlLnJJX++9Un+6JcIcUh0rSp7qh00WvsImAKYunJw8ZTOQ2T/ts0w0j1EkxTAsinBOwxdOXo/lMlArSy3oxXPw6Z9/QYlsCoFdO/zDMc2OsPa/s3ZUKetfhR6hUahSlDYaZ13Cfrz8RvkiglwjYPTJQT6G5UqhQ6d5mXtmWZHsjVDRYWiJkBo7d9uUAJVTRbwjkMDr6nlR1pDoC6RlzV4VfOlrzdcDQTxM6gypOws8PzAB79+OlUeTrnk0vYoGncpgXKfT5eskvRxzAY/9nzQDVYWpvtKYIMAm0rmTLq6eqSnDsO/exa13+tK4NhVAqsqDG8f/2L9EbKjxSvBLapiYzMybKDRrqfVue3CO0C1xWOsIQm18E3q9pqVRdXVbb5CgKJ1/CEa7jMH8T+VmadF93Kl+f/1RjvCuadDGxWx8Z4F/vdRnV/yyfiF7ewv9MrkRoi9/4v3KoFVnNp+qubedF066kMcbeRjfksMCHqjj/ImJVB07NCyCbxoQXsEEVj7sjw5AIaV3e12O4JmKwTI2oKu8QQ+39nvT32qssQF+pbAzXaEOn1eWqzvW9anQ6rRDa5EyWsHGJstgaJnR+gSE7bcs8Qhb1OvXp0iy5zq2hGGzUtIAwsPxWbntWOsIWvH2nQJEVstgQ2keQSwQ4DXRsPVlz5/Den7VRgNJgkLIaQt6/4V/NTettb7dA9V+Sxs/n6tHgkfkQC5rETiW7cj9DlYtwmwPEaJD8QR1Wi17sjHJbX1w7xV0OveGmPH1tUVZoVIDqjXt3ifHuJObPEFx5EG7YSbPYp0525i8AcprBQDdFgFD+pcUAlLeo1nTpssgZ0lpP7+wOrXTpYjBn3Iq8Bqsy+zDYHAzJ37P6cVhbapBELToWZq7JEx4CeqUuEA+xC9NzrufCMBK2VI5MLbqagQFkyjCmEed2zRlVIAMZqb67Jm/Gw1Wu25zhGjND/w8/mS/3g9D9aH9ZLGPlmJu3XMRbiC4bkSUux9HCLY8QO+DKfTLaGuRx3I4s4B2FL89kwY3hqVaqbEIWhuXyCJwscD6EDkUueO09+r3HSJvkBRnFM3zG9EkDesIk0YYRxSh9b5FpIAsRZXbL3OE96XvhlGE2pWCKl7XsLwpdgdHkWCOZIuXY8AKWBoWT31AGeYQ31OUn9rKbgNz3JzglEpkuzFxHdlT3lyLpb4WeAJy7pCsCdfiQE/jfRAqK+gy3yEHEy3gmlmpS9QxAeCp79KEr1kJbnyD1iLvdD7irs+MGk/3pXwQuZBAV92W/xOSXsWk8MXtzcoYA8mw5lnpzFgJ9S3MM48KPOW2cgJWWYeZd8g6jrzSRRuR24xy3xPI2HIGCrF9swo1nYwX8cmp2vf2k6tiIY72BwzIVUyLbMZZf5vtrdQcwukiVW+c7EJp2FHRADxrc9G1gJ+JobQ5U/xTZbXV3mVV3mVV3mVV3mVV3mVV3mVV3mVV3mVV3mVV3mVV3kV9hUPotghIpeSA5udAZ9fX/PIroStIsVn3YS7CrmSwGOXHzFw+KTwZZ9ze1cNs//6v1X/Jszb5qEZl/H3u8ed30xlyxVhaCYzb770wMhzzfg7ykZ44P+v2CEAxDaVXRrPTNTp9w1toHkv+slMnyex89JCC0C7usz/67omG++i1lH5P7GHhWzfQ9myPvYWP7PCd0bdkXBKmgQK0BmAMs1DvLi7QoGwsvDH56pBgbup2wCID3Bc3KKu7J9v8lCtADi7CJkkqOYGlm6vl+Z5c9HqAKgbi1cXwHlIsLr4WdfZuYx677I5/zxAb76zZ7h59wzLnJsAWlbSAvvhLsKNERQVqYy9YBm6+jO5SFY+tUF2QrgP3QpiMt/mw16gpx7PhQh0DSGp3Kh5jHOl1gD80Q0Y4lZ8tL6VlefqJgCxHeNlG4AulJFzVES9A0B/j9LdyUPZBBBJ/Di1AqAJ5KS1/aKyUUW6bHH/rn1Po3GdTfCxevyUKlnL8/ySrL60BUD3US1/zdxjQqluBlDFN82E641rx25nJqcYw7UL4Ftkxga5YHfn2FmFdVMuNGXgFgAtCQs/KHHdwcJ2wtyvEUhi++QAerIWIQ1qD0C0A7G5WFv8NnY0ilknRQX1oBpNAOcEAo2XNgBoCRCdUgA7FberDUhl3hybresYAc5OXq4B6LxvlWuvsp2wdDzq5mB7q/CppUjfQ4F2SCPE+E/bAbTxp0JIMzv5Mui+Ir1KNW0AMOx4NDbWJR4i3qljAOg++y1bBwu9ZCQFI9QB9KOWc7yqdQDPoY0WgEGP4XUE3xFA9mAAPSCCAgjvD6BRPQU2FcV3BHBosDBfCzHWZGHSeOM7vAeAVkjKLCbvewLIQYSYly1JtsSu3QWgzKLe6o8AcK53AU/wdQD/aq3QHQBPGpoRQ3BRNKrj/mO0P2aiywDTbJcaY5dV9+ZY3xo8GsBzTLtcpUA7pL16YNTOdV0vcgOxYVmb2pyPTijTMIWrAIq4ARH1ncODAbQcNd+JliPvTWa+sbR9K+eDojZecso92gzZLQp0m8H51ifHuuG0OWOvlU1ywkbM+P0Axv7r8VsvnAaQbqcdwR0AzllAsBkwdrE14O+mMUEvoxK7jAk0JE4t3VsDwDqBuOToCwXWK/kr18hb1q4RW6FedKvJWTLwGIO1NirfYft95qgPp5bBcf3NX/VNEhn1hb0hjuwR94WH7hGGvt5ide+9tNKhG9V1uOV8b5kPfFgW4f5BtIJbBgNtG3foccuoxK3G7E8Kr6I+6YD+3fr92NCiGwjj/TqG55/Q/LEkfE5QOgnyffAT4iMR9Dti9eERNTEeTzy2YatywtZc8vkysDNwZAzL+NHeGnD1SuMV3idK4gflz1jOgj42ffSi+j76y+lKgp66RTQUSLcY1Z875bMyL2KRwS/EFrgv64fcmsWqll6BhurdmkbsMAA+KG3KuDV/wWMApCz8sQDmLAyBdab72j1vTQP2KADhUzKeqDhR9+FogqDHCNdV2fooFnYd4sfnvRv9MPMMS/iQ/KtcA/sYAJVx6PmELaSyXko6JgiCx6VPGjkftwv/PoBK+EL861OnQOcuBzbboEhqh7BGxW82tGIRXzF9WVA9TIA9g0neEED9BvsAhr6yLtMewfWoLlWzgm+CjHo/BS7K9T3u/XQSTZUDWlcPWm9QAHXmcpkMtmnr6Ye2qlTdBmD8SJL97b3vZtM36U+Oy2eM/xTLHHT87Rw6/yXccimSmUoZehqcwZbz5fzUxDMLjn8OwmvsDHoUaNG34eVskdSXQocex3NwLTQIJO0GvPQYFvmYPG8LgMTnbPKb3mAxD0nwfpBxj0VeLpq2y1srBWYJJX1DUX04zTZVTo6OktjVyHU50C4LZ9FKo5FckTRb0g/L9PizdM1LmzBDgP0A8jSCtPdgSgAkiRw5PaemWb3zWOgoQ0MEwP9FohkVkUYNhBmA0EzFV3nCawDy2GMO4MAbWXh3Aih4Lb9bCuAy2UUrREKU1XQGXlQQAMN3wEZyzbkpmQHYSMVXD13vBkcBHPBUB7CVkdX4Iu0EEKtfIQNwedsdSpFfsJkOYswpEGufJAVQbANQdxJEUwB/npoAylYu5b0A1r9jBiDleFFycCPu7wApgARz0Zi/2gJgu0fz8VUF3pKFmwgMdwNoU7DmABY8TDi4mdCF24aqADYIcDOAsv3xtwIoWoO+G0BeAXDIkthSDiZtIYxAxLvxS6kCGCUgCj04vwFH3NsAXMY/K0FJlNyBbQSQ2AcxXYtvATCN1IvlIkLqO/oUZJYyXwcpe9cA5MsrUzh4R2enywGcN3XEtyCa1J3XS1A4x4SHNwLovVTGcFdsMVnsBtCexo+YZAEuABSpCEYi5zhlLjvBZbWYj/sTANHdS4VkpbGYOPW60ANZQw/Urr5DVKZiNAEQJ9djDqA5exFLpGt+O4Deu0wmqaYzAMmgMMkIy2lTEvL0wWMG4KXMKIvTmWzrcgDN7MiHbR3qYBPAJan0z35G3dsBHBaKbgJIc9PKGRRBCEiX9jqgYz0n6by9wQLL1DawaydiHg4gpTFpgGgCKEKPFQDN/88wx8i2G7ybAURW25uVAMqa3mKuvcgkc1eSNDgDMH76Ug0xYgR2beXqeScyAJEAXrBwo4n9Wznh0yr1AEzOKpZ/8zKlfLGgLwCSAOdDMXS399sMIG92SAHk5LJmToHXhiLCapfhKDwZgLANQEI0V3rA1QcQEwCXaxrVfJRghe0WAOsbwQqARtw0AGwmMmO5UpEz6Ghu5++mQMLDhIPZLgCvy+mAqk2gVKTrAHYyCW4FsP0JCIDJcRA/0WPRW1iY8C3hYKimjl+jQCvwJixrbwEwJd9C6G4B0Pn+JqJ7ARBz0xRLbDTefLcbQIh9ol4sC3RTcqqlQBcNAK3iMmZSvDAmVAGkmqcsVfcNACaKzznThCi2IipOmNLlTRQYkXhLn+Cpc6e5BWCwICcrIU92uVAz6UMiwAv+2srCQ6GELG3KRC772wGpxesmAMv9s8gAdKZBZy2dZysUtAG0Fmi3KouNAJ6iuh2H9h9w7pi4F8BFKbNt/g0D0WZTM/W8nUwmfmXsVgBz+4WOlxgSE6Azo6M7mKwC6FCZtL8YJTYCOIUtS87UfP8ikjSRbuW6Uj3upG9gYfa71hRjdEEjHwwLizQB0Ntfxmsy/6kG4JgaPbAQGtQSsJsC3V7vTKbQTxfsjwZvAlBkDQtW0Eh5eFEDkIJC1z8738KYMBTKDpXoPDta2riI6FOziZ6aaXbzcDOAmRkzHtM2jYvIoAEgtuqX1pii8jz/6XSnHtgjsvpGiSjRNwOY2QCI21vji/E6gE178lgHEArC1vcDKHoAqhaCkgG7A8D0u1Gvo2t9Y99gYSV5ffKiag/MSNAYMODunUibBNvpgnEgUCzHmtsBTLYAWPfqo/YVaOuBAltHagWADM5YkEHKxHyLHojdQ6W3Qre8Zlo+AnF+uJGFaa+JWVLlm/PYm6juhaGA0B/E1wBUyTprXRAgeZ3v1wOzb47kNJgYHIU/cDFZfYfMzYYjcQlJPUGdk4X0f6TXDkfk+Xuxv1+mP7SpISW51XaNHqa/MnsoGd/ilSOrztzSVp0rgl6+ALp3jaEa6Tt6qg3yB6btmoTKrgnjxAcRkJZb0nvHVU2vZ633lnmk9TP6QfFv2BGBdnOjzWC0FQ/3yrWR9CdVvViietdNRLiomDoaNl+JBtbkhUa/RYRB6keYvSNqTVTa7TTxKq/yKq/yKq/yKuzrB4DPyz+eeTL/oBoPe6eAFO9dbsiSrYrLKQ8Z9+OmOwyb015cr5ePzrMBsGu616tuz/Ns4znbIh96+Vpbv/bVnAjGTHTv7TogNiPc0JYJAy2qmSTmQEPW8Qx5Gpge2oMHFzn01IuheCOAwH75+F1ilL2qdwFoTZ1yCSnu3DCE6L6B8ZpEHj4ZvfGUJb5wKwAOxkBmDf2cRPoA+nlFEpQmMwfQHxUQCgybRgyegOn74APOSqYaMUYgjb9TC28CjI7bUtB8THUKIl0UrVonAx+9TGbDB2eL+x9OZgbw81Rpy73lAPzlAR8WE7RMLA+X5BJoYH+5xKeD5dbPLBA0CwBG46km9/oYiQU/MEKBlxIc15otZyNthK7Eupg//cAIBQbCqFtxYuTr2UI3ZFUgOY+wn3WgFCjzq3sRQHdoze0puo/u5QncuvKGGGhnFwhEz6u3ng2VOJunL856iTZeawhBoj2AiP7AZbb7yXjfxfs5D/Y96SnQ3d/hFV6zMeYNcV15eR/ZYDaE5BaBhbnt0Fi4JS9E0x/ntxkFJ+3YAmjn5mJouQ49Bfq29GJRx5QC5zYNgC4a9fxV8bfzPLFO6fb8Rvg/TLKXqw3fJ23UEeR8OXqxNTyAtuEIoA2766tai7Svav0TkDwiLnZoPIqkchXcOa/OCBCNDVuXAPoQ42mr5qiVepyqpEoE0N00QGf8NwCqtC2NbqKYU6ClPzdGbo33F+tyLcLtmclajA3dXV2USGDu888tnu2AJ3/o5ijwlLLwJKzLDDrEgtOONCGqwF98JPrP4HhNhPrmr98YIz0HhhTKchKULKzcpVhNwh7YZ4qyqRhDFUgADDMzHdvDFyd8zEGDDfLqMEpk4OQeBvkV5cGcn8ff34pR35UBULvzBPSeRJzFGvJEKJAsIq4x28Hgnpmhx1DVmi547nu6GQz2/6P1FErZ/GqbkYsLVLaI+FbP1MehuABtq0ibpIhQoA5r8XLaMlfkdp2w5AJBPF6j05w9BsboAKeX4zDrmh/j5zLlO7GOAb46dzXsRBIAl3UinOxoFoDwD1V8lAAYBuK4cVDKCAmehjyeHMbC+9FGCgTqJUUEJwU3rZJSoPkqf5kKf/mvGipaP3n3wSDVA73zHEbnbx3ECaYAKgfgXwmA+CMCyKoAQqgbALRY/9M8lCo+qgCICEEciBTAzD08A5B0GAEUQRwFncpV+dkAEIIeKOJET7IA0LMwujaoCgJBii2MEljYt+G4lkp0s8scCgDhb0/4jAUWdtdsmBu6Z9cqC5ORpABC+L4OI6AAAtBWCQVqn+oBAkFKMnkK4NX6x9kRkrbcOmE3CgIYWURGA7HtfXQCUnKIAPrA2OjbsMrLInYmrxWpWANLClzUa3AC2y8inAIok2DUMqQqEQ0ATUc+UujktIAIoCDoCAOZSuN0W+0AJSxVMgCTEbo2R1cRlkjhb3QRAb/AezXGq5vcOyOFK4/2L25FrAVQqfBj2AThZE/oKYCmEaNKgtOPzMOLGn1VDNem3SPIsntwN/4agGDZ0av3brgWQOuBaDscy1a9l4IlWhxg6TinwHlmGDyxPAvbwVgATZYPPgU1xi834Ok4RNCBGEPvNHkXGidHOWNRV1p+HJxS4GL5UT3Q1xDBv2QyD1V4T3hF2vpe8J+nxH0Bos9MBHCkAGJwmQvqnd8La/QO1K7VdDMb9Hkf4pf7KgULxxH6QQnvFGLXJ+f7YP/6L90Jw08oj1v+AAAAAElFTkSuQmCC" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Santiago</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:26px;line-height:1.3;color:#102d69;font-weight:800;">Tu reserva fue<br>aprobada</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 30px 40px;">\n<p style="margin:0 0 20px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Tu reserva #2 fue <strong>aprobada</strong>:</p>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 22px;background-color:#d1fae5;border-left:4px solid #10b981;border-radius:8px;">\n<tr>\n<td style="padding:14px 18px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:800;color:#065f46;">Laboratorio de Sistemas de Control y Robotica</p>\n<p style="margin:6px 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;color:#4a4f58;">2026-09-02 &middot; 14:00:00&ndash;15:00:00</p>\n</td>\n</tr>\n</table>\n\n\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;line-height:1.7;color:#4a4f58;">Ingresá al sistema de reservas para más detalles.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático del Sistema de Reservas de Laboratorios.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-01 18:20:35.320716+00	2026-09-01 18:20:36.907879+00	t	reserva-2.ics	text/calendar	QkVHSU46VkNBTEVOREFSDQpWRVJTSU9OOjIuMA0KUFJPRElEOi0vL1Npc3RlbWEgZGUgUmVzZXJ2YXMgZGUgTGFib3JhdG9yaW9zLy9FUw0KQ0FMU0NBTEU6R1JFR09SSUFODQpNRVRIT0Q6UFVCTElTSA0KQkVHSU46VkVWRU5UDQpVSUQ6cmVzZXJ2YS0yQHJlc2VydmFzLXBhcnF1ZWkNCkRUU1RBTVA6MjAyNjA5MDFUMTgyMDM1Wg0KRFRTVEFSVDoyMDI2MDkwMlQxNDAwMDANCkRURU5EOjIwMjYwOTAyVDE1MDAwMA0KU1VNTUFSWTpMYWJvcmF0b3JpbyBkZSBTaXN0ZW1hcyBkZSBDb250cm9sIHkgUm9ib3RpY2ENCkRFU0NSSVBUSU9OOlJlc2VydmEgIzIgY29uZmlybWFkYSBlbiBMYWJvcmF0b3JpbyBkZSBTaXN0ZW1hcyBkZSBDb250cm9sIHkgUm9ib3RpY2EuDQpMT0NBVElPTjpMYWJvcmF0b3JpbyBkZSBTaXN0ZW1hcyBkZSBDb250cm9sIHkgUm9ib3RpY2ENCkVORDpWRVZFTlQNCkVORDpWQ0FMRU5EQVINCg==
17	santiagosuarez1136374@correo.itm.edu.co	Tu reserva fue eliminada	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">Tu reserva #2 de Laboratorio de Sistemas de Control y Robotica fue eliminada.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="data:image/png;base64,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" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Santiago</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:26px;line-height:1.3;color:#102d69;font-weight:800;">Tu reserva fue<br>eliminada</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 30px 40px;">\n<p style="margin:0 0 20px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Tu reserva #2 fue eliminada:</p>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 22px;background-color:#f1f5f9;border-left:4px solid #6b7280;border-radius:8px;">\n<tr>\n<td style="padding:14px 18px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:800;color:#334155;">Laboratorio de Sistemas de Control y Robotica</p>\n<p style="margin:6px 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;color:#4a4f58;">2026-09-02 &middot; 14:00:00&ndash;15:00:00</p>\n</td>\n</tr>\n</table>\n\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;line-height:1.7;color:#4a4f58;">Si tenés dudas sobre este cambio, contactá al gestor del espacio.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático del Sistema de Reservas de Laboratorios.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-01 18:24:36.648445+00	2026-09-01 18:24:38.473447+00	t	\N	\N	\N
18	juanmorales@itm.edu.co	Tu reserva fue aprobada	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">Tu reserva #3 de Laboratorio de Sistemas de Control y Robotica fue aprobada.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="data:image/png;base64,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" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Juan Carlos Morales</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:26px;line-height:1.3;color:#102d69;font-weight:800;">Tu reserva fue<br>aprobada</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 30px 40px;">\n<p style="margin:0 0 20px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Tu reserva #3 fue <strong>aprobada</strong>:</p>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 22px;background-color:#d1fae5;border-left:4px solid #10b981;border-radius:8px;">\n<tr>\n<td style="padding:14px 18px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:800;color:#065f46;">Laboratorio de Sistemas de Control y Robotica</p>\n<p style="margin:6px 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;color:#4a4f58;">2026-09-01 &middot; 14:00:00&ndash;16:00:00</p>\n</td>\n</tr>\n</table>\n\n\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;line-height:1.7;color:#4a4f58;">Ingresá al sistema de reservas para más detalles.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático del Sistema de Reservas de Laboratorios.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-01 18:28:17.443299+00	2026-09-01 18:28:19.052057+00	t	reserva-3.ics	text/calendar	QkVHSU46VkNBTEVOREFSDQpWRVJTSU9OOjIuMA0KUFJPRElEOi0vL1Npc3RlbWEgZGUgUmVzZXJ2YXMgZGUgTGFib3JhdG9yaW9zLy9FUw0KQ0FMU0NBTEU6R1JFR09SSUFODQpNRVRIT0Q6UFVCTElTSA0KQkVHSU46VkVWRU5UDQpVSUQ6cmVzZXJ2YS0zQHJlc2VydmFzLXBhcnF1ZWkNCkRUU1RBTVA6MjAyNjA5MDFUMTgyODE3Wg0KRFRTVEFSVDoyMDI2MDkwMVQxNDAwMDANCkRURU5EOjIwMjYwOTAxVDE2MDAwMA0KU1VNTUFSWTpMYWJvcmF0b3JpbyBkZSBTaXN0ZW1hcyBkZSBDb250cm9sIHkgUm9ib3RpY2ENCkRFU0NSSVBUSU9OOlJlc2VydmEgIzMgY29uZmlybWFkYSBlbiBMYWJvcmF0b3JpbyBkZSBTaXN0ZW1hcyBkZSBDb250cm9sIHkgUm9ib3RpY2EuDQpMT0NBVElPTjpMYWJvcmF0b3JpbyBkZSBTaXN0ZW1hcyBkZSBDb250cm9sIHkgUm9ib3RpY2ENCkVORDpWRVZFTlQNCkVORDpWQ0FMRU5EQVINCg==
19	juanmorales@itm.edu.co	Tu reserva empieza pronto	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">Tu reserva #3 de Laboratorio de Sistemas de Control y Robotica empieza pronto.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="data:image/png;base64,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" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Juan Carlos Morales</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:26px;line-height:1.3;color:#102d69;font-weight:800;">Tu reserva<br>empieza pronto</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 30px 40px;">\n<p style="margin:0 0 20px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Tu reserva #3 empieza pronto:</p>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 22px;background-color:#d1fae5;border-left:4px solid #10b981;border-radius:8px;">\n<tr>\n<td style="padding:14px 18px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:800;color:#065f46;">Laboratorio de Sistemas de Control y Robotica</p>\n<p style="margin:6px 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;color:#4a4f58;">2026-09-01 &middot; 14:00:00&ndash;16:00:00</p>\n</td>\n</tr>\n</table>\n\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;line-height:1.7;color:#4a4f58;">Si ya no la necesitás, cancelala desde la app para liberar el cupo.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático del Sistema de Reservas de Laboratorios.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-01 18:40:09.280894+00	2026-09-01 18:40:10.97475+00	t	\N	\N	\N
22	juanmorales@itm.edu.co	Tu reserva empieza pronto	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">Tu reserva #4 de Laboratorio de Sistemas de Control y Robotica empieza pronto.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="data:image/png;base64,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" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Juan Carlos Morales</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:26px;line-height:1.3;color:#102d69;font-weight:800;">Tu reserva<br>empieza pronto</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 30px 40px;">\n<p style="margin:0 0 20px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Tu reserva #4 empieza pronto:</p>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 22px;background-color:#d1fae5;border-left:4px solid #10b981;border-radius:8px;">\n<tr>\n<td style="padding:14px 18px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:800;color:#065f46;">Laboratorio de Sistemas de Control y Robotica</p>\n<p style="margin:6px 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;color:#4a4f58;">2026-09-01 &middot; 16:00:00&ndash;18:00:00</p>\n</td>\n</tr>\n</table>\n\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;line-height:1.7;color:#4a4f58;">Si ya no la necesitás, cancelala desde la app para liberar el cupo.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático del Sistema de Reservas de Laboratorios.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-01 20:10:09.289936+00	2026-09-01 20:10:11.203898+00	t	\N	\N	\N
23	juanmorales@itm.edu.co	Tu reserva empieza pronto	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">Tu reserva #5 de Laboratorio de Sistemas de Control y Robotica empieza pronto.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="data:image/png;base64,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" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Juan Carlos Morales</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:26px;line-height:1.3;color:#102d69;font-weight:800;">Tu reserva<br>empieza pronto</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 30px 40px;">\n<p style="margin:0 0 20px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Tu reserva #5 empieza pronto:</p>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 22px;background-color:#d1fae5;border-left:4px solid #10b981;border-radius:8px;">\n<tr>\n<td style="padding:14px 18px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:800;color:#065f46;">Laboratorio de Sistemas de Control y Robotica</p>\n<p style="margin:6px 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;color:#4a4f58;">2026-09-01 &middot; 18:00:00&ndash;20:00:00</p>\n</td>\n</tr>\n</table>\n\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;line-height:1.7;color:#4a4f58;">Si ya no la necesitás, cancelala desde la app para liberar el cupo.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático del Sistema de Reservas de Laboratorios.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-01 22:10:09.283368+00	2026-09-01 22:10:11.109501+00	t	\N	\N	\N
20	juanmorales@itm.edu.co	Tu reserva fue aprobada	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">Tu reserva #4 de Laboratorio de Sistemas de Control y Robotica fue aprobada.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="data:image/png;base64,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" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Juan Carlos Morales</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:26px;line-height:1.3;color:#102d69;font-weight:800;">Tu reserva fue<br>aprobada</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 30px 40px;">\n<p style="margin:0 0 20px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Tu reserva #4 fue <strong>aprobada</strong>:</p>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 22px;background-color:#d1fae5;border-left:4px solid #10b981;border-radius:8px;">\n<tr>\n<td style="padding:14px 18px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:800;color:#065f46;">Laboratorio de Sistemas de Control y Robotica</p>\n<p style="margin:6px 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;color:#4a4f58;">2026-09-01 &middot; 16:00:00&ndash;18:00:00</p>\n</td>\n</tr>\n</table>\n\n\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;line-height:1.7;color:#4a4f58;">Ingresá al sistema de reservas para más detalles.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático del Sistema de Reservas de Laboratorios.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-01 18:47:45.191681+00	2026-09-01 18:47:46.921779+00	t	reserva-4.ics	text/calendar	QkVHSU46VkNBTEVOREFSDQpWRVJTSU9OOjIuMA0KUFJPRElEOi0vL1Npc3RlbWEgZGUgUmVzZXJ2YXMgZGUgTGFib3JhdG9yaW9zLy9FUw0KQ0FMU0NBTEU6R1JFR09SSUFODQpNRVRIT0Q6UFVCTElTSA0KQkVHSU46VkVWRU5UDQpVSUQ6cmVzZXJ2YS00QHJlc2VydmFzLXBhcnF1ZWkNCkRUU1RBTVA6MjAyNjA5MDFUMTg0NzQ1Wg0KRFRTVEFSVDoyMDI2MDkwMVQxNjAwMDANCkRURU5EOjIwMjYwOTAxVDE4MDAwMA0KU1VNTUFSWTpMYWJvcmF0b3JpbyBkZSBTaXN0ZW1hcyBkZSBDb250cm9sIHkgUm9ib3RpY2ENCkRFU0NSSVBUSU9OOlJlc2VydmEgIzQgY29uZmlybWFkYSBlbiBMYWJvcmF0b3JpbyBkZSBTaXN0ZW1hcyBkZSBDb250cm9sIHkgUm9ib3RpY2EuDQpMT0NBVElPTjpMYWJvcmF0b3JpbyBkZSBTaXN0ZW1hcyBkZSBDb250cm9sIHkgUm9ib3RpY2ENCkVORDpWRVZFTlQNCkVORDpWQ0FMRU5EQVINCg==
21	juanmorales@itm.edu.co	Tu reserva fue aprobada	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">Tu reserva #5 de Laboratorio de Sistemas de Control y Robotica fue aprobada.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="data:image/png;base64,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" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Juan Carlos Morales</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:26px;line-height:1.3;color:#102d69;font-weight:800;">Tu reserva fue<br>aprobada</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 30px 40px;">\n<p style="margin:0 0 20px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Tu reserva #5 fue <strong>aprobada</strong>:</p>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 22px;background-color:#d1fae5;border-left:4px solid #10b981;border-radius:8px;">\n<tr>\n<td style="padding:14px 18px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:800;color:#065f46;">Laboratorio de Sistemas de Control y Robotica</p>\n<p style="margin:6px 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;color:#4a4f58;">2026-09-01 &middot; 18:00:00&ndash;20:00:00</p>\n</td>\n</tr>\n</table>\n\n\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;line-height:1.7;color:#4a4f58;">Ingresá al sistema de reservas para más detalles.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático del Sistema de Reservas de Laboratorios.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-01 18:48:53.9029+00	2026-09-01 18:48:55.783145+00	t	reserva-5.ics	text/calendar	QkVHSU46VkNBTEVOREFSDQpWRVJTSU9OOjIuMA0KUFJPRElEOi0vL1Npc3RlbWEgZGUgUmVzZXJ2YXMgZGUgTGFib3JhdG9yaW9zLy9FUw0KQ0FMU0NBTEU6R1JFR09SSUFODQpNRVRIT0Q6UFVCTElTSA0KQkVHSU46VkVWRU5UDQpVSUQ6cmVzZXJ2YS01QHJlc2VydmFzLXBhcnF1ZWkNCkRUU1RBTVA6MjAyNjA5MDFUMTg0ODUzWg0KRFRTVEFSVDoyMDI2MDkwMVQxODAwMDANCkRURU5EOjIwMjYwOTAxVDIwMDAwMA0KU1VNTUFSWTpMYWJvcmF0b3JpbyBkZSBTaXN0ZW1hcyBkZSBDb250cm9sIHkgUm9ib3RpY2ENCkRFU0NSSVBUSU9OOlJlc2VydmEgIzUgY29uZmlybWFkYSBlbiBMYWJvcmF0b3JpbyBkZSBTaXN0ZW1hcyBkZSBDb250cm9sIHkgUm9ib3RpY2EuDQpMT0NBVElPTjpMYWJvcmF0b3JpbyBkZSBTaXN0ZW1hcyBkZSBDb250cm9sIHkgUm9ib3RpY2ENCkVORDpWRVZFTlQNCkVORDpWQ0FMRU5EQVINCg==
24	santiagosuarez1136374@correo.itm.edu.co	Recuperación de contraseña — Reservas Parque i	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">Restablecé tu contraseña en Reservas Parque i, Institución Universitaria ITM.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="data:image/png;base64,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" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Santiago</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:26px;line-height:1.3;color:#102d69;font-weight:800;">Restablecé tu contraseña</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 6px 40px;">\n<p style="margin:0 0 30px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Recibimos una solicitud para restablecer la contraseña de tu cuenta en el sistema de reservas de los Laboratorios de Investigación del Parque i. Si fuiste vos, hacé clic abajo para elegir una nueva.</p>\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:0 40px 30px 40px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="width:100%;">\n<tr>\n<td align="center" style="border-radius:8px;background-color:#102d69;">\n<a href="https://ijktwqnkknemjrokwcdn.supabase.co/auth/v1/verify?token=447bf2b9751fd33cf73a047851cd99d4e8ea0d25b0e27dcbe7ee0872&amp;type=recovery&amp;redirect_to=http://172.20.10.18:8091/completar-cuenta" target="_blank" style="display:block;padding:16px 24px;font-family:'Montserrat',Arial,sans-serif;font-size:15px;font-weight:800;letter-spacing:0.6px;color:#ffffff;text-align:center;text-transform:uppercase;">Restablecer contraseña</a>\n</td>\n</tr>\n</table>\n\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático. Si no solicitaste este cambio,<br>podés ignorar este mensaje: tu contraseña actual sigue siendo válida.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-02 16:37:28.775926+00	2026-09-02 16:37:30.837807+00	t	\N	\N	\N
25	santiagosuarez1136374@correo.itm.edu.co	Tu contraseña fue actualizada — Reservas Parque i	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">Tu contraseña en Reservas Parque i fue actualizada.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="data:image/png;base64,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" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Santiago</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:26px;line-height:1.3;color:#102d69;font-weight:800;">Tu contraseña fue<br>actualizada</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 30px 40px;">\n<p style="margin:0 0 20px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">La contraseña de tu cuenta en Reservas Parque i se actualizó correctamente.</p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;line-height:1.7;color:#4a4f58;">Si no hiciste este cambio vos, contactá a soporte de inmediato.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático de seguridad. Si no reconocés este cambio,<br>contactá a soporte de inmediato.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-02 16:47:31.96408+00	2026-09-02 16:47:33.575028+00	t	\N	\N	\N
26	juanmorales@itm.edu.co	Tu reserva fue aprobada	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">Tu reserva #6 de Laboratorio de Sistemas de Control y Robotica fue aprobada.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="data:image/png;base64,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" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Juan Carlos Morales</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:26px;line-height:1.3;color:#102d69;font-weight:800;">Tu reserva fue<br>aprobada</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 30px 40px;">\n<p style="margin:0 0 20px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Tu reserva #6 fue <strong>aprobada</strong>:</p>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 22px;background-color:#d1fae5;border-left:4px solid #10b981;border-radius:8px;">\n<tr>\n<td style="padding:14px 18px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:800;color:#065f46;">Laboratorio de Sistemas de Control y Robotica</p>\n<p style="margin:6px 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;color:#4a4f58;">2026-09-03 &middot; 07:00:00&ndash;12:00:00</p>\n</td>\n</tr>\n</table>\n\n<div style="margin:16px 0 0 0;"><table role="presentation" cellpadding="0" cellspacing="0" style="width:100%;">\n<tr>\n<td align="center" style="border-radius:8px;background-color:#102d69;">\n<a href="http://localhost:8091/reservas/mis-reservas#6" target="_blank" style="display:block;padding:16px 24px;font-family:'Montserrat',Arial,sans-serif;font-size:15px;font-weight:800;letter-spacing:0.6px;color:#ffffff;text-align:center;text-transform:uppercase;">Ver reserva</a>\n</td>\n</tr>\n</table>\n</div>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;line-height:1.7;color:#4a4f58;">Ingresá al sistema de reservas para más detalles.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático del Sistema de Reservas de Laboratorios.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-02 21:01:03.076395+00	2026-09-02 21:01:05.286978+00	t	reserva-6.ics	text/calendar	QkVHSU46VkNBTEVOREFSDQpWRVJTSU9OOjIuMA0KUFJPRElEOi0vL1Npc3RlbWEgZGUgUmVzZXJ2YXMgZGUgTGFib3JhdG9yaW9zLy9FUw0KQ0FMU0NBTEU6R1JFR09SSUFODQpNRVRIT0Q6UFVCTElTSA0KQkVHSU46VkVWRU5UDQpVSUQ6cmVzZXJ2YS02QHJlc2VydmFzLXBhcnF1ZWkNCkRUU1RBTVA6MjAyNjA5MDJUMjEwMTAzWg0KRFRTVEFSVDoyMDI2MDkwM1QwNzAwMDANCkRURU5EOjIwMjYwOTAzVDEyMDAwMA0KU1VNTUFSWTpMYWJvcmF0b3JpbyBkZSBTaXN0ZW1hcyBkZSBDb250cm9sIHkgUm9ib3RpY2ENCkRFU0NSSVBUSU9OOlJlc2VydmEgIzYgY29uZmlybWFkYSBlbiBMYWJvcmF0b3JpbyBkZSBTaXN0ZW1hcyBkZSBDb250cm9sIHkgUm9ib3RpY2EuDQpMT0NBVElPTjpMYWJvcmF0b3JpbyBkZSBTaXN0ZW1hcyBkZSBDb250cm9sIHkgUm9ib3RpY2ENCkVORDpWRVZFTlQNCkVORDpWQ0FMRU5EQVINCg==
27	juanmorales@itm.edu.co	Tu reserva empieza pronto	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">Tu reserva #6 de Laboratorio de Sistemas de Control y Robotica empieza pronto.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="data:image/png;base64,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" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Juan Carlos Morales</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:26px;line-height:1.3;color:#102d69;font-weight:800;">Tu reserva<br>empieza pronto</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 30px 40px;">\n<p style="margin:0 0 20px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Tu reserva #6 empieza pronto:</p>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 22px;background-color:#d1fae5;border-left:4px solid #10b981;border-radius:8px;">\n<tr>\n<td style="padding:14px 18px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:800;color:#065f46;">Laboratorio de Sistemas de Control y Robotica</p>\n<p style="margin:6px 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;color:#4a4f58;">2026-09-03 &middot; 07:00:00&ndash;12:00:00</p>\n</td>\n</tr>\n</table>\n\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;line-height:1.7;color:#4a4f58;">Si ya no la necesitás, cancelala desde la app para liberar el cupo.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático del Sistema de Reservas de Laboratorios.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-03 11:14:58.883857+00	2026-09-03 11:15:01.149514+00	t	\N	\N	\N
28	santiagosuarez1136374@correo.itm.edu.co	Recuperación de contraseña — Reservas Parque i	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">Restablecé tu contraseña en Reservas Parque i, Institución Universitaria ITM.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAUAAAADUCAMAAADazgp5AAAAYFBMVEUAAAABGl4DCWYPJmYYLmwZVnFWZpMAAP/29/iZn7Q4T4QvQ3p4jKpoanGmrdFIWYktQXk7ToIA//+y1dfy8rOifKf/AAAAAKr//wC06bTloeX/f3///3//v79/AH9VAABpFBxlAAAAIHRSTlMA+wmgYRgWAQULJU8SBQlIi1MBBwUHAQMBBQQCAgQCAxc68EwAABimSURBVHja7V2JcuM4zqYBXpJsd2e7e2Z3/2Pf/y1XPAWekmwnkROzpqY6FsXjEwCCIAgw9tlFMaY5nmzhksGOV0EALPW1lMDngnM51QqeEOfnAHIIDYBiz15mADiZJLBNUwKCnBTConbaUQySIH1TT46fTGc+rtCgEiJUGEaD3On2gh7EJ6ZDYCKfVAdACNhpARzvgY6CKJ6YDIFBMSNZZWIQkeweBR3B0NCheEoEx3I6ophKkHcDPBy7iCE8IxUqJitz+cEuFfDkfdJuA4SCMXg6Bq5hAnEeXuRdx3fGLkAonww/USXAk/SLLbjV4mPA82rocxFhnQBxWTHkR4LnOv/zVAjq2hyEE3pywo9GzyJ4TiTw0VXoBgGykX8GeD0t6ll0wNPpfPlE8OwX1PDMADq+nTe23O77k/ITfXnvlQSeRQs8F4OfZgk4rMtOfQYJE99tQthWxLMgWK7CnNha2iVDU47AH7pDwedZiWW+F5jhUVtkuFIwa9mCgqmNMRC/2TqSmGJu1WINlowYB++nxqeRgvM4z55oULB7dwFqoUhjdbiLh59hCTHSTJoJSykv2sg9YUEUplxC2SAKw9/uPWNu9eaH6VYUkT23kfoRoiHacG7C8BlUmHEyJVX0RjN184/pRyjrq7E0lDzORZ7nImV8FEywN5gjnkH48brsGXaK+rpBIh6seJsOfjkA2b9OVUtgFdeOslHfDhpdeG3L+NwysDEnvYdW7CxB46ltU6xqm18EQKybM3fMdTKfoUWxeq2vFeEgnmsLspDNDg6+ztsR9mdViMGeNp9lM9xcQvS+JaQJzsKDsJ+BZ4PW8XdyDQ4Wu6hENcGhAOLX28lB7TTYcjDu2m21wYkA3sLAp4E962GS3EUl0CZY3v9Ui+X2SU0JQ0N126UEQoc7PQaK/V+nSqu3y2FNB94HqsFWe5VA0ZGYXg/pMbBoSVzxvEqg2KMEdpcHR4HQa9Foild8GiXab/91W7HYpwQObOxV9xatob/ZqO4cj2iNjhs31MGj1BS8x47AQK5pwl0NJtAoX3UNOxLPplskzCCZtgM4rugnxtNadGtAXUoecgVe9F3pARTWgJxtzHbaEboqj17dgizWBn54ARi/MhLxkvHXbiWwCzeubkGwygl4PehxXMLB4FYUmfGkU3Tm85H5UKPKe/HgA4TsKMhRyeEbDVbEInY+uBt5ssDxzjEYdjYXW3a4qyxOpfGiT8JBNRgGzqPFQ+DPP0p0DIGZczhRV3OWozcBKyojX7Uh0MU21JXP4NjWdEpV67au7TZSo+X0pei5sG0gHHgHspyhtdCBdQ4W222kUD9yaYkMNfeIlyc5C9b1jZlYs3UlJHNdVRP5qiKeqgnz+gvP5wxTO8Fo2rpgh5FejjsPPaR+mms2uGqAG1ZNJLJyDTNFG1csf+NT0Js3IEgqB8UaOm1bV6/GlLnJJX++9Un+6JcIcUh0rSp7qh00WvsImAKYunJw8ZTOQ2T/ts0w0j1EkxTAsinBOwxdOXo/lMlArSy3oxXPw6Z9/QYlsCoFdO/zDMc2OsPa/s3ZUKetfhR6hUahSlDYaZ13Cfrz8RvkiglwjYPTJQT6G5UqhQ6d5mXtmWZHsjVDRYWiJkBo7d9uUAJVTRbwjkMDr6nlR1pDoC6RlzV4VfOlrzdcDQTxM6gypOws8PzAB79+OlUeTrnk0vYoGncpgXKfT5eskvRxzAY/9nzQDVYWpvtKYIMAm0rmTLq6eqSnDsO/exa13+tK4NhVAqsqDG8f/2L9EbKjxSvBLapiYzMybKDRrqfVue3CO0C1xWOsIQm18E3q9pqVRdXVbb5CgKJ1/CEa7jMH8T+VmadF93Kl+f/1RjvCuadDGxWx8Z4F/vdRnV/yyfiF7ewv9MrkRoi9/4v3KoFVnNp+qubedF066kMcbeRjfksMCHqjj/ImJVB07NCyCbxoQXsEEVj7sjw5AIaV3e12O4JmKwTI2oKu8QQ+39nvT32qssQF+pbAzXaEOn1eWqzvW9anQ6rRDa5EyWsHGJstgaJnR+gSE7bcs8Qhb1OvXp0iy5zq2hGGzUtIAwsPxWbntWOsIWvH2nQJEVstgQ2keQSwQ4DXRsPVlz5/Den7VRgNJgkLIaQt6/4V/NTettb7dA9V+Sxs/n6tHgkfkQC5rETiW7cj9DlYtwmwPEaJD8QR1Wi17sjHJbX1w7xV0OveGmPH1tUVZoVIDqjXt3ifHuJObPEFx5EG7YSbPYp0525i8AcprBQDdFgFD+pcUAlLeo1nTpssgZ0lpP7+wOrXTpYjBn3Iq8Bqsy+zDYHAzJ37P6cVhbapBELToWZq7JEx4CeqUuEA+xC9NzrufCMBK2VI5MLbqagQFkyjCmEed2zRlVIAMZqb67Jm/Gw1Wu25zhGjND/w8/mS/3g9D9aH9ZLGPlmJu3XMRbiC4bkSUux9HCLY8QO+DKfTLaGuRx3I4s4B2FL89kwY3hqVaqbEIWhuXyCJwscD6EDkUueO09+r3HSJvkBRnFM3zG9EkDesIk0YYRxSh9b5FpIAsRZXbL3OE96XvhlGE2pWCKl7XsLwpdgdHkWCOZIuXY8AKWBoWT31AGeYQ31OUn9rKbgNz3JzglEpkuzFxHdlT3lyLpb4WeAJy7pCsCdfiQE/jfRAqK+gy3yEHEy3gmlmpS9QxAeCp79KEr1kJbnyD1iLvdD7irs+MGk/3pXwQuZBAV92W/xOSXsWk8MXtzcoYA8mw5lnpzFgJ9S3MM48KPOW2cgJWWYeZd8g6jrzSRRuR24xy3xPI2HIGCrF9swo1nYwX8cmp2vf2k6tiIY72BwzIVUyLbMZZf5vtrdQcwukiVW+c7EJp2FHRADxrc9G1gJ+JobQ5U/xTZbXV3mVV3mVV3mVV3mVV3mVV3mVV3mVV3mVV3mVV3mVV3kV9hUPotghIpeSA5udAZ9fX/PIroStIsVn3YS7CrmSwGOXHzFw+KTwZZ9ze1cNs//6v1X/Jszb5qEZl/H3u8ed30xlyxVhaCYzb770wMhzzfg7ykZ44P+v2CEAxDaVXRrPTNTp9w1toHkv+slMnyex89JCC0C7usz/67omG++i1lH5P7GHhWzfQ9myPvYWP7PCd0bdkXBKmgQK0BmAMs1DvLi7QoGwsvDH56pBgbup2wCID3Bc3KKu7J9v8lCtADi7CJkkqOYGlm6vl+Z5c9HqAKgbi1cXwHlIsLr4WdfZuYx677I5/zxAb76zZ7h59wzLnJsAWlbSAvvhLsKNERQVqYy9YBm6+jO5SFY+tUF2QrgP3QpiMt/mw16gpx7PhQh0DSGp3Kh5jHOl1gD80Q0Y4lZ8tL6VlefqJgCxHeNlG4AulJFzVES9A0B/j9LdyUPZBBBJ/Di1AqAJ5KS1/aKyUUW6bHH/rn1Po3GdTfCxevyUKlnL8/ySrL60BUD3US1/zdxjQqluBlDFN82E641rx25nJqcYw7UL4Ftkxga5YHfn2FmFdVMuNGXgFgAtCQs/KHHdwcJ2wtyvEUhi++QAerIWIQ1qD0C0A7G5WFv8NnY0ilknRQX1oBpNAOcEAo2XNgBoCRCdUgA7FberDUhl3hybresYAc5OXq4B6LxvlWuvsp2wdDzq5mB7q/CppUjfQ4F2SCPE+E/bAbTxp0JIMzv5Mui+Ir1KNW0AMOx4NDbWJR4i3qljAOg++y1bBwu9ZCQFI9QB9KOWc7yqdQDPoY0WgEGP4XUE3xFA9mAAPSCCAgjvD6BRPQU2FcV3BHBosDBfCzHWZGHSeOM7vAeAVkjKLCbvewLIQYSYly1JtsSu3QWgzKLe6o8AcK53AU/wdQD/aq3QHQBPGpoRQ3BRNKrj/mO0P2aiywDTbJcaY5dV9+ZY3xo8GsBzTLtcpUA7pL16YNTOdV0vcgOxYVmb2pyPTijTMIWrAIq4ARH1ncODAbQcNd+JliPvTWa+sbR9K+eDojZecso92gzZLQp0m8H51ifHuuG0OWOvlU1ywkbM+P0Axv7r8VsvnAaQbqcdwR0AzllAsBkwdrE14O+mMUEvoxK7jAk0JE4t3VsDwDqBuOToCwXWK/kr18hb1q4RW6FedKvJWTLwGIO1NirfYft95qgPp5bBcf3NX/VNEhn1hb0hjuwR94WH7hGGvt5ide+9tNKhG9V1uOV8b5kPfFgW4f5BtIJbBgNtG3foccuoxK3G7E8Kr6I+6YD+3fr92NCiGwjj/TqG55/Q/LEkfE5QOgnyffAT4iMR9Dti9eERNTEeTzy2YatywtZc8vkysDNwZAzL+NHeGnD1SuMV3idK4gflz1jOgj42ffSi+j76y+lKgp66RTQUSLcY1Z875bMyL2KRwS/EFrgv64fcmsWqll6BhurdmkbsMAA+KG3KuDV/wWMApCz8sQDmLAyBdab72j1vTQP2KADhUzKeqDhR9+FogqDHCNdV2fooFnYd4sfnvRv9MPMMS/iQ/KtcA/sYAJVx6PmELaSyXko6JgiCx6VPGjkftwv/PoBK+EL861OnQOcuBzbboEhqh7BGxW82tGIRXzF9WVA9TIA9g0neEED9BvsAhr6yLtMewfWoLlWzgm+CjHo/BS7K9T3u/XQSTZUDWlcPWm9QAHXmcpkMtmnr6Ye2qlTdBmD8SJL97b3vZtM36U+Oy2eM/xTLHHT87Rw6/yXccimSmUoZehqcwZbz5fzUxDMLjn8OwmvsDHoUaNG34eVskdSXQocex3NwLTQIJO0GvPQYFvmYPG8LgMTnbPKb3mAxD0nwfpBxj0VeLpq2y1srBWYJJX1DUX04zTZVTo6OktjVyHU50C4LZ9FKo5FckTRb0g/L9PizdM1LmzBDgP0A8jSCtPdgSgAkiRw5PaemWb3zWOgoQ0MEwP9FohkVkUYNhBmA0EzFV3nCawDy2GMO4MAbWXh3Aih4Lb9bCuAy2UUrREKU1XQGXlQQAMN3wEZyzbkpmQHYSMVXD13vBkcBHPBUB7CVkdX4Iu0EEKtfIQNwedsdSpFfsJkOYswpEGufJAVQbANQdxJEUwB/npoAylYu5b0A1r9jBiDleFFycCPu7wApgARz0Zi/2gJgu0fz8VUF3pKFmwgMdwNoU7DmABY8TDi4mdCF24aqADYIcDOAsv3xtwIoWoO+G0BeAXDIkthSDiZtIYxAxLvxS6kCGCUgCj04vwFH3NsAXMY/K0FJlNyBbQSQ2AcxXYtvATCN1IvlIkLqO/oUZJYyXwcpe9cA5MsrUzh4R2enywGcN3XEtyCa1J3XS1A4x4SHNwLovVTGcFdsMVnsBtCexo+YZAEuABSpCEYi5zhlLjvBZbWYj/sTANHdS4VkpbGYOPW60ANZQw/Urr5DVKZiNAEQJ9djDqA5exFLpGt+O4Deu0wmqaYzAMmgMMkIy2lTEvL0wWMG4KXMKIvTmWzrcgDN7MiHbR3qYBPAJan0z35G3dsBHBaKbgJIc9PKGRRBCEiX9jqgYz0n6by9wQLL1DawaydiHg4gpTFpgGgCKEKPFQDN/88wx8i2G7ybAURW25uVAMqa3mKuvcgkc1eSNDgDMH76Ug0xYgR2beXqeScyAJEAXrBwo4n9Wznh0yr1AEzOKpZ/8zKlfLGgLwCSAOdDMXS399sMIG92SAHk5LJmToHXhiLCapfhKDwZgLANQEI0V3rA1QcQEwCXaxrVfJRghe0WAOsbwQqARtw0AGwmMmO5UpEz6Ghu5++mQMLDhIPZLgCvy+mAqk2gVKTrAHYyCW4FsP0JCIDJcRA/0WPRW1iY8C3hYKimjl+jQCvwJixrbwEwJd9C6G4B0Pn+JqJ7ARBz0xRLbDTefLcbQIh9ol4sC3RTcqqlQBcNAK3iMmZSvDAmVAGkmqcsVfcNACaKzznThCi2IipOmNLlTRQYkXhLn+Cpc6e5BWCwICcrIU92uVAz6UMiwAv+2srCQ6GELG3KRC772wGpxesmAMv9s8gAdKZBZy2dZysUtAG0Fmi3KouNAJ6iuh2H9h9w7pi4F8BFKbNt/g0D0WZTM/W8nUwmfmXsVgBz+4WOlxgSE6Azo6M7mKwC6FCZtL8YJTYCOIUtS87UfP8ikjSRbuW6Uj3upG9gYfa71hRjdEEjHwwLizQB0Ntfxmsy/6kG4JgaPbAQGtQSsJsC3V7vTKbQTxfsjwZvAlBkDQtW0Eh5eFEDkIJC1z8738KYMBTKDpXoPDta2riI6FOziZ6aaXbzcDOAmRkzHtM2jYvIoAEgtuqX1pii8jz/6XSnHtgjsvpGiSjRNwOY2QCI21vji/E6gE178lgHEArC1vcDKHoAqhaCkgG7A8D0u1Gvo2t9Y99gYSV5ffKiag/MSNAYMODunUibBNvpgnEgUCzHmtsBTLYAWPfqo/YVaOuBAltHagWADM5YkEHKxHyLHojdQ6W3Qre8Zlo+AnF+uJGFaa+JWVLlm/PYm6juhaGA0B/E1wBUyTprXRAgeZ3v1wOzb47kNJgYHIU/cDFZfYfMzYYjcQlJPUGdk4X0f6TXDkfk+Xuxv1+mP7SpISW51XaNHqa/MnsoGd/ilSOrztzSVp0rgl6+ALp3jaEa6Tt6qg3yB6btmoTKrgnjxAcRkJZb0nvHVU2vZ633lnmk9TP6QfFv2BGBdnOjzWC0FQ/3yrWR9CdVvViietdNRLiomDoaNl+JBtbkhUa/RYRB6keYvSNqTVTa7TTxKq/yKq/yKq/yKuzrB4DPyz+eeTL/oBoPe6eAFO9dbsiSrYrLKQ8Z9+OmOwyb015cr5ePzrMBsGu616tuz/Ns4znbIh96+Vpbv/bVnAjGTHTv7TogNiPc0JYJAy2qmSTmQEPW8Qx5Gpge2oMHFzn01IuheCOAwH75+F1ilL2qdwFoTZ1yCSnu3DCE6L6B8ZpEHj4ZvfGUJb5wKwAOxkBmDf2cRPoA+nlFEpQmMwfQHxUQCgybRgyegOn74APOSqYaMUYgjb9TC28CjI7bUtB8THUKIl0UrVonAx+9TGbDB2eL+x9OZgbw81Rpy73lAPzlAR8WE7RMLA+X5BJoYH+5xKeD5dbPLBA0CwBG46km9/oYiQU/MEKBlxIc15otZyNthK7Eupg//cAIBQbCqFtxYuTr2UI3ZFUgOY+wn3WgFCjzq3sRQHdoze0puo/u5QncuvKGGGhnFwhEz6u3ng2VOJunL856iTZeawhBoj2AiP7AZbb7yXjfxfs5D/Y96SnQ3d/hFV6zMeYNcV15eR/ZYDaE5BaBhbnt0Fi4JS9E0x/ntxkFJ+3YAmjn5mJouQ49Bfq29GJRx5QC5zYNgC4a9fxV8bfzPLFO6fb8Rvg/TLKXqw3fJ23UEeR8OXqxNTyAtuEIoA2766tai7Svav0TkDwiLnZoPIqkchXcOa/OCBCNDVuXAPoQ42mr5qiVepyqpEoE0N00QGf8NwCqtC2NbqKYU6ClPzdGbo33F+tyLcLtmclajA3dXV2USGDu888tnu2AJ3/o5ijwlLLwJKzLDDrEgtOONCGqwF98JPrP4HhNhPrmr98YIz0HhhTKchKULKzcpVhNwh7YZ4qyqRhDFUgADDMzHdvDFyd8zEGDDfLqMEpk4OQeBvkV5cGcn8ff34pR35UBULvzBPSeRJzFGvJEKJAsIq4x28Hgnpmhx1DVmi547nu6GQz2/6P1FErZ/GqbkYsLVLaI+FbP1MehuABtq0ibpIhQoA5r8XLaMlfkdp2w5AJBPF6j05w9BsboAKeX4zDrmh/j5zLlO7GOAb46dzXsRBIAl3UinOxoFoDwD1V8lAAYBuK4cVDKCAmehjyeHMbC+9FGCgTqJUUEJwU3rZJSoPkqf5kKf/mvGipaP3n3wSDVA73zHEbnbx3ECaYAKgfgXwmA+CMCyKoAQqgbALRY/9M8lCo+qgCICEEciBTAzD08A5B0GAEUQRwFncpV+dkAEIIeKOJET7IA0LMwujaoCgJBii2MEljYt+G4lkp0s8scCgDhb0/4jAUWdtdsmBu6Z9cqC5ORpABC+L4OI6AAAtBWCQVqn+oBAkFKMnkK4NX6x9kRkrbcOmE3CgIYWURGA7HtfXQCUnKIAPrA2OjbsMrLInYmrxWpWANLClzUa3AC2y8inAIok2DUMqQqEQ0ATUc+UujktIAIoCDoCAOZSuN0W+0AJSxVMgCTEbo2R1cRlkjhb3QRAb/AezXGq5vcOyOFK4/2L25FrAVQqfBj2AThZE/oKYCmEaNKgtOPzMOLGn1VDNem3SPIsntwN/4agGDZ0av3brgWQOuBaDscy1a9l4IlWhxg6TinwHlmGDyxPAvbwVgATZYPPgU1xi834Ok4RNCBGEPvNHkXGidHOWNRV1p+HJxS4GL5UT3Q1xDBv2QyD1V4T3hF2vpe8J+nxH0Bos9MBHCkAGJwmQvqnd8La/QO1K7VdDMb9Hkf4pf7KgULxxH6QQnvFGLXJ+f7YP/6L90Jw08oj1v+AAAAAElFTkSuQmCC" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Santiago</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:26px;line-height:1.3;color:#102d69;font-weight:800;">Restablecé tu contraseña</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 6px 40px;">\n<p style="margin:0 0 30px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Recibimos una solicitud para restablecer la contraseña de tu cuenta en el sistema de reservas de los Laboratorios de Investigación del Parque i. Si fuiste vos, hacé clic abajo para elegir una nueva.</p>\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:0 40px 30px 40px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="width:100%;">\n<tr>\n<td align="center" style="border-radius:8px;background-color:#102d69;">\n<a href="https://ijktwqnkknemjrokwcdn.supabase.co/auth/v1/verify?token=8f072fbd28afa2d94839f4626ec0eb9da7f14fa1ad10c7967e65042f&amp;type=recovery&amp;redirect_to=http://172.20.10.18:8091/completar-cuenta" target="_blank" style="display:block;padding:16px 24px;font-family:'Montserrat',Arial,sans-serif;font-size:15px;font-weight:800;letter-spacing:0.6px;color:#ffffff;text-align:center;text-transform:uppercase;">Restablecer contraseña</a>\n</td>\n</tr>\n</table>\n\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático. Si no solicitaste este cambio,<br>podés ignorar este mensaje: tu contraseña actual sigue siendo válida.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-04 03:14:24.421912+00	2026-09-04 03:14:26.022199+00	t	\N	\N	\N
29	santiagosuarez1136374@correo.itm.edu.co	Recuperación de contraseña — Reservas Parque i	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">Restablecé tu contraseña en Reservas Parque i, Institución Universitaria ITM.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="data:image/png;base64,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" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Santiago</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:26px;line-height:1.3;color:#102d69;font-weight:800;">Restablecé tu contraseña</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 6px 40px;">\n<p style="margin:0 0 30px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Recibimos una solicitud para restablecer la contraseña de tu cuenta en el sistema de reservas de los Laboratorios de Investigación del Parque i. Si fuiste vos, hacé clic abajo para elegir una nueva.</p>\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:0 40px 30px 40px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="width:100%;">\n<tr>\n<td align="center" style="border-radius:8px;background-color:#102d69;">\n<a href="https://ijktwqnkknemjrokwcdn.supabase.co/auth/v1/verify?token=068fbd5b32181bc7412f3b5843acfd368ea291df879435446baf4c41&amp;type=recovery&amp;redirect_to=http://172.20.10.18:8091/completar-cuenta" target="_blank" style="display:block;padding:16px 24px;font-family:'Montserrat',Arial,sans-serif;font-size:15px;font-weight:800;letter-spacing:0.6px;color:#ffffff;text-align:center;text-transform:uppercase;">Restablecer contraseña</a>\n</td>\n</tr>\n</table>\n\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático. Si no solicitaste este cambio,<br>podés ignorar este mensaje: tu contraseña actual sigue siendo válida.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-04 03:18:13.656486+00	2026-09-04 03:18:15.37656+00	t	\N	\N	\N
30	santiagosuarez1136374@correo.itm.edu.co	Recuperación de contraseña — Reservas Parque i	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">Restablecé tu contraseña en Reservas Parque i, Institución Universitaria ITM.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="cid:logo-itm" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Santiago</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:26px;line-height:1.3;color:#102d69;font-weight:800;">Restablecé tu contraseña</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 6px 40px;">\n<p style="margin:0 0 30px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Recibimos una solicitud para restablecer la contraseña de tu cuenta en el sistema de reservas de los Laboratorios de Investigación del Parque i. Si fuiste vos, hacé clic abajo para elegir una nueva.</p>\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:0 40px 30px 40px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="width:100%;">\n<tr>\n<td align="center" style="border-radius:8px;background-color:#102d69;">\n<a href="https://ijktwqnkknemjrokwcdn.supabase.co/auth/v1/verify?token=b7c81dac5c29ce51ba4295fb19d85c5b598a4d14510f065a7a057043&amp;type=recovery&amp;redirect_to=http://172.20.10.18:8091/completar-cuenta" target="_blank" style="display:block;padding:16px 24px;font-family:'Montserrat',Arial,sans-serif;font-size:15px;font-weight:800;letter-spacing:0.6px;color:#ffffff;text-align:center;text-transform:uppercase;">Restablecer contraseña</a>\n</td>\n</tr>\n</table>\n\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático. Si no solicitaste este cambio,<br>podés ignorar este mensaje: tu contraseña actual sigue siendo válida.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-04 04:13:09.548335+00	2026-09-04 04:13:11.565301+00	t	\N	\N	\N
31	santiagosuarez1136374@correo.itm.edu.co	Recuperación de contraseña — Reservas Parque i	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">Restablecé tu contraseña en Reservas Parque i, Institución Universitaria ITM.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="cid:logo-itm" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Santiago</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:26px;line-height:1.3;color:#102d69;font-weight:800;">Restablecé tu contraseña</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 6px 40px;">\n<p style="margin:0 0 30px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Recibimos una solicitud para restablecer la contraseña de tu cuenta en el sistema de reservas de los Laboratorios de Investigación del Parque i. Si fuiste vos, hacé clic abajo para elegir una nueva.</p>\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:0 40px 30px 40px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="width:100%;">\n<tr>\n<td align="center" style="border-radius:8px;background-color:#102d69;">\n<a href="https://ijktwqnkknemjrokwcdn.supabase.co/auth/v1/verify?token=e8932b7260c3b05366ad1aec91baf8da0a3b61c50ce8d5c38c1d3a03&amp;type=recovery&amp;redirect_to=http://172.20.10.18:8091/completar-cuenta" target="_blank" style="display:block;padding:16px 24px;font-family:'Montserrat',Arial,sans-serif;font-size:15px;font-weight:800;letter-spacing:0.6px;color:#ffffff;text-align:center;text-transform:uppercase;">Restablecer contraseña</a>\n</td>\n</tr>\n</table>\n\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático. Si no solicitaste este cambio,<br>podés ignorar este mensaje: tu contraseña actual sigue siendo válida.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-06 00:20:33.310365+00	2026-09-06 00:20:34.944483+00	t	\N	\N	\N
32	santiagosuarez1136374@correo.itm.edu.co	Invitación a Reservas Parque i	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">¡Bienvenida/o! Ya podés crear tu cuenta en Reservas Parque i, Institución Universitaria ITM.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="cid:logo-itm" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" width="56%" valign="top">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Santiago</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:29px;line-height:1.28;color:#102d69;font-weight:800;">¡Bienvenida/o!<br>Ya podés crear tu cuenta</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n<td class="stack-col" width="6%">&nbsp;</td>\n<td class="stack-col" width="38%" valign="top">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-radius:12px;overflow:hidden;background-color:#fbfcfe;border:1px solid #edf1f6;">\n<tr>\n<td align="center" valign="middle" style="padding:14px;">\n<img src="cid:icono-bienvenida" alt="" style="display:block;width:150px;max-width:100%;height:auto;margin:0 auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 6px 40px;">\n<p style="margin:0 0 16px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Te invitaron a crear tu cuenta en el sistema de reservas de los Laboratorios de Investigación del Parque i.</p>\n<p style="margin:0 0 30px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">Con ella vas a poder reservar espacios y equipos, y hacer seguimiento a tus solicitudes.</p>\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:0 40px 30px 40px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="width:100%;">\n<tr>\n<td align="center" style="border-radius:8px;background-color:#102d69;">\n<a href="https://ijktwqnkknemjrokwcdn.supabase.co/auth/v1/verify?token=a3b0e19e07130f8d768872755f8308fbc68d6e6767e4f34d1d4307a6&amp;type=invite&amp;redirect_to=http://172.20.10.18:8091/completar-cuenta" target="_blank" style="display:block;padding:16px 24px;font-family:'Montserrat',Arial,sans-serif;font-size:15px;font-weight:800;letter-spacing:0.6px;color:#ffffff;text-align:center;text-transform:uppercase;">Ingresá aquí</a>\n</td>\n</tr>\n</table>\n\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático. Si no solicitaste este acceso,<br>podés ignorar este mensaje.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-06 00:31:02.9237+00	2026-09-06 00:31:04.421402+00	t	\N	\N	\N
33	santiagosuarez1136374@correo.itm.edu.co	Tu contraseña fue actualizada — Reservas Parque i	<!DOCTYPE html>\n<html lang="es" xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Reservas Parque i - Institución Universitaria ITM</title>\n<!--[if mso]>\n<noscript>\n<xml>\n<o:OfficeDocumentSettings>\n<o:PixelsPerInch>96</o:PixelsPerInch>\n</o:OfficeDocumentSettings>\n</xml>\n</noscript>\n<![endif]-->\n<style>\nbody, table, td, a { -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }\ntable, td { mso-table-lspace:0pt; mso-table-rspace:0pt; }\nimg { -ms-interpolation-mode:bicubic; border:0; height:auto; line-height:100%; outline:none; text-decoration:none; }\nbody { margin:0; padding:0; width:100% !important; height:100% !important; background-color:#eef1f6; }\na { text-decoration:none; }\n@media screen and (max-width:600px) {\n  .email-container { width:100% !important; }\n  .fluid-padding { padding-left:24px !important; padding-right:24px !important; }\n  .stack-col { display:block !important; width:100% !important; }\n  .header-right { text-align:left !important; padding-top:16px !important; }\n  .h1-mobile { font-size:24px !important; }\n}\n</style>\n</head>\n<body style="margin:0;padding:0;background-color:#eef1f6;font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;">\n<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#eef1f6;">Tu contraseña en Reservas Parque i fue actualizada.</div>\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef1f6;">\n<tr>\n<td align="center" style="padding:32px 16px;">\n<table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 20px rgba(11,27,77,0.09);">\n<tr>\n<td class="fluid-padding" style="padding:30px 40px 22px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0">\n<tr>\n<td class="stack-col" valign="middle" align="left">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr>\n<td valign="top" style="padding-right:14px;">\n<table role="presentation" cellpadding="0" cellspacing="0">\n<tr><td style="width:5px;height:12px;background-color:#102d69;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td></tr>\n<tr><td style="width:5px;height:12px;background-color:#56acde;font-size:0;line-height:0;">&nbsp;</td></tr>\n</table>\n</td>\n<td valign="middle">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:23px;font-weight:800;color:#102d69;line-height:1.25;">Reservas Parque i</p>\n<p style="margin:2px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;font-weight:600;color:#00a0b7;">Laboratorios de Investigación</p>\n</td>\n</tr>\n</table>\n</td>\n<td class="stack-col header-right" valign="middle" align="right" style="padding-left:16px;">\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin-left:auto;">\n<tr>\n<td style="border-left:1px solid #e3e7ee;padding-left:16px;">\n<img src="cid:logo-itm" alt="Institución Universitaria ITM" style="display:block;width:130px;max-width:130px;height:auto;">\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #e9ecf2;margin:0;">\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:32px 40px 6px 40px;">\n<p style="margin:0 0 6px 0;font-family:'Montserrat',Arial,sans-serif;font-size:20px;color:#102d69;font-weight:500;">Hola, <strong style="font-weight:800;">Santiago</strong></p>\n<h1 class="h1-mobile" style="margin:14px 0 0 0;font-family:'Montserrat',Arial,sans-serif;font-size:26px;line-height:1.3;color:#102d69;font-weight:800;">Tu contraseña fue<br>actualizada</h1>\n<table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 0 0;">\n<tr><td style="width:64px;height:4px;background-color:#00a0b7;font-size:0;line-height:0;border-radius:2px;">&nbsp;</td></tr>\n</table>\n</td>\n</tr>\n<tr>\n<td class="fluid-padding" style="padding:26px 40px 30px 40px;">\n<p style="margin:0 0 20px 0;font-family:'Montserrat',Arial,sans-serif;font-size:15px;line-height:1.75;color:#4a4f58;">La contraseña de tu cuenta en Reservas Parque i se actualizó correctamente.</p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:14px;line-height:1.7;color:#4a4f58;">Si no hiciste este cambio vos, contactá a soporte de inmediato.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px;">\n<hr style="border:none;border-top:1px solid #cfe6ee;margin:0;">\n</td>\n</tr>\n<tr>\n<td align="center" style="padding:20px 40px 28px 40px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;line-height:1.7;color:#9199a6;text-align:center;">Este es un correo automático de seguridad. Si no reconocés este cambio,<br>contactá a soporte de inmediato.</p>\n</td>\n</tr>\n<tr>\n<td style="padding:0 40px 36px 40px;">\n<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#eef4f9;border-radius:10px;">\n<tr>\n<td style="width:4px;background-color:#00a0b7;font-size:0;line-height:0;">&nbsp;</td>\n<td style="padding:18px 22px;">\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13.5px;font-weight:800;color:#102d69;">Soporte de reservas</p>\n<p style="margin:0 0 5px 0;font-family:'Montserrat',Arial,sans-serif;font-size:13px;"><a href="mailto:reservaslabparquei@correo.itm.edu.co" style="color:#00a0b7;font-weight:600;">reservaslabparquei@correo.itm.edu.co</a></p>\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:12.5px;color:#7a828d;">Institución Universitaria ITM</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n<table role="presentation" width="600" class="email-container" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">\n<tr>\n<td align="center" style="padding:18px 16px 0 16px;">\n<p style="margin:0;font-family:'Montserrat',Arial,sans-serif;font-size:11px;color:#a7adb6;">&copy; 2026 Institución Universitaria ITM &middot; Reacreditada en Alta Calidad</p>\n</td>\n</tr>\n</table>\n</td>\n</tr>\n</table>\n</body>\n</html>\n	enviado	0	2026-09-06 00:32:23.905346+00	2026-09-06 00:32:25.258077+00	t	\N	\N	\N
\.


--
-- Data for Name: ensayos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ensayos (id, nombre, zona_id, estado, created_at, updated_at, created_by, updated_by) FROM stdin;
\.


--
-- Data for Name: espacio_recursos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.espacio_recursos (id, espacio_id, recurso_id) FROM stdin;
2	2	2
3	2	3
\.


--
-- Data for Name: espacios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.espacios (id, nombre, laboratorio_id, descripcion, capacidad, estado, created_at, updated_at, created_by, updated_by) FROM stdin;
1	Ensayos	5	Sala de ensayos	2	activo	2026-08-24 17:37:54.034702+00	2026-08-24 17:37:54.034702+00	\N	\N
2	Sala 1	7	\N	2	activo	2026-09-01 18:49:19.928246+00	2026-09-01 18:49:19.928246+00	4	4
3	Sala 2	7	\N	10	activo	2026-09-02 20:59:22.112791+00	2026-09-02 20:59:22.112791+00	4	4
\.


--
-- Data for Name: evento_calendario_saliente; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.evento_calendario_saliente (id, reserva_id, accion, estado, intentos, graph_event_id, asunto, cuerpo, ubicacion, inicio, fin, asistentes, comentario, creado_en, procesado_en) FROM stdin;
\.


--
-- Data for Name: laboratorios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.laboratorios (id, nombre, ubicacion, capacidad, estado, descripcion, dias_atencion, hora_apertura, hora_cierre, horario_atencion, horas_antelacion, aprobacion_automatica, modalidad_reserva, correo, create_at, updated_at, created_by, updated_by, notificar_por_correo) FROM stdin;
5	Auditorio Pequeño	Edificio de Humanidades, Primer Piso	80	activo	\N	[0, 1, 2, 3, 4, 5]	07:00:00	20:00:00	{"0": [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "1": [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "2": [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "3": [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "4": [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], "5": [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]}	24	f	equipos	\N	\N	2026-08-24 21:15:03.438138+00	\N	\N	t
7	Laboratorio de Sistemas de Control y Robotica	Fraternidad	20	activo	\N	[0, 1, 2, 3, 4]	07:00:00	20:00:00	{"0": [7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19], "1": [7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19], "2": [7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19], "3": [7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19], "4": [7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19]}	0	f	mixto	robotica@itm.edu.co	\N	2026-09-02 20:58:28.667182+00	\N	4	t
\.


--
-- Data for Name: lista_espera; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.lista_espera (id, usuario_id, personal_id, recurso_id, fecha, hora_inicio, hora_fin, estado, created_at, notificada_en) FROM stdin;
\.


--
-- Data for Name: motivos_solicitud; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.motivos_solicitud (id, laboratorio_id, nombre, codigo, estado, created_at, updated_at, created_by, updated_by) FROM stdin;
1	5	Reserva en laboratorio	reserva_en_laboratorio	activo	2026-09-02 18:26:09.50755+00	2026-09-02 18:26:09.50755+00	\N	\N
2	5	Reserva fuera del laboratorio	reserva_fuera_laboratorio	activo	2026-09-02 18:26:09.50755+00	2026-09-02 18:26:09.50755+00	\N	\N
3	5	Orden de salida	orden_salida	activo	2026-09-02 18:26:09.50755+00	2026-09-02 18:26:09.50755+00	\N	\N
4	7	Reserva en laboratorio	reserva_en_laboratorio	activo	2026-09-02 18:26:09.50755+00	2026-09-02 18:26:09.50755+00	\N	\N
5	7	Reserva fuera del laboratorio	reserva_fuera_laboratorio	activo	2026-09-02 18:26:09.50755+00	2026-09-02 18:26:09.50755+00	\N	\N
6	7	Orden de salida	orden_salida	activo	2026-09-02 18:26:09.50755+00	2026-09-02 18:26:09.50755+00	\N	\N
\.


--
-- Data for Name: notificaciones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notificaciones (id, usuario_id, reserva_id, tipo, leida, created_at, personal_id) FROM stdin;
\.


--
-- Data for Name: personal; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.personal (id, username, email, supabase_id, rol, documento_identificacion, telefono, institucion, vinculacion, dependencia, created_at, updated_at, recibir_correos) FROM stdin;
1	administrador	admin@itm.edu.co	b5b3198a-78fa-43ac-9f18-2370807f0f29	admin	1034917433	3053695592	ITM	contratista_empleado	Parque i	2026-08-19 16:17:44.860143+00	2026-08-28 22:37:56.906885+00	t
2	juandorado	juandorado@itm.edu.co	0a3cdbad-fbe4-4586-9d31-9e43454de7de	gestor	\N	\N	\N	\N	\N	2026-09-01 16:27:49.072693+00	2026-09-01 16:27:49.072693+00	t
4	Juan Carlos Morales	juanmorales@itm.edu.co	8739232a-c23d-4081-8b9f-5c4b471381cd	gestor	80013068	3016868154	Institución Universitaria ITM	docente	Mecatronica	2026-09-01 16:42:38.539454+00	2026-09-02 21:02:38.821856+00	t
5	Santiago	santiagosuarez1136374@correo.itm.edu.co	1be59660-2207-4c18-85f1-1119e680f331	gestor	1034917433	3053695592	ITM	contratista_empleado	Direccion de la investigacion	2026-09-06 00:31:02.017593+00	2026-09-06 00:32:44.692723+00	t
\.


--
-- Data for Name: recursos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.recursos (id, nombre, laboratorio_id, tipo_recurso_id, descripcion, capacidad, estado, es_prestacion_servicio, create_at, update_at, created_by, update_by, placa, requiere_apoyo_auxiliar) FROM stdin;
2	Mesa 1	7	1	Mesa	1	activo	f	2026-09-01 18:14:55.641113+00	2026-09-01 18:14:55.641113+00	4	4	\N	f
3	Impresora 3D	7	1	\N	1	activo	f	2026-09-01 18:29:05.473118+00	2026-09-01 18:29:05.473118+00	4	4	\N	f
\.


--
-- Data for Name: reserva_acompanantes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reserva_acompanantes (id, reserva_id, nombre, correo) FROM stdin;
\.


--
-- Data for Name: reserva_ensayos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reserva_ensayos (id, reserva_id, ensayo_id) FROM stdin;
\.


--
-- Data for Name: reserva_espacios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reserva_espacios (id, reserva_id, espacio_id, fecha, hora_inicio, hora_fin, estado) FROM stdin;
\.


--
-- Data for Name: reserva_recursos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reserva_recursos (id, reserva_id, recurso_id, fecha, hora_inicio, hora_fin, estado) FROM stdin;
5	3	2	2026-09-01	14:00:00	16:00:00	aprobada
6	3	3	2026-09-01	14:00:00	16:00:00	aprobada
7	4	2	2026-09-01	16:00:00	18:00:00	aprobada
8	4	3	2026-09-01	16:00:00	18:00:00	aprobada
9	5	3	2026-09-01	18:00:00	20:00:00	aprobada
10	6	3	2026-09-03	07:00:00	12:00:00	aprobada
\.


--
-- Data for Name: reservas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reservas (id, usuario_id, laboratorio_id, recurso_id, fecha, hora_inicio, hora_fin, estado, asistentes, tipo, asistio, created_at, updated_at, motivo_rechazo, descripcion, tipo_solicitud, ubicacion_uso, requiere_apoyo_auxiliar, personal_id, recordatorio_enviado_en, serie_id, tipo_reserva_id, propuesta_motivo, propuesta_horarios, propuesta_por, propuesta_en, motivo_solicitud_id, grupo_id, graph_event_id, calendario_secuencia) FROM stdin;
3	\N	7	2	2026-09-01	14:00:00	16:00:00	aprobada	1	trabajo_investigacion	\N	2026-09-01 18:28:17.443299+00	2026-09-01 18:40:09.280894+00	\N	\N	reserva_en_laboratorio	\N	f	4	2026-09-01 13:40:09.277558+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	0
4	\N	7	2	2026-09-01	16:00:00	18:00:00	aprobada	1	trabajo_investigacion	\N	2026-09-01 18:47:45.191681+00	2026-09-01 20:10:09.289936+00	\N	\N	reserva_fuera_laboratorio	Dentro del Campus	t	4	2026-09-01 15:10:09.278842+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	0
5	\N	7	3	2026-09-01	18:00:00	20:00:00	aprobada	1	trabajo_investigacion	\N	2026-09-01 18:48:53.9029+00	2026-09-01 22:10:09.283368+00	\N	\N	reserva_en_laboratorio	\N	f	4	2026-09-01 17:10:09.278739+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	0
6	\N	7	3	2026-09-03	07:00:00	12:00:00	aprobada	1	\N	\N	2026-09-02 21:01:03.076395+00	2026-09-03 11:14:58.883857+00	\N	\N	reserva_en_laboratorio	\N	f	4	2026-09-03 06:14:58.880868+00	\N	1	\N	\N	\N	\N	6	\N	\N	0
\.


--
-- Data for Name: tipos_recursos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tipos_recursos (id, nombre, descripcion, activo) FROM stdin;
1	General	Tipo general de recurso	activo
\.


--
-- Data for Name: tipos_reserva; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tipos_reserva (id, laboratorio_id, nombre, estado, created_at, updated_at, created_by, updated_by) FROM stdin;
1	7	Investigación	activo	2026-09-02 20:57:39.210157+00	2026-09-02 20:57:39.210157+00	4	4
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuarios (id, username, email, hashed_password, rol, created_at, updated_at, debe_cambiar_password, supabase_id, documento_identificacion, telefono, institucion, vinculacion, dependencia, recibir_correos) FROM stdin;
2	Santi	prueba@gmail.com	$2b$12$r1CXloS5aksfCKpClcYkEeSmqZqcG8BIQF.4k0ppq1y0X.i6DUAE2	usuario	2026-08-19 16:21:26.133568+00	2026-08-27 19:16:40.872814+00	f	\N	\N	\N	\N	\N	\N	t
10	prueba	sgc-lia@itm.edu.co	$2b$12$/PDaYZ2mjDTsMG229g5EcOdCssRtQ90JInHNHpbF5iRiibeG0oZ8G	usuario	2026-08-28 22:38:37.324554+00	2026-08-28 22:38:37.324554+00	f	9ce29f44-0119-456d-82b5-1d4f52fe1a23	\N	\N	\N	\N	\N	t
\.


--
-- Data for Name: usuarios_laboratorios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuarios_laboratorios (id, usuario_id, laboratorio_id) FROM stdin;
3	2	7
5	4	7
6	5	5
\.


--
-- Name: control_cambios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.control_cambios_id_seq', 66, true);


--
-- Name: correo_saliente_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.correo_saliente_id_seq', 33, true);


--
-- Name: ensayos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ensayos_id_seq', 1, false);


--
-- Name: espacios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.espacios_id_seq', 7, true);


--
-- Name: evento_calendario_saliente_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.evento_calendario_saliente_id_seq', 1, false);


--
-- Name: lista_espera_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.lista_espera_id_seq', 1, false);


--
-- Name: motivos_solicitud_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.motivos_solicitud_id_seq', 6, true);


--
-- Name: notificaciones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notificaciones_id_seq', 4, true);


--
-- Name: personal_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.personal_id_seq', 5, true);


--
-- Name: recursos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.recursos_id_seq', 3, true);


--
-- Name: reserva_acompanantes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reserva_acompanantes_id_seq', 1, false);


--
-- Name: reserva_ensayos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reserva_ensayos_id_seq', 1, false);


--
-- Name: reserva_recursos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reserva_recursos_id_seq', 10, true);


--
-- Name: reserva_zonas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reserva_zonas_id_seq', 1, false);


--
-- Name: reservas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reservas_id_seq', 6, true);


--
-- Name: tipos_recursos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tipos_recursos_id_seq', 1, true);


--
-- Name: tipos_reserva_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tipos_reserva_id_seq', 1, true);


--
-- Name: usuarios_espacios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuarios_espacios_id_seq', 6, true);


--
-- Name: usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuarios_id_seq', 11, true);


--
-- Name: zona_recursos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.zona_recursos_id_seq', 3, true);


--
-- Name: zonas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.zonas_id_seq', 3, true);


--
-- Name: control_cambios control_cambios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.control_cambios
    ADD CONSTRAINT control_cambios_pkey PRIMARY KEY (id);


--
-- Name: correo_saliente correo_saliente_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.correo_saliente
    ADD CONSTRAINT correo_saliente_pkey PRIMARY KEY (id);


--
-- Name: ensayos ensayos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ensayos
    ADD CONSTRAINT ensayos_pkey PRIMARY KEY (id);


--
-- Name: laboratorios espacios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.laboratorios
    ADD CONSTRAINT espacios_pkey PRIMARY KEY (id);


--
-- Name: evento_calendario_saliente evento_calendario_saliente_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evento_calendario_saliente
    ADD CONSTRAINT evento_calendario_saliente_pkey PRIMARY KEY (id);


--
-- Name: lista_espera lista_espera_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lista_espera
    ADD CONSTRAINT lista_espera_pkey PRIMARY KEY (id);


--
-- Name: motivos_solicitud motivos_solicitud_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.motivos_solicitud
    ADD CONSTRAINT motivos_solicitud_pkey PRIMARY KEY (id);


--
-- Name: notificaciones notificaciones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notificaciones
    ADD CONSTRAINT notificaciones_pkey PRIMARY KEY (id);


--
-- Name: personal personal_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personal
    ADD CONSTRAINT personal_pkey PRIMARY KEY (id);


--
-- Name: recursos recursos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recursos
    ADD CONSTRAINT recursos_pkey PRIMARY KEY (id);


--
-- Name: reserva_acompanantes reserva_acompanantes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_acompanantes
    ADD CONSTRAINT reserva_acompanantes_pkey PRIMARY KEY (id);


--
-- Name: reserva_ensayos reserva_ensayos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_ensayos
    ADD CONSTRAINT reserva_ensayos_pkey PRIMARY KEY (id);


--
-- Name: reserva_espacios reserva_espacios_sin_solapamiento; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_espacios
    ADD CONSTRAINT reserva_espacios_sin_solapamiento EXCLUDE USING gist (espacio_id WITH =, fecha WITH =, tsrange((fecha + hora_inicio), (fecha + hora_fin), '[)'::text) WITH &&) WHERE (((estado)::text = ANY ((ARRAY['esperando'::character varying, 'aprobada'::character varying])::text[])));


--
-- Name: reserva_recursos reserva_recursos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_recursos
    ADD CONSTRAINT reserva_recursos_pkey PRIMARY KEY (id);


--
-- Name: reserva_recursos reserva_recursos_sin_solapamiento; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_recursos
    ADD CONSTRAINT reserva_recursos_sin_solapamiento EXCLUDE USING gist (recurso_id WITH =, fecha WITH =, tsrange((fecha + hora_inicio), (fecha + hora_fin), '[)'::text) WITH &&) WHERE (((estado)::text = ANY ((ARRAY['esperando'::character varying, 'aprobada'::character varying])::text[])));


--
-- Name: reserva_espacios reserva_zonas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_espacios
    ADD CONSTRAINT reserva_zonas_pkey PRIMARY KEY (id);


--
-- Name: reservas reservas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservas
    ADD CONSTRAINT reservas_pkey PRIMARY KEY (id);


--
-- Name: reservas reservas_sin_solapamiento; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservas
    ADD CONSTRAINT reservas_sin_solapamiento EXCLUDE USING gist (recurso_id WITH =, fecha WITH =, tsrange((fecha + hora_inicio), (fecha + hora_fin), '[)'::text) WITH &&) WHERE (((estado)::text = ANY ((ARRAY['esperando'::character varying, 'aprobada'::character varying])::text[])));


--
-- Name: tipos_recursos tipos_recursos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipos_recursos
    ADD CONSTRAINT tipos_recursos_pkey PRIMARY KEY (id);


--
-- Name: tipos_reserva tipos_reserva_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipos_reserva
    ADD CONSTRAINT tipos_reserva_pkey PRIMARY KEY (id);


--
-- Name: espacio_recursos uq_espacio_recursos_recurso; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.espacio_recursos
    ADD CONSTRAINT uq_espacio_recursos_recurso UNIQUE (recurso_id);


--
-- Name: motivos_solicitud uq_motivos_solicitud_laboratorio_codigo; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.motivos_solicitud
    ADD CONSTRAINT uq_motivos_solicitud_laboratorio_codigo UNIQUE (laboratorio_id, codigo);


--
-- Name: motivos_solicitud uq_motivos_solicitud_laboratorio_nombre; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.motivos_solicitud
    ADD CONSTRAINT uq_motivos_solicitud_laboratorio_nombre UNIQUE (laboratorio_id, nombre);


--
-- Name: reserva_acompanantes uq_reserva_acompanantes_correo; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_acompanantes
    ADD CONSTRAINT uq_reserva_acompanantes_correo UNIQUE (reserva_id, correo);


--
-- Name: reserva_ensayos uq_reserva_ensayos_par; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_ensayos
    ADD CONSTRAINT uq_reserva_ensayos_par UNIQUE (reserva_id, ensayo_id);


--
-- Name: reserva_espacios uq_reserva_espacios_reserva_espacio; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_espacios
    ADD CONSTRAINT uq_reserva_espacios_reserva_espacio UNIQUE (reserva_id, espacio_id);


--
-- Name: reserva_recursos uq_reserva_recursos_reserva_recurso; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_recursos
    ADD CONSTRAINT uq_reserva_recursos_reserva_recurso UNIQUE (reserva_id, recurso_id);


--
-- Name: tipos_reserva uq_tipos_reserva_laboratorio_nombre; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipos_reserva
    ADD CONSTRAINT uq_tipos_reserva_laboratorio_nombre UNIQUE (laboratorio_id, nombre);


--
-- Name: usuarios_laboratorios uq_usuarios_laboratorios_usuario; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios_laboratorios
    ADD CONSTRAINT uq_usuarios_laboratorios_usuario UNIQUE (usuario_id);


--
-- Name: usuarios_laboratorios usuarios_espacios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios_laboratorios
    ADD CONSTRAINT usuarios_espacios_pkey PRIMARY KEY (id);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- Name: espacio_recursos zona_recursos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.espacio_recursos
    ADD CONSTRAINT zona_recursos_pkey PRIMARY KEY (id);


--
-- Name: espacios zonas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.espacios
    ADD CONSTRAINT zonas_pkey PRIMARY KEY (id);


--
-- Name: ix_control_cambios_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_control_cambios_created_at ON public.control_cambios USING btree (created_at);


--
-- Name: ix_control_cambios_entidad; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_control_cambios_entidad ON public.control_cambios USING btree (entidad);


--
-- Name: ix_control_cambios_usuario_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_control_cambios_usuario_id ON public.control_cambios USING btree (usuario_id);


--
-- Name: ix_ensayos_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ensayos_id ON public.ensayos USING btree (id);


--
-- Name: ix_ensayos_zona_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ensayos_zona_id ON public.ensayos USING btree (zona_id);


--
-- Name: ix_espacios_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_espacios_id ON public.laboratorios USING btree (id);


--
-- Name: ix_evento_calendario_saliente_reserva_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_evento_calendario_saliente_reserva_id ON public.evento_calendario_saliente USING btree (reserva_id);


--
-- Name: ix_lista_espera_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_lista_espera_fecha ON public.lista_espera USING btree (fecha);


--
-- Name: ix_lista_espera_recurso_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_lista_espera_recurso_id ON public.lista_espera USING btree (recurso_id);


--
-- Name: ix_motivos_solicitud_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_motivos_solicitud_id ON public.motivos_solicitud USING btree (id);


--
-- Name: ix_motivos_solicitud_laboratorio_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_motivos_solicitud_laboratorio_id ON public.motivos_solicitud USING btree (laboratorio_id);


--
-- Name: ix_personal_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_personal_email ON public.personal USING btree (email);


--
-- Name: ix_personal_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_personal_id ON public.personal USING btree (id);


--
-- Name: ix_personal_supabase_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_personal_supabase_id ON public.personal USING btree (supabase_id);


--
-- Name: ix_personal_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_personal_username ON public.personal USING btree (username);


--
-- Name: ix_recursos_laboratorio_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_recursos_laboratorio_id ON public.recursos USING btree (laboratorio_id);


--
-- Name: ix_reserva_acompanantes_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reserva_acompanantes_id ON public.reserva_acompanantes USING btree (id);


--
-- Name: ix_reserva_acompanantes_reserva_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reserva_acompanantes_reserva_id ON public.reserva_acompanantes USING btree (reserva_id);


--
-- Name: ix_reserva_ensayos_ensayo_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reserva_ensayos_ensayo_id ON public.reserva_ensayos USING btree (ensayo_id);


--
-- Name: ix_reserva_ensayos_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reserva_ensayos_id ON public.reserva_ensayos USING btree (id);


--
-- Name: ix_reserva_ensayos_reserva_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reserva_ensayos_reserva_id ON public.reserva_ensayos USING btree (reserva_id);


--
-- Name: ix_reserva_recursos_recurso_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reserva_recursos_recurso_id ON public.reserva_recursos USING btree (recurso_id);


--
-- Name: ix_reserva_recursos_reserva_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reserva_recursos_reserva_id ON public.reserva_recursos USING btree (reserva_id);


--
-- Name: ix_reserva_zonas_reserva_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reserva_zonas_reserva_id ON public.reserva_espacios USING btree (reserva_id);


--
-- Name: ix_reserva_zonas_zona_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reserva_zonas_zona_id ON public.reserva_espacios USING btree (espacio_id);


--
-- Name: ix_reservas_espacio_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reservas_espacio_id ON public.reservas USING btree (laboratorio_id);


--
-- Name: ix_reservas_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reservas_estado ON public.reservas USING btree (estado);


--
-- Name: ix_reservas_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reservas_fecha ON public.reservas USING btree (fecha);


--
-- Name: ix_reservas_grupo_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reservas_grupo_id ON public.reservas USING btree (grupo_id);


--
-- Name: ix_reservas_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reservas_id ON public.reservas USING btree (id);


--
-- Name: ix_reservas_recurso_fecha_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reservas_recurso_fecha_estado ON public.reservas USING btree (recurso_id, fecha, estado);


--
-- Name: ix_reservas_recurso_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reservas_recurso_id ON public.reservas USING btree (recurso_id);


--
-- Name: ix_reservas_serie_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reservas_serie_id ON public.reservas USING btree (serie_id);


--
-- Name: ix_reservas_usuario_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reservas_usuario_id ON public.reservas USING btree (usuario_id);


--
-- Name: ix_tipos_reserva_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tipos_reserva_id ON public.tipos_reserva USING btree (id);


--
-- Name: ix_tipos_reserva_laboratorio_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tipos_reserva_laboratorio_id ON public.tipos_reserva USING btree (laboratorio_id);


--
-- Name: ix_usuarios_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_usuarios_email ON public.usuarios USING btree (email);


--
-- Name: ix_usuarios_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_usuarios_id ON public.usuarios USING btree (id);


--
-- Name: ix_usuarios_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_usuarios_username ON public.usuarios USING btree (username);


--
-- Name: ix_zona_recursos_zona_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_zona_recursos_zona_id ON public.espacio_recursos USING btree (espacio_id);


--
-- Name: ix_zonas_espacio_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_zonas_espacio_id ON public.espacios USING btree (laboratorio_id);


--
-- Name: ix_zonas_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_zonas_id ON public.espacios USING btree (id);


--
-- Name: uq_recursos_placa; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_recursos_placa ON public.recursos USING btree (placa);


--
-- Name: uq_usuarios_supabase_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_usuarios_supabase_id ON public.usuarios USING btree (supabase_id);


--
-- Name: control_cambios control_cambios_personal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.control_cambios
    ADD CONSTRAINT control_cambios_personal_id_fkey FOREIGN KEY (personal_id) REFERENCES public.personal(id) ON DELETE SET NULL;


--
-- Name: control_cambios control_cambios_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.control_cambios
    ADD CONSTRAINT control_cambios_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: ensayos ensayos_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ensayos
    ADD CONSTRAINT ensayos_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.personal(id);


--
-- Name: ensayos ensayos_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ensayos
    ADD CONSTRAINT ensayos_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.personal(id);


--
-- Name: ensayos ensayos_zona_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ensayos
    ADD CONSTRAINT ensayos_zona_id_fkey FOREIGN KEY (zona_id) REFERENCES public.espacios(id);


--
-- Name: espacios espacios_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.espacios
    ADD CONSTRAINT espacios_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.personal(id);


--
-- Name: espacios espacios_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.espacios
    ADD CONSTRAINT espacios_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.personal(id);


--
-- Name: evento_calendario_saliente evento_calendario_saliente_reserva_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evento_calendario_saliente
    ADD CONSTRAINT evento_calendario_saliente_reserva_id_fkey FOREIGN KEY (reserva_id) REFERENCES public.reservas(id) ON DELETE CASCADE;


--
-- Name: recursos fk_recursos_tipo; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recursos
    ADD CONSTRAINT fk_recursos_tipo FOREIGN KEY (tipo_recurso_id) REFERENCES public.tipos_recursos(id);


--
-- Name: reservas fk_reservas_recurso; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservas
    ADD CONSTRAINT fk_reservas_recurso FOREIGN KEY (recurso_id) REFERENCES public.recursos(id);


--
-- Name: laboratorios laboratorios_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.laboratorios
    ADD CONSTRAINT laboratorios_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.personal(id);


--
-- Name: laboratorios laboratorios_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.laboratorios
    ADD CONSTRAINT laboratorios_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.personal(id);


--
-- Name: lista_espera lista_espera_personal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lista_espera
    ADD CONSTRAINT lista_espera_personal_id_fkey FOREIGN KEY (personal_id) REFERENCES public.personal(id) ON DELETE CASCADE;


--
-- Name: lista_espera lista_espera_recurso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lista_espera
    ADD CONSTRAINT lista_espera_recurso_id_fkey FOREIGN KEY (recurso_id) REFERENCES public.recursos(id) ON DELETE CASCADE;


--
-- Name: lista_espera lista_espera_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lista_espera
    ADD CONSTRAINT lista_espera_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE;


--
-- Name: motivos_solicitud motivos_solicitud_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.motivos_solicitud
    ADD CONSTRAINT motivos_solicitud_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.personal(id);


--
-- Name: motivos_solicitud motivos_solicitud_laboratorio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.motivos_solicitud
    ADD CONSTRAINT motivos_solicitud_laboratorio_id_fkey FOREIGN KEY (laboratorio_id) REFERENCES public.laboratorios(id);


--
-- Name: motivos_solicitud motivos_solicitud_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.motivos_solicitud
    ADD CONSTRAINT motivos_solicitud_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.personal(id);


--
-- Name: notificaciones notificaciones_personal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notificaciones
    ADD CONSTRAINT notificaciones_personal_id_fkey FOREIGN KEY (personal_id) REFERENCES public.personal(id) ON DELETE CASCADE;


--
-- Name: notificaciones notificaciones_reserva_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notificaciones
    ADD CONSTRAINT notificaciones_reserva_id_fkey FOREIGN KEY (reserva_id) REFERENCES public.reservas(id) ON DELETE CASCADE;


--
-- Name: notificaciones notificaciones_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notificaciones
    ADD CONSTRAINT notificaciones_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE;


--
-- Name: recursos recursos_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recursos
    ADD CONSTRAINT recursos_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.personal(id);


--
-- Name: recursos recursos_espacio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recursos
    ADD CONSTRAINT recursos_espacio_id_fkey FOREIGN KEY (laboratorio_id) REFERENCES public.laboratorios(id);


--
-- Name: recursos recursos_tipo_recurso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recursos
    ADD CONSTRAINT recursos_tipo_recurso_id_fkey FOREIGN KEY (tipo_recurso_id) REFERENCES public.tipos_recursos(id);


--
-- Name: recursos recursos_update_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recursos
    ADD CONSTRAINT recursos_update_by_fkey FOREIGN KEY (update_by) REFERENCES public.personal(id);


--
-- Name: reserva_acompanantes reserva_acompanantes_reserva_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_acompanantes
    ADD CONSTRAINT reserva_acompanantes_reserva_id_fkey FOREIGN KEY (reserva_id) REFERENCES public.reservas(id) ON DELETE CASCADE;


--
-- Name: reserva_ensayos reserva_ensayos_ensayo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_ensayos
    ADD CONSTRAINT reserva_ensayos_ensayo_id_fkey FOREIGN KEY (ensayo_id) REFERENCES public.ensayos(id);


--
-- Name: reserva_ensayos reserva_ensayos_reserva_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_ensayos
    ADD CONSTRAINT reserva_ensayos_reserva_id_fkey FOREIGN KEY (reserva_id) REFERENCES public.reservas(id) ON DELETE CASCADE;


--
-- Name: reserva_recursos reserva_recursos_recurso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_recursos
    ADD CONSTRAINT reserva_recursos_recurso_id_fkey FOREIGN KEY (recurso_id) REFERENCES public.recursos(id);


--
-- Name: reserva_recursos reserva_recursos_reserva_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_recursos
    ADD CONSTRAINT reserva_recursos_reserva_id_fkey FOREIGN KEY (reserva_id) REFERENCES public.reservas(id) ON DELETE CASCADE;


--
-- Name: reserva_espacios reserva_zonas_reserva_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_espacios
    ADD CONSTRAINT reserva_zonas_reserva_id_fkey FOREIGN KEY (reserva_id) REFERENCES public.reservas(id) ON DELETE CASCADE;


--
-- Name: reserva_espacios reserva_zonas_zona_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_espacios
    ADD CONSTRAINT reserva_zonas_zona_id_fkey FOREIGN KEY (espacio_id) REFERENCES public.espacios(id);


--
-- Name: reservas reservas_espacio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservas
    ADD CONSTRAINT reservas_espacio_id_fkey FOREIGN KEY (laboratorio_id) REFERENCES public.laboratorios(id);


--
-- Name: reservas reservas_motivo_solicitud_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservas
    ADD CONSTRAINT reservas_motivo_solicitud_id_fkey FOREIGN KEY (motivo_solicitud_id) REFERENCES public.motivos_solicitud(id);


--
-- Name: reservas reservas_personal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservas
    ADD CONSTRAINT reservas_personal_id_fkey FOREIGN KEY (personal_id) REFERENCES public.personal(id);


--
-- Name: reservas reservas_recurso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservas
    ADD CONSTRAINT reservas_recurso_id_fkey FOREIGN KEY (recurso_id) REFERENCES public.recursos(id);


--
-- Name: reservas reservas_tipo_reserva_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservas
    ADD CONSTRAINT reservas_tipo_reserva_id_fkey FOREIGN KEY (tipo_reserva_id) REFERENCES public.tipos_reserva(id);


--
-- Name: reservas reservas_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservas
    ADD CONSTRAINT reservas_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id);


--
-- Name: tipos_reserva tipos_reserva_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipos_reserva
    ADD CONSTRAINT tipos_reserva_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.personal(id);


--
-- Name: tipos_reserva tipos_reserva_laboratorio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipos_reserva
    ADD CONSTRAINT tipos_reserva_laboratorio_id_fkey FOREIGN KEY (laboratorio_id) REFERENCES public.laboratorios(id);


--
-- Name: tipos_reserva tipos_reserva_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipos_reserva
    ADD CONSTRAINT tipos_reserva_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.personal(id);


--
-- Name: usuarios_laboratorios usuarios_espacios_espacio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios_laboratorios
    ADD CONSTRAINT usuarios_espacios_espacio_id_fkey FOREIGN KEY (laboratorio_id) REFERENCES public.laboratorios(id);


--
-- Name: usuarios_laboratorios usuarios_laboratorios_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios_laboratorios
    ADD CONSTRAINT usuarios_laboratorios_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.personal(id);


--
-- Name: espacio_recursos zona_recursos_recurso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.espacio_recursos
    ADD CONSTRAINT zona_recursos_recurso_id_fkey FOREIGN KEY (recurso_id) REFERENCES public.recursos(id) ON DELETE CASCADE;


--
-- Name: espacio_recursos zona_recursos_zona_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.espacio_recursos
    ADD CONSTRAINT zona_recursos_zona_id_fkey FOREIGN KEY (espacio_id) REFERENCES public.espacios(id) ON DELETE CASCADE;


--
-- Name: espacios zonas_espacio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.espacios
    ADD CONSTRAINT zonas_espacio_id_fkey FOREIGN KEY (laboratorio_id) REFERENCES public.laboratorios(id);


--
-- PostgreSQL database dump complete
--

\unrestrict 3Iaej6gMlEaVAESqsfUpXYpr2w6fEcfVbSlFYWW6DwS4NsKGN46NYZvBYnyG8tr

--
-- PostgreSQL database cluster dump complete
--

