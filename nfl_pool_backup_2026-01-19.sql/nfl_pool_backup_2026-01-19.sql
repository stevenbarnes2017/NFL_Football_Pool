--
-- PostgreSQL database dump
--

\restrict CmObuXEwVMI8AgdHNpQxDdNgYnfE3rF6gt3KaCMt2YeJRaMX3jYaPYRyg3RRLdZ

-- Dumped from database version 17.6 (Debian 17.6-2.pgdg12+1)
-- Dumped by pg_dump version 18.1 (Debian 18.1-1.pgdg12+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: pickarena_prod_db_user
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO pickarena_prod_db_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: pickarena_prod_db_user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO pickarena_prod_db_user;

--
-- Name: announcement; Type: TABLE; Schema: public; Owner: pickarena_prod_db_user
--

CREATE TABLE public.announcement (
    id integer NOT NULL,
    title character varying(140) NOT NULL,
    body text NOT NULL,
    created_at timestamp without time zone NOT NULL,
    created_by_user_id integer NOT NULL,
    season_year integer,
    season_type character varying(20),
    week integer,
    pinned boolean NOT NULL,
    is_active boolean NOT NULL
);


ALTER TABLE public.announcement OWNER TO pickarena_prod_db_user;

--
-- Name: announcement_id_seq; Type: SEQUENCE; Schema: public; Owner: pickarena_prod_db_user
--

CREATE SEQUENCE public.announcement_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.announcement_id_seq OWNER TO pickarena_prod_db_user;

--
-- Name: announcement_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pickarena_prod_db_user
--

ALTER SEQUENCE public.announcement_id_seq OWNED BY public.announcement.id;


--
-- Name: board_post; Type: TABLE; Schema: public; Owner: pickarena_prod_db_user
--

CREATE TABLE public.board_post (
    id integer NOT NULL,
    thread_id integer NOT NULL,
    author_user_id integer NOT NULL,
    body text NOT NULL,
    created_at timestamp without time zone NOT NULL,
    is_active boolean NOT NULL,
    edited_at timestamp without time zone
);


ALTER TABLE public.board_post OWNER TO pickarena_prod_db_user;

--
-- Name: board_post_id_seq; Type: SEQUENCE; Schema: public; Owner: pickarena_prod_db_user
--

CREATE SEQUENCE public.board_post_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.board_post_id_seq OWNER TO pickarena_prod_db_user;

--
-- Name: board_post_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pickarena_prod_db_user
--

ALTER SEQUENCE public.board_post_id_seq OWNED BY public.board_post.id;


--
-- Name: board_thread; Type: TABLE; Schema: public; Owner: pickarena_prod_db_user
--

CREATE TABLE public.board_thread (
    id integer NOT NULL,
    title character varying(180) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    created_by_user_id integer NOT NULL,
    season_year integer,
    season_type character varying(20),
    week integer,
    pinned boolean NOT NULL,
    locked boolean NOT NULL,
    is_active boolean NOT NULL,
    last_activity_at timestamp without time zone NOT NULL
);


ALTER TABLE public.board_thread OWNER TO pickarena_prod_db_user;

--
-- Name: board_thread_id_seq; Type: SEQUENCE; Schema: public; Owner: pickarena_prod_db_user
--

CREATE SEQUENCE public.board_thread_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.board_thread_id_seq OWNER TO pickarena_prod_db_user;

--
-- Name: board_thread_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pickarena_prod_db_user
--

ALTER SEQUENCE public.board_thread_id_seq OWNED BY public.board_thread.id;


--
-- Name: game; Type: TABLE; Schema: public; Owner: pickarena_prod_db_user
--

CREATE TABLE public.game (
    id integer NOT NULL,
    game_id character varying(50) NOT NULL,
    home_team character varying(50) NOT NULL,
    away_team character varying(50) NOT NULL,
    spread double precision,
    favorite_team character varying(50),
    commence_time_mt timestamp with time zone,
    home_team_score integer,
    away_team_score integer,
    saved_at timestamp without time zone,
    status character varying(50),
    week integer,
    season_year integer NOT NULL,
    season_type character varying(20) NOT NULL,
    week_label character varying(10)
);


ALTER TABLE public.game OWNER TO pickarena_prod_db_user;

--
-- Name: game_id_seq; Type: SEQUENCE; Schema: public; Owner: pickarena_prod_db_user
--

CREATE SEQUENCE public.game_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.game_id_seq OWNER TO pickarena_prod_db_user;

--
-- Name: game_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pickarena_prod_db_user
--

ALTER SEQUENCE public.game_id_seq OWNED BY public.game.id;


--
-- Name: job_run; Type: TABLE; Schema: public; Owner: pickarena_prod_db_user
--

CREATE TABLE public.job_run (
    id integer NOT NULL,
    job_name character varying(50) NOT NULL,
    ran_at timestamp without time zone NOT NULL,
    ok boolean NOT NULL,
    inserted integer,
    updated integer,
    unchanged integer,
    failed_weeks integer,
    message character varying(255)
);


ALTER TABLE public.job_run OWNER TO pickarena_prod_db_user;

--
-- Name: job_run_id_seq; Type: SEQUENCE; Schema: public; Owner: pickarena_prod_db_user
--

CREATE SEQUENCE public.job_run_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.job_run_id_seq OWNER TO pickarena_prod_db_user;

--
-- Name: job_run_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pickarena_prod_db_user
--

ALTER SEQUENCE public.job_run_id_seq OWNED BY public.job_run.id;


--
-- Name: pick; Type: TABLE; Schema: public; Owner: pickarena_prod_db_user
--

CREATE TABLE public.pick (
    id integer NOT NULL,
    user_id integer NOT NULL,
    game_id integer NOT NULL,
    team_picked character varying(100),
    confidence integer,
    pick_time timestamp without time zone,
    week integer NOT NULL,
    points_earned integer,
    is_overridden boolean
);


ALTER TABLE public.pick OWNER TO pickarena_prod_db_user;

--
-- Name: pick_id_seq; Type: SEQUENCE; Schema: public; Owner: pickarena_prod_db_user
--

CREATE SEQUENCE public.pick_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pick_id_seq OWNER TO pickarena_prod_db_user;

--
-- Name: pick_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pickarena_prod_db_user
--

ALTER SEQUENCE public.pick_id_seq OWNED BY public.pick.id;


--
-- Name: settings; Type: TABLE; Schema: public; Owner: pickarena_prod_db_user
--

CREATE TABLE public.settings (
    id integer NOT NULL,
    current_week integer NOT NULL,
    season_year integer NOT NULL,
    season_type character varying(10) NOT NULL,
    season_locked boolean NOT NULL
);


ALTER TABLE public.settings OWNER TO pickarena_prod_db_user;

--
-- Name: settings_id_seq; Type: SEQUENCE; Schema: public; Owner: pickarena_prod_db_user
--

CREATE SEQUENCE public.settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.settings_id_seq OWNER TO pickarena_prod_db_user;

--
-- Name: settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pickarena_prod_db_user
--

ALTER SEQUENCE public.settings_id_seq OWNED BY public.settings.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: pickarena_prod_db_user
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    username character varying(150) NOT NULL,
    full_name character varying(150),
    email character varying(150),
    phone character varying(20),
    favorite_team character varying(50),
    password character varying(255) NOT NULL,
    is_admin boolean,
    sms_opt_in boolean DEFAULT false NOT NULL
);


ALTER TABLE public."user" OWNER TO pickarena_prod_db_user;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: pickarena_prod_db_user
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_id_seq OWNER TO pickarena_prod_db_user;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pickarena_prod_db_user
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: user_score; Type: TABLE; Schema: public; Owner: pickarena_prod_db_user
--

CREATE TABLE public.user_score (
    id integer NOT NULL,
    user_id integer NOT NULL,
    week integer NOT NULL,
    score double precision NOT NULL,
    calculated_at timestamp without time zone,
    season_year integer NOT NULL,
    season_type character varying(10) NOT NULL
);


ALTER TABLE public.user_score OWNER TO pickarena_prod_db_user;

--
-- Name: user_score_id_seq; Type: SEQUENCE; Schema: public; Owner: pickarena_prod_db_user
--

CREATE SEQUENCE public.user_score_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_score_id_seq OWNER TO pickarena_prod_db_user;

--
-- Name: user_score_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pickarena_prod_db_user
--

ALTER SEQUENCE public.user_score_id_seq OWNED BY public.user_score.id;


--
-- Name: announcement id; Type: DEFAULT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.announcement ALTER COLUMN id SET DEFAULT nextval('public.announcement_id_seq'::regclass);


--
-- Name: board_post id; Type: DEFAULT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.board_post ALTER COLUMN id SET DEFAULT nextval('public.board_post_id_seq'::regclass);


--
-- Name: board_thread id; Type: DEFAULT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.board_thread ALTER COLUMN id SET DEFAULT nextval('public.board_thread_id_seq'::regclass);


--
-- Name: game id; Type: DEFAULT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.game ALTER COLUMN id SET DEFAULT nextval('public.game_id_seq'::regclass);


--
-- Name: job_run id; Type: DEFAULT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.job_run ALTER COLUMN id SET DEFAULT nextval('public.job_run_id_seq'::regclass);


--
-- Name: pick id; Type: DEFAULT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.pick ALTER COLUMN id SET DEFAULT nextval('public.pick_id_seq'::regclass);


--
-- Name: settings id; Type: DEFAULT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.settings ALTER COLUMN id SET DEFAULT nextval('public.settings_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Name: user_score id; Type: DEFAULT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.user_score ALTER COLUMN id SET DEFAULT nextval('public.user_score_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: pickarena_prod_db_user
--

COPY public.alembic_version (version_num) FROM stdin;
94d2f735e51c
\.


--
-- Data for Name: announcement; Type: TABLE DATA; Schema: public; Owner: pickarena_prod_db_user
--

COPY public.announcement (id, title, body, created_at, created_by_user_id, season_year, season_type, week, pinned, is_active) FROM stdin;
1	Hi Everyone We have announcments now	adding	2026-01-08 17:32:04.387821	1	2025	POST	\N	t	f
2	The Announcements area	This is the new announcment area. Only the admin will be able to post announcments that go to everyone. \r\n\r\nAnother messge board will be coming soon that everyone will be able to use to communicate between everyone.	2026-01-08 22:20:08.857569	1	2025	POST	\N	f	t
\.


--
-- Data for Name: board_post; Type: TABLE DATA; Schema: public; Owner: pickarena_prod_db_user
--

COPY public.board_post (id, thread_id, author_user_id, body, created_at, is_active, edited_at) FROM stdin;
\.


--
-- Data for Name: board_thread; Type: TABLE DATA; Schema: public; Owner: pickarena_prod_db_user
--

COPY public.board_thread (id, title, created_at, created_by_user_id, season_year, season_type, week, pinned, locked, is_active, last_activity_at) FROM stdin;
\.


--
-- Data for Name: game; Type: TABLE DATA; Schema: public; Owner: pickarena_prod_db_user
--

COPY public.game (id, game_id, home_team, away_team, spread, favorite_team, commence_time_mt, home_team_score, away_team_score, saved_at, status, week, season_year, season_type, week_label) FROM stdin;
307	2025-S3-W4-E401831718	AFC	NFC	\N	\N	2026-02-04 01:00:00+00	\N	\N	2026-01-06 04:26:38.79429	\N	4	2025	POST	\N
295	2025-S3-W1-E401772979	Carolina Panthers	Los Angeles Rams	-10.5	Los Angeles Rams	2026-01-10 21:30:00+00	31	34	2026-01-06 21:01:19.283167	STATUS_FINAL	1	2025	POST	\N
296	2025-S3-W1-E401772981	Chicago Bears	Green Bay Packers	-1.5	Green Bay Packers	2026-01-11 01:00:00+00	31	27	2026-01-06 21:01:19.283167	STATUS_FINAL	1	2025	POST	\N
297	2025-S3-W1-E401772977	Jacksonville Jaguars	Buffalo Bills	-1.5	Buffalo Bills	2026-01-11 18:00:00+00	24	27	2026-01-06 21:01:19.283167	STATUS_FINAL	1	2025	POST	\N
298	2025-S3-W1-E401772980	Philadelphia Eagles	San Francisco 49ers	-4.5	Philadelphia Eagles	2026-01-11 21:30:00+00	19	23	2026-01-06 21:01:19.283167	STATUS_FINAL	1	2025	POST	\N
299	2025-S3-W1-E401772978	New England Patriots	Los Angeles Chargers	-3.5	New England Patriots	2026-01-12 01:15:00+00	16	3	2026-01-06 21:01:19.283167	STATUS_FINAL	1	2025	POST	\N
308	2025-S3-W5-E401772988	TBD	TBD	\N	\N	2026-02-08 23:30:00+00	\N	\N	2026-01-06 04:26:39.450424	\N	5	2025	POST	\N
300	2025-S3-W1-E401772976	Pittsburgh Steelers	Houston Texans	-3	Houston Texans	2026-01-13 01:15:00+00	6	30	2026-01-06 21:01:19.283167	STATUS_FINAL	1	2025	POST	\N
305	2025-S3-W3-E401772986	Denver Broncos	New England Patriots	-4.5	New England Patriots	2026-01-25 20:00:00+00	0	0	2026-01-06 04:26:38.048705	STATUS_SCHEDULED	3	2025	POST	\N
306	2025-S3-W3-E401772987	Seattle Seahawks	Los Angeles Rams	-2.5	Seattle Seahawks	2026-01-25 23:30:00+00	0	0	2026-01-06 04:26:38.049767	STATUS_SCHEDULED	3	2025	POST	\N
301	2025-S3-W2-E401772982	Denver Broncos	Buffalo Bills	-1.5	Denver Broncos	2026-01-17 21:30:00+00	33	30	2026-01-06 04:26:37.154504	STATUS_FINAL	2	2025	POST	\N
302	2025-S3-W2-E401772983	New England Patriots	Houston Texans	-3	New England Patriots	2026-01-18 20:00:00+00	28	16	2026-01-06 04:26:37.154504	STATUS_FINAL	2	2025	POST	\N
303	2025-S3-W2-E401772984	Seattle Seahawks	San Francisco 49ers	-7.5	Seattle Seahawks	2026-01-18 01:00:00+00	41	6	2026-01-06 04:26:37.154504	STATUS_FINAL	2	2025	POST	\N
304	2025-S3-W2-E401772985	Chicago Bears	Los Angeles Rams	-3.5	Los Angeles Rams	2026-01-18 23:30:00+00	17	20	2026-01-06 04:26:37.154504	STATUS_FINAL	2	2025	POST	\N
242	2025-W17-DET-at-MIN	Minnesota Vikings	Detroit Lions	-6	Detroit Lions	2025-12-25 14:30:00+00	23	10	2025-12-23 14:00:00.326033	STATUS_FINAL	17	2025	regular	\N
243	2025-W17-DEN-at-KC	Kansas City Chiefs	Denver Broncos	-12.5	Denver Broncos	2025-12-25 18:15:00+00	13	20	2025-12-23 14:00:00.326053	STATUS_FINAL	17	2025	regular	\N
244	2025-W17-ARI-at-CIN	Cincinnati Bengals	Arizona Cardinals	-7	Cincinnati Bengals	2025-12-28 11:00:00+00	37	14	2025-12-23 14:00:00.32609	STATUS_FINAL	17	2025	regular	\N
245	2025-W17-BAL-at-GB	Green Bay Packers	Baltimore Ravens	-2.5	Green Bay Packers	2025-12-27 18:00:00+00	24	41	2025-12-23 14:00:00.326079	STATUS_FINAL	17	2025	regular	\N
246	2025-W17-NYG-at-LV	Las Vegas Raiders	New York Giants	-1.5	Las Vegas Raiders	2025-12-28 14:05:00+00	10	34	2025-12-23 14:00:00.32617	STATUS_FINAL	17	2025	regular	\N
247	2025-W17-HOU-at-LAC	Los Angeles Chargers	Houston Texans	-2.5	Los Angeles Chargers	2025-12-27 14:30:00+00	16	20	2025-12-23 14:00:00.326067	STATUS_FINAL	17	2025	regular	\N
248	2025-W17-SEA-at-CAR	Carolina Panthers	Seattle Seahawks	-7.5	Seattle Seahawks	2025-12-28 11:00:00+00	10	27	2025-12-23 14:00:00.326101	STATUS_FINAL	17	2025	regular	\N
249	2025-W17-PIT-at-CLE	Cleveland Browns	Pittsburgh Steelers	-3.5	Pittsburgh Steelers	2025-12-28 11:00:00+00	13	6	2025-12-23 14:00:00.326115	STATUS_FINAL	17	2025	regular	\N
250	2025-W17-NO-at-TEN	Tennessee Titans	New Orleans Saints	-2.5	New Orleans Saints	2025-12-28 11:00:00+00	26	34	2025-12-23 14:00:00.32616	STATUS_FINAL	17	2025	regular	\N
251	2025-W17-JAX-at-IND	Indianapolis Colts	Jacksonville Jaguars	-6.5	Jacksonville Jaguars	2025-12-28 11:00:00+00	17	23	2025-12-23 14:00:00.326128	STATUS_FINAL	17	2025	regular	\N
252	2025-W17-TB-at-MIA	Miami Dolphins	Tampa Bay Buccaneers	-5.5	Tampa Bay Buccaneers	2025-12-28 11:00:00+00	20	17	2025-12-23 14:00:00.326139	STATUS_FINAL	17	2025	regular	\N
1	2025-W1-DAL-at-PHI	Philadelphia Eagles	Dallas Cowboys	-8.5	Philadelphia Eagles	2025-09-04 18:20:00+00	24	20	2025-09-02 13:00:00.418393	STATUS_FINAL	1	2025	regular	\N
2	2025-W1-KC-at-LAC	Los Angeles Chargers	Kansas City Chiefs	-3	Kansas City Chiefs	2025-09-05 18:00:00+00	27	21	2025-09-02 13:00:00.418554	STATUS_FINAL	1	2025	regular	\N
3	2025-W1-TB-at-ATL	Atlanta Falcons	Tampa Bay Buccaneers	-2.5	Tampa Bay Buccaneers	2025-09-07 11:00:00+00	20	23	2025-09-02 13:00:00.41858	STATUS_FINAL	1	2025	regular	\N
4	2025-W1-CIN-at-CLE	Cleveland Browns	Cincinnati Bengals	-5.5	Cincinnati Bengals	2025-09-07 11:00:00+00	16	17	2025-09-02 13:00:00.418654	STATUS_FINAL	1	2025	regular	\N
5	2025-W1-MIA-at-IND	Indianapolis Colts	Miami Dolphins	-1.5	Indianapolis Colts	2025-09-07 11:00:00+00	33	8	2025-09-02 13:00:00.418676	STATUS_FINAL	1	2025	regular	\N
6	2025-W1-LV-at-NE	New England Patriots	Las Vegas Raiders	-2.5	New England Patriots	2025-09-07 11:00:00+00	13	20	2025-09-02 13:00:00.418703	STATUS_FINAL	1	2025	regular	\N
7	2025-W1-ARI-at-NO	New Orleans Saints	Arizona Cardinals	-6.5	Arizona Cardinals	2025-09-07 11:00:00+00	13	20	2025-09-02 13:00:00.418637	STATUS_FINAL	1	2025	regular	\N
8	2025-W1-PIT-at-NYJ	New York Jets	Pittsburgh Steelers	-3	Pittsburgh Steelers	2025-09-07 11:00:00+00	32	34	2025-09-02 13:00:00.418721	STATUS_FINAL	1	2025	regular	\N
9	2025-W1-NYG-at-WSH	Washington Commanders	New York Giants	-5.5	Washington Commanders	2025-09-07 11:00:00+00	21	6	2025-09-02 13:00:00.418619	STATUS_FINAL	1	2025	regular	\N
225	2025-W16-LAR-at-SEA	Seattle Seahawks	Los Angeles Rams	-1.5	Seattle Seahawks	2025-12-18 18:15:00+00	38	37	2025-12-16 14:00:00.239124	STATUS_FINAL	16	2025	regular	\N
228	2025-W16-BUF-at-CLE	Cleveland Browns	Buffalo Bills	-10	Buffalo Bills	2025-12-21 11:00:00+00	20	23	2025-12-16 14:00:00.239201	STATUS_FINAL	16	2025	regular	\N
10	2025-W1-CAR-at-JAX	Jacksonville Jaguars	Carolina Panthers	-3.5	Jacksonville Jaguars	2025-09-07 11:00:00+00	26	10	2025-09-02 13:00:00.4186	STATUS_FINAL	1	2025	regular	\N
11	2025-W1-TEN-at-DEN	Denver Broncos	Tennessee Titans	-7.5	Denver Broncos	2025-09-07 14:05:00+00	20	12	2025-09-02 13:00:00.418738	STATUS_FINAL	1	2025	regular	\N
12	2025-W1-SF-at-SEA	Seattle Seahawks	San Francisco 49ers	-2.5	San Francisco 49ers	2025-09-07 14:05:00+00	13	17	2025-09-02 13:00:00.418753	STATUS_FINAL	1	2025	regular	\N
13	2025-W1-DET-at-GB	Green Bay Packers	Detroit Lions	-2.5	Green Bay Packers	2025-09-07 14:25:00+00	27	13	2025-09-02 13:00:00.418769	STATUS_FINAL	1	2025	regular	\N
14	2025-W1-HOU-at-LAR	Los Angeles Rams	Houston Texans	-3	Los Angeles Rams	2025-09-07 14:25:00+00	14	9	2025-09-02 13:00:00.418785	STATUS_FINAL	1	2025	regular	\N
15	2025-W1-BAL-at-BUF	Buffalo Bills	Baltimore Ravens	-1.5	Buffalo Bills	2025-09-07 18:20:00+00	41	40	2025-09-02 13:00:00.418799	STATUS_FINAL	1	2025	regular	\N
16	2025-W1-MIN-at-CHI	Chicago Bears	Minnesota Vikings	-1.5	Minnesota Vikings	2025-09-08 18:15:00+00	24	27	2025-09-02 13:00:00.418832	STATUS_FINAL	1	2025	regular	\N
17	2025-W2-WSH-at-GB	Green Bay Packers	Washington Commanders	-3.5	Green Bay Packers	2025-09-11 18:15:00+00	27	18	2025-09-09 13:00:00.292595	STATUS_FINAL	2	2025	regular	\N
18	2025-W2-JAX-at-CIN	Cincinnati Bengals	Jacksonville Jaguars	-3.5	Cincinnati Bengals	2025-09-14 11:00:00+00	31	27	2025-09-09 13:00:00.292674	STATUS_FINAL	2	2025	regular	\N
19	2025-W2-NYG-at-DAL	Dallas Cowboys	New York Giants	-6	Dallas Cowboys	2025-09-14 11:00:00+00	40	37	2025-09-09 13:00:00.292689	STATUS_FINAL	2	2025	regular	\N
20	2025-W2-CHI-at-DET	Detroit Lions	Chicago Bears	-4.5	Detroit Lions	2025-09-14 11:00:00+00	52	21	2025-09-09 13:00:00.292655	STATUS_FINAL	2	2025	regular	\N
21	2025-W2-LAR-at-TEN	Tennessee Titans	Los Angeles Rams	-5.5	Los Angeles Rams	2025-09-14 11:00:00+00	19	33	2025-09-09 13:00:00.292743	STATUS_FINAL	2	2025	regular	\N
22	2025-W2-NE-at-MIA	Miami Dolphins	New England Patriots	-1.5	Miami Dolphins	2025-09-14 11:00:00+00	27	33	2025-09-09 13:00:00.292703	STATUS_FINAL	2	2025	regular	\N
23	2025-W2-SF-at-NO	New Orleans Saints	San Francisco 49ers	-4.5	San Francisco 49ers	2025-09-14 11:00:00+00	21	26	2025-09-09 13:00:00.292756	STATUS_FINAL	2	2025	regular	\N
24	2025-W2-BUF-at-NYJ	New York Jets	Buffalo Bills	-7	Buffalo Bills	2025-09-14 11:00:00+00	10	30	2025-09-09 13:00:00.29273	STATUS_FINAL	2	2025	regular	\N
25	2025-W2-SEA-at-PIT	Pittsburgh Steelers	Seattle Seahawks	-3	Pittsburgh Steelers	2025-09-14 11:00:00+00	17	31	2025-09-09 13:00:00.292769	STATUS_FINAL	2	2025	regular	\N
26	2025-W2-CLE-at-BAL	Baltimore Ravens	Cleveland Browns	-12.5	Baltimore Ravens	2025-09-14 11:00:00+00	41	17	2025-09-09 13:00:00.292717	STATUS_FINAL	2	2025	regular	\N
27	2025-W2-DEN-at-IND	Indianapolis Colts	Denver Broncos	-2.5	Denver Broncos	2025-09-14 14:05:00+00	29	28	2025-09-09 13:00:00.292795	STATUS_FINAL	2	2025	regular	\N
28	2025-W2-CAR-at-ARI	Arizona Cardinals	Carolina Panthers	-6.5	Arizona Cardinals	2025-09-14 14:05:00+00	27	22	2025-09-09 13:00:00.292782	STATUS_FINAL	2	2025	regular	\N
29	2025-W2-PHI-at-KC	Kansas City Chiefs	Philadelphia Eagles	-1.5	Philadelphia Eagles	2025-09-14 14:25:00+00	17	20	2025-09-09 13:00:00.292808	STATUS_FINAL	2	2025	regular	\N
30	2025-W2-ATL-at-MIN	Minnesota Vikings	Atlanta Falcons	-5.5	Minnesota Vikings	2025-09-14 18:20:00+00	6	22	2025-09-09 13:00:00.29283	STATUS_FINAL	2	2025	regular	\N
31	2025-W2-TB-at-HOU	Houston Texans	Tampa Bay Buccaneers	-2.5	Houston Texans	2025-09-15 17:00:00+00	19	20	2025-09-09 13:00:00.292844	STATUS_FINAL	2	2025	regular	\N
32	2025-W2-LAC-at-LV	Las Vegas Raiders	Los Angeles Chargers	-3.5	Los Angeles Chargers	2025-09-15 20:00:00+00	9	20	2025-09-09 13:00:00.292857	STATUS_FINAL	2	2025	regular	\N
33	2025-W3-MIA-at-BUF	Buffalo Bills	Miami Dolphins	-12.5	Buffalo Bills	2025-09-18 18:15:00+00	31	21	2025-09-16 13:00:00.280701	STATUS_FINAL	3	2025	regular	\N
34	2025-W3-GB-at-CLE	Cleveland Browns	Green Bay Packers	-8.5	Green Bay Packers	2025-09-21 11:00:00+00	13	10	2025-09-16 13:00:00.280826	STATUS_FINAL	3	2025	regular	\N
35	2025-W3-IND-at-TEN	Tennessee Titans	Indianapolis Colts	-3.5	Indianapolis Colts	2025-09-21 11:00:00+00	20	41	2025-09-16 13:00:00.280935	STATUS_FINAL	3	2025	regular	\N
36	2025-W3-CIN-at-MIN	Minnesota Vikings	Cincinnati Bengals	-3	Minnesota Vikings	2025-09-21 11:00:00+00	48	10	2025-09-16 13:00:00.2808	STATUS_FINAL	3	2025	regular	\N
37	2025-W3-PIT-at-NE	New England Patriots	Pittsburgh Steelers	-0.5	Pittsburgh Steelers	2025-09-21 11:00:00+00	14	21	2025-09-16 13:00:00.280892	STATUS_FINAL	3	2025	regular	\N
38	2025-W3-LAR-at-PHI	Philadelphia Eagles	Los Angeles Rams	-3	Philadelphia Eagles	2025-09-21 11:00:00+00	33	26	2025-09-16 13:00:00.280955	STATUS_FINAL	3	2025	regular	\N
39	2025-W3-NYJ-at-TB	Tampa Bay Buccaneers	New York Jets	-7	Tampa Bay Buccaneers	2025-09-21 11:00:00+00	29	27	2025-09-16 13:00:00.280913	STATUS_FINAL	3	2025	regular	\N
40	2025-W3-LV-at-WSH	Washington Commanders	Las Vegas Raiders	-3.5	Washington Commanders	2025-09-21 11:00:00+00	41	24	2025-09-16 13:00:00.280871	STATUS_FINAL	3	2025	regular	\N
41	2025-W3-ATL-at-CAR	Carolina Panthers	Atlanta Falcons	-5.5	Atlanta Falcons	2025-09-21 11:00:00+00	30	0	2025-09-16 13:00:00.280772	STATUS_FINAL	3	2025	regular	\N
42	2025-W3-HOU-at-JAX	Jacksonville Jaguars	Houston Texans	-0.5	Jacksonville Jaguars	2025-09-21 11:00:00+00	17	10	2025-09-16 13:00:00.280849	STATUS_FINAL	3	2025	regular	\N
43	2025-W3-DEN-at-LAC	Los Angeles Chargers	Denver Broncos	-2.5	Los Angeles Chargers	2025-09-21 14:05:00+00	23	20	2025-09-16 13:00:00.280975	STATUS_FINAL	3	2025	regular	\N
44	2025-W3-NO-at-SEA	Seattle Seahawks	New Orleans Saints	-7.5	Seattle Seahawks	2025-09-21 14:05:00+00	44	13	2025-09-16 13:00:00.280994	STATUS_FINAL	3	2025	regular	\N
45	2025-W3-DAL-at-CHI	Chicago Bears	Dallas Cowboys	-1.5	Chicago Bears	2025-09-21 14:25:00+00	31	14	2025-09-16 13:00:00.281014	STATUS_FINAL	3	2025	regular	\N
46	2025-W3-ARI-at-SF	San Francisco 49ers	Arizona Cardinals	-1.5	San Francisco 49ers	2025-09-21 14:25:00+00	16	15	2025-09-16 13:00:00.281053	STATUS_FINAL	3	2025	regular	\N
47	2025-W3-KC-at-NYG	New York Giants	Kansas City Chiefs	-6	Kansas City Chiefs	2025-09-21 18:20:00+00	9	22	2025-09-16 13:00:00.281073	STATUS_FINAL	3	2025	regular	\N
48	2025-W3-DET-at-BAL	Baltimore Ravens	Detroit Lions	-6	Baltimore Ravens	2025-09-22 18:15:00+00	30	38	2025-09-16 13:00:00.281092	STATUS_FINAL	3	2025	regular	\N
49	2025-W4-SEA-at-ARI	Arizona Cardinals	Seattle Seahawks	-1.5	Arizona Cardinals	2025-09-25 18:15:00+00	20	23	2025-09-23 13:00:00.324924	STATUS_FINAL	4	2025	regular	\N
50	2025-W4-MIN-at-PIT	Pittsburgh Steelers	Minnesota Vikings	-2.5	Minnesota Vikings	2025-09-28 07:30:00+00	24	21	2025-09-23 13:00:00.324988	STATUS_FINAL	4	2025	regular	\N
51	2025-W4-WSH-at-ATL	Atlanta Falcons	Washington Commanders	-2.5	Washington Commanders	2025-09-28 11:00:00+00	34	27	2025-09-23 13:00:00.32503	STATUS_FINAL	4	2025	regular	\N
52	2025-W4-NO-at-BUF	Buffalo Bills	New Orleans Saints	-16.5	Buffalo Bills	2025-09-28 11:00:00+00	31	19	2025-09-23 13:00:00.325046	STATUS_FINAL	4	2025	regular	\N
53	2025-W4-CLE-at-DET	Detroit Lions	Cleveland Browns	-8.5	Detroit Lions	2025-09-28 11:00:00+00	34	10	2025-09-23 13:00:00.325011	STATUS_FINAL	4	2025	regular	\N
54	2025-W4-CAR-at-NE	New England Patriots	Carolina Panthers	-5.5	New England Patriots	2025-09-28 11:00:00+00	42	13	2025-09-23 13:00:00.32506	STATUS_FINAL	4	2025	regular	\N
55	2025-W4-LAC-at-NYG	New York Giants	Los Angeles Chargers	-6	Los Angeles Chargers	2025-09-28 11:00:00+00	21	18	2025-09-23 13:00:00.32509	STATUS_FINAL	4	2025	regular	\N
56	2025-W4-PHI-at-TB	Tampa Bay Buccaneers	Philadelphia Eagles	-3	Philadelphia Eagles	2025-09-28 11:00:00+00	25	31	2025-09-23 13:00:00.325116	STATUS_FINAL	4	2025	regular	\N
57	2025-W4-TEN-at-HOU	Houston Texans	Tennessee Titans	-7	Houston Texans	2025-09-28 11:00:00+00	26	0	2025-09-23 13:00:00.325074	STATUS_FINAL	4	2025	regular	\N
58	2025-W4-IND-at-LAR	Los Angeles Rams	Indianapolis Colts	-3.5	Los Angeles Rams	2025-09-28 14:05:00+00	27	20	2025-09-23 13:00:00.32513	STATUS_FINAL	4	2025	regular	\N
59	2025-W4-JAX-at-SF	San Francisco 49ers	Jacksonville Jaguars	-3	San Francisco 49ers	2025-09-28 14:05:00+00	21	26	2025-09-23 13:00:00.325143	STATUS_FINAL	4	2025	regular	\N
60	2025-W4-BAL-at-KC	Kansas City Chiefs	Baltimore Ravens	-2.5	Baltimore Ravens	2025-09-28 14:25:00+00	37	20	2025-09-23 13:00:00.325157	STATUS_FINAL	4	2025	regular	\N
61	2025-W4-CHI-at-LV	Las Vegas Raiders	Chicago Bears	-1.5	Chicago Bears	2025-09-28 14:25:00+00	24	25	2025-09-23 13:00:00.325169	STATUS_FINAL	4	2025	regular	\N
62	2025-W4-GB-at-DAL	Dallas Cowboys	Green Bay Packers	-7	Green Bay Packers	2025-09-28 18:20:00+00	40	40	2025-09-23 13:00:00.325182	STATUS_FINAL	4	2025	regular	\N
63	2025-W4-NYJ-at-MIA	Miami Dolphins	New York Jets	-2.5	Miami Dolphins	2025-09-29 17:15:00+00	27	21	2025-09-23 13:00:00.325194	STATUS_FINAL	4	2025	regular	\N
64	2025-W4-CIN-at-DEN	Denver Broncos	Cincinnati Bengals	-7	Denver Broncos	2025-09-29 18:15:00+00	28	3	2025-09-23 13:00:00.325207	STATUS_FINAL	4	2025	regular	\N
65	2025-W5-SF-at-LAR	Los Angeles Rams	San Francisco 49ers	-5.5	Los Angeles Rams	2025-10-02 18:15:00+00	23	26	2025-09-30 13:00:00.30754	STATUS_FINAL	5	2025	regular	\N
66	2025-W5-MIN-at-CLE	Cleveland Browns	Minnesota Vikings	-4.5	Minnesota Vikings	2025-10-05 07:30:00+00	17	21	2025-09-30 13:00:00.307614	STATUS_FINAL	5	2025	regular	\N
67	2025-W5-LV-at-IND	Indianapolis Colts	Las Vegas Raiders	-6.5	Indianapolis Colts	2025-10-05 11:00:00+00	40	6	2025-09-30 13:00:00.307731	STATUS_FINAL	5	2025	regular	\N
68	2025-W5-NYG-at-NO	New Orleans Saints	New York Giants	-1.5	New Orleans Saints	2025-10-05 11:00:00+00	26	14	2025-09-30 13:00:00.307752	STATUS_FINAL	5	2025	regular	\N
69	2025-W5-DAL-at-NYJ	New York Jets	Dallas Cowboys	-3	Dallas Cowboys	2025-10-05 11:00:00+00	22	37	2025-09-30 13:00:00.307688	STATUS_FINAL	5	2025	regular	\N
70	2025-W5-DEN-at-PHI	Philadelphia Eagles	Denver Broncos	-4.5	Philadelphia Eagles	2025-10-05 11:00:00+00	17	21	2025-09-30 13:00:00.307709	STATUS_FINAL	5	2025	regular	\N
71	2025-W5-MIA-at-CAR	Carolina Panthers	Miami Dolphins	-1.5	Carolina Panthers	2025-10-05 11:00:00+00	27	24	2025-09-30 13:00:00.307668	STATUS_FINAL	5	2025	regular	\N
72	2025-W5-HOU-at-BAL	Baltimore Ravens	Houston Texans	-3.5	Baltimore Ravens	2025-10-05 11:00:00+00	10	44	2025-09-30 13:00:00.307644	STATUS_FINAL	5	2025	regular	\N
73	2025-W5-TEN-at-ARI	Arizona Cardinals	Tennessee Titans	-8.5	Arizona Cardinals	2025-10-05 14:05:00+00	21	22	2025-09-30 13:00:00.307772	STATUS_FINAL	5	2025	regular	\N
74	2025-W5-TB-at-SEA	Seattle Seahawks	Tampa Bay Buccaneers	-3	Seattle Seahawks	2025-10-05 14:05:00+00	35	38	2025-09-30 13:00:00.307792	STATUS_FINAL	5	2025	regular	\N
75	2025-W5-DET-at-CIN	Cincinnati Bengals	Detroit Lions	-10	Detroit Lions	2025-10-05 14:25:00+00	24	37	2025-09-30 13:00:00.307811	STATUS_FINAL	5	2025	regular	\N
76	2025-W5-WSH-at-LAC	Los Angeles Chargers	Washington Commanders	-2.5	Los Angeles Chargers	2025-10-05 14:25:00+00	10	27	2025-09-30 13:00:00.307832	STATUS_FINAL	5	2025	regular	\N
77	2025-W5-NE-at-BUF	Buffalo Bills	New England Patriots	-8.5	Buffalo Bills	2025-10-05 18:20:00+00	20	23	2025-09-30 13:00:00.307853	STATUS_FINAL	5	2025	regular	\N
78	2025-W5-KC-at-JAX	Jacksonville Jaguars	Kansas City Chiefs	-3.5	Kansas City Chiefs	2025-10-06 18:15:00+00	31	28	2025-09-30 13:00:00.307873	STATUS_FINAL	5	2025	regular	\N
79	2025-W6-PHI-at-NYG	New York Giants	Philadelphia Eagles	-7	Philadelphia Eagles	2025-10-09 18:15:00+00	34	17	2025-10-07 13:00:00.289075	STATUS_FINAL	6	2025	regular	\N
80	2025-W6-DEN-at-NYJ	New York Jets	Denver Broncos	-7.5	Denver Broncos	2025-10-12 07:30:00+00	11	13	2025-10-07 13:00:00.289122	STATUS_FINAL	6	2025	regular	\N
81	2025-W6-ARI-at-IND	Indianapolis Colts	Arizona Cardinals	-6.5	Indianapolis Colts	2025-10-12 11:00:00+00	31	27	2025-10-07 13:00:00.289149	STATUS_FINAL	6	2025	regular	\N
82	2025-W6-LAC-at-MIA	Miami Dolphins	Los Angeles Chargers	-4.5	Los Angeles Chargers	2025-10-12 11:00:00+00	27	29	2025-10-07 13:00:00.289208	STATUS_FINAL	6	2025	regular	\N
83	2025-W6-CLE-at-PIT	Pittsburgh Steelers	Cleveland Browns	-4.5	Pittsburgh Steelers	2025-10-12 11:00:00+00	23	9	2025-10-07 13:00:00.289196	STATUS_FINAL	6	2025	regular	\N
84	2025-W6-SF-at-TB	Tampa Bay Buccaneers	San Francisco 49ers	-3	Tampa Bay Buccaneers	2025-10-12 14:25:00+00	30	19	2025-10-07 13:00:00.289252	STATUS_FINAL	6	2025	regular	\N
85	2025-W6-DAL-at-CAR	Carolina Panthers	Dallas Cowboys	-3.5	Dallas Cowboys	2025-10-12 11:00:00+00	30	27	2025-10-07 13:00:00.28917	STATUS_FINAL	6	2025	regular	\N
86	2025-W6-SEA-at-JAX	Jacksonville Jaguars	Seattle Seahawks	-1.5	Jacksonville Jaguars	2025-10-12 11:00:00+00	12	20	2025-10-07 13:00:00.289137	STATUS_FINAL	6	2025	regular	\N
87	2025-W6-LAR-at-BAL	Baltimore Ravens	Los Angeles Rams	-7.5	Los Angeles Rams	2025-10-12 11:00:00+00	3	17	2025-10-07 13:00:00.28916	STATUS_FINAL	6	2025	regular	\N
88	2025-W6-TEN-at-LV	Las Vegas Raiders	Tennessee Titans	-4.5	Las Vegas Raiders	2025-10-12 14:05:00+00	20	10	2025-10-07 13:00:00.28922	STATUS_FINAL	6	2025	regular	\N
89	2025-W6-CIN-at-GB	Green Bay Packers	Cincinnati Bengals	-14.5	Green Bay Packers	2025-10-12 14:25:00+00	27	18	2025-10-07 13:00:00.289243	STATUS_FINAL	6	2025	regular	\N
90	2025-W6-NE-at-NO	New Orleans Saints	New England Patriots	-3.5	New England Patriots	2025-10-12 11:00:00+00	19	25	2025-10-07 13:00:00.289232	STATUS_FINAL	6	2025	regular	\N
91	2025-W6-DET-at-KC	Kansas City Chiefs	Detroit Lions	-1.5	Kansas City Chiefs	2025-10-12 18:20:00+00	30	17	2025-10-07 13:00:00.289262	STATUS_FINAL	6	2025	regular	\N
92	2025-W6-BUF-at-ATL	Atlanta Falcons	Buffalo Bills	-4.5	Buffalo Bills	2025-10-13 17:15:00+00	24	14	2025-10-07 13:00:00.289272	STATUS_FINAL	6	2025	regular	\N
93	2025-W6-CHI-at-WSH	Washington Commanders	Chicago Bears	-4.5	Washington Commanders	2025-10-13 18:15:00+00	24	25	2025-10-07 13:00:00.289281	STATUS_FINAL	6	2025	regular	\N
94	2025-W7-PIT-at-CIN	Cincinnati Bengals	Pittsburgh Steelers	-5.5	Pittsburgh Steelers	2025-10-16 18:15:00+00	33	31	2025-10-14 13:00:00.264598	STATUS_FINAL	7	2025	regular	\N
95	2025-W7-LAR-at-JAX	Jacksonville Jaguars	Los Angeles Rams	-3	Los Angeles Rams	2025-10-19 07:30:00+00	7	35	2025-10-14 13:00:00.264669	STATUS_FINAL	7	2025	regular	\N
96	2025-W7-NO-at-CHI	Chicago Bears	New Orleans Saints	-5.5	Chicago Bears	2025-10-19 11:00:00+00	26	14	2025-10-14 13:00:00.264685	STATUS_FINAL	7	2025	regular	\N
97	2025-W7-MIA-at-CLE	Cleveland Browns	Miami Dolphins	-2.5	Cleveland Browns	2025-10-19 11:00:00+00	31	6	2025-10-14 13:00:00.264709	STATUS_FINAL	7	2025	regular	\N
98	2025-W7-NE-at-TEN	Tennessee Titans	New England Patriots	-7	New England Patriots	2025-10-19 11:00:00+00	13	31	2025-10-14 13:00:00.264742	STATUS_FINAL	7	2025	regular	\N
99	2025-W7-LV-at-KC	Kansas City Chiefs	Las Vegas Raiders	-11.5	Kansas City Chiefs	2025-10-19 11:00:00+00	31	0	2025-10-14 13:00:00.264721	STATUS_FINAL	7	2025	regular	\N
100	2025-W7-PHI-at-MIN	Minnesota Vikings	Philadelphia Eagles	-2.5	Philadelphia Eagles	2025-10-19 11:00:00+00	22	28	2025-10-14 13:00:00.264731	STATUS_FINAL	7	2025	regular	\N
101	2025-W7-CAR-at-NYJ	New York Jets	Carolina Panthers	-1.5	Carolina Panthers	2025-10-19 11:00:00+00	6	13	2025-10-14 13:00:00.264697	STATUS_FINAL	7	2025	regular	\N
102	2025-W7-NYG-at-DEN	Denver Broncos	New York Giants	-7	Denver Broncos	2025-10-19 14:05:00+00	33	32	2025-10-14 13:00:00.264753	STATUS_FINAL	7	2025	regular	\N
103	2025-W7-IND-at-LAC	Los Angeles Chargers	Indianapolis Colts	-1.5	Los Angeles Chargers	2025-10-19 14:05:00+00	24	38	2025-10-14 13:00:00.264764	STATUS_FINAL	7	2025	regular	\N
104	2025-W7-WSH-at-DAL	Dallas Cowboys	Washington Commanders	-2.5	Washington Commanders	2025-10-19 14:25:00+00	44	22	2025-10-14 13:00:00.264775	STATUS_FINAL	7	2025	regular	\N
105	2025-W7-GB-at-ARI	Arizona Cardinals	Green Bay Packers	-6.5	Green Bay Packers	2025-10-19 14:25:00+00	23	27	2025-10-14 13:00:00.264786	STATUS_FINAL	7	2025	regular	\N
106	2025-W7-ATL-at-SF	San Francisco 49ers	Atlanta Falcons	-3	San Francisco 49ers	2025-10-19 18:20:00+00	20	10	2025-10-14 13:00:00.264796	STATUS_FINAL	7	2025	regular	\N
107	2025-W7-TB-at-DET	Detroit Lions	Tampa Bay Buccaneers	-4.5	Detroit Lions	2025-10-20 17:00:00+00	24	9	2025-10-14 13:00:00.264807	STATUS_FINAL	7	2025	regular	\N
108	2025-W7-HOU-at-SEA	Seattle Seahawks	Houston Texans	-3	Seattle Seahawks	2025-10-20 20:00:00+00	27	19	2025-10-14 13:00:00.264818	STATUS_FINAL	7	2025	regular	\N
109	2025-W8-MIN-at-LAC	Los Angeles Chargers	Minnesota Vikings	-3	Los Angeles Chargers	2025-10-23 18:15:00+00	37	10	2025-10-21 13:00:00.263126	STATUS_FINAL	8	2025	regular	\N
110	2025-W8-MIA-at-ATL	Atlanta Falcons	Miami Dolphins	-7	Atlanta Falcons	2025-10-26 11:00:00+00	10	34	2025-10-21 13:00:00.263181	STATUS_FINAL	8	2025	regular	\N
111	2025-W8-NYJ-at-CIN	Cincinnati Bengals	New York Jets	-6.5	Cincinnati Bengals	2025-10-26 11:00:00+00	38	39	2025-10-21 13:00:00.26323	STATUS_FINAL	8	2025	regular	\N
112	2025-W8-CLE-at-NE	New England Patriots	Cleveland Browns	-7	New England Patriots	2025-10-26 11:00:00+00	32	13	2025-10-21 13:00:00.263243	STATUS_FINAL	8	2025	regular	\N
113	2025-W8-NYG-at-PHI	Philadelphia Eagles	New York Giants	-7	Philadelphia Eagles	2025-10-26 11:00:00+00	38	20	2025-10-21 13:00:00.26327	STATUS_FINAL	8	2025	regular	\N
114	2025-W8-BUF-at-CAR	Carolina Panthers	Buffalo Bills	-7.5	Buffalo Bills	2025-10-26 11:00:00+00	9	40	2025-10-21 13:00:00.263216	STATUS_FINAL	8	2025	regular	\N
115	2025-W8-CHI-at-BAL	Baltimore Ravens	Chicago Bears	-6.5	Baltimore Ravens	2025-10-26 11:00:00+00	30	16	2025-10-21 13:00:00.263201	STATUS_FINAL	8	2025	regular	\N
116	2025-W8-SF-at-HOU	Houston Texans	San Francisco 49ers	-1.5	San Francisco 49ers	2025-10-26 11:00:00+00	26	15	2025-10-21 13:00:00.263257	STATUS_FINAL	8	2025	regular	\N
117	2025-W8-TB-at-NO	New Orleans Saints	Tampa Bay Buccaneers	-4.5	Tampa Bay Buccaneers	2025-10-26 14:05:00+00	3	23	2025-10-21 13:00:00.263295	STATUS_FINAL	8	2025	regular	\N
118	2025-W8-DAL-at-DEN	Denver Broncos	Dallas Cowboys	-3	Denver Broncos	2025-10-26 14:25:00+00	44	24	2025-10-21 13:00:00.26331	STATUS_FINAL	8	2025	regular	\N
119	2025-W8-TEN-at-IND	Indianapolis Colts	Tennessee Titans	-14	Indianapolis Colts	2025-10-26 14:25:00+00	38	14	2025-10-21 13:00:00.263322	STATUS_FINAL	8	2025	regular	\N
120	2025-W8-GB-at-PIT	Pittsburgh Steelers	Green Bay Packers	-3.5	Green Bay Packers	2025-10-26 18:20:00+00	25	35	2025-10-21 13:00:00.263334	STATUS_FINAL	8	2025	regular	\N
121	2025-W8-WSH-at-KC	Kansas City Chiefs	Washington Commanders	-10.5	Kansas City Chiefs	2025-10-27 18:15:00+00	28	7	2025-10-21 13:00:00.263347	STATUS_FINAL	8	2025	regular	\N
122	2025-W9-BAL-at-MIA	Miami Dolphins	Baltimore Ravens	-7.5	Baltimore Ravens	2025-10-30 18:15:00+00	6	28	2025-10-28 13:00:00.272137	STATUS_FINAL	9	2025	regular	\N
123	2025-W9-CHI-at-CIN	Cincinnati Bengals	Chicago Bears	-2.5	Chicago Bears	2025-11-02 11:00:00+00	42	47	2025-10-28 13:00:00.272232	STATUS_FINAL	9	2025	regular	\N
124	2025-W9-MIN-at-DET	Detroit Lions	Minnesota Vikings	-8.5	Detroit Lions	2025-11-02 11:00:00+00	24	27	2025-10-28 13:00:00.272268	STATUS_FINAL	9	2025	regular	\N
125	2025-W9-CAR-at-GB	Green Bay Packers	Carolina Panthers	-12.5	Green Bay Packers	2025-11-02 11:00:00+00	13	16	2025-10-28 13:00:00.272218	STATUS_FINAL	9	2025	regular	\N
126	2025-W9-LAC-at-TEN	Tennessee Titans	Los Angeles Chargers	-10	Los Angeles Chargers	2025-11-02 11:00:00+00	20	27	2025-10-28 13:00:00.272306	STATUS_FINAL	9	2025	regular	\N
127	2025-W9-ATL-at-NE	New England Patriots	Atlanta Falcons	-5.5	New England Patriots	2025-11-02 11:00:00+00	24	23	2025-10-28 13:00:00.272201	STATUS_FINAL	9	2025	regular	\N
128	2025-W9-SF-at-NYG	New York Giants	San Francisco 49ers	-2.5	San Francisco 49ers	2025-11-02 11:00:00+00	24	34	2025-10-28 13:00:00.272325	STATUS_FINAL	9	2025	regular	\N
129	2025-W9-IND-at-PIT	Pittsburgh Steelers	Indianapolis Colts	-3	Indianapolis Colts	2025-11-02 11:00:00+00	27	20	2025-10-28 13:00:00.272287	STATUS_FINAL	9	2025	regular	\N
130	2025-W9-DEN-at-HOU	Houston Texans	Denver Broncos	-1.5	Houston Texans	2025-11-02 11:00:00+00	15	18	2025-10-28 13:00:00.272249	STATUS_FINAL	9	2025	regular	\N
131	2025-W9-JAX-at-LV	Las Vegas Raiders	Jacksonville Jaguars	-3	Jacksonville Jaguars	2025-11-02 14:05:00+00	29	30	2025-10-28 13:00:00.272344	STATUS_FINAL	9	2025	regular	\N
132	2025-W9-NO-at-LAR	Los Angeles Rams	New Orleans Saints	-13.5	Los Angeles Rams	2025-11-02 14:05:00+00	34	10	2025-10-28 13:00:00.27238	STATUS_FINAL	9	2025	regular	\N
133	2025-W9-KC-at-BUF	Buffalo Bills	Kansas City Chiefs	-1.5	Kansas City Chiefs	2025-11-02 14:25:00+00	28	21	2025-10-28 13:00:00.2724	STATUS_FINAL	9	2025	regular	\N
134	2025-W9-SEA-at-WSH	Washington Commanders	Seattle Seahawks	-3.5	Seattle Seahawks	2025-11-02 18:20:00+00	14	38	2025-10-28 13:00:00.272416	STATUS_FINAL	9	2025	regular	\N
135	2025-W9-ARI-at-DAL	Dallas Cowboys	Arizona Cardinals	-2.5	Dallas Cowboys	2025-11-03 18:15:00+00	17	27	2025-10-28 13:00:00.272433	STATUS_FINAL	9	2025	regular	\N
136	2025-W10-LV-at-DEN	Denver Broncos	Las Vegas Raiders	-9.5	Denver Broncos	2025-11-06 18:15:00+00	10	7	2025-11-04 14:00:00.305285	STATUS_FINAL	10	2025	regular	\N
137	2025-W10-ATL-at-IND	Indianapolis Colts	Atlanta Falcons	-6	Indianapolis Colts	2025-11-09 07:30:00+00	31	25	2025-11-04 14:00:00.305347	STATUS_FINAL	10	2025	regular	\N
138	2025-W10-NYG-at-CHI	Chicago Bears	New York Giants	-3.5	Chicago Bears	2025-11-09 11:00:00+00	24	20	2025-11-04 14:00:00.305459	STATUS_FINAL	10	2025	regular	\N
139	2025-W10-BUF-at-MIA	Miami Dolphins	Buffalo Bills	-9.5	Buffalo Bills	2025-11-09 11:00:00+00	30	13	2025-11-04 14:00:00.305419	STATUS_FINAL	10	2025	regular	\N
140	2025-W10-BAL-at-MIN	Minnesota Vikings	Baltimore Ravens	-3.5	Baltimore Ravens	2025-11-09 11:00:00+00	19	27	2025-11-04 14:00:00.305397	STATUS_FINAL	10	2025	regular	\N
141	2025-W10-CLE-at-NYJ	New York Jets	Cleveland Browns	-1.5	New York Jets	2025-11-09 11:00:00+00	27	20	2025-11-04 14:00:00.305478	STATUS_FINAL	10	2025	regular	\N
142	2025-W10-NE-at-TB	Tampa Bay Buccaneers	New England Patriots	-2.5	Tampa Bay Buccaneers	2025-11-09 11:00:00+00	23	28	2025-11-04 14:00:00.305515	STATUS_FINAL	10	2025	regular	\N
143	2025-W10-NO-at-CAR	Carolina Panthers	New Orleans Saints	-5.5	Carolina Panthers	2025-11-09 11:00:00+00	7	17	2025-11-04 14:00:00.30544	STATUS_FINAL	10	2025	regular	\N
144	2025-W10-JAX-at-HOU	Houston Texans	Jacksonville Jaguars	-1.5	Houston Texans	2025-11-09 11:00:00+00	36	29	2025-11-04 14:00:00.305496	STATUS_FINAL	10	2025	regular	\N
145	2025-W10-ARI-at-SEA	Seattle Seahawks	Arizona Cardinals	-6.5	Seattle Seahawks	2025-11-09 14:05:00+00	44	22	2025-11-04 14:00:00.305532	STATUS_FINAL	10	2025	regular	\N
146	2025-W10-LAR-at-SF	San Francisco 49ers	Los Angeles Rams	-3.5	Los Angeles Rams	2025-11-09 14:25:00+00	26	42	2025-11-04 14:00:00.305568	STATUS_FINAL	10	2025	regular	\N
147	2025-W10-DET-at-WSH	Washington Commanders	Detroit Lions	-8.5	Detroit Lions	2025-11-09 14:25:00+00	22	44	2025-11-04 14:00:00.30555	STATUS_FINAL	10	2025	regular	\N
148	2025-W10-PIT-at-LAC	Los Angeles Chargers	Pittsburgh Steelers	-3	Los Angeles Chargers	2025-11-09 18:20:00+00	25	10	2025-11-04 14:00:00.305586	STATUS_FINAL	10	2025	regular	\N
149	2025-W10-PHI-at-GB	Green Bay Packers	Philadelphia Eagles	-2.5	Green Bay Packers	2025-11-10 18:15:00+00	0	0	2025-11-04 14:00:00.305603	STATUS_SCHEDULED	10	2025	regular	\N
150	2025-W11-NYJ-at-NE	New England Patriots	New York Jets	-11.5	New England Patriots	2025-11-13 18:15:00+00	27	14	2025-11-11 14:00:00.279496	STATUS_FINAL	11	2025	regular	\N
151	2025-W11-WSH-at-MIA	Miami Dolphins	Washington Commanders	-2.5	Miami Dolphins	2025-11-16 07:30:00+00	16	13	2025-11-11 14:00:00.279557	STATUS_FINAL	11	2025	regular	\N
152	2025-W11-CAR-at-ATL	Atlanta Falcons	Carolina Panthers	-3.5	Atlanta Falcons	2025-11-16 11:00:00+00	27	30	2025-11-11 14:00:00.279575	STATUS_FINAL	11	2025	regular	\N
153	2025-W11-TB-at-BUF	Buffalo Bills	Tampa Bay Buccaneers	-5.5	Buffalo Bills	2025-11-16 11:00:00+00	44	32	2025-11-11 14:00:00.279588	STATUS_FINAL	11	2025	regular	\N
154	2025-W11-HOU-at-TEN	Tennessee Titans	Houston Texans	-7.5	Houston Texans	2025-11-16 11:00:00+00	13	16	2025-11-11 14:00:00.279634	STATUS_FINAL	11	2025	regular	\N
155	2025-W11-CHI-at-MIN	Minnesota Vikings	Chicago Bears	-3	Minnesota Vikings	2025-11-16 11:00:00+00	17	19	2025-11-11 14:00:00.2796	STATUS_FINAL	11	2025	regular	\N
156	2025-W11-GB-at-NYG	New York Giants	Green Bay Packers	-7.5	Green Bay Packers	2025-11-16 11:00:00+00	20	27	2025-11-11 14:00:00.279621	STATUS_FINAL	11	2025	regular	\N
157	2025-W11-CIN-at-PIT	Pittsburgh Steelers	Cincinnati Bengals	-5.5	Pittsburgh Steelers	2025-11-16 11:00:00+00	34	12	2025-11-11 14:00:00.279611	STATUS_FINAL	11	2025	regular	\N
158	2025-W11-LAC-at-JAX	Jacksonville Jaguars	Los Angeles Chargers	-3	Los Angeles Chargers	2025-11-16 11:00:00+00	35	6	2025-11-11 14:00:00.279647	STATUS_FINAL	11	2025	regular	\N
159	2025-W11-SEA-at-LAR	Los Angeles Rams	Seattle Seahawks	-2.5	Los Angeles Rams	2025-11-16 14:05:00+00	21	19	2025-11-11 14:00:00.27967	STATUS_FINAL	11	2025	regular	\N
160	2025-W11-SF-at-ARI	Arizona Cardinals	San Francisco 49ers	-2.5	San Francisco 49ers	2025-11-16 14:05:00+00	22	41	2025-11-11 14:00:00.279658	STATUS_FINAL	11	2025	regular	\N
161	2025-W11-BAL-at-CLE	Cleveland Browns	Baltimore Ravens	-8.5	Baltimore Ravens	2025-11-16 14:25:00+00	16	23	2025-11-11 14:00:00.27968	STATUS_FINAL	11	2025	regular	\N
162	2025-W11-KC-at-DEN	Denver Broncos	Kansas City Chiefs	-3.5	Kansas City Chiefs	2025-11-16 14:25:00+00	22	19	2025-11-11 14:00:00.279689	STATUS_FINAL	11	2025	regular	\N
163	2025-W11-DET-at-PHI	Philadelphia Eagles	Detroit Lions	-1.5	Philadelphia Eagles	2025-11-16 18:20:00+00	16	9	2025-11-11 14:00:00.279699	STATUS_FINAL	11	2025	regular	\N
164	2025-W11-DAL-at-LV	Las Vegas Raiders	Dallas Cowboys	-3.5	Dallas Cowboys	2025-11-17 18:15:00+00	16	33	2025-11-11 14:00:00.279708	STATUS_FINAL	11	2025	regular	\N
165	2025-W12-BUF-at-HOU	Houston Texans	Buffalo Bills	-5.5	Buffalo Bills	2025-11-20 18:15:00+00	23	19	2025-11-18 14:00:00.300026	STATUS_FINAL	12	2025	regular	\N
166	2025-W12-PIT-at-CHI	Chicago Bears	Pittsburgh Steelers	-3	Chicago Bears	2025-11-23 11:00:00+00	31	28	2025-11-18 14:00:00.300096	STATUS_FINAL	12	2025	regular	\N
167	2025-W12-NE-at-CIN	Cincinnati Bengals	New England Patriots	-8.5	New England Patriots	2025-11-23 11:00:00+00	20	26	2025-11-18 14:00:00.300109	STATUS_FINAL	12	2025	regular	\N
168	2025-W12-NYG-at-DET	Detroit Lions	New York Giants	-10.5	Detroit Lions	2025-11-23 11:00:00+00	34	27	2025-11-18 14:00:00.300121	STATUS_FINAL	12	2025	regular	\N
169	2025-W12-MIN-at-GB	Green Bay Packers	Minnesota Vikings	-6.5	Green Bay Packers	2025-11-23 11:00:00+00	23	6	2025-11-18 14:00:00.300131	STATUS_FINAL	12	2025	regular	\N
170	2025-W12-SEA-at-TEN	Tennessee Titans	Seattle Seahawks	-13.5	Seattle Seahawks	2025-11-23 11:00:00+00	24	30	2025-11-18 14:00:00.300151	STATUS_FINAL	12	2025	regular	\N
171	2025-W12-IND-at-KC	Kansas City Chiefs	Indianapolis Colts	-3	Kansas City Chiefs	2025-11-23 11:00:00+00	23	20	2025-11-18 14:00:00.300141	STATUS_FINAL	12	2025	regular	\N
172	2025-W12-NYJ-at-BAL	Baltimore Ravens	New York Jets	-13.5	Baltimore Ravens	2025-11-23 11:00:00+00	23	10	2025-11-18 14:00:00.30008	STATUS_FINAL	12	2025	regular	\N
173	2025-W12-CLE-at-LV	Las Vegas Raiders	Cleveland Browns	-3	Las Vegas Raiders	2025-11-23 14:05:00+00	10	24	2025-11-18 14:00:00.300171	STATUS_FINAL	12	2025	regular	\N
174	2025-W12-JAX-at-ARI	Arizona Cardinals	Jacksonville Jaguars	-2.5	Jacksonville Jaguars	2025-11-23 14:05:00+00	24	27	2025-11-18 14:00:00.300161	STATUS_FINAL	12	2025	regular	\N
175	2025-W12-PHI-at-DAL	Dallas Cowboys	Philadelphia Eagles	-3.5	Philadelphia Eagles	2025-11-23 14:25:00+00	24	21	2025-11-18 14:00:00.300189	STATUS_FINAL	12	2025	regular	\N
176	2025-W12-ATL-at-NO	New Orleans Saints	Atlanta Falcons	-1.5	New Orleans Saints	2025-11-23 14:25:00+00	10	24	2025-11-18 14:00:00.30018	STATUS_FINAL	12	2025	regular	\N
177	2025-W12-TB-at-LAR	Los Angeles Rams	Tampa Bay Buccaneers	-6.5	Los Angeles Rams	2025-11-23 18:20:00+00	34	7	2025-11-18 14:00:00.300197	STATUS_FINAL	12	2025	regular	\N
178	2025-W12-CAR-at-SF	San Francisco 49ers	Carolina Panthers	-7	San Francisco 49ers	2025-11-24 18:15:00+00	20	9	2025-11-18 14:00:00.300207	STATUS_FINAL	12	2025	regular	\N
179	2025-W13-GB-at-DET	Detroit Lions	Green Bay Packers	-2.5	Detroit Lions	2025-11-27 11:00:00+00	24	31	2025-11-25 14:00:00.273546	STATUS_FINAL	13	2025	regular	\N
180	2025-W13-KC-at-DAL	Dallas Cowboys	Kansas City Chiefs	-3.5	Kansas City Chiefs	2025-11-27 14:30:00+00	31	28	2025-11-25 14:00:00.273592	STATUS_FINAL	13	2025	regular	\N
181	2025-W13-CIN-at-BAL	Baltimore Ravens	Cincinnati Bengals	-7	Baltimore Ravens	2025-11-27 18:20:00+00	14	32	2025-11-25 14:00:00.273609	STATUS_FINAL	13	2025	regular	\N
182	2025-W13-CHI-at-PHI	Philadelphia Eagles	Chicago Bears	-7	Philadelphia Eagles	2025-11-28 13:00:00+00	15	24	2025-11-25 14:00:00.273621	STATUS_FINAL	13	2025	regular	\N
183	2025-W13-SF-at-CLE	Cleveland Browns	San Francisco 49ers	-6	San Francisco 49ers	2025-11-30 11:00:00+00	8	26	2025-11-25 14:00:00.273663	STATUS_FINAL	13	2025	regular	\N
184	2025-W13-JAX-at-TEN	Tennessee Titans	Jacksonville Jaguars	-6.5	Jacksonville Jaguars	2025-11-30 11:00:00+00	3	25	2025-11-25 14:00:00.273682	STATUS_FINAL	13	2025	regular	\N
185	2025-W13-HOU-at-IND	Indianapolis Colts	Houston Texans	-4.5	Indianapolis Colts	2025-11-30 11:00:00+00	16	20	2025-11-25 14:00:00.273673	STATUS_FINAL	13	2025	regular	\N
186	2025-W13-NO-at-MIA	Miami Dolphins	New Orleans Saints	-6	Miami Dolphins	2025-11-30 11:00:00+00	21	17	2025-11-25 14:00:00.273693	STATUS_FINAL	13	2025	regular	\N
187	2025-W13-ATL-at-NYJ	New York Jets	Atlanta Falcons	-2.5	Atlanta Falcons	2025-11-30 11:00:00+00	27	24	2025-11-25 14:00:00.273643	STATUS_FINAL	13	2025	regular	\N
188	2025-W13-ARI-at-TB	Tampa Bay Buccaneers	Arizona Cardinals	-3	Tampa Bay Buccaneers	2025-11-30 11:00:00+00	20	17	2025-11-25 14:00:00.273633	STATUS_FINAL	13	2025	regular	\N
189	2025-W13-LAR-at-CAR	Carolina Panthers	Los Angeles Rams	-10.5	Los Angeles Rams	2025-11-30 11:00:00+00	31	28	2025-11-25 14:00:00.273653	STATUS_FINAL	13	2025	regular	\N
190	2025-W13-MIN-at-SEA	Seattle Seahawks	Minnesota Vikings	-10.5	Seattle Seahawks	2025-11-30 14:05:00+00	26	0	2025-11-25 14:00:00.273703	STATUS_FINAL	13	2025	regular	\N
191	2025-W13-BUF-at-PIT	Pittsburgh Steelers	Buffalo Bills	-3.5	Buffalo Bills	2025-11-30 14:25:00+00	7	26	2025-11-25 14:00:00.273712	STATUS_FINAL	13	2025	regular	\N
192	2025-W13-LV-at-LAC	Los Angeles Chargers	Las Vegas Raiders	-10	Los Angeles Chargers	2025-11-30 14:25:00+00	31	14	2025-11-25 14:00:00.273722	STATUS_FINAL	13	2025	regular	\N
193	2025-W13-DEN-at-WSH	Washington Commanders	Denver Broncos	-6.5	Denver Broncos	2025-11-30 18:20:00+00	26	27	2025-11-25 14:00:00.273732	STATUS_FINAL	13	2025	regular	\N
194	2025-W13-NYG-at-NE	New England Patriots	New York Giants	-7.5	New England Patriots	2025-12-01 18:15:00+00	33	15	2025-11-25 14:00:00.273742	STATUS_FINAL	13	2025	regular	\N
195	2025-W14-DAL-at-DET	Detroit Lions	Dallas Cowboys	-3	Detroit Lions	2025-12-04 18:15:00+00	44	30	2025-12-02 14:00:00.280746	STATUS_FINAL	14	2025	regular	\N
196	2025-W14-SEA-at-ATL	Atlanta Falcons	Seattle Seahawks	-7.5	Seattle Seahawks	2025-12-07 11:00:00+00	9	37	2025-12-02 14:00:00.280796	STATUS_FINAL	14	2025	regular	\N
197	2025-W14-TEN-at-CLE	Cleveland Browns	Tennessee Titans	-4.5	Cleveland Browns	2025-12-07 11:00:00+00	29	31	2025-12-02 14:00:00.280836	STATUS_FINAL	14	2025	regular	\N
198	2025-W14-CHI-at-GB	Green Bay Packers	Chicago Bears	-6.5	Green Bay Packers	2025-12-07 14:25:00+00	28	21	2025-12-02 14:00:00.280932	STATUS_FINAL	14	2025	regular	\N
199	2025-W14-WSH-at-MIN	Minnesota Vikings	Washington Commanders	-1.5	Washington Commanders	2025-12-07 11:00:00+00	31	0	2025-12-02 14:00:00.28089	STATUS_FINAL	14	2025	regular	\N
200	2025-W14-MIA-at-NYJ	New York Jets	Miami Dolphins	-2.5	Miami Dolphins	2025-12-07 11:00:00+00	10	34	2025-12-02 14:00:00.280873	STATUS_FINAL	14	2025	regular	\N
201	2025-W14-NO-at-TB	Tampa Bay Buccaneers	New Orleans Saints	-8.5	Tampa Bay Buccaneers	2025-12-07 11:00:00+00	20	24	2025-12-02 14:00:00.280902	STATUS_FINAL	14	2025	regular	\N
202	2025-W14-IND-at-JAX	Jacksonville Jaguars	Indianapolis Colts	-1.5	Indianapolis Colts	2025-12-07 11:00:00+00	36	19	2025-12-02 14:00:00.280855	STATUS_FINAL	14	2025	regular	\N
203	2025-W14-PIT-at-BAL	Baltimore Ravens	Pittsburgh Steelers	-5.5	Baltimore Ravens	2025-12-07 11:00:00+00	22	27	2025-12-02 14:00:00.280812	STATUS_FINAL	14	2025	regular	\N
204	2025-W14-DEN-at-LV	Las Vegas Raiders	Denver Broncos	-7.5	Denver Broncos	2025-12-07 14:05:00+00	17	24	2025-12-02 14:00:00.280912	STATUS_FINAL	14	2025	regular	\N
205	2025-W14-CIN-at-BUF	Buffalo Bills	Cincinnati Bengals	-6	Buffalo Bills	2025-12-07 11:00:00+00	39	34	2025-12-02 14:00:00.280824	STATUS_FINAL	14	2025	regular	\N
206	2025-W14-LAR-at-ARI	Arizona Cardinals	Los Angeles Rams	-8.5	Los Angeles Rams	2025-12-07 14:25:00+00	17	45	2025-12-02 14:00:00.280922	STATUS_FINAL	14	2025	regular	\N
207	2025-W14-HOU-at-KC	Kansas City Chiefs	Houston Texans	-3.5	Kansas City Chiefs	2025-12-07 18:20:00+00	10	20	2025-12-02 14:00:00.280942	STATUS_FINAL	14	2025	regular	\N
208	2025-W14-PHI-at-LAC	Los Angeles Chargers	Philadelphia Eagles	-2.5	Philadelphia Eagles	2025-12-08 18:15:00+00	22	19	2025-12-02 14:00:00.280951	STATUS_FINAL	14	2025	regular	\N
209	2025-W15-ATL-at-TB	Tampa Bay Buccaneers	Atlanta Falcons	-4.5	Tampa Bay Buccaneers	2025-12-11 18:15:00+00	28	29	2025-12-09 14:00:00.314995	STATUS_FINAL	15	2025	regular	\N
210	2025-W15-CLE-at-CHI	Chicago Bears	Cleveland Browns	-7.5	Chicago Bears	2025-12-14 11:00:00+00	31	3	2025-12-09 14:00:00.315142	STATUS_FINAL	15	2025	regular	\N
211	2025-W15-BAL-at-CIN	Cincinnati Bengals	Baltimore Ravens	-2.5	Baltimore Ravens	2025-12-14 11:00:00+00	0	24	2025-12-09 14:00:00.315106	STATUS_FINAL	15	2025	regular	\N
212	2025-W15-LAC-at-KC	Kansas City Chiefs	Los Angeles Chargers	-3.5	Kansas City Chiefs	2025-12-14 11:00:00+00	13	16	2025-12-09 14:00:00.315177	STATUS_FINAL	15	2025	regular	\N
213	2025-W15-BUF-at-NE	New England Patriots	Buffalo Bills	-1.5	Buffalo Bills	2025-12-14 11:00:00+00	31	35	2025-12-09 14:00:00.315125	STATUS_FINAL	15	2025	regular	\N
214	2025-W15-WSH-at-NYG	New York Giants	Washington Commanders	-2.5	New York Giants	2025-12-14 11:00:00+00	21	29	2025-12-09 14:00:00.315209	STATUS_FINAL	15	2025	regular	\N
215	2025-W15-LV-at-PHI	Philadelphia Eagles	Las Vegas Raiders	-11.5	Philadelphia Eagles	2025-12-14 11:00:00+00	31	0	2025-12-09 14:00:00.315192	STATUS_FINAL	15	2025	regular	\N
216	2025-W15-NYJ-at-JAX	Jacksonville Jaguars	New York Jets	-12.5	Jacksonville Jaguars	2025-12-14 11:00:00+00	48	20	2025-12-09 14:00:00.31516	STATUS_FINAL	15	2025	regular	\N
217	2025-W15-ARI-at-HOU	Houston Texans	Arizona Cardinals	-9.5	Houston Texans	2025-12-14 11:00:00+00	40	20	2025-12-09 14:00:00.315081	STATUS_FINAL	15	2025	regular	\N
218	2025-W15-GB-at-DEN	Denver Broncos	Green Bay Packers	-2.5	Green Bay Packers	2025-12-14 14:25:00+00	34	26	2025-12-09 14:00:00.315242	STATUS_FINAL	15	2025	regular	\N
219	2025-W15-DET-at-LAR	Los Angeles Rams	Detroit Lions	-5.5	Los Angeles Rams	2025-12-14 14:25:00+00	41	34	2025-12-09 14:00:00.315259	STATUS_FINAL	15	2025	regular	\N
220	2025-W15-CAR-at-NO	New Orleans Saints	Carolina Panthers	-2.5	Carolina Panthers	2025-12-14 14:25:00+00	20	17	2025-12-09 14:00:00.315226	STATUS_FINAL	15	2025	regular	\N
221	2025-W15-TEN-at-SF	San Francisco 49ers	Tennessee Titans	-12.5	San Francisco 49ers	2025-12-14 14:25:00+00	37	24	2025-12-09 14:00:00.31529	STATUS_FINAL	15	2025	regular	\N
222	2025-W15-IND-at-SEA	Seattle Seahawks	Indianapolis Colts	-13.5	Seattle Seahawks	2025-12-14 14:25:00+00	18	16	2025-12-09 14:00:00.315274	STATUS_FINAL	15	2025	regular	\N
223	2025-W15-MIN-at-DAL	Dallas Cowboys	Minnesota Vikings	-6	Dallas Cowboys	2025-12-14 18:20:00+00	26	34	2025-12-09 14:00:00.315305	STATUS_FINAL	15	2025	regular	\N
224	2025-W15-MIA-at-PIT	Pittsburgh Steelers	Miami Dolphins	-3	Pittsburgh Steelers	2025-12-15 18:15:00+00	28	15	2025-12-09 14:00:00.315319	STATUS_FINAL	15	2025	regular	\N
226	2025-W16-GB-at-CHI	Chicago Bears	Green Bay Packers	-1.5	Green Bay Packers	2025-12-20 18:20:00+00	22	16	2025-12-16 14:00:00.23919	STATUS_FINAL	16	2025	regular	\N
227	2025-W16-PHI-at-WSH	Washington Commanders	Philadelphia Eagles	-6.5	Philadelphia Eagles	2025-12-20 15:00:00+00	18	29	2025-12-16 14:00:00.239174	STATUS_FINAL	16	2025	regular	\N
229	2025-W16-LAC-at-DAL	Dallas Cowboys	Los Angeles Chargers	-1.5	Dallas Cowboys	2025-12-21 11:00:00+00	17	34	2025-12-16 14:00:00.239234	STATUS_FINAL	16	2025	regular	\N
230	2025-W16-KC-at-TEN	Tennessee Titans	Kansas City Chiefs	-3.5	Kansas City Chiefs	2025-12-21 11:00:00+00	26	9	2025-12-16 14:00:00.239245	STATUS_FINAL	16	2025	regular	\N
231	2025-W16-NYJ-at-NO	New Orleans Saints	New York Jets	-4.5	New Orleans Saints	2025-12-21 11:00:00+00	29	6	2025-12-16 14:00:00.239266	STATUS_FINAL	16	2025	regular	\N
232	2025-W16-MIN-at-NYG	New York Giants	Minnesota Vikings	-3	Minnesota Vikings	2025-12-21 11:00:00+00	13	16	2025-12-16 14:00:00.239255	STATUS_FINAL	16	2025	regular	\N
233	2025-W16-TB-at-CAR	Carolina Panthers	Tampa Bay Buccaneers	-3	Tampa Bay Buccaneers	2025-12-21 11:00:00+00	23	20	2025-12-16 14:00:00.239213	STATUS_FINAL	16	2025	regular	\N
234	2025-W16-NE-at-BAL	Baltimore Ravens	New England Patriots	-3	Baltimore Ravens	2025-12-21 18:20:00+00	24	28	2025-12-16 14:00:00.239316	STATUS_FINAL	16	2025	regular	\N
235	2025-W16-JAX-at-DEN	Denver Broncos	Jacksonville Jaguars	-3	Denver Broncos	2025-12-21 14:05:00+00	20	34	2025-12-16 14:00:00.239286	STATUS_FINAL	16	2025	regular	\N
236	2025-W16-ATL-at-ARI	Arizona Cardinals	Atlanta Falcons	-2.5	Atlanta Falcons	2025-12-21 14:05:00+00	19	26	2025-12-16 14:00:00.239276	STATUS_FINAL	16	2025	regular	\N
237	2025-W16-PIT-at-DET	Detroit Lions	Pittsburgh Steelers	-7	Detroit Lions	2025-12-21 14:25:00+00	24	29	2025-12-16 14:00:00.239296	STATUS_FINAL	16	2025	regular	\N
238	2025-W16-LV-at-HOU	Houston Texans	Las Vegas Raiders	-14.5	Houston Texans	2025-12-21 14:25:00+00	23	21	2025-12-16 14:00:00.239306	STATUS_FINAL	16	2025	regular	\N
239	2025-W16-CIN-at-MIA	Miami Dolphins	Cincinnati Bengals	-1.5	Cincinnati Bengals	2025-12-21 11:00:00+00	21	45	2025-12-16 14:00:00.239223	STATUS_FINAL	16	2025	regular	\N
240	2025-W16-SF-at-IND	Indianapolis Colts	San Francisco 49ers	-5.5	San Francisco 49ers	2025-12-22 18:15:00+00	27	48	2025-12-16 14:00:00.239325	STATUS_FINAL	16	2025	regular	\N
241	2025-W17-DAL-at-WSH	Washington Commanders	Dallas Cowboys	-6.5	Dallas Cowboys	2025-12-25 11:00:00+00	23	30	2025-12-23 14:00:00.325954	STATUS_FINAL	17	2025	regular	\N
253	2025-W17-NE-at-NYJ	New York Jets	New England Patriots	-13.5	New England Patriots	2025-12-28 11:00:00+00	10	42	2025-12-23 14:00:00.32615	STATUS_FINAL	17	2025	regular	\N
254	2025-W17-PHI-at-BUF	Buffalo Bills	Philadelphia Eagles	-1.5	Buffalo Bills	2025-12-28 14:25:00+00	12	13	2025-12-23 14:00:00.326179	STATUS_FINAL	17	2025	regular	\N
255	2025-W17-CHI-at-SF	San Francisco 49ers	Chicago Bears	-3	San Francisco 49ers	2025-12-28 18:20:00+00	42	38	2025-12-23 14:00:00.326189	STATUS_FINAL	17	2025	regular	\N
256	2025-W17-LAR-at-ATL	Atlanta Falcons	Los Angeles Rams	-8.5	Los Angeles Rams	2025-12-29 18:15:00+00	27	24	2025-12-23 14:00:00.326198	STATUS_FINAL	17	2025	regular	\N
264	2025-W18-GB-at-MIN	Minnesota Vikings	Green Bay Packers	-6.5	Minnesota Vikings	2026-01-04 11:00:00+00	16	3	2025-12-30 14:00:00.283817	STATUS_FINAL	18	2025	regular	\N
266	2025-W18-DAL-at-NYG	New York Giants	Dallas Cowboys	-4.5	Dallas Cowboys	2026-01-04 11:00:00+00	34	17	2025-12-30 14:00:00.2838	STATUS_FINAL	18	2025	regular	\N
271	2025-W18-TEN-at-JAX	Jacksonville Jaguars	Tennessee Titans	-12.5	Jacksonville Jaguars	2026-01-04 11:00:00+00	41	7	2025-12-30 14:00:00.283853	STATUS_FINAL	18	2025	regular	\N
267	2025-W18-WSH-at-PHI	Philadelphia Eagles	Washington Commanders	-7	Philadelphia Eagles	2026-01-04 14:25:00+00	17	24	2025-12-30 14:00:00.283976	STATUS_FINAL	18	2025	regular	\N
268	2025-W18-BAL-at-PIT	Pittsburgh Steelers	Baltimore Ravens	-3.5	Baltimore Ravens	2026-01-04 18:20:00+00	26	24	2025-12-30 14:00:00.283993	STATUS_FINAL	18	2025	regular	\N
272	2025-W18-IND-at-HOU	Houston Texans	Indianapolis Colts	-10	Houston Texans	2026-01-04 11:00:00+00	38	30	2025-12-30 14:00:00.283835	STATUS_FINAL	18	2025	regular	\N
258	2025-W18-NYJ-at-BUF	Buffalo Bills	New York Jets	-7	Buffalo Bills	2026-01-04 14:25:00+00	35	8	2025-12-30 14:00:00.283889	STATUS_FINAL	18	2025	regular	\N
270	2025-W18-CAR-at-TB	Tampa Bay Buccaneers	Carolina Panthers	-2.5	Tampa Bay Buccaneers	2026-01-03 14:30:00+00	16	14	2025-12-30 14:00:00.283649	STATUS_FINAL	18	2025	regular	\N
269	2025-W18-SEA-at-SF	San Francisco 49ers	Seattle Seahawks	-1.5	Seattle Seahawks	2026-01-03 18:00:00+00	3	13	2025-12-30 14:00:00.283734	STATUS_FINAL	18	2025	regular	\N
257	2025-W18-NO-at-ATL	Atlanta Falcons	New Orleans Saints	-3	Atlanta Falcons	2026-01-04 11:00:00+00	19	17	2025-12-30 14:00:00.283761	STATUS_FINAL	18	2025	regular	\N
260	2025-W18-CLE-at-CIN	Cincinnati Bengals	Cleveland Browns	-7.5	Cincinnati Bengals	2026-01-04 11:00:00+00	18	20	2025-12-30 14:00:00.283781	STATUS_FINAL	18	2025	regular	\N
259	2025-W18-DET-at-CHI	Chicago Bears	Detroit Lions	-2.5	Chicago Bears	2026-01-04 14:25:00+00	16	19	2025-12-30 14:00:00.283906	STATUS_FINAL	18	2025	regular	\N
261	2025-W18-LAC-at-DEN	Denver Broncos	Los Angeles Chargers	-12.5	Denver Broncos	2026-01-04 14:25:00+00	19	3	2025-12-30 14:00:00.283925	STATUS_FINAL	18	2025	regular	\N
262	2025-W18-KC-at-LV	Las Vegas Raiders	Kansas City Chiefs	-5.5	Kansas City Chiefs	2026-01-04 14:25:00+00	14	12	2025-12-30 14:00:00.283943	STATUS_FINAL	18	2025	regular	\N
263	2025-W18-ARI-at-LAR	Los Angeles Rams	Arizona Cardinals	-7.5	Los Angeles Rams	2026-01-04 14:25:00+00	37	20	2025-12-30 14:00:00.28387	STATUS_FINAL	18	2025	regular	\N
265	2025-W18-MIA-at-NE	New England Patriots	Miami Dolphins	-11.5	New England Patriots	2026-01-04 14:25:00+00	38	10	2025-12-30 14:00:00.283959	STATUS_FINAL	18	2025	regular	\N
\.


--
-- Data for Name: job_run; Type: TABLE DATA; Schema: public; Owner: pickarena_prod_db_user
--

COPY public.job_run (id, job_name, ran_at, ok, inserted, updated, unchanged, failed_weeks, message) FROM stdin;
1	schedule_update	2026-01-07 23:17:31.704236	t	0	0	14	0	Manual schedule update from admin (Y2025 POST, weeks 1-18)
2	schedule_update	2026-01-13 13:20:00.56668	t	0	8	6	0	2025 POST W1-5
3	schedule_update	2026-01-19 15:57:43.784676	t	0	2	12	0	Manual schedule update from admin (Y2025 POST, weeks 1-18)
\.


--
-- Data for Name: pick; Type: TABLE DATA; Schema: public; Owner: pickarena_prod_db_user
--

COPY public.pick (id, user_id, game_id, team_picked, confidence, pick_time, week, points_earned, is_overridden) FROM stdin;
1	14	1	Philadelphia Eagles	3	2025-09-02 14:46:17.905442	1	0	f
2	14	2	Los Angeles Chargers	4	2025-09-05 17:07:59.621518	1	4	f
3	14	3	Tampa Bay Buccaneers	12	2025-09-05 17:07:59.622612	1	12	f
4	14	4	Cincinnati Bengals	5	2025-09-05 17:07:59.623227	1	0	f
5	14	5	Indianapolis Colts	15	2025-09-05 17:07:59.623839	1	15	f
6	14	6	New England Patriots	16	2025-09-05 17:07:59.624519	1	0	f
7	14	7	Arizona Cardinals	11	2025-09-05 17:07:59.625253	1	11	f
8	14	8	New York Jets	7	2025-09-05 17:07:59.626046	1	7	f
9	14	9	Washington Commanders	13	2025-09-05 17:07:59.629611	1	13	f
10	14	10	Jacksonville Jaguars	8	2025-09-05 17:07:59.630349	1	8	f
11	14	11	Denver Broncos	9	2025-09-05 17:07:59.631231	1	9	f
12	14	12	Seattle Seahawks	6	2025-09-05 17:07:59.631946	1	0	f
13	14	13	Green Bay Packers	2	2025-09-05 17:07:59.632638	1	2	f
14	14	14	Los Angeles Rams	14	2025-09-05 17:07:59.633395	1	14	f
15	14	15	Buffalo Bills	10	2025-09-05 17:07:59.634221	1	0	f
16	14	16	Chicago Bears	1	2025-09-05 17:07:59.634931	1	0	f
17	1	1	Philadelphia Eagles	8	2025-09-02 13:23:20.782112	1	0	f
18	1	2	Kansas City Chiefs	15	2025-09-02 13:23:20.783824	1	0	f
19	1	3	Tampa Bay Buccaneers	9	2025-09-02 13:23:20.784963	1	9	f
20	1	4	Cincinnati Bengals	7	2025-09-02 13:23:20.785977	1	0	f
21	1	5	Indianapolis Colts	6	2025-09-02 13:23:20.786938	1	6	f
22	1	6	New England Patriots	5	2025-09-02 13:23:20.787881	1	0	f
23	1	7	Arizona Cardinals	3	2025-09-02 13:23:20.78884	1	3	f
24	1	8	New York Jets	2	2025-09-02 13:23:20.789787	1	2	f
25	1	9	Washington Commanders	4	2025-09-02 13:23:20.790704	1	4	f
26	1	10	Jacksonville Jaguars	1	2025-09-02 13:23:20.791615	1	1	f
27	1	11	Denver Broncos	16	2025-09-02 13:23:20.792554	1	16	f
28	1	12	San Francisco 49ers	10	2025-09-02 13:23:20.793491	1	10	f
29	1	13	Detroit Lions	14	2025-09-02 13:23:20.794391	1	0	f
30	1	14	Los Angeles Rams	11	2025-09-02 13:23:20.795295	1	11	f
31	1	15	Buffalo Bills	12	2025-09-02 13:23:20.7962	1	0	f
32	1	16	Minnesota Vikings	13	2025-09-02 13:23:20.796892	1	13	f
33	2	1	Philadelphia Eagles	5	2025-09-02 15:03:24.909333	1	0	f
34	2	2	Kansas City Chiefs	8	2025-09-02 15:03:24.91019	1	0	f
35	2	3	Atlanta Falcons	3	2025-09-02 15:03:24.910839	1	0	f
36	2	4	Cincinnati Bengals	9	2025-09-02 15:03:24.911476	1	0	f
37	2	5	Miami Dolphins	10	2025-09-02 15:03:24.912099	1	0	f
38	2	6	Las Vegas Raiders	2	2025-09-02 15:03:24.912787	1	2	f
39	2	7	New Orleans Saints	11	2025-09-02 15:03:24.913432	1	0	f
40	2	8	Pittsburgh Steelers	7	2025-09-02 15:03:24.914238	1	0	f
41	2	9	Washington Commanders	6	2025-09-02 15:03:24.914919	1	6	f
42	2	10	Carolina Panthers	1	2025-09-02 15:03:24.915562	1	0	f
43	2	11	Denver Broncos	16	2025-09-02 15:03:24.916312	1	16	f
44	2	12	San Francisco 49ers	15	2025-09-02 15:03:24.917114	1	15	f
45	2	13	Green Bay Packers	12	2025-09-02 15:03:24.917771	1	12	f
46	2	14	Los Angeles Rams	13	2025-09-02 15:03:24.918432	1	13	f
47	2	15	Buffalo Bills	14	2025-09-02 15:03:24.919076	1	0	f
48	2	16	Minnesota Vikings	4	2025-09-02 15:03:24.919594	1	4	f
49	9	1	Philadelphia Eagles	5	2025-09-02 18:26:03.960111	1	0	f
50	9	2	Los Angeles Chargers	3	2025-09-02 18:26:03.961358	1	3	f
51	9	3	Tampa Bay Buccaneers	4	2025-09-02 18:26:03.962152	1	4	f
52	9	4	Cincinnati Bengals	2	2025-09-02 18:26:03.962856	1	0	f
53	9	5	Miami Dolphins	6	2025-09-02 18:26:03.963714	1	0	f
54	9	6	Las Vegas Raiders	8	2025-09-02 18:26:03.964352	1	8	f
55	9	7	Arizona Cardinals	16	2025-09-02 18:26:03.965038	1	16	f
56	9	8	Pittsburgh Steelers	11	2025-09-02 18:26:03.965685	1	0	f
57	9	9	Washington Commanders	10	2025-09-02 18:26:03.966344	1	10	f
58	9	10	Jacksonville Jaguars	14	2025-09-02 18:26:03.96704	1	14	f
59	9	11	Denver Broncos	13	2025-09-02 18:26:03.967695	1	13	f
60	9	12	San Francisco 49ers	7	2025-09-02 18:26:03.968278	1	7	f
61	9	13	Detroit Lions	12	2025-09-02 18:26:03.968894	1	0	f
62	9	14	Houston Texans	1	2025-09-02 18:26:03.969502	1	0	f
63	9	15	Buffalo Bills	9	2025-09-02 18:26:03.970108	1	0	f
64	9	16	Minnesota Vikings	15	2025-09-02 18:26:03.970565	1	15	f
65	22	1	Philadelphia Eagles	16	2025-09-02 20:25:10.162623	1	0	f
66	22	2	Kansas City Chiefs	15	2025-09-02 20:25:10.164509	1	0	f
67	22	3	Tampa Bay Buccaneers	4	2025-09-02 20:25:10.16605	1	4	f
68	22	4	Cincinnati Bengals	14	2025-09-02 20:25:10.167097	1	0	f
69	22	5	Indianapolis Colts	3	2025-09-02 20:25:10.168029	1	3	f
70	22	6	New England Patriots	12	2025-09-02 20:25:10.168972	1	0	f
71	22	7	New Orleans Saints	10	2025-09-02 20:25:10.169886	1	0	f
72	22	8	Pittsburgh Steelers	9	2025-09-02 20:25:10.170803	1	0	f
73	22	9	Washington Commanders	13	2025-09-02 20:25:10.17177	1	13	f
74	22	10	Jacksonville Jaguars	5	2025-09-02 20:25:10.172666	1	5	f
75	22	11	Denver Broncos	11	2025-09-02 20:25:10.173571	1	11	f
76	22	12	San Francisco 49ers	6	2025-09-02 20:25:10.174473	1	6	f
77	22	13	Detroit Lions	7	2025-09-02 20:25:10.175331	1	0	f
78	22	14	Los Angeles Rams	8	2025-09-02 20:25:10.176277	1	8	f
79	22	15	Baltimore Ravens	2	2025-09-02 20:25:10.177769	1	2	f
80	22	16	Chicago Bears	1	2025-09-02 20:25:10.17928	1	0	f
81	10	1	Philadelphia Eagles	7	2025-09-02 20:30:14.255921	1	0	f
82	13	1	Philadelphia Eagles	5	2025-09-02 20:43:33.371688	1	0	f
83	13	2	Los Angeles Chargers	7	2025-09-02 20:43:33.372833	1	7	f
84	13	3	Tampa Bay Buccaneers	6	2025-09-07 01:57:57.757593	1	6	f
85	13	4	Cincinnati Bengals	3	2025-09-07 01:57:57.759225	1	0	f
86	13	5	Miami Dolphins	1	2025-09-07 01:57:57.760012	1	0	f
87	13	6	Las Vegas Raiders	14	2025-09-07 01:57:57.760717	1	14	f
88	13	7	Arizona Cardinals	4	2025-09-07 01:57:57.761307	1	4	f
89	13	8	New York Jets	13	2025-09-07 01:57:57.761918	1	13	f
90	13	9	Washington Commanders	10	2025-09-07 01:57:57.762582	1	10	f
91	13	10	Carolina Panthers	8	2025-09-07 01:57:57.763161	1	0	f
92	13	11	Denver Broncos	12	2025-09-07 01:57:57.763753	1	12	f
93	13	12	Seattle Seahawks	11	2025-09-07 01:57:57.764382	1	0	f
94	13	13	Detroit Lions	15	2025-09-07 01:57:57.765037	1	0	f
95	13	14	Houston Texans	9	2025-09-07 01:57:57.765634	1	0	f
96	13	15	Buffalo Bills	2	2025-09-07 01:57:57.766209	1	0	f
97	13	16	Minnesota Vikings	16	2025-09-07 01:57:57.7668	1	16	f
98	23	1	Philadelphia Eagles	16	2025-09-02 22:23:19.686957	1	0	f
99	23	2	Los Angeles Chargers	5	2025-09-02 22:23:19.688162	1	5	f
100	23	3	Tampa Bay Buccaneers	6	2025-09-02 22:23:19.689071	1	6	f
101	23	4	Cincinnati Bengals	2	2025-09-02 22:23:19.689901	1	0	f
102	23	5	Indianapolis Colts	3	2025-09-02 22:23:19.690699	1	3	f
103	23	6	New England Patriots	1	2025-09-02 22:23:19.691454	1	0	f
104	23	7	Arizona Cardinals	7	2025-09-02 22:23:19.692212	1	7	f
105	23	8	Pittsburgh Steelers	12	2025-09-02 22:23:19.692963	1	0	f
106	23	9	Washington Commanders	10	2025-09-02 22:23:19.693756	1	10	f
107	23	10	Jacksonville Jaguars	8	2025-09-02 22:23:19.694505	1	8	f
108	23	11	Denver Broncos	15	2025-09-02 22:23:19.69522	1	15	f
109	23	12	San Francisco 49ers	9	2025-09-02 22:23:19.695959	1	9	f
110	23	13	Detroit Lions	14	2025-09-02 22:23:19.696894	1	0	f
111	23	14	Los Angeles Rams	13	2025-09-02 22:23:19.697641	1	13	f
112	23	15	Buffalo Bills	11	2025-09-02 22:23:19.698367	1	0	f
113	23	16	Chicago Bears	4	2025-09-02 22:23:19.69892	1	0	f
114	17	1	Philadelphia Eagles	1	2025-09-04 20:59:34.167648	1	0	f
115	17	10	Carolina Panthers	5	2025-09-07 15:09:05.224848	1	0	f
116	17	2	Los Angeles Chargers	2	2025-09-05 23:46:41.847998	1	2	f
117	16	1	Philadelphia Eagles	14	2025-09-02 22:45:24.382269	1	0	f
118	16	2	Kansas City Chiefs	11	2025-09-02 22:45:24.383226	1	0	f
119	16	3	Atlanta Falcons	7	2025-09-02 22:45:24.383916	1	0	f
120	16	4	Cincinnati Bengals	12	2025-09-02 22:45:24.384766	1	0	f
121	16	5	Indianapolis Colts	2	2025-09-02 22:45:24.385577	1	2	f
122	16	6	Las Vegas Raiders	5	2025-09-02 22:45:24.386511	1	5	f
123	16	7	Arizona Cardinals	15	2025-09-02 22:45:24.387334	1	15	f
124	16	8	Pittsburgh Steelers	8	2025-09-02 22:45:24.388126	1	0	f
125	16	9	Washington Commanders	13	2025-09-02 22:45:24.388764	1	13	f
126	16	10	Jacksonville Jaguars	10	2025-09-02 22:45:24.389328	1	10	f
127	16	11	Denver Broncos	16	2025-09-02 22:45:24.389959	1	16	f
128	16	12	Seattle Seahawks	6	2025-09-02 22:45:24.390567	1	0	f
129	16	13	Detroit Lions	4	2025-09-02 22:45:24.391323	1	0	f
130	16	14	Houston Texans	9	2025-09-02 22:45:24.391952	1	0	f
131	16	15	Baltimore Ravens	3	2025-09-02 22:45:24.392567	1	3	f
132	16	16	Minnesota Vikings	1	2025-09-02 22:45:24.393126	1	1	f
133	21	1	Dallas Cowboys	7	2025-09-03 19:13:13.35231	1	7	f
134	21	2	Kansas City Chiefs	8	2025-09-03 19:13:13.353696	1	0	f
135	21	3	Tampa Bay Buccaneers	13	2025-09-03 19:13:13.354642	1	13	f
136	21	4	Cincinnati Bengals	12	2025-09-03 19:13:13.355596	1	0	f
137	21	6	New England Patriots	3	2025-09-03 19:13:13.357653	1	0	f
138	21	7	Arizona Cardinals	2	2025-09-03 19:13:13.358564	1	2	f
139	21	8	Pittsburgh Steelers	9	2025-09-03 19:13:13.359476	1	0	f
140	21	9	Washington Commanders	14	2025-09-03 19:13:13.36037	1	14	f
141	21	10	Jacksonville Jaguars	4	2025-09-03 19:13:13.361318	1	4	f
142	21	11	Denver Broncos	16	2025-09-03 19:13:13.362248	1	16	f
143	21	12	San Francisco 49ers	11	2025-09-03 19:13:13.363209	1	11	f
144	21	13	Detroit Lions	10	2025-09-03 19:13:13.364131	1	0	f
145	21	14	Los Angeles Rams	5	2025-09-03 19:13:13.365136	1	5	f
146	21	15	Buffalo Bills	15	2025-09-03 19:13:13.36604	1	0	f
147	21	16	Chicago Bears	6	2025-09-03 19:13:13.366963	1	0	f
148	21	5	Indianapolis Colts	1	2025-09-03 19:13:13.357112	1	1	f
149	24	1	Philadelphia Eagles	5	2025-09-03 19:17:25.961832	1	0	f
150	24	2	Kansas City Chiefs	6	2025-09-03 19:17:25.962985	1	0	f
151	24	3	Atlanta Falcons	7	2025-09-03 19:17:25.963828	1	0	f
152	24	4	Cincinnati Bengals	1	2025-09-03 19:17:25.964773	1	0	f
153	24	5	Indianapolis Colts	4	2025-09-03 19:17:25.965663	1	4	f
154	24	6	New England Patriots	3	2025-09-03 19:17:25.966563	1	0	f
155	24	7	Arizona Cardinals	8	2025-09-03 19:17:25.967539	1	8	f
156	24	8	New York Jets	9	2025-09-03 19:17:25.96834	1	9	f
157	24	9	Washington Commanders	10	2025-09-03 19:17:25.970552	1	10	f
158	24	10	Jacksonville Jaguars	11	2025-09-03 19:17:25.971549	1	11	f
159	24	11	Tennessee Titans	12	2025-09-03 19:17:25.972449	1	0	f
160	24	12	San Francisco 49ers	16	2025-09-03 19:17:25.973132	1	16	f
161	24	13	Detroit Lions	15	2025-09-03 19:17:25.973991	1	0	f
162	24	14	Houston Texans	13	2025-09-03 19:17:25.974861	1	0	f
163	24	15	Baltimore Ravens	2	2025-09-03 19:17:25.975687	1	2	f
164	24	16	Minnesota Vikings	14	2025-09-03 19:17:25.976575	1	14	f
165	12	1	Dallas Cowboys	5	2025-09-03 23:39:01.05401	1	5	f
166	12	2	Kansas City Chiefs	7	2025-09-03 23:39:01.055141	1	0	f
167	12	3	Tampa Bay Buccaneers	12	2025-09-03 23:39:01.056159	1	12	f
168	12	4	Cleveland Browns	1	2025-09-03 23:39:01.0571	1	1	f
169	12	5	Indianapolis Colts	6	2025-09-03 23:39:01.057841	1	6	f
170	12	6	New England Patriots	10	2025-09-03 23:39:01.058462	1	0	f
171	12	7	Arizona Cardinals	9	2025-09-03 23:39:01.059048	1	9	f
172	12	8	Pittsburgh Steelers	13	2025-09-03 23:39:01.059651	1	0	f
173	12	9	Washington Commanders	14	2025-09-03 23:39:01.06027	1	14	f
174	12	10	Jacksonville Jaguars	2	2025-09-03 23:39:01.060962	1	2	f
175	12	11	Denver Broncos	16	2025-09-03 23:39:01.061571	1	16	f
176	12	12	San Francisco 49ers	8	2025-09-03 23:39:01.062185	1	8	f
177	12	13	Green Bay Packers	11	2025-09-03 23:39:01.062787	1	11	f
178	12	14	Los Angeles Rams	3	2025-09-03 23:39:01.063346	1	3	f
179	12	15	Baltimore Ravens	4	2025-09-03 23:39:01.063952	1	4	f
180	12	16	Minnesota Vikings	15	2025-09-03 23:39:01.064546	1	15	f
181	15	1	Philadelphia Eagles	7	2025-09-03 23:57:35.727678	1	0	f
182	15	2	Los Angeles Chargers	4	2025-09-03 23:57:35.728784	1	4	f
183	5	1	Philadelphia Eagles	2	2025-09-04 00:44:04.411394	1	0	f
184	5	2	Kansas City Chiefs	15	2025-09-04 00:44:04.412513	1	0	f
185	5	3	Tampa Bay Buccaneers	14	2025-09-04 00:44:04.41314	1	14	f
186	5	4	Cincinnati Bengals	4	2025-09-04 00:44:04.413809	1	0	f
187	5	5	Indianapolis Colts	16	2025-09-04 00:44:04.414378	1	16	f
188	5	6	Las Vegas Raiders	11	2025-09-04 00:44:04.414976	1	11	f
189	5	7	Arizona Cardinals	5	2025-09-04 00:44:04.415616	1	5	f
190	5	8	Pittsburgh Steelers	8	2025-09-04 00:44:04.416187	1	0	f
191	5	9	Washington Commanders	3	2025-09-04 00:44:04.416917	1	3	f
192	5	10	Jacksonville Jaguars	9	2025-09-04 00:44:04.417703	1	9	f
193	5	11	Denver Broncos	10	2025-09-04 00:44:04.418393	1	10	f
194	5	12	San Francisco 49ers	7	2025-09-04 00:44:04.419141	1	7	f
195	5	13	Detroit Lions	6	2025-09-04 00:44:04.419838	1	0	f
196	5	14	Los Angeles Rams	13	2025-09-04 00:44:04.420499	1	13	f
197	5	15	Baltimore Ravens	1	2025-09-04 00:44:04.421159	1	1	f
198	5	16	Minnesota Vikings	12	2025-09-04 00:44:04.421814	1	12	f
199	4	1	Philadelphia Eagles	10	2025-09-04 00:57:37.631074	1	0	f
200	4	2	Los Angeles Chargers	7	2025-09-04 00:57:37.632335	1	7	f
201	4	3	Tampa Bay Buccaneers	6	2025-09-04 00:57:37.633559	1	6	f
202	4	4	Cincinnati Bengals	15	2025-09-04 00:57:37.634522	1	0	f
203	4	5	Indianapolis Colts	2	2025-09-04 00:57:37.635318	1	2	f
204	4	6	Las Vegas Raiders	4	2025-09-04 00:57:37.636136	1	4	f
205	4	7	Arizona Cardinals	9	2025-09-04 00:57:37.636986	1	9	f
206	4	8	Pittsburgh Steelers	11	2025-09-04 00:57:37.637875	1	0	f
207	4	9	Washington Commanders	12	2025-09-04 00:57:37.638682	1	12	f
208	4	10	Jacksonville Jaguars	13	2025-09-04 00:57:37.63953	1	13	f
209	4	11	Denver Broncos	16	2025-09-04 00:57:37.640377	1	16	f
210	4	12	San Francisco 49ers	8	2025-09-04 00:57:37.641578	1	8	f
211	4	13	Detroit Lions	5	2025-09-04 00:57:37.642383	1	0	f
212	4	14	Houston Texans	14	2025-09-04 00:57:37.643197	1	0	f
213	4	15	Buffalo Bills	3	2025-09-04 00:57:37.64403	1	0	f
214	4	16	Minnesota Vikings	1	2025-09-04 00:57:37.644843	1	1	f
215	8	1	Dallas Cowboys	8	2025-09-04 03:46:47.180322	1	8	f
216	8	2	Kansas City Chiefs	11	2025-09-04 03:46:47.181614	1	0	f
217	8	3	Tampa Bay Buccaneers	10	2025-09-04 03:46:47.182538	1	10	f
218	8	4	Cleveland Browns	14	2025-09-04 03:46:47.183451	1	14	f
219	8	5	Miami Dolphins	13	2025-09-04 03:46:47.184327	1	0	f
220	8	6	New England Patriots	16	2025-09-04 03:46:47.185235	1	0	f
221	8	7	Arizona Cardinals	9	2025-09-04 03:46:47.186145	1	9	f
222	8	8	Pittsburgh Steelers	7	2025-09-04 03:46:47.187038	1	0	f
223	8	9	Washington Commanders	15	2025-09-04 03:46:47.187931	1	15	f
224	8	10	Carolina Panthers	5	2025-09-04 03:46:47.188831	1	0	f
225	8	11	Denver Broncos	12	2025-09-04 03:46:47.18964	1	12	f
226	8	12	San Francisco 49ers	2	2025-09-04 03:46:47.190233	1	2	f
227	8	13	Detroit Lions	3	2025-09-04 03:46:47.190877	1	0	f
228	8	14	Houston Texans	6	2025-09-04 03:46:47.191485	1	0	f
229	8	15	Buffalo Bills	1	2025-09-04 03:46:47.192057	1	0	f
230	8	16	Minnesota Vikings	4	2025-09-04 03:46:47.19266	1	4	f
231	18	1	Dallas Cowboys	8	2025-09-04 05:22:47.68825	1	8	f
232	18	2	Kansas City Chiefs	2	2025-09-04 05:22:47.68952	1	0	f
233	18	3	Tampa Bay Buccaneers	13	2025-09-04 05:22:47.690443	1	13	f
234	18	4	Cleveland Browns	3	2025-09-04 05:22:47.691256	1	3	f
235	18	5	Miami Dolphins	14	2025-09-04 05:22:47.69211	1	0	f
236	18	6	Las Vegas Raiders	15	2025-09-04 05:22:47.692998	1	15	f
237	18	7	Arizona Cardinals	12	2025-09-04 05:22:47.693899	1	12	f
238	18	8	Pittsburgh Steelers	10	2025-09-04 05:22:47.694793	1	0	f
239	18	10	Jacksonville Jaguars	7	2025-09-04 05:22:47.696628	1	7	f
240	18	11	Denver Broncos	16	2025-09-04 05:22:47.697533	1	16	f
241	18	12	San Francisco 49ers	5	2025-09-04 05:22:47.698442	1	5	f
242	18	13	Green Bay Packers	4	2025-09-04 05:22:47.699713	1	4	f
243	18	14	Houston Texans	6	2025-09-04 05:22:47.70062	1	0	f
244	18	15	Buffalo Bills	11	2025-09-04 05:22:47.701612	1	0	f
245	18	16	Minnesota Vikings	9	2025-09-04 05:22:47.702498	1	9	f
246	18	9	New York Giants	1	2025-09-04 05:22:47.695643	1	0	f
247	19	1	Philadelphia Eagles	16	2025-09-04 16:58:03.417857	1	0	f
248	17	3	Tampa Bay Buccaneers	14	2025-09-07 15:09:05.217569	1	14	f
249	20	1	Dallas Cowboys	8	2025-09-04 23:16:29.695014	1	8	f
250	20	2	Los Angeles Chargers	5	2025-09-05 17:01:41.790432	1	5	f
251	20	3	Tampa Bay Buccaneers	1	2025-09-06 20:05:12.646435	1	1	f
252	20	4	Cleveland Browns	16	2025-09-06 20:05:12.64761	1	16	f
253	20	5	Miami Dolphins	3	2025-09-06 20:05:12.648453	1	0	f
254	20	6	Las Vegas Raiders	6	2025-09-06 20:05:12.64923	1	6	f
255	20	7	Arizona Cardinals	7	2025-09-06 20:05:12.650007	1	7	f
256	20	8	Pittsburgh Steelers	10	2025-09-06 20:05:12.650769	1	0	f
257	20	9	Washington Commanders	11	2025-09-06 20:05:12.651512	1	11	f
258	20	10	Carolina Panthers	2	2025-09-06 20:05:12.65222	1	0	f
259	20	11	Denver Broncos	15	2025-09-06 20:05:12.652945	1	15	f
260	20	12	San Francisco 49ers	13	2025-09-06 20:05:12.653689	1	13	f
261	20	13	Detroit Lions	12	2025-09-06 20:05:12.654398	1	0	f
262	20	14	Los Angeles Rams	14	2025-09-06 20:05:12.655886	1	14	f
263	20	15	Baltimore Ravens	4	2025-09-06 20:05:12.656663	1	4	f
264	20	16	Minnesota Vikings	9	2025-09-06 20:05:12.657386	1	9	f
265	19	2	Kansas City Chiefs	5	2025-09-05 19:20:36.790102	1	0	f
266	10	2	Los Angeles Chargers	11	2025-09-05 22:18:24.973372	1	11	f
267	10	3	Tampa Bay Buccaneers	14	2025-09-06 15:02:26.200383	1	14	f
268	10	4	Cleveland Browns	6	2025-09-06 15:02:26.201607	1	6	f
269	10	5	Miami Dolphins	10	2025-09-06 15:02:26.202475	1	0	f
270	10	6	New England Patriots	5	2025-09-06 15:02:26.203245	1	0	f
271	10	7	Arizona Cardinals	9	2025-09-06 15:02:26.204046	1	9	f
272	10	8	Pittsburgh Steelers	13	2025-09-06 15:02:26.204795	1	0	f
273	10	9	Washington Commanders	15	2025-09-06 15:02:26.205539	1	15	f
274	10	10	Carolina Panthers	4	2025-09-06 15:02:26.206243	1	0	f
275	10	11	Denver Broncos	16	2025-09-06 15:02:26.20697	1	16	f
276	10	12	Seattle Seahawks	2	2025-09-06 15:02:26.207762	1	0	f
277	10	13	Green Bay Packers	3	2025-09-06 15:02:26.208536	1	3	f
278	10	14	Houston Texans	12	2025-09-06 15:02:26.209238	1	0	f
279	10	15	Buffalo Bills	1	2025-09-06 15:02:26.209963	1	0	f
280	10	16	Chicago Bears	8	2025-09-08 23:43:36.295279	1	0	f
281	15	3	Atlanta Falcons	5	2025-09-06 23:38:24.546656	1	0	f
282	15	4	Cincinnati Bengals	10	2025-09-06 23:38:24.547632	1	0	f
283	15	5	Miami Dolphins	13	2025-09-06 23:38:24.548524	1	0	f
284	15	6	Las Vegas Raiders	11	2025-09-06 23:38:24.549366	1	11	f
285	15	7	Arizona Cardinals	1	2025-09-06 23:38:24.550245	1	1	f
286	15	8	Pittsburgh Steelers	12	2025-09-06 23:38:24.551063	1	0	f
287	15	9	Washington Commanders	15	2025-09-06 23:38:24.55188	1	15	f
288	15	10	Jacksonville Jaguars	14	2025-09-06 23:38:24.552661	1	14	f
289	15	11	Denver Broncos	16	2025-09-06 23:38:24.553469	1	16	f
290	15	12	San Francisco 49ers	9	2025-09-06 23:38:24.554218	1	9	f
291	15	13	Detroit Lions	8	2025-09-06 23:38:24.555012	1	0	f
292	15	14	Houston Texans	3	2025-09-06 23:38:24.555792	1	0	f
293	15	15	Buffalo Bills	2	2025-09-06 23:38:24.556579	1	0	f
294	15	16	Minnesota Vikings	6	2025-09-06 23:38:24.557188	1	6	f
295	17	4	Cincinnati Bengals	15	2025-09-07 15:09:05.21959	1	0	f
296	17	5	Miami Dolphins	13	2025-09-07 15:09:05.220667	1	0	f
297	17	6	Las Vegas Raiders	9	2025-09-07 15:09:05.221663	1	9	f
298	17	7	Arizona Cardinals	12	2025-09-07 15:09:05.222595	1	12	f
299	17	8	Pittsburgh Steelers	7	2025-09-07 15:09:05.223508	1	0	f
300	17	9	New York Giants	10	2025-09-07 15:09:05.224383	1	0	f
301	17	11	Denver Broncos	16	2025-09-07 15:09:05.226212	1	16	f
302	17	12	Seattle Seahawks	4	2025-09-07 15:09:05.227111	1	0	f
303	17	13	Detroit Lions	8	2025-09-07 15:09:05.227996	1	0	f
304	17	14	Houston Texans	6	2025-09-07 15:09:05.228852	1	0	f
305	17	15	Baltimore Ravens	3	2025-09-07 15:09:05.23287	1	3	f
306	17	16	Chicago Bears	11	2025-09-07 15:09:05.233676	1	0	f
307	19	3	Tampa Bay Buccaneers	14	2025-09-07 15:16:59.588177	1	14	f
308	19	4	Cincinnati Bengals	11	2025-09-07 15:16:59.589363	1	0	f
309	19	5	Miami Dolphins	7	2025-09-07 15:16:59.590303	1	0	f
310	19	6	Las Vegas Raiders	8	2025-09-07 15:16:59.591234	1	8	f
311	19	7	Arizona Cardinals	13	2025-09-07 15:16:59.592175	1	13	f
312	19	8	Pittsburgh Steelers	2	2025-09-07 15:16:59.593114	1	0	f
313	19	9	Washington Commanders	12	2025-09-07 15:16:59.594031	1	12	f
314	19	10	Jacksonville Jaguars	9	2025-09-07 15:16:59.594948	1	9	f
315	19	11	Denver Broncos	6	2025-09-07 15:16:59.595864	1	6	f
316	19	12	Seattle Seahawks	1	2025-09-07 15:16:59.596789	1	0	f
317	19	13	Detroit Lions	10	2025-09-07 15:16:59.597812	1	0	f
318	19	14	Los Angeles Rams	4	2025-09-07 15:16:59.59875	1	4	f
319	19	15	Buffalo Bills	3	2025-09-07 15:16:59.59967	1	0	f
320	19	16	Minnesota Vikings	15	2025-09-07 15:16:59.600333	1	15	f
321	25	3	Atlanta Falcons	9	2025-09-07 15:36:42.289728	1	0	f
322	25	4	Cleveland Browns	6	2025-09-07 15:36:42.290995	1	6	f
323	25	5	Indianapolis Colts	8	2025-09-07 15:36:42.291944	1	8	f
324	25	6	Las Vegas Raiders	7	2025-09-07 15:36:42.292797	1	7	f
325	25	7	New Orleans Saints	5	2025-09-07 15:36:42.293609	1	0	f
326	25	8	Pittsburgh Steelers	12	2025-09-07 15:36:42.294373	1	0	f
327	25	9	Washington Commanders	10	2025-09-07 15:36:42.295135	1	10	f
328	25	10	Carolina Panthers	11	2025-09-07 15:36:42.295892	1	0	f
329	25	11	Denver Broncos	4	2025-09-07 15:36:42.296635	1	4	f
330	25	12	San Francisco 49ers	3	2025-09-07 15:36:42.297367	1	3	f
331	25	13	Detroit Lions	13	2025-09-07 15:36:42.298108	1	0	f
332	25	14	Los Angeles Rams	2	2025-09-07 15:36:42.29885	1	2	f
333	25	15	Baltimore Ravens	1	2025-09-07 15:36:42.299599	1	1	f
334	25	16	Minnesota Vikings	14	2025-09-07 15:36:42.300316	1	14	f
335	2	17	Green Bay Packers	2	2025-09-09 15:15:03.452153	2	2	f
336	2	18	Jacksonville Jaguars	1	2025-09-12 21:31:57.681019	2	0	f
337	2	19	Dallas Cowboys	11	2025-09-12 21:31:57.682378	2	0	f
338	2	20	Chicago Bears	4	2025-09-12 21:31:57.683351	2	0	f
339	2	21	Tennessee Titans	6	2025-09-12 21:31:57.684227	2	0	f
340	2	22	Miami Dolphins	14	2025-09-12 21:31:57.685089	2	0	f
341	2	23	New Orleans Saints	7	2025-09-12 21:31:57.685942	2	0	f
342	2	24	Buffalo Bills	9	2025-09-12 21:31:57.687359	2	9	f
343	2	25	Pittsburgh Steelers	10	2025-09-12 21:31:57.688205	2	0	f
344	2	26	Cleveland Browns	3	2025-09-12 21:31:57.689074	2	0	f
345	2	27	Denver Broncos	16	2025-09-12 21:31:57.689833	2	0	f
346	2	28	Arizona Cardinals	5	2025-09-12 21:31:57.690604	2	0	f
347	2	29	Kansas City Chiefs	8	2025-09-12 21:31:57.691418	2	0	f
348	2	30	Minnesota Vikings	12	2025-09-12 21:31:57.69221	2	0	f
349	2	31	Houston Texans	15	2025-09-12 21:31:57.69319	2	0	f
350	2	32	Los Angeles Chargers	13	2025-09-12 21:31:57.695412	2	13	f
351	1	17	Washington Commanders	5	2025-09-09 15:06:33.117956	2	0	f
352	1	18	Cincinnati Bengals	6	2025-09-09 15:06:33.119136	2	6	f
353	1	19	Dallas Cowboys	7	2025-09-09 15:06:33.120059	2	0	f
354	1	20	Detroit Lions	8	2025-09-09 15:06:33.120825	2	8	f
355	1	21	Los Angeles Rams	9	2025-09-09 15:06:33.121536	2	9	f
356	1	22	New England Patriots	10	2025-09-09 15:06:33.12216	2	10	f
357	1	23	San Francisco 49ers	11	2025-09-09 15:06:33.122777	2	11	f
358	1	24	Buffalo Bills	4	2025-09-09 15:06:33.12346	2	4	f
359	1	25	Pittsburgh Steelers	12	2025-09-09 15:06:33.12421	2	0	f
360	1	26	Baltimore Ravens	13	2025-09-09 15:06:33.124929	2	13	f
361	1	27	Denver Broncos	16	2025-09-09 15:06:33.125613	2	0	f
362	1	28	Arizona Cardinals	15	2025-09-09 15:06:33.126467	2	0	f
363	1	29	Kansas City Chiefs	14	2025-09-09 15:06:33.127286	2	0	f
364	1	30	Minnesota Vikings	3	2025-09-09 15:06:33.128127	2	0	f
365	1	31	Tampa Bay Buccaneers	2	2025-09-15 17:05:59.062209	2	2	f
366	1	32	Los Angeles Chargers	1	2025-09-15 17:05:59.063144	2	1	f
367	13	17	Washington Commanders	4	2025-09-10 14:18:37.199835	2	0	f
368	13	18	Jacksonville Jaguars	2	2025-09-12 22:50:58.904518	2	0	f
369	13	19	Dallas Cowboys	11	2025-09-12 22:50:58.905658	2	0	f
370	13	20	Detroit Lions	10	2025-09-12 22:50:58.906489	2	10	f
371	13	21	Tennessee Titans	5	2025-09-12 22:50:58.907247	2	0	f
372	13	22	New England Patriots	12	2025-09-12 22:50:58.907962	2	12	f
373	13	23	New Orleans Saints	3	2025-09-12 22:50:58.908708	2	0	f
374	13	24	New York Jets	7	2025-09-12 22:50:58.909447	2	0	f
375	13	25	Pittsburgh Steelers	14	2025-09-12 22:50:58.910178	2	0	f
376	13	26	Cleveland Browns	8	2025-09-12 22:50:58.910872	2	0	f
377	13	27	Denver Broncos	16	2025-09-12 22:50:58.911585	2	0	f
378	13	28	Carolina Panthers	6	2025-09-12 22:50:58.912306	2	6	f
379	13	29	Philadelphia Eagles	1	2025-09-12 22:50:58.912998	2	1	f
380	13	30	Minnesota Vikings	9	2025-09-12 22:50:58.913717	2	0	f
381	13	31	Tampa Bay Buccaneers	15	2025-09-12 22:50:58.914454	2	15	f
382	13	32	Las Vegas Raiders	13	2025-09-12 22:50:58.915161	2	0	f
383	14	17	Green Bay Packers	11	2025-09-10 11:28:26.440566	2	11	f
384	14	18	Jacksonville Jaguars	8	2025-09-10 11:28:26.441656	2	0	f
385	14	19	Dallas Cowboys	12	2025-09-10 11:28:26.442367	2	0	f
386	14	20	Detroit Lions	5	2025-09-10 11:28:26.443059	2	5	f
387	14	21	Los Angeles Rams	6	2025-09-10 11:28:26.443684	2	6	f
388	14	22	New England Patriots	13	2025-09-10 11:28:26.444282	2	13	f
389	14	23	San Francisco 49ers	9	2025-09-10 11:28:26.444876	2	9	f
390	14	24	New York Jets	7	2025-09-10 11:28:26.445461	2	0	f
391	14	25	Pittsburgh Steelers	10	2025-09-10 11:28:26.446017	2	0	f
392	14	26	Baltimore Ravens	15	2025-09-10 11:28:26.446632	2	15	f
393	14	27	Denver Broncos	4	2025-09-10 11:28:26.447201	2	0	f
394	14	28	Arizona Cardinals	16	2025-09-10 11:28:26.447798	2	0	f
395	14	29	Philadelphia Eagles	1	2025-09-10 11:28:26.448363	2	1	f
396	14	30	Minnesota Vikings	3	2025-09-10 11:28:26.448985	2	0	f
397	14	31	Tampa Bay Buccaneers	2	2025-09-10 11:28:26.449565	2	2	f
398	14	32	Los Angeles Chargers	14	2025-09-10 11:28:26.450117	2	14	f
399	12	17	Green Bay Packers	10	2025-09-11 16:53:04.237469	2	10	f
400	12	18	Cincinnati Bengals	8	2025-09-14 16:23:41.81674	2	8	f
401	12	19	Dallas Cowboys	14	2025-09-14 16:23:41.817768	2	0	f
402	12	20	Detroit Lions	15	2025-09-14 16:23:41.818453	2	15	f
403	12	21	Los Angeles Rams	11	2025-09-14 16:23:41.819101	2	11	f
404	12	22	New England Patriots	4	2025-09-14 16:23:41.819707	2	4	f
405	12	23	San Francisco 49ers	6	2025-09-14 16:23:41.820342	2	6	f
406	12	24	New York Jets	1	2025-09-14 16:23:41.820916	2	0	f
407	12	25	Pittsburgh Steelers	13	2025-09-14 16:23:41.82172	2	0	f
408	12	26	Cleveland Browns	5	2025-09-14 16:23:41.822466	2	0	f
409	12	27	Denver Broncos	16	2025-09-14 16:23:41.823095	2	0	f
410	12	28	Carolina Panthers	12	2025-09-14 16:23:41.823682	2	12	f
411	12	29	Kansas City Chiefs	7	2025-09-14 16:23:41.82429	2	0	f
412	12	30	Minnesota Vikings	3	2025-09-14 16:23:41.824883	2	0	f
413	12	31	Tampa Bay Buccaneers	9	2025-09-14 16:23:41.825567	2	9	f
414	12	32	Los Angeles Chargers	2	2025-09-14 16:23:41.826206	2	2	f
415	20	19	Dallas Cowboys	16	2025-09-12 04:06:24.183556	2	0	f
416	20	20	Detroit Lions	15	2025-09-12 04:06:24.184236	2	15	f
417	20	27	Denver Broncos	13	2025-09-12 04:06:24.188806	2	0	f
418	20	29	Philadelphia Eagles	8	2025-09-12 04:06:24.190068	2	8	f
419	10	17	Green Bay Packers	12	2025-09-10 02:42:14.529124	2	12	f
420	10	18	Cincinnati Bengals	11	2025-09-10 02:42:14.530192	2	11	f
421	10	19	Dallas Cowboys	13	2025-09-10 02:42:14.530973	2	0	f
422	10	20	Detroit Lions	10	2025-09-10 02:42:14.531705	2	10	f
423	10	21	Tennessee Titans	1	2025-09-10 02:42:14.532384	2	0	f
424	10	22	New England Patriots	2	2025-09-10 02:42:14.533113	2	2	f
425	10	23	New Orleans Saints	3	2025-09-10 02:42:14.533804	2	0	f
426	10	24	New York Jets	4	2025-09-10 02:42:14.53445	2	0	f
427	10	25	Pittsburgh Steelers	14	2025-09-10 02:42:14.535083	2	0	f
428	10	26	Cleveland Browns	15	2025-09-10 02:42:14.53576	2	0	f
429	10	27	Denver Broncos	16	2025-09-10 02:42:14.536445	2	0	f
430	10	28	Arizona Cardinals	5	2025-09-10 02:42:14.537119	2	0	f
431	10	29	Philadelphia Eagles	6	2025-09-10 02:42:14.538022	2	6	f
432	10	30	Atlanta Falcons	7	2025-09-10 02:42:14.538735	2	7	f
433	10	31	Tampa Bay Buccaneers	8	2025-09-10 02:42:14.53934	2	8	f
434	10	32	Los Angeles Chargers	9	2025-09-10 02:42:14.539822	2	9	f
435	9	17	Green Bay Packers	4	2025-09-10 14:58:45.156375	2	4	f
436	9	18	Cincinnati Bengals	7	2025-09-10 14:58:45.157282	2	7	f
437	9	19	Dallas Cowboys	3	2025-09-10 14:58:45.157937	2	0	f
438	9	20	Detroit Lions	9	2025-09-10 14:58:45.158583	2	9	f
439	9	21	Tennessee Titans	5	2025-09-10 14:58:45.159191	2	0	f
440	9	22	New England Patriots	2	2025-09-10 14:58:45.159839	2	2	f
441	9	23	San Francisco 49ers	12	2025-09-10 14:58:45.160485	2	12	f
442	9	24	New York Jets	15	2025-09-10 14:58:45.161112	2	0	f
443	9	25	Pittsburgh Steelers	8	2025-09-10 14:58:45.161851	2	0	f
444	9	26	Cleveland Browns	13	2025-09-10 14:58:45.162493	2	0	f
445	9	27	Denver Broncos	6	2025-09-10 14:58:45.163093	2	0	f
446	9	28	Arizona Cardinals	16	2025-09-10 14:58:45.163735	2	0	f
447	9	29	Philadelphia Eagles	1	2025-09-10 14:58:45.164343	2	1	f
448	9	30	Atlanta Falcons	10	2025-09-10 14:58:45.16497	2	10	f
449	9	31	Tampa Bay Buccaneers	11	2025-09-10 14:58:45.165592	2	11	f
450	9	32	Los Angeles Chargers	14	2025-09-10 14:58:45.16604	2	14	f
451	21	17	Washington Commanders	1	2025-09-10 15:48:38.978918	2	0	f
452	21	18	Cincinnati Bengals	14	2025-09-10 15:48:38.980227	2	14	f
453	21	19	Dallas Cowboys	13	2025-09-10 15:48:38.981693	2	0	f
454	21	20	Detroit Lions	12	2025-09-10 15:48:38.983354	2	12	f
455	21	21	Tennessee Titans	6	2025-09-10 15:48:38.984678	2	0	f
456	21	22	New England Patriots	7	2025-09-10 15:48:38.986115	2	7	f
457	21	23	San Francisco 49ers	11	2025-09-10 15:48:38.987141	2	11	f
458	21	24	Buffalo Bills	5	2025-09-10 15:48:38.988534	2	5	f
459	21	25	Pittsburgh Steelers	16	2025-09-10 15:48:38.989342	2	0	f
460	21	26	Cleveland Browns	4	2025-09-10 15:48:38.990627	2	0	f
461	21	27	Denver Broncos	10	2025-09-10 15:48:38.9914	2	0	f
462	21	28	Arizona Cardinals	15	2025-09-10 15:48:38.992214	2	0	f
463	21	29	Philadelphia Eagles	3	2025-09-10 15:48:38.993032	2	3	f
464	21	30	Atlanta Falcons	2	2025-09-10 15:48:38.993879	2	2	f
465	21	31	Tampa Bay Buccaneers	9	2025-09-10 15:48:38.99603	2	9	f
466	21	32	Los Angeles Chargers	8	2025-09-10 15:48:38.998244	2	8	f
467	8	17	Green Bay Packers	7	2025-09-11 00:20:47.159305	2	7	f
468	8	18	Cincinnati Bengals	2	2025-09-11 00:20:47.160503	2	2	f
469	8	19	Dallas Cowboys	6	2025-09-11 00:20:47.161588	2	0	f
470	8	20	Detroit Lions	8	2025-09-11 00:20:47.162506	2	8	f
471	8	21	Los Angeles Rams	16	2025-09-11 00:20:47.163297	2	16	f
472	8	22	New England Patriots	10	2025-09-11 00:20:47.164119	2	10	f
473	8	23	San Francisco 49ers	13	2025-09-11 00:20:47.164911	2	13	f
474	8	24	Buffalo Bills	3	2025-09-11 00:20:47.165704	2	3	f
475	8	25	Pittsburgh Steelers	4	2025-09-11 00:20:47.166507	2	0	f
476	8	26	Baltimore Ravens	14	2025-09-11 00:20:47.167266	2	14	f
477	8	27	Denver Broncos	12	2025-09-11 00:20:47.168066	2	0	f
478	8	28	Arizona Cardinals	1	2025-09-11 00:20:47.168844	2	0	f
479	8	29	Philadelphia Eagles	5	2025-09-11 00:20:47.169624	2	5	f
480	8	30	Minnesota Vikings	9	2025-09-11 00:20:47.170386	2	0	f
481	8	31	Tampa Bay Buccaneers	15	2025-09-11 00:20:47.171168	2	15	f
482	8	32	Los Angeles Chargers	11	2025-09-11 00:20:47.171958	2	11	f
483	22	17	Washington Commanders	3	2025-09-11 01:57:09.239681	2	0	f
484	22	18	Jacksonville Jaguars	2	2025-09-11 01:57:09.240966	2	0	f
485	22	19	Dallas Cowboys	4	2025-09-11 01:57:09.241933	2	0	f
486	22	20	Detroit Lions	12	2025-09-11 01:57:09.242824	2	12	f
487	22	21	Los Angeles Rams	10	2025-09-11 01:57:09.243674	2	10	f
488	22	22	New England Patriots	5	2025-09-11 01:57:09.244526	2	5	f
489	22	23	San Francisco 49ers	15	2025-09-11 01:57:09.245182	2	15	f
490	22	24	Buffalo Bills	16	2025-09-11 01:57:09.245883	2	16	f
491	22	25	Pittsburgh Steelers	14	2025-09-11 01:57:09.246669	2	0	f
492	22	26	Baltimore Ravens	13	2025-09-11 01:57:09.247467	2	13	f
493	22	27	Denver Broncos	11	2025-09-11 01:57:09.24824	2	0	f
494	22	28	Carolina Panthers	1	2025-09-11 01:57:09.249034	2	1	f
495	22	29	Kansas City Chiefs	6	2025-09-11 01:57:09.249806	2	0	f
496	22	30	Minnesota Vikings	9	2025-09-11 01:57:09.250581	2	0	f
497	22	31	Tampa Bay Buccaneers	8	2025-09-11 01:57:09.25129	2	8	f
498	22	32	Los Angeles Chargers	7	2025-09-11 01:57:09.251961	2	7	f
499	18	17	Green Bay Packers	10	2025-09-11 15:40:13.705614	2	10	f
500	18	18	Cincinnati Bengals	9	2025-09-11 15:40:13.710713	2	9	f
501	18	19	Dallas Cowboys	11	2025-09-11 15:40:13.716499	2	0	f
502	18	20	Chicago Bears	8	2025-09-11 15:40:13.719613	2	0	f
503	18	21	Los Angeles Rams	13	2025-09-11 15:40:13.722081	2	13	f
504	18	22	Miami Dolphins	12	2025-09-11 15:40:13.723081	2	0	f
505	18	23	San Francisco 49ers	7	2025-09-11 15:40:13.723999	2	7	f
506	18	24	New York Jets	6	2025-09-11 15:40:13.728865	2	0	f
507	18	25	Pittsburgh Steelers	14	2025-09-11 15:40:13.72983	2	0	f
508	18	26	Cleveland Browns	3	2025-09-11 15:40:13.730705	2	0	f
509	18	27	Denver Broncos	4	2025-09-11 15:40:13.741346	2	0	f
510	18	28	Arizona Cardinals	15	2025-09-11 15:40:13.749227	2	0	f
511	18	29	Philadelphia Eagles	16	2025-09-11 15:40:13.750672	2	16	f
512	18	30	Atlanta Falcons	5	2025-09-11 15:40:13.751678	2	5	f
513	18	31	Houston Texans	1	2025-09-11 15:40:13.762744	2	0	f
514	18	32	Los Angeles Chargers	2	2025-09-11 15:40:13.763705	2	2	f
515	17	17	Green Bay Packers	1	2025-09-11 17:26:29.300148	2	1	f
516	17	18	Cincinnati Bengals	13	2025-09-14 16:20:29.19699	2	13	f
517	5	17	Green Bay Packers	13	2025-09-11 17:39:20.975827	2	13	f
518	5	18	Jacksonville Jaguars	3	2025-09-11 17:39:20.976977	2	0	f
519	5	19	Dallas Cowboys	7	2025-09-11 17:39:20.97771	2	0	f
520	5	20	Detroit Lions	2	2025-09-11 17:39:20.978438	2	2	f
521	5	21	Tennessee Titans	5	2025-09-11 17:39:20.979098	2	0	f
522	5	22	New England Patriots	9	2025-09-11 17:39:20.979722	2	9	f
523	5	23	San Francisco 49ers	16	2025-09-11 17:39:20.98037	2	16	f
524	5	24	Buffalo Bills	6	2025-09-11 17:39:20.980959	2	6	f
525	5	25	Pittsburgh Steelers	15	2025-09-11 17:39:20.981602	2	0	f
526	5	26	Baltimore Ravens	1	2025-09-11 17:39:20.98229	2	1	f
527	5	27	Indianapolis Colts	10	2025-09-11 17:39:20.982905	2	10	f
528	5	28	Arizona Cardinals	14	2025-09-11 17:39:20.983583	2	0	f
529	5	29	Kansas City Chiefs	4	2025-09-11 17:39:20.984219	2	0	f
530	5	30	Atlanta Falcons	8	2025-09-11 17:39:20.984851	2	8	f
531	5	31	Tampa Bay Buccaneers	11	2025-09-11 17:39:20.985538	2	11	f
532	5	32	Las Vegas Raiders	12	2025-09-11 17:39:20.986008	2	0	f
533	4	17	Washington Commanders	5	2025-09-11 22:43:56.534864	2	0	f
534	4	18	Cincinnati Bengals	7	2025-09-11 22:43:56.535936	2	7	f
535	4	19	Dallas Cowboys	8	2025-09-11 22:43:56.536726	2	0	f
536	4	20	Detroit Lions	10	2025-09-11 22:43:56.537428	2	10	f
537	4	21	Tennessee Titans	2	2025-09-11 22:43:56.53819	2	0	f
538	4	22	Miami Dolphins	12	2025-09-11 22:43:56.53899	2	0	f
539	4	23	San Francisco 49ers	11	2025-09-11 22:43:56.539691	2	11	f
540	4	24	Buffalo Bills	13	2025-09-11 22:43:56.540313	2	13	f
541	4	25	Pittsburgh Steelers	9	2025-09-11 22:43:56.540873	2	0	f
542	4	26	Baltimore Ravens	15	2025-09-11 22:43:56.541478	2	15	f
543	4	27	Denver Broncos	16	2025-09-11 22:43:56.542161	2	0	f
544	4	28	Arizona Cardinals	14	2025-09-11 22:43:56.542812	2	0	f
545	4	29	Philadelphia Eagles	6	2025-09-11 22:43:56.543489	2	6	f
546	4	30	Minnesota Vikings	3	2025-09-11 22:43:56.544193	2	0	f
547	15	17	Washington Commanders	4	2025-09-11 22:29:19.664512	2	0	f
548	4	31	Houston Texans	1	2025-09-11 22:43:56.545568	2	0	f
549	4	32	Los Angeles Chargers	4	2025-09-11 22:43:56.546322	2	4	f
550	19	17	Green Bay Packers	6	2025-09-11 22:52:51.143675	2	6	f
551	19	18	Cincinnati Bengals	8	2025-09-14 15:19:11.643349	2	8	f
552	19	19	Dallas Cowboys	9	2025-09-14 15:19:11.646878	2	0	f
553	19	20	Chicago Bears	14	2025-09-14 15:19:11.647712	2	0	f
554	19	22	New England Patriots	3	2025-09-14 15:19:11.649366	2	3	f
555	19	23	San Francisco 49ers	10	2025-09-14 15:19:11.650071	2	10	f
556	19	24	Buffalo Bills	11	2025-09-14 15:19:11.65074	2	11	f
557	19	25	Seattle Seahawks	1	2025-09-14 15:19:11.651471	2	1	f
558	19	26	Cleveland Browns	12	2025-09-14 15:19:11.6521	2	0	f
559	19	27	Denver Broncos	4	2025-09-14 15:19:11.652998	2	0	f
560	19	28	Arizona Cardinals	13	2025-09-14 15:19:11.653615	2	0	f
561	19	29	Philadelphia Eagles	5	2025-09-14 15:19:11.654268	2	5	f
562	19	30	Atlanta Falcons	7	2025-09-14 15:19:11.654838	2	7	f
563	26	17	Washington Commanders	5	2025-09-11 23:21:48.430633	2	0	f
564	23	17	Washington Commanders	14	2025-09-11 23:35:01.621282	2	0	f
565	23	18	Cincinnati Bengals	10	2025-09-11 23:35:01.622375	2	10	f
566	23	19	Dallas Cowboys	15	2025-09-11 23:35:01.623265	2	0	f
567	23	20	Chicago Bears	5	2025-09-11 23:35:01.624175	2	0	f
568	23	21	Tennessee Titans	7	2025-09-11 23:35:01.625015	2	0	f
569	23	22	Miami Dolphins	6	2025-09-11 23:35:01.625828	2	0	f
570	23	23	San Francisco 49ers	8	2025-09-11 23:35:01.626681	2	8	f
571	23	24	Buffalo Bills	13	2025-09-11 23:35:01.627465	2	13	f
572	23	25	Pittsburgh Steelers	12	2025-09-11 23:35:01.628256	2	0	f
573	23	26	Baltimore Ravens	2	2025-09-11 23:35:01.628982	2	2	f
574	23	27	Denver Broncos	16	2025-09-11 23:35:01.629887	2	0	f
575	23	28	Arizona Cardinals	9	2025-09-11 23:35:01.63063	2	0	f
576	23	29	Philadelphia Eagles	11	2025-09-11 23:35:01.631337	2	11	f
577	23	30	Atlanta Falcons	4	2025-09-11 23:35:01.63195	2	4	f
578	23	31	Tampa Bay Buccaneers	3	2025-09-11 23:35:01.632603	2	3	f
579	23	32	Los Angeles Chargers	1	2025-09-11 23:35:01.633102	2	1	f
580	16	17	Washington Commanders	1	2025-09-11 23:36:37.547443	2	0	f
581	16	18	Cincinnati Bengals	2	2025-09-11 23:36:37.548436	2	2	f
582	16	19	Dallas Cowboys	3	2025-09-11 23:36:37.549151	2	0	f
583	16	20	Detroit Lions	4	2025-09-11 23:36:37.549814	2	4	f
584	16	21	Los Angeles Rams	5	2025-09-11 23:36:37.550487	2	5	f
585	16	22	Miami Dolphins	6	2025-09-11 23:36:37.551146	2	0	f
586	16	23	San Francisco 49ers	7	2025-09-11 23:36:37.551756	2	7	f
587	16	24	Buffalo Bills	8	2025-09-11 23:36:37.552391	2	8	f
588	16	25	Seattle Seahawks	9	2025-09-11 23:36:37.55312	2	9	f
589	16	26	Baltimore Ravens	10	2025-09-11 23:36:37.553791	2	10	f
590	16	27	Denver Broncos	11	2025-09-11 23:36:37.555611	2	0	f
591	16	28	Arizona Cardinals	12	2025-09-11 23:36:37.556424	2	0	f
592	16	29	Philadelphia Eagles	13	2025-09-11 23:36:37.557236	2	13	f
593	16	30	Minnesota Vikings	14	2025-09-11 23:36:37.55799	2	0	f
594	16	31	Houston Texans	15	2025-09-11 23:36:37.558686	2	0	f
595	16	32	Los Angeles Chargers	16	2025-09-11 23:36:37.55919	2	16	f
596	24	18	Cincinnati Bengals	10	2025-09-12 00:21:47.739092	2	10	f
597	24	19	Dallas Cowboys	7	2025-09-12 00:21:47.740471	2	0	f
598	24	20	Detroit Lions	4	2025-09-12 00:21:47.741587	2	4	f
599	24	21	Los Angeles Rams	8	2025-09-12 00:21:47.742659	2	8	f
600	24	22	Miami Dolphins	6	2025-09-12 00:21:47.743668	2	0	f
601	24	23	San Francisco 49ers	14	2025-09-12 00:21:47.74464	2	14	f
602	24	24	Buffalo Bills	5	2025-09-12 00:21:47.745574	2	5	f
603	24	25	Pittsburgh Steelers	3	2025-09-12 00:21:47.746463	2	0	f
604	24	26	Baltimore Ravens	15	2025-09-12 00:21:47.747396	2	15	f
605	24	27	Denver Broncos	9	2025-09-12 00:21:47.748338	2	0	f
606	24	28	Arizona Cardinals	11	2025-09-12 00:21:47.749175	2	0	f
607	24	29	Philadelphia Eagles	2	2025-09-12 00:21:47.750082	2	2	f
608	24	30	Atlanta Falcons	12	2025-09-12 00:21:47.750935	2	12	f
609	24	31	Tampa Bay Buccaneers	1	2025-09-12 00:21:47.751822	2	1	f
610	24	32	Los Angeles Chargers	13	2025-09-12 00:21:47.75252	2	13	f
611	20	18	Jacksonville Jaguars	11	2025-09-12 04:06:24.183015	2	0	f
612	20	21	Los Angeles Rams	4	2025-09-12 04:06:24.185163	2	4	f
613	20	22	Miami Dolphins	1	2025-09-12 04:06:24.185787	2	0	f
614	20	23	San Francisco 49ers	2	2025-09-12 04:06:24.186445	2	2	f
615	20	24	New York Jets	9	2025-09-12 04:06:24.187078	2	0	f
616	20	25	Seattle Seahawks	14	2025-09-12 04:06:24.187782	2	14	f
617	20	26	Cleveland Browns	5	2025-09-12 04:06:24.188487	2	0	f
618	20	28	Arizona Cardinals	7	2025-09-12 04:06:24.189727	2	0	f
619	20	30	Atlanta Falcons	3	2025-09-12 04:06:24.190962	2	3	f
620	20	31	Houston Texans	6	2025-09-12 04:06:24.191587	2	0	f
621	20	32	Los Angeles Chargers	10	2025-09-12 04:06:24.192077	2	10	f
622	15	18	Cincinnati Bengals	10	2025-09-12 22:55:55.082057	2	10	f
623	15	19	Dallas Cowboys	2	2025-09-12 22:55:55.083372	2	0	f
624	15	20	Detroit Lions	13	2025-09-12 22:55:55.085121	2	13	f
625	15	21	Tennessee Titans	3	2025-09-12 22:55:55.086228	2	0	f
626	15	22	New England Patriots	6	2025-09-12 22:55:55.087192	2	6	f
627	15	23	New Orleans Saints	5	2025-09-12 22:55:55.088151	2	0	f
628	15	24	Buffalo Bills	7	2025-09-12 22:55:55.08959	2	7	f
629	15	25	Pittsburgh Steelers	14	2025-09-12 22:55:55.090689	2	0	f
630	15	26	Cleveland Browns	1	2025-09-12 22:55:55.091741	2	0	f
631	15	27	Denver Broncos	16	2025-09-12 22:55:55.092913	2	0	f
632	15	28	Arizona Cardinals	12	2025-09-12 22:55:55.094679	2	0	f
633	15	29	Philadelphia Eagles	8	2025-09-12 22:55:55.095631	2	8	f
634	15	30	Minnesota Vikings	9	2025-09-12 22:55:55.09658	2	0	f
635	15	31	Tampa Bay Buccaneers	11	2025-09-12 22:55:55.097515	2	11	f
636	15	32	Los Angeles Chargers	15	2025-09-12 22:55:55.098246	2	15	f
637	26	18	Cincinnati Bengals	8	2025-09-13 22:07:16.324388	2	8	f
638	26	19	Dallas Cowboys	6	2025-09-13 22:07:16.325783	2	0	f
639	26	20	Detroit Lions	3	2025-09-13 22:07:16.326697	2	3	f
640	26	21	Tennessee Titans	4	2025-09-13 22:07:16.327545	2	0	f
641	26	22	New England Patriots	10	2025-09-13 22:07:16.328553	2	10	f
642	26	23	San Francisco 49ers	12	2025-09-13 22:07:16.329426	2	12	f
643	26	24	Buffalo Bills	13	2025-09-13 22:07:16.330334	2	13	f
644	26	25	Pittsburgh Steelers	14	2025-09-13 22:07:16.331239	2	0	f
645	26	26	Baltimore Ravens	2	2025-09-13 22:07:16.332146	2	2	f
646	26	27	Denver Broncos	11	2025-09-13 22:07:16.332919	2	0	f
647	26	28	Carolina Panthers	1	2025-09-13 22:07:16.333564	2	1	f
648	26	29	Kansas City Chiefs	9	2025-09-13 22:07:16.334215	2	0	f
649	26	30	Minnesota Vikings	7	2025-09-13 22:07:16.334881	2	0	f
650	26	31	Tampa Bay Buccaneers	15	2025-09-13 22:07:16.335767	2	15	f
651	26	32	Los Angeles Chargers	16	2025-09-13 22:07:16.336451	2	16	f
652	17	19	Dallas Cowboys	8	2025-09-14 16:20:29.197947	2	0	f
653	17	20	Detroit Lions	7	2025-09-14 16:20:29.198627	2	7	f
654	17	21	Tennessee Titans	5	2025-09-14 16:20:29.199301	2	0	f
655	17	22	New England Patriots	15	2025-09-14 16:20:29.199934	2	15	f
656	17	23	New Orleans Saints	6	2025-09-14 16:20:29.200619	2	0	f
657	17	24	New York Jets	9	2025-09-14 16:20:29.201224	2	0	f
658	17	25	Pittsburgh Steelers	11	2025-09-14 16:20:29.201789	2	0	f
659	17	26	Cleveland Browns	10	2025-09-14 16:20:29.202388	2	0	f
660	17	27	Denver Broncos	14	2025-09-14 16:20:29.20295	2	0	f
661	17	28	Arizona Cardinals	12	2025-09-14 16:20:29.203555	2	0	f
662	17	29	Philadelphia Eagles	4	2025-09-14 16:20:29.204149	2	4	f
663	17	30	Atlanta Falcons	16	2025-09-14 16:20:29.204743	2	16	f
664	17	31	Tampa Bay Buccaneers	3	2025-09-14 16:20:29.205341	2	3	f
665	17	32	Las Vegas Raiders	2	2025-09-14 16:20:29.205971	2	0	f
666	19	21	Los Angeles Rams	2	2025-09-14 15:19:11.64892	2	2	f
667	19	31	Tampa Bay Buccaneers	15	2025-09-14 15:19:11.655862	2	15	f
668	19	32	Los Angeles Chargers	16	2025-09-14 15:19:11.656531	2	16	f
669	14	33	Buffalo Bills	11	2025-09-18 17:47:46.172707	3	0	f
670	14	34	Green Bay Packers	4	2025-09-19 19:16:33.718991	3	0	f
671	14	35	Indianapolis Colts	5	2025-09-19 19:16:33.720115	3	5	f
672	14	36	Minnesota Vikings	3	2025-09-19 19:16:33.721049	3	3	f
673	14	37	Pittsburgh Steelers	10	2025-09-19 19:16:33.721795	3	10	f
674	14	38	Los Angeles Rams	6	2025-09-19 19:16:33.722534	3	0	f
675	14	39	Tampa Bay Buccaneers	9	2025-09-19 19:16:33.723168	3	0	f
676	14	40	Washington Commanders	12	2025-09-19 19:16:33.72387	3	12	f
677	14	41	Atlanta Falcons	15	2025-09-19 19:16:33.724626	3	0	f
678	14	42	Houston Texans	7	2025-09-19 19:16:33.725391	3	0	f
679	14	43	Los Angeles Chargers	16	2025-09-19 19:16:33.726118	3	16	f
680	14	44	Seattle Seahawks	2	2025-09-19 19:16:33.726899	3	2	f
681	14	45	Dallas Cowboys	13	2025-09-19 19:16:33.727718	3	0	f
682	14	46	San Francisco 49ers	8	2025-09-19 19:16:33.728521	3	0	f
683	14	47	Kansas City Chiefs	14	2025-09-19 19:16:33.729295	3	14	f
684	14	48	Detroit Lions	1	2025-09-19 19:16:33.730104	3	1	f
685	2	33	Buffalo Bills	3	2025-09-16 14:28:46.133202	3	0	f
686	2	34	Cleveland Browns	1	2025-09-16 14:28:46.134424	3	1	f
687	2	35	Indianapolis Colts	6	2025-09-16 14:28:46.135351	3	6	f
688	2	36	Minnesota Vikings	12	2025-09-16 14:28:46.136231	3	12	f
689	2	37	Pittsburgh Steelers	8	2025-09-16 14:28:46.137111	3	8	f
690	2	38	Philadelphia Eagles	7	2025-09-16 14:28:46.137923	3	7	f
691	2	39	New York Jets	2	2025-09-16 14:28:46.138749	3	2	f
692	2	40	Washington Commanders	11	2025-09-16 14:28:46.139556	3	11	f
693	2	41	Atlanta Falcons	14	2025-09-16 14:28:46.140362	3	0	f
694	2	42	Jacksonville Jaguars	5	2025-09-16 14:28:46.141144	3	5	f
695	2	43	Denver Broncos	16	2025-09-16 14:28:46.141902	3	0	f
696	2	44	New Orleans Saints	9	2025-09-16 14:28:46.142697	3	0	f
697	2	45	Chicago Bears	4	2025-09-16 14:28:46.143468	3	4	f
698	2	46	Arizona Cardinals	13	2025-09-16 14:28:46.144245	3	13	f
699	2	47	Kansas City Chiefs	15	2025-09-16 14:28:46.145009	3	15	f
700	2	48	Baltimore Ravens	10	2025-09-16 14:28:46.145611	3	0	f
701	20	33	Buffalo Bills	4	2025-09-16 16:32:45.231439	3	0	f
702	20	34	Green Bay Packers	11	2025-09-16 16:32:45.233066	3	0	f
703	20	35	Tennessee Titans	3	2025-09-16 16:32:45.23785	3	0	f
704	20	36	Minnesota Vikings	10	2025-09-16 16:32:45.239364	3	10	f
705	20	37	Pittsburgh Steelers	9	2025-09-16 16:32:45.240592	3	9	f
706	20	38	Philadelphia Eagles	15	2025-09-16 16:32:45.244533	3	15	f
707	20	39	New York Jets	1	2025-09-16 16:32:45.25445	3	1	f
708	20	40	Washington Commanders	12	2025-09-16 16:32:45.258589	3	12	f
709	20	41	Atlanta Falcons	14	2025-09-16 16:32:45.260171	3	0	f
710	20	42	Houston Texans	2	2025-09-16 16:32:45.261421	3	0	f
711	20	43	Denver Broncos	7	2025-09-16 16:32:45.274173	3	0	f
712	20	44	Seattle Seahawks	5	2025-09-16 16:32:45.280917	3	5	f
713	20	45	Dallas Cowboys	16	2025-09-16 16:32:45.286563	3	0	f
714	20	47	New York Giants	8	2025-09-16 16:32:45.29135	3	0	f
715	20	48	Detroit Lions	13	2025-09-16 16:32:45.294569	3	13	f
716	20	46	San Francisco 49ers	6	2025-09-16 16:32:45.289025	3	0	f
717	1	33	Buffalo Bills	3	2025-09-16 17:02:36.428002	3	0	f
718	1	34	Green Bay Packers	4	2025-09-16 17:02:36.429571	3	0	f
719	1	35	Indianapolis Colts	14	2025-09-16 17:02:36.435607	3	14	f
720	1	36	Minnesota Vikings	6	2025-09-16 17:02:36.437051	3	6	f
721	1	37	New England Patriots	2	2025-09-16 17:02:36.438263	3	0	f
722	1	38	Philadelphia Eagles	7	2025-09-16 17:02:36.439391	3	7	f
723	1	39	Tampa Bay Buccaneers	8	2025-09-16 17:02:36.440479	3	0	f
724	1	40	Washington Commanders	9	2025-09-16 17:02:36.441774	3	9	f
725	1	41	Atlanta Falcons	10	2025-09-16 17:02:36.444611	3	0	f
726	1	42	Houston Texans	11	2025-09-16 17:02:36.445603	3	0	f
727	1	43	Denver Broncos	16	2025-09-16 17:02:36.446491	3	0	f
728	1	44	Seattle Seahawks	1	2025-09-16 17:02:36.447333	3	1	f
729	1	45	Dallas Cowboys	12	2025-09-16 17:02:36.448182	3	0	f
730	1	46	Arizona Cardinals	13	2025-09-16 17:02:36.449011	3	13	f
731	1	47	New York Giants	5	2025-09-16 17:02:36.449885	3	0	f
732	1	48	Detroit Lions	15	2025-09-16 17:02:36.450515	3	15	f
733	12	33	Miami Dolphins	11	2025-09-17 12:21:28.886509	3	11	f
734	12	34	Green Bay Packers	4	2025-09-19 02:56:47.832061	3	0	f
735	12	38	Los Angeles Rams	9	2025-09-19 02:56:47.835627	3	0	f
736	12	43	Denver Broncos	10	2025-09-19 02:56:47.839292	3	0	f
737	12	45	Dallas Cowboys	16	2025-09-19 02:56:47.840745	3	0	f
738	12	46	Arizona Cardinals	15	2025-09-19 02:56:47.841459	3	15	f
739	12	35	Indianapolis Colts	14	2025-09-19 02:56:47.833208	3	14	f
740	12	36	Minnesota Vikings	5	2025-09-19 02:56:47.834081	3	5	f
741	12	37	New England Patriots	3	2025-09-19 02:56:47.834865	3	0	f
742	12	40	Washington Commanders	7	2025-09-19 02:56:47.837118	3	7	f
743	12	41	Atlanta Falcons	1	2025-09-19 02:56:47.837863	3	0	f
744	12	42	Houston Texans	12	2025-09-19 02:56:47.838587	3	0	f
745	12	47	New York Giants	2	2025-09-19 02:56:47.842136	3	0	f
746	12	48	Baltimore Ravens	8	2025-09-19 02:56:47.842854	3	0	f
747	13	33	Miami Dolphins	4	2025-09-17 20:20:50.765408	3	4	f
748	13	34	Green Bay Packers	15	2025-09-17 20:20:50.76685	3	0	f
749	13	35	Indianapolis Colts	7	2025-09-17 20:20:50.767536	3	7	f
750	13	36	Cincinnati Bengals	12	2025-09-17 20:20:50.768203	3	0	f
751	13	37	New England Patriots	9	2025-09-17 20:20:50.768939	3	0	f
752	13	38	Los Angeles Rams	10	2025-09-17 20:20:50.76971	3	0	f
753	13	39	Tampa Bay Buccaneers	2	2025-09-17 20:20:50.770357	3	0	f
754	13	40	Las Vegas Raiders	11	2025-09-17 20:20:50.771034	3	0	f
755	13	41	Atlanta Falcons	13	2025-09-17 20:20:50.771676	3	0	f
756	13	42	Jacksonville Jaguars	14	2025-09-17 20:20:50.772286	3	14	f
757	13	43	Denver Broncos	6	2025-09-17 20:20:50.772932	3	0	f
758	13	44	New Orleans Saints	8	2025-09-17 20:20:50.773566	3	0	f
759	13	45	Dallas Cowboys	16	2025-09-17 20:20:50.774229	3	0	f
760	13	46	Arizona Cardinals	1	2025-09-17 20:20:50.774985	3	1	f
761	13	47	New York Giants	3	2025-09-17 20:20:50.775707	3	0	f
762	13	48	Detroit Lions	5	2025-09-17 20:20:50.776181	3	5	f
763	9	33	Buffalo Bills	1	2025-09-18 01:07:20.929393	3	0	f
764	9	34	Green Bay Packers	16	2025-09-18 01:07:20.930314	3	0	f
765	9	35	Tennessee Titans	4	2025-09-18 01:07:20.931118	3	0	f
766	9	36	Minnesota Vikings	6	2025-09-18 01:07:20.931788	3	6	f
767	9	37	New England Patriots	3	2025-09-18 01:07:20.932552	3	0	f
768	9	38	Philadelphia Eagles	10	2025-09-18 01:07:20.933186	3	10	f
769	9	39	Tampa Bay Buccaneers	15	2025-09-18 01:07:20.933889	3	0	f
770	9	40	Washington Commanders	11	2025-09-18 01:07:20.934753	3	11	f
771	9	41	Atlanta Falcons	12	2025-09-18 01:07:20.935736	3	0	f
772	9	42	Houston Texans	2	2025-09-18 01:07:20.936532	3	0	f
773	9	43	Los Angeles Chargers	13	2025-09-18 01:07:20.937361	3	13	f
774	9	44	Seattle Seahawks	5	2025-09-18 01:07:20.938093	3	5	f
775	9	45	Dallas Cowboys	14	2025-09-18 01:07:20.939012	3	0	f
776	9	46	Arizona Cardinals	9	2025-09-18 01:07:20.939923	3	9	f
777	9	47	New York Giants	8	2025-09-18 01:07:20.940844	3	0	f
778	9	48	Detroit Lions	7	2025-09-18 01:07:20.94206	3	7	f
779	18	33	Buffalo Bills	12	2025-09-18 07:20:32.91144	3	0	f
780	18	34	Green Bay Packers	11	2025-09-18 07:20:32.912431	3	0	f
781	18	35	Indianapolis Colts	13	2025-09-18 07:20:32.913186	3	13	f
782	18	36	Cincinnati Bengals	1	2025-09-18 07:20:32.913989	3	0	f
783	18	37	Pittsburgh Steelers	14	2025-09-18 07:20:32.914745	3	14	f
784	18	38	Philadelphia Eagles	9	2025-09-18 07:20:32.915461	3	9	f
785	18	39	Tampa Bay Buccaneers	10	2025-09-18 07:20:32.916195	3	0	f
786	18	40	Las Vegas Raiders	15	2025-09-18 07:20:32.916929	3	0	f
787	18	41	Atlanta Falcons	8	2025-09-18 07:20:32.917664	3	0	f
788	18	42	Houston Texans	7	2025-09-18 07:20:32.918376	3	0	f
789	18	43	Los Angeles Chargers	16	2025-09-18 07:20:32.919131	3	16	f
790	18	44	Seattle Seahawks	6	2025-09-18 07:20:32.919866	3	6	f
791	18	45	Dallas Cowboys	5	2025-09-18 07:20:32.920628	3	0	f
792	18	46	Arizona Cardinals	4	2025-09-18 07:20:32.921307	3	4	f
793	18	47	Kansas City Chiefs	3	2025-09-18 07:20:32.922125	3	3	f
794	18	48	Detroit Lions	2	2025-09-18 07:20:32.922682	3	2	f
795	8	33	Buffalo Bills	10	2025-09-18 13:46:30.947986	3	0	f
796	21	33	Miami Dolphins	1	2025-09-18 15:43:05.057412	3	1	f
797	21	34	Green Bay Packers	10	2025-09-18 15:43:05.05898	3	0	f
798	21	35	Indianapolis Colts	11	2025-09-18 15:43:05.060217	3	11	f
799	21	36	Cincinnati Bengals	9	2025-09-18 15:43:05.06131	3	0	f
800	21	37	Pittsburgh Steelers	12	2025-09-18 15:43:05.062366	3	12	f
801	21	38	Philadelphia Eagles	13	2025-09-18 15:43:05.063486	3	13	f
802	21	39	Tampa Bay Buccaneers	2	2025-09-18 15:43:05.064512	3	0	f
803	21	40	Las Vegas Raiders	6	2025-09-18 15:43:05.065496	3	0	f
804	21	41	Carolina Panthers	5	2025-09-18 15:43:05.066454	3	5	f
805	21	42	Houston Texans	8	2025-09-18 15:43:05.067415	3	0	f
806	21	43	Los Angeles Chargers	14	2025-09-18 15:43:05.06836	3	14	f
807	21	44	Seattle Seahawks	7	2025-09-18 15:43:05.069282	3	7	f
808	21	45	Dallas Cowboys	15	2025-09-18 15:43:05.0702	3	0	f
809	21	46	San Francisco 49ers	16	2025-09-18 15:43:05.071112	3	0	f
810	21	47	New York Giants	4	2025-09-18 15:43:05.072032	3	0	f
811	21	48	Detroit Lions	3	2025-09-18 15:43:05.072881	3	3	f
812	24	33	Miami Dolphins	1	2025-09-18 16:30:03.382806	3	1	f
813	24	34	Cleveland Browns	2	2025-09-18 16:30:03.384008	3	2	f
814	24	35	Indianapolis Colts	16	2025-09-18 16:30:03.384826	3	16	f
815	24	36	Cincinnati Bengals	5	2025-09-18 16:30:03.3856	3	0	f
816	24	37	New England Patriots	4	2025-09-18 16:30:03.386346	3	0	f
817	24	38	Philadelphia Eagles	10	2025-09-18 16:30:03.387129	3	10	f
818	24	39	Tampa Bay Buccaneers	11	2025-09-18 16:30:03.387946	3	0	f
819	24	40	Washington Commanders	7	2025-09-18 16:30:03.388745	3	7	f
820	24	41	Atlanta Falcons	12	2025-09-18 16:30:03.389507	3	0	f
821	24	42	Houston Texans	6	2025-09-18 16:30:03.390289	3	0	f
822	24	43	Los Angeles Chargers	13	2025-09-18 16:30:03.391119	3	13	f
823	24	44	New Orleans Saints	3	2025-09-18 16:30:03.392109	3	0	f
824	24	45	Dallas Cowboys	8	2025-09-18 16:30:03.392981	3	0	f
825	24	46	San Francisco 49ers	15	2025-09-18 16:30:03.393755	3	0	f
826	24	47	New York Giants	9	2025-09-18 16:30:03.394487	3	0	f
827	24	48	Detroit Lions	14	2025-09-18 16:30:03.395248	3	14	f
828	22	33	Buffalo Bills	9	2025-09-18 19:37:45.85654	3	0	f
829	22	34	Green Bay Packers	11	2025-09-18 19:37:45.857611	3	0	f
830	22	35	Indianapolis Colts	12	2025-09-18 19:37:45.858348	3	12	f
831	22	36	Cincinnati Bengals	6	2025-09-18 19:37:45.858996	3	0	f
832	22	37	Pittsburgh Steelers	4	2025-09-18 19:37:45.859617	3	4	f
833	22	38	Los Angeles Rams	3	2025-09-18 19:37:45.860213	3	0	f
834	22	39	Tampa Bay Buccaneers	16	2025-09-18 19:37:45.860827	3	0	f
835	22	40	Washington Commanders	13	2025-09-18 19:37:45.861411	3	13	f
836	22	41	Atlanta Falcons	15	2025-09-18 19:37:45.862041	3	0	f
837	22	42	Houston Texans	8	2025-09-18 19:37:45.862651	3	0	f
838	22	43	Denver Broncos	10	2025-09-18 19:37:45.863228	3	0	f
839	22	44	Seattle Seahawks	14	2025-09-18 19:37:45.864103	3	14	f
840	22	45	Dallas Cowboys	5	2025-09-18 19:37:45.864809	3	0	f
841	22	46	San Francisco 49ers	2	2025-09-18 19:37:45.865458	3	0	f
842	22	47	Kansas City Chiefs	7	2025-09-18 19:37:45.866114	3	7	f
843	22	48	Baltimore Ravens	1	2025-09-18 19:37:45.866727	3	0	f
844	4	33	Miami Dolphins	5	2025-09-18 19:17:35.592601	3	5	f
845	10	33	Miami Dolphins	5	2025-09-18 19:46:51.018631	3	5	f
846	26	33	Buffalo Bills	7	2025-09-18 20:27:59.948438	3	0	f
847	16	33	Buffalo Bills	1	2025-09-18 21:07:00.535631	3	0	f
848	16	34	Green Bay Packers	2	2025-09-18 21:07:00.536721	3	0	f
849	16	35	Tennessee Titans	8	2025-09-18 21:07:00.537435	3	0	f
850	16	36	Minnesota Vikings	11	2025-09-18 21:07:00.53815	3	11	f
851	16	37	Pittsburgh Steelers	15	2025-09-18 21:07:00.538888	3	15	f
852	16	38	Philadelphia Eagles	10	2025-09-18 21:07:00.539552	3	10	f
853	16	39	New York Jets	4	2025-09-18 21:07:00.540203	3	4	f
854	16	40	Washington Commanders	9	2025-09-18 21:07:00.54084	3	9	f
855	16	41	Carolina Panthers	7	2025-09-18 21:07:00.541451	3	7	f
856	16	42	Jacksonville Jaguars	16	2025-09-18 21:07:00.542105	3	16	f
857	16	43	Denver Broncos	12	2025-09-18 21:07:00.542769	3	0	f
858	16	44	Seattle Seahawks	3	2025-09-18 21:07:00.54349	3	3	f
859	16	45	Dallas Cowboys	14	2025-09-18 21:07:00.544132	3	0	f
860	16	46	San Francisco 49ers	13	2025-09-18 21:07:00.544754	3	0	f
861	16	47	Kansas City Chiefs	5	2025-09-18 21:07:00.545428	3	5	f
862	16	48	Detroit Lions	6	2025-09-18 21:07:00.545933	3	6	f
863	23	33	Buffalo Bills	16	2025-09-18 21:46:11.968499	3	0	f
864	23	34	Green Bay Packers	9	2025-09-18 21:46:11.969475	3	0	f
865	23	35	Indianapolis Colts	14	2025-09-18 21:46:11.970202	3	14	f
866	23	36	Minnesota Vikings	5	2025-09-18 21:46:11.970935	3	5	f
867	23	37	Pittsburgh Steelers	3	2025-09-18 21:46:11.97189	3	3	f
868	23	38	Philadelphia Eagles	13	2025-09-18 21:46:11.972819	3	13	f
869	23	39	Tampa Bay Buccaneers	12	2025-09-18 21:46:11.973756	3	0	f
870	23	40	Las Vegas Raiders	10	2025-09-18 21:46:11.974715	3	0	f
871	23	41	Atlanta Falcons	7	2025-09-18 21:46:11.975635	3	0	f
872	23	42	Jacksonville Jaguars	11	2025-09-18 21:46:11.976535	3	11	f
873	23	43	Denver Broncos	15	2025-09-18 21:46:11.977459	3	0	f
874	23	44	New Orleans Saints	8	2025-09-18 21:46:11.978383	3	0	f
875	23	45	Chicago Bears	6	2025-09-18 21:46:11.979283	3	6	f
876	23	46	San Francisco 49ers	4	2025-09-18 21:46:11.980086	3	0	f
877	23	47	New York Giants	2	2025-09-18 21:46:11.980832	3	0	f
878	23	48	Baltimore Ravens	1	2025-09-18 21:46:11.981334	3	0	f
879	17	33	Buffalo Bills	16	2025-09-18 23:03:24.863451	3	0	f
880	19	33	Buffalo Bills	16	2025-09-18 23:06:20.132838	3	0	f
881	19	34	Cleveland Browns	14	2025-09-21 15:14:12.027403	3	14	f
882	19	35	Indianapolis Colts	13	2025-09-21 15:14:12.028698	3	13	f
883	19	37	New England Patriots	6	2025-09-21 15:14:12.03072	3	0	f
884	19	38	Philadelphia Eagles	5	2025-09-21 15:14:12.032103	3	5	f
885	19	39	Tampa Bay Buccaneers	15	2025-09-21 15:14:12.033034	3	0	f
886	19	41	Atlanta Falcons	11	2025-09-21 15:14:12.034806	3	0	f
887	15	33	Buffalo Bills	5	2025-09-18 23:45:33.000486	3	0	f
888	25	33	Miami Dolphins	10	2025-09-18 23:50:01.82554	3	10	f
889	25	34	Green Bay Packers	11	2025-09-18 23:50:01.826717	3	0	f
890	25	35	Tennessee Titans	2	2025-09-18 23:50:01.827602	3	0	f
891	25	36	Minnesota Vikings	8	2025-09-18 23:50:01.828276	3	8	f
892	25	37	Pittsburgh Steelers	16	2025-09-18 23:50:01.828958	3	16	f
893	25	38	Philadelphia Eagles	5	2025-09-18 23:50:01.829583	3	5	f
894	25	39	Tampa Bay Buccaneers	13	2025-09-18 23:50:01.83017	3	0	f
895	25	40	Las Vegas Raiders	9	2025-09-18 23:50:01.830793	3	0	f
896	25	41	Atlanta Falcons	7	2025-09-18 23:50:01.831398	3	0	f
897	25	42	Houston Texans	1	2025-09-18 23:50:01.831999	3	0	f
898	25	43	Denver Broncos	3	2025-09-18 23:50:01.832622	3	0	f
899	25	44	New Orleans Saints	4	2025-09-18 23:50:01.833227	3	0	f
900	25	45	Dallas Cowboys	12	2025-09-18 23:50:01.833836	3	0	f
901	25	46	San Francisco 49ers	14	2025-09-18 23:50:01.834439	3	0	f
902	25	47	Kansas City Chiefs	15	2025-09-18 23:50:01.835026	3	15	f
903	25	48	Detroit Lions	6	2025-09-18 23:50:01.835623	3	6	f
904	12	39	Tampa Bay Buccaneers	13	2025-09-19 02:56:47.836377	3	0	f
905	12	44	Seattle Seahawks	6	2025-09-19 02:56:47.84002	3	6	f
906	10	34	Green Bay Packers	8	2025-09-21 16:30:03.120612	3	0	f
907	10	35	Indianapolis Colts	15	2025-09-21 16:30:03.121521	3	15	f
908	10	36	Cincinnati Bengals	7	2025-09-21 16:30:03.122165	3	0	f
909	10	37	Pittsburgh Steelers	9	2025-09-21 16:30:03.122833	3	9	f
910	10	38	Los Angeles Rams	6	2025-09-21 16:30:03.123477	3	0	f
911	10	39	Tampa Bay Buccaneers	10	2025-09-21 16:30:03.124147	3	0	f
912	10	40	Las Vegas Raiders	11	2025-09-21 16:30:03.124782	3	0	f
913	10	41	Carolina Panthers	14	2025-09-21 16:30:03.125419	3	14	f
914	10	42	Houston Texans	2	2025-09-21 16:30:03.126008	3	0	f
915	10	43	Denver Broncos	16	2025-09-21 16:30:03.126639	3	0	f
916	10	44	Seattle Seahawks	13	2025-09-21 16:30:03.127314	3	13	f
917	10	45	Dallas Cowboys	1	2025-09-21 16:30:03.128043	3	0	f
918	10	46	Arizona Cardinals	3	2025-09-21 16:30:03.12866	3	3	f
919	10	47	New York Giants	4	2025-09-21 16:30:03.129231	3	0	f
920	10	48	Detroit Lions	12	2025-09-21 16:30:03.129842	3	12	f
921	4	34	Green Bay Packers	6	2025-09-19 17:52:18.965172	3	0	f
922	4	35	Indianapolis Colts	10	2025-09-19 17:52:18.966309	3	10	f
923	4	36	Minnesota Vikings	4	2025-09-19 17:52:18.967177	3	4	f
924	4	37	Pittsburgh Steelers	16	2025-09-19 17:52:18.96801	3	16	f
925	4	38	Philadelphia Eagles	9	2025-09-19 17:52:18.968798	3	9	f
926	4	39	Tampa Bay Buccaneers	8	2025-09-19 17:52:18.969575	3	0	f
927	4	40	Washington Commanders	7	2025-09-19 17:52:18.970347	3	7	f
928	4	41	Atlanta Falcons	11	2025-09-19 17:52:18.971114	3	0	f
929	4	42	Houston Texans	3	2025-09-19 17:52:18.971872	3	0	f
930	4	43	Denver Broncos	12	2025-09-19 17:52:18.972637	3	0	f
931	4	44	Seattle Seahawks	13	2025-09-19 17:52:18.9734	3	13	f
932	4	45	Dallas Cowboys	14	2025-09-19 17:52:18.974131	3	0	f
933	4	46	Arizona Cardinals	15	2025-09-19 17:52:18.974902	3	15	f
934	4	47	Kansas City Chiefs	1	2025-09-19 17:52:18.975693	3	1	f
935	4	48	Detroit Lions	2	2025-09-19 17:52:18.976263	3	2	f
936	5	34	Green Bay Packers	10	2025-09-19 19:16:18.233772	3	0	f
937	5	35	Indianapolis Colts	15	2025-09-19 19:16:18.234801	3	15	f
938	5	36	Cincinnati Bengals	2	2025-09-19 19:16:18.235563	3	0	f
939	5	37	Pittsburgh Steelers	14	2025-09-19 19:16:18.23622	3	14	f
940	5	38	Los Angeles Rams	4	2025-09-19 19:16:18.236875	3	0	f
941	5	39	Tampa Bay Buccaneers	13	2025-09-19 19:16:18.23751	3	0	f
942	5	40	Washington Commanders	12	2025-09-19 19:16:18.238117	3	12	f
943	5	41	Atlanta Falcons	6	2025-09-19 19:16:18.238774	3	0	f
944	5	42	Houston Texans	8	2025-09-19 19:16:18.239415	3	0	f
945	5	43	Los Angeles Chargers	5	2025-09-19 19:16:18.240046	3	5	f
946	5	44	Seattle Seahawks	1	2025-09-19 19:16:18.240685	3	1	f
947	5	45	Dallas Cowboys	3	2025-09-19 19:16:18.241298	3	0	f
948	5	46	San Francisco 49ers	9	2025-09-19 19:16:18.24196	3	0	f
949	5	48	Baltimore Ravens	11	2025-09-19 19:16:18.24429	3	0	f
950	5	47	Kansas City Chiefs	7	2025-09-19 19:16:18.243079	3	7	f
951	8	34	Cleveland Browns	6	2025-09-19 20:27:24.894103	3	6	f
952	8	35	Indianapolis Colts	12	2025-09-19 20:27:24.895119	3	12	f
953	8	36	Cincinnati Bengals	4	2025-09-19 20:27:24.895833	3	0	f
954	8	37	New England Patriots	8	2025-09-19 20:27:24.896491	3	0	f
955	8	38	Los Angeles Rams	5	2025-09-19 20:27:24.897122	3	0	f
956	8	39	Tampa Bay Buccaneers	11	2025-09-19 20:27:24.897748	3	0	f
957	8	40	Las Vegas Raiders	15	2025-09-19 20:27:24.89834	3	0	f
958	8	41	Atlanta Falcons	1	2025-09-19 20:27:24.89897	3	0	f
959	8	42	Jacksonville Jaguars	13	2025-09-19 20:27:24.89959	3	13	f
960	8	43	Denver Broncos	3	2025-09-19 20:27:24.900161	3	0	f
961	8	44	New Orleans Saints	7	2025-09-19 20:27:24.900763	3	0	f
962	8	45	Dallas Cowboys	14	2025-09-19 20:27:24.901396	3	0	f
963	8	46	San Francisco 49ers	9	2025-09-19 20:27:24.901988	3	0	f
964	8	47	New York Giants	2	2025-09-19 20:27:24.902604	3	0	f
965	8	48	Detroit Lions	16	2025-09-19 20:27:24.903225	3	16	f
966	26	34	Green Bay Packers	10	2025-09-21 06:51:17.735223	3	0	f
967	26	35	Indianapolis Colts	8	2025-09-21 06:51:17.736527	3	8	f
968	26	36	Cincinnati Bengals	5	2025-09-21 06:51:17.737473	3	0	f
969	26	37	Pittsburgh Steelers	9	2025-09-21 06:51:17.738408	3	9	f
970	26	38	Philadelphia Eagles	12	2025-09-21 06:51:17.739326	3	12	f
971	26	39	Tampa Bay Buccaneers	16	2025-09-21 06:51:17.740273	3	0	f
972	26	40	Washington Commanders	6	2025-09-21 06:51:17.741201	3	6	f
973	26	41	Atlanta Falcons	11	2025-09-21 06:51:17.742131	3	0	f
974	26	42	Jacksonville Jaguars	3	2025-09-21 06:51:17.743055	3	3	f
975	26	43	Los Angeles Chargers	1	2025-09-21 06:51:17.743994	3	1	f
976	26	45	Dallas Cowboys	14	2025-09-21 06:51:17.74586	3	0	f
977	26	46	San Francisco 49ers	15	2025-09-21 06:51:17.746806	3	0	f
978	26	47	Kansas City Chiefs	13	2025-09-21 06:51:17.747834	3	13	f
979	26	48	Baltimore Ravens	2	2025-09-21 06:51:17.748755	3	0	f
980	26	44	Seattle Seahawks	4	2025-09-21 06:51:17.744923	3	4	f
981	17	34	Green Bay Packers	14	2025-09-21 14:00:12.713326	3	0	f
982	17	35	Indianapolis Colts	13	2025-09-21 14:00:12.714613	3	13	f
983	17	36	Minnesota Vikings	1	2025-09-21 14:00:12.715534	3	1	f
984	17	37	New England Patriots	4	2025-09-21 14:00:12.716328	3	0	f
985	17	38	Philadelphia Eagles	2	2025-09-21 14:00:12.717106	3	2	f
986	17	39	Tampa Bay Buccaneers	9	2025-09-21 14:00:12.717862	3	0	f
987	17	40	Las Vegas Raiders	5	2025-09-21 14:00:12.718638	3	0	f
988	17	41	Atlanta Falcons	10	2025-09-21 14:00:12.719345	3	0	f
989	17	42	Houston Texans	15	2025-09-21 14:00:12.720072	3	0	f
990	17	43	Los Angeles Chargers	12	2025-09-21 14:00:12.720821	3	12	f
991	17	44	Seattle Seahawks	11	2025-09-21 14:00:12.721549	3	11	f
992	17	45	Dallas Cowboys	6	2025-09-21 14:00:12.722259	3	0	f
993	17	46	Arizona Cardinals	7	2025-09-21 14:00:12.722982	3	7	f
994	17	47	New York Giants	3	2025-09-21 14:00:12.723702	3	0	f
995	17	48	Detroit Lions	8	2025-09-21 14:00:12.724422	3	8	f
996	19	36	Cincinnati Bengals	2	2025-09-21 15:14:12.030155	3	0	f
997	19	40	Las Vegas Raiders	7	2025-09-21 15:14:12.034227	3	0	f
998	19	42	Houston Texans	4	2025-09-21 15:14:12.035962	3	0	f
999	19	43	Los Angeles Chargers	12	2025-09-21 15:14:12.036758	3	12	f
1000	19	44	Seattle Seahawks	1	2025-09-21 15:14:12.037525	3	1	f
1001	19	45	Dallas Cowboys	10	2025-09-21 15:14:12.038213	3	0	f
1002	19	46	San Francisco 49ers	9	2025-09-21 15:14:12.038907	3	0	f
1003	19	47	New York Giants	8	2025-09-21 15:14:12.039824	3	0	f
1004	19	48	Detroit Lions	3	2025-09-21 15:14:12.040483	3	3	f
1005	15	34	Green Bay Packers	12	2025-09-21 15:23:59.167273	3	0	f
1006	15	35	Indianapolis Colts	15	2025-09-21 15:23:59.168541	3	15	f
1007	15	36	Cincinnati Bengals	14	2025-09-21 15:23:59.169488	3	0	f
1008	15	37	Pittsburgh Steelers	13	2025-09-21 15:23:59.170475	3	13	f
1009	15	38	Philadelphia Eagles	1	2025-09-21 15:23:59.171307	3	1	f
1010	15	39	Tampa Bay Buccaneers	2	2025-09-21 15:23:59.172191	3	0	f
1011	15	40	Washington Commanders	3	2025-09-21 15:23:59.173008	3	3	f
1012	15	41	Atlanta Falcons	4	2025-09-21 15:23:59.173884	3	0	f
1013	15	42	Houston Texans	6	2025-09-21 15:23:59.174675	3	0	f
1014	15	43	Denver Broncos	16	2025-09-21 15:23:59.175428	3	0	f
1015	15	44	New Orleans Saints	7	2025-09-21 15:23:59.176109	3	0	f
1016	15	45	Dallas Cowboys	10	2025-09-21 15:23:59.176739	3	0	f
1017	15	46	Arizona Cardinals	11	2025-09-21 15:23:59.17733	3	11	f
1018	15	47	Kansas City Chiefs	8	2025-09-21 15:23:59.178249	3	8	f
1019	15	48	Detroit Lions	9	2025-09-21 15:23:59.178949	3	9	f
1020	1	49	Arizona Cardinals	14	2025-09-24 22:07:53.926668	4	0	f
1021	1	50	Minnesota Vikings	10	2025-09-24 22:07:53.928112	4	0	f
1022	1	51	Washington Commanders	13	2025-09-24 22:07:53.929199	4	0	f
1023	1	52	Buffalo Bills	1	2025-09-24 22:07:53.930319	4	0	f
1024	1	53	Detroit Lions	11	2025-09-24 22:07:53.931277	4	11	f
1025	1	54	New England Patriots	8	2025-09-24 22:07:53.932478	4	8	f
1026	1	55	Los Angeles Chargers	7	2025-09-24 22:07:53.933451	4	0	f
1027	1	56	Philadelphia Eagles	15	2025-09-24 22:07:53.934396	4	15	f
1028	1	57	Houston Texans	6	2025-09-24 22:07:53.935279	4	6	f
1029	1	58	Los Angeles Rams	4	2025-09-24 22:07:53.938584	4	4	f
1030	1	59	San Francisco 49ers	3	2025-09-24 22:07:53.939502	4	0	f
1031	1	60	Baltimore Ravens	2	2025-09-24 22:07:53.9404	4	0	f
1032	1	61	Chicago Bears	12	2025-09-24 22:07:53.941243	4	0	f
1033	1	62	Green Bay Packers	9	2025-09-24 22:07:53.942157	4	0	f
1034	1	63	Miami Dolphins	5	2025-09-24 22:07:53.94307	4	5	f
1035	1	64	Denver Broncos	16	2025-09-24 22:07:53.943954	4	16	f
1036	2	49	Arizona Cardinals	3	2025-09-23 14:49:37.780907	4	0	f
1037	2	50	Minnesota Vikings	4	2025-09-23 14:49:37.78187	4	0	f
1038	2	51	Washington Commanders	6	2025-09-23 14:49:37.782591	4	0	f
1039	2	52	Buffalo Bills	2	2025-09-23 14:49:37.78324	4	0	f
1040	2	53	Cleveland Browns	5	2025-09-23 14:49:37.783909	4	0	f
1041	2	54	Carolina Panthers	8	2025-09-23 14:49:37.784618	4	0	f
1042	2	55	Los Angeles Chargers	7	2025-09-23 14:49:37.785274	4	0	f
1043	2	56	Philadelphia Eagles	9	2025-09-23 14:49:37.78595	4	9	f
1044	2	57	Tennessee Titans	11	2025-09-23 14:49:37.786647	4	0	f
1045	2	58	Indianapolis Colts	12	2025-09-23 14:49:37.787293	4	0	f
1046	2	59	San Francisco 49ers	1	2025-09-23 14:49:37.787975	4	0	f
1047	2	60	Kansas City Chiefs	10	2025-09-23 14:49:37.788644	4	10	f
1048	2	61	Chicago Bears	13	2025-09-23 14:49:37.78927	4	0	f
1049	2	62	Dallas Cowboys	14	2025-09-23 14:49:37.789934	4	14	f
1050	2	63	Miami Dolphins	15	2025-09-23 14:49:37.790594	4	15	f
1051	2	64	Denver Broncos	16	2025-09-23 14:49:37.791063	4	16	f
1052	14	49	Seattle Seahawks	13	2025-09-25 23:15:45.921306	4	13	f
1053	14	50	Minnesota Vikings	14	2025-09-28 03:07:18.233179	4	0	f
1054	14	51	Atlanta Falcons	6	2025-09-28 03:07:18.234242	4	6	f
1055	14	52	Buffalo Bills	8	2025-09-28 03:07:18.234962	4	0	f
1056	14	53	Detroit Lions	12	2025-09-28 03:07:18.235647	4	12	f
1057	14	54	Carolina Panthers	2	2025-09-28 03:07:18.236263	4	0	f
1058	14	55	Los Angeles Chargers	10	2025-09-28 03:07:18.236911	4	0	f
1059	14	56	Philadelphia Eagles	16	2025-09-28 03:07:18.237545	4	16	f
1060	14	57	Houston Texans	7	2025-09-28 03:07:18.238139	4	7	f
1061	14	58	Los Angeles Rams	4	2025-09-28 03:07:18.238764	4	4	f
1062	14	59	San Francisco 49ers	5	2025-09-28 03:07:18.239346	4	0	f
1063	14	60	Kansas City Chiefs	1	2025-09-28 03:07:18.239976	4	1	f
1064	14	61	Las Vegas Raiders	9	2025-09-28 03:07:18.240595	4	9	f
1065	14	62	Green Bay Packers	15	2025-09-28 03:07:18.241176	4	0	f
1066	14	63	Miami Dolphins	3	2025-09-28 03:07:18.241819	4	3	f
1067	14	64	Denver Broncos	11	2025-09-28 03:07:18.242428	4	11	f
1068	24	49	Arizona Cardinals	16	2025-09-23 20:37:29.287499	4	0	f
1069	24	50	Minnesota Vikings	11	2025-09-23 20:37:29.288776	4	0	f
1070	24	51	Washington Commanders	13	2025-09-23 20:37:29.289793	4	0	f
1071	24	52	Buffalo Bills	1	2025-09-23 20:37:29.290765	4	0	f
1072	24	53	Detroit Lions	10	2025-09-23 20:37:29.29175	4	10	f
1073	24	54	Carolina Panthers	6	2025-09-23 20:37:29.292725	4	0	f
1074	24	55	Los Angeles Chargers	3	2025-09-23 20:37:29.293686	4	0	f
1075	24	56	Philadelphia Eagles	9	2025-09-23 20:37:29.294646	4	9	f
1076	24	57	Tennessee Titans	2	2025-09-23 20:37:29.295638	4	0	f
1077	24	58	Los Angeles Rams	7	2025-09-23 20:37:29.296592	4	7	f
1078	24	59	Jacksonville Jaguars	4	2025-09-23 20:37:29.297569	4	4	f
1079	24	60	Baltimore Ravens	14	2025-09-23 20:37:29.298533	4	0	f
1080	24	61	Chicago Bears	15	2025-09-23 20:37:29.29951	4	0	f
1081	24	62	Dallas Cowboys	5	2025-09-23 20:37:29.300474	4	5	f
1082	24	63	Miami Dolphins	12	2025-09-23 20:37:29.301425	4	12	f
1083	24	64	Cincinnati Bengals	8	2025-09-23 20:37:29.302395	4	0	f
1084	12	49	Arizona Cardinals	8	2025-09-25 22:02:42.373479	4	0	f
1085	12	50	Minnesota Vikings	11	2025-09-25 22:02:42.3746	4	0	f
1086	12	51	Atlanta Falcons	7	2025-09-25 22:02:42.375404	4	7	f
1087	12	52	Buffalo Bills	4	2025-09-25 22:02:42.376183	4	0	f
1088	12	53	Cleveland Browns	2	2025-09-25 22:02:42.377038	4	0	f
1089	12	54	New England Patriots	16	2025-09-25 22:02:42.377924	4	16	f
1090	12	55	Los Angeles Chargers	13	2025-09-25 22:02:42.378817	4	0	f
1091	12	56	Tampa Bay Buccaneers	9	2025-09-25 22:02:42.380556	4	0	f
1092	12	57	Tennessee Titans	3	2025-09-25 22:02:42.381392	4	0	f
1093	12	58	Los Angeles Rams	5	2025-09-25 22:02:42.38216	4	5	f
1094	12	59	Jacksonville Jaguars	6	2025-09-25 22:02:42.382952	4	6	f
1095	12	60	Baltimore Ravens	10	2025-09-25 22:02:42.383827	4	0	f
1096	12	61	Chicago Bears	12	2025-09-25 22:02:42.38464	4	0	f
1097	12	62	Green Bay Packers	14	2025-09-25 22:02:42.385415	4	0	f
1098	12	63	New York Jets	1	2025-09-25 22:02:42.386154	4	0	f
1099	12	64	Denver Broncos	15	2025-09-25 22:02:42.386913	4	15	f
1100	20	49	Seattle Seahawks	3	2025-09-24 03:58:45.598226	4	3	f
1101	20	50	Minnesota Vikings	16	2025-09-24 03:58:45.599436	4	0	f
1102	20	56	Philadelphia Eagles	10	2025-09-24 03:58:45.604151	4	10	f
1103	20	61	Chicago Bears	15	2025-09-24 03:58:45.60814	4	0	f
1104	20	62	Dallas Cowboys	11	2025-09-24 03:58:45.608904	4	11	f
1105	20	63	Miami Dolphins	1	2025-09-24 03:58:45.609675	4	1	f
1106	20	64	Denver Broncos	6	2025-09-24 03:58:45.61042	4	6	f
1107	20	51	Atlanta Falcons	12	2025-09-24 03:58:45.600292	4	12	f
1108	20	52	New Orleans Saints	9	2025-09-24 03:58:45.60112	4	9	f
1109	20	53	Cleveland Browns	5	2025-09-24 03:58:45.601905	4	0	f
1110	20	54	New England Patriots	2	2025-09-24 03:58:45.602666	4	2	f
1111	20	60	Kansas City Chiefs	7	2025-09-24 03:58:45.607387	4	7	f
1112	20	55	Los Angeles Chargers	4	2025-09-24 03:58:45.603411	4	0	f
1113	20	57	Tennessee Titans	8	2025-09-24 03:58:45.604907	4	0	f
1114	20	58	Indianapolis Colts	14	2025-09-24 03:58:45.605729	4	0	f
1115	20	59	San Francisco 49ers	13	2025-09-24 03:58:45.606939	4	0	f
1116	9	49	Arizona Cardinals	5	2025-09-24 21:20:50.786221	4	0	f
1117	9	50	Pittsburgh Steelers	4	2025-09-24 21:20:50.787477	4	4	f
1118	9	51	Washington Commanders	9	2025-09-24 21:20:50.788374	4	0	f
1119	9	52	Buffalo Bills	14	2025-09-24 21:20:50.789267	4	0	f
1120	9	53	Cleveland Browns	3	2025-09-24 21:20:50.790106	4	0	f
1121	9	54	New England Patriots	12	2025-09-24 21:20:50.790938	4	12	f
1122	9	55	Los Angeles Chargers	16	2025-09-24 21:20:50.791747	4	0	f
1123	9	56	Tampa Bay Buccaneers	6	2025-09-24 21:20:50.792584	4	0	f
1124	9	57	Tennessee Titans	7	2025-09-24 21:20:50.793395	4	0	f
1125	9	58	Indianapolis Colts	2	2025-09-24 21:20:50.794248	4	0	f
1126	9	59	Jacksonville Jaguars	10	2025-09-24 21:20:50.795089	4	10	f
1127	9	60	Kansas City Chiefs	1	2025-09-24 21:20:50.795895	4	1	f
1128	9	61	Chicago Bears	15	2025-09-24 21:20:50.797335	4	0	f
1129	9	62	Green Bay Packers	13	2025-09-24 21:20:50.798173	4	0	f
1130	9	63	Miami Dolphins	8	2025-09-24 21:20:50.799021	4	8	f
1131	9	64	Denver Broncos	11	2025-09-24 21:20:50.799744	4	11	f
1132	25	49	Seattle Seahawks	10	2025-09-25 00:17:24.983397	4	10	f
1133	25	50	Pittsburgh Steelers	16	2025-09-25 00:17:24.984408	4	16	f
1134	25	51	Washington Commanders	8	2025-09-25 00:17:24.985148	4	0	f
1135	25	52	New Orleans Saints	12	2025-09-25 00:17:24.985852	4	12	f
1136	25	53	Detroit Lions	15	2025-09-25 00:17:24.986527	4	15	f
1137	25	54	Carolina Panthers	5	2025-09-25 00:17:24.987179	4	0	f
1138	25	55	Los Angeles Chargers	3	2025-09-25 00:17:24.987834	4	0	f
1139	25	56	Tampa Bay Buccaneers	4	2025-09-25 00:17:24.988512	4	0	f
1140	25	57	Tennessee Titans	13	2025-09-25 00:17:24.989154	4	0	f
1141	25	58	Indianapolis Colts	9	2025-09-25 00:17:24.989815	4	0	f
1142	25	59	San Francisco 49ers	11	2025-09-25 00:17:24.990515	4	0	f
1143	25	60	Kansas City Chiefs	2	2025-09-25 00:17:24.991146	4	2	f
1144	25	61	Chicago Bears	7	2025-09-25 00:17:24.991777	4	0	f
1145	25	62	Dallas Cowboys	1	2025-09-25 00:17:24.992407	4	1	f
1146	25	63	Miami Dolphins	\N	2025-09-25 00:17:24.993021	4	0	f
1147	25	64	Denver Broncos	14	2025-09-25 00:17:24.993546	4	14	f
1148	8	49	Seattle Seahawks	10	2025-09-25 19:58:13.801191	4	10	f
1149	5	49	Seattle Seahawks	14	2025-09-25 14:49:52.890557	4	14	f
1150	22	49	Seattle Seahawks	9	2025-09-25 15:09:42.458396	4	9	f
1151	22	50	Pittsburgh Steelers	2	2025-09-25 15:09:42.459775	4	2	f
1152	22	51	Washington Commanders	8	2025-09-25 15:09:42.461964	4	0	f
1153	22	52	Buffalo Bills	16	2025-09-25 15:09:42.463871	4	0	f
1154	22	53	Detroit Lions	12	2025-09-25 15:09:42.465378	4	12	f
1155	22	54	Carolina Panthers	7	2025-09-25 15:09:42.466316	4	0	f
1156	22	55	Los Angeles Chargers	15	2025-09-25 15:09:42.467302	4	0	f
1157	22	56	Tampa Bay Buccaneers	1	2025-09-25 15:09:42.4682	4	0	f
1158	22	57	Houston Texans	13	2025-09-25 15:09:42.469067	4	13	f
1159	22	58	Los Angeles Rams	4	2025-09-25 15:09:42.470024	4	4	f
1160	22	59	San Francisco 49ers	3	2025-09-25 15:09:42.470896	4	0	f
1161	22	60	Baltimore Ravens	6	2025-09-25 15:09:42.471757	4	0	f
1162	22	61	Chicago Bears	5	2025-09-25 15:09:42.472628	4	0	f
1163	22	62	Green Bay Packers	11	2025-09-25 15:09:42.473479	4	0	f
1164	22	63	Miami Dolphins	10	2025-09-25 15:09:42.474279	4	10	f
1165	22	64	Denver Broncos	14	2025-09-25 15:09:42.474907	4	14	f
1166	21	49	Seattle Seahawks	5	2025-09-25 15:43:09.000445	4	5	f
1167	21	50	Pittsburgh Steelers	12	2025-09-25 15:43:09.001859	4	12	f
1168	21	51	Washington Commanders	11	2025-09-25 15:43:09.003001	4	0	f
1169	21	52	Buffalo Bills	4	2025-09-25 15:43:09.004048	4	0	f
1170	21	53	Cleveland Browns	3	2025-09-25 15:43:09.005088	4	0	f
1171	21	54	New England Patriots	6	2025-09-25 15:43:09.006088	4	6	f
1172	21	55	Los Angeles Chargers	13	2025-09-25 15:43:09.007116	4	0	f
1173	21	56	Philadelphia Eagles	2	2025-09-25 15:43:09.00812	4	2	f
1174	21	57	Tennessee Titans	1	2025-09-25 15:43:09.009115	4	0	f
1175	21	58	Indianapolis Colts	10	2025-09-25 15:43:09.010258	4	0	f
1176	21	59	San Francisco 49ers	14	2025-09-25 15:43:09.011216	4	0	f
1177	21	60	Kansas City Chiefs	7	2025-09-25 15:43:09.011933	4	7	f
1178	21	61	Chicago Bears	15	2025-09-25 15:43:09.012654	4	0	f
1179	21	62	Dallas Cowboys	8	2025-09-25 15:43:09.013295	4	8	f
1180	21	63	Miami Dolphins	9	2025-09-25 15:43:09.013989	4	9	f
1181	21	64	Denver Broncos	16	2025-09-25 15:43:09.014509	4	16	f
1182	26	49	Seattle Seahawks	4	2025-09-25 19:15:03.498946	4	4	f
1183	26	50	Minnesota Vikings	3	2025-09-25 19:15:03.500228	4	0	f
1184	26	51	Washington Commanders	8	2025-09-25 19:15:03.501164	4	0	f
1185	26	52	Buffalo Bills	2	2025-09-25 19:15:03.501992	4	0	f
1186	26	53	Detroit Lions	10	2025-09-25 19:15:03.502888	4	10	f
1187	26	54	New England Patriots	6	2025-09-25 19:15:03.503626	4	6	f
1188	26	55	Los Angeles Chargers	14	2025-09-25 19:15:03.504256	4	0	f
1189	26	56	Philadelphia Eagles	7	2025-09-25 19:15:03.504896	4	7	f
1190	26	57	Tennessee Titans	5	2025-09-25 19:15:03.505548	4	0	f
1191	26	58	Indianapolis Colts	11	2025-09-25 19:15:03.506169	4	0	f
1192	26	59	San Francisco 49ers	15	2025-09-25 19:15:03.50684	4	0	f
1193	26	60	Kansas City Chiefs	1	2025-09-25 19:15:03.507483	4	1	f
1194	26	61	Chicago Bears	13	2025-09-25 19:15:03.50811	4	0	f
1195	26	62	Green Bay Packers	12	2025-09-25 19:15:03.508766	4	0	f
1196	26	63	Miami Dolphins	9	2025-09-25 19:15:03.509383	4	9	f
1197	26	64	Denver Broncos	16	2025-09-25 19:15:03.509987	4	16	f
1198	8	50	Minnesota Vikings	7	2025-09-25 19:58:13.802658	4	0	f
1199	8	51	Washington Commanders	16	2025-09-25 19:58:13.803698	4	0	f
1200	8	52	Buffalo Bills	11	2025-09-25 19:58:13.804717	4	0	f
1201	8	53	Cleveland Browns	2	2025-09-25 19:58:13.805683	4	0	f
1202	8	54	New England Patriots	9	2025-09-25 19:58:13.806716	4	9	f
1203	8	55	Los Angeles Chargers	15	2025-09-25 19:58:13.807709	4	0	f
1204	8	56	Tampa Bay Buccaneers	13	2025-09-25 19:58:13.808649	4	0	f
1205	8	57	Houston Texans	8	2025-09-25 19:58:13.809584	4	8	f
1206	8	58	Los Angeles Rams	4	2025-09-25 19:58:13.810554	4	4	f
1207	8	59	San Francisco 49ers	6	2025-09-25 19:58:13.811545	4	0	f
1208	8	60	Baltimore Ravens	1	2025-09-25 19:58:13.812564	4	0	f
1209	8	61	Chicago Bears	12	2025-09-25 19:58:13.813541	4	0	f
1210	8	62	Green Bay Packers	14	2025-09-25 19:58:13.814523	4	0	f
1211	8	63	Miami Dolphins	5	2025-09-25 19:58:13.815514	4	5	f
1212	8	64	Denver Broncos	3	2025-09-25 19:58:13.81649	4	3	f
1213	17	49	Seattle Seahawks	16	2025-09-25 22:16:41.584336	4	16	f
1214	13	49	Seattle Seahawks	5	2025-09-25 22:38:51.334685	4	5	f
1215	10	49	Seattle Seahawks	14	2025-09-25 22:43:29.376778	4	14	f
1216	4	49	Arizona Cardinals	10	2025-09-25 22:44:45.63547	4	0	f
1217	19	49	Seattle Seahawks	5	2025-09-25 22:50:48.882775	4	5	f
1218	19	50	Minnesota Vikings	7	2025-09-28 13:07:09.987424	4	0	f
1219	19	51	Washington Commanders	14	2025-09-28 15:37:59.0685	4	0	f
1220	19	52	Buffalo Bills	13	2025-09-28 15:37:59.069529	4	0	f
1221	19	53	Cleveland Browns	4	2025-09-28 15:37:59.070199	4	0	f
1222	19	54	New England Patriots	12	2025-09-28 15:37:59.070884	4	12	f
1223	19	55	Los Angeles Chargers	3	2025-09-28 15:37:59.071614	4	0	f
1224	19	56	Tampa Bay Buccaneers	6	2025-09-28 15:37:59.072246	4	0	f
1225	19	58	Los Angeles Rams	2	2025-09-28 15:37:59.073776	4	2	f
1226	19	59	San Francisco 49ers	16	2025-09-28 15:37:59.074459	4	0	f
1227	19	60	Baltimore Ravens	15	2025-09-28 15:37:59.075057	4	0	f
1228	19	61	Las Vegas Raiders	1	2025-09-28 15:37:59.075678	4	1	f
1229	19	62	Dallas Cowboys	10	2025-09-28 15:37:59.076276	4	10	f
1230	19	63	New York Jets	9	2025-09-28 15:37:59.076911	4	0	f
1231	19	64	Cincinnati Bengals	8	2025-09-28 15:37:59.077525	4	0	f
1232	15	49	Seattle Seahawks	8	2025-09-25 22:56:39.419174	4	8	f
1233	18	49	Arizona Cardinals	16	2025-09-25 23:36:54.279892	4	0	f
1234	18	50	Pittsburgh Steelers	10	2025-09-25 23:36:54.281648	4	10	f
1235	18	51	Atlanta Falcons	15	2025-09-25 23:36:54.282438	4	15	f
1236	18	52	New Orleans Saints	5	2025-09-25 23:36:54.28317	4	5	f
1237	18	53	Cleveland Browns	14	2025-09-25 23:36:54.283917	4	0	f
1238	18	54	Carolina Panthers	12	2025-09-25 23:36:54.284674	4	0	f
1239	18	55	Los Angeles Chargers	13	2025-09-25 23:36:54.285415	4	0	f
1240	18	56	Philadelphia Eagles	6	2025-09-25 23:36:54.286104	4	6	f
1241	18	57	Tennessee Titans	9	2025-09-25 23:36:54.286842	4	0	f
1242	18	58	Los Angeles Rams	4	2025-09-25 23:36:54.287566	4	4	f
1243	18	59	Jacksonville Jaguars	3	2025-09-25 23:36:54.288234	4	3	f
1244	18	60	Kansas City Chiefs	11	2025-09-25 23:36:54.28895	4	11	f
1245	18	61	Las Vegas Raiders	8	2025-09-25 23:36:54.289646	4	8	f
1246	18	62	Green Bay Packers	7	2025-09-25 23:36:54.290322	4	0	f
1247	18	63	Miami Dolphins	2	2025-09-25 23:36:54.29104	4	2	f
1248	18	64	Denver Broncos	1	2025-09-25 23:36:54.291557	4	1	f
1249	23	49	Seattle Seahawks	5	2025-09-25 23:46:48.553031	4	5	f
1250	23	50	Minnesota Vikings	7	2025-09-25 23:46:48.554212	4	0	f
1251	23	51	Atlanta Falcons	2	2025-09-25 23:46:48.555113	4	2	f
1252	23	52	Buffalo Bills	15	2025-09-25 23:46:48.555956	4	0	f
1253	23	53	Detroit Lions	3	2025-09-25 23:46:48.556773	4	3	f
1254	23	54	New England Patriots	6	2025-09-25 23:46:48.557601	4	6	f
1255	23	55	Los Angeles Chargers	10	2025-09-25 23:46:48.558391	4	0	f
1256	23	56	Philadelphia Eagles	14	2025-09-25 23:46:48.559163	4	14	f
1257	23	57	Tennessee Titans	13	2025-09-25 23:46:48.559956	4	0	f
1258	23	58	Los Angeles Rams	9	2025-09-25 23:46:48.56075	4	9	f
1259	23	59	San Francisco 49ers	8	2025-09-25 23:46:48.561537	4	0	f
1260	23	60	Baltimore Ravens	12	2025-09-25 23:46:48.562288	4	0	f
1261	23	61	Chicago Bears	1	2025-09-25 23:46:48.563329	4	0	f
1262	23	62	Green Bay Packers	11	2025-09-25 23:46:48.564156	4	0	f
1263	23	63	Miami Dolphins	4	2025-09-25 23:46:48.564991	4	4	f
1264	23	64	Denver Broncos	16	2025-09-25 23:46:48.565617	4	16	f
1265	16	49	Arizona Cardinals	16	2025-09-25 23:57:05.847187	4	0	f
1266	16	50	Pittsburgh Steelers	10	2025-09-25 23:57:05.848155	4	10	f
1267	16	51	Washington Commanders	11	2025-09-25 23:57:05.84887	4	0	f
1268	16	52	Buffalo Bills	1	2025-09-25 23:57:05.849585	4	0	f
1269	16	53	Detroit Lions	2	2025-09-25 23:57:05.850238	4	2	f
1270	16	54	Carolina Panthers	6	2025-09-25 23:57:05.850909	4	0	f
1271	16	55	Los Angeles Chargers	12	2025-09-25 23:57:05.851644	4	0	f
1272	16	56	Philadelphia Eagles	13	2025-09-25 23:57:05.852378	4	13	f
1273	16	57	Tennessee Titans	4	2025-09-25 23:57:05.853015	4	0	f
1274	16	58	Los Angeles Rams	7	2025-09-25 23:57:05.853733	4	7	f
1275	16	59	San Francisco 49ers	8	2025-09-25 23:57:05.854422	4	0	f
1276	16	60	Baltimore Ravens	14	2025-09-25 23:57:05.85513	4	0	f
1277	16	61	Chicago Bears	15	2025-09-25 23:57:05.855856	4	0	f
1278	16	62	Green Bay Packers	3	2025-09-25 23:57:05.856515	4	0	f
1279	16	63	Miami Dolphins	9	2025-09-25 23:57:05.857138	4	9	f
1280	16	64	Denver Broncos	5	2025-09-25 23:57:05.857657	4	5	f
1281	5	50	Minnesota Vikings	4	2025-09-26 00:22:50.835661	4	0	f
1282	5	51	Washington Commanders	13	2025-09-26 00:22:50.836634	4	0	f
1283	5	52	Buffalo Bills	1	2025-09-26 00:22:50.837335	4	0	f
1284	5	53	Detroit Lions	2	2025-09-26 00:22:50.838032	4	2	f
1285	5	54	Carolina Panthers	3	2025-09-26 00:22:50.838792	4	0	f
1286	5	55	Los Angeles Chargers	15	2025-09-26 00:22:50.839494	4	0	f
1287	5	56	Tampa Bay Buccaneers	6	2025-09-26 00:22:50.840238	4	0	f
1288	5	57	Houston Texans	5	2025-09-26 00:22:50.840935	4	5	f
1289	5	58	Indianapolis Colts	16	2025-09-26 00:22:50.84164	4	0	f
1290	5	59	San Francisco 49ers	8	2025-09-26 00:22:50.842574	4	0	f
1291	5	60	Baltimore Ravens	12	2025-09-26 00:22:50.843372	4	0	f
1292	5	61	Chicago Bears	9	2025-09-26 00:22:50.844332	4	0	f
1293	5	62	Green Bay Packers	7	2025-09-26 00:22:50.845049	4	0	f
1294	5	63	Miami Dolphins	10	2025-09-26 00:22:50.84572	4	10	f
1295	5	64	Denver Broncos	11	2025-09-26 00:22:50.846211	4	11	f
1296	4	50	Pittsburgh Steelers	5	2025-09-26 00:31:53.78417	4	5	f
1297	4	51	Washington Commanders	9	2025-09-26 00:31:53.785159	4	0	f
1298	4	52	New Orleans Saints	7	2025-09-26 00:31:53.785886	4	7	f
1299	4	53	Detroit Lions	8	2025-09-26 00:31:53.786616	4	8	f
1300	4	54	Carolina Panthers	4	2025-09-26 00:31:53.787278	4	0	f
1301	4	55	Los Angeles Chargers	11	2025-09-26 00:31:53.787974	4	0	f
1302	4	56	Philadelphia Eagles	6	2025-09-26 00:31:53.788868	4	6	f
1303	4	57	Houston Texans	3	2025-09-26 00:31:53.789827	4	3	f
1304	4	58	Indianapolis Colts	12	2025-09-26 00:31:53.790557	4	0	f
1305	4	59	San Francisco 49ers	13	2025-09-26 00:31:53.791288	4	0	f
1306	4	60	Baltimore Ravens	14	2025-09-26 00:31:53.792003	4	0	f
1307	4	61	Chicago Bears	15	2025-09-26 00:31:53.792704	4	0	f
1308	4	62	Dallas Cowboys	2	2025-09-26 00:31:53.793396	4	2	f
1309	4	63	Miami Dolphins	1	2025-09-26 00:31:53.79403	4	1	f
1310	4	64	Denver Broncos	16	2025-09-26 00:31:53.794598	4	16	f
1311	10	50	Pittsburgh Steelers	7	2025-09-27 12:38:16.094776	4	7	f
1312	10	51	Atlanta Falcons	6	2025-09-27 12:38:16.09598	4	6	f
1313	10	52	Buffalo Bills	1	2025-09-27 12:38:16.096898	4	0	f
1314	10	53	Detroit Lions	12	2025-09-27 12:38:16.098834	4	12	f
1315	10	54	New England Patriots	5	2025-09-27 12:38:16.100167	4	5	f
1316	10	55	Los Angeles Chargers	15	2025-09-27 12:38:16.101065	4	0	f
1317	10	56	Tampa Bay Buccaneers	4	2025-09-27 12:38:16.102015	4	0	f
1318	10	57	Houston Texans	3	2025-09-27 12:38:16.102987	4	3	f
1319	10	58	Indianapolis Colts	11	2025-09-27 12:38:16.103928	4	0	f
1320	10	59	San Francisco 49ers	10	2025-09-27 12:38:16.104863	4	0	f
1321	10	60	Baltimore Ravens	13	2025-09-27 12:38:16.105832	4	0	f
1322	10	61	Las Vegas Raiders	8	2025-09-27 12:38:16.106817	4	8	f
1323	10	62	Dallas Cowboys	9	2025-09-27 12:38:16.10781	4	9	f
1324	10	63	New York Jets	2	2025-09-27 12:38:16.1088	4	0	f
1325	10	64	Denver Broncos	16	2025-09-27 12:38:16.109736	4	16	f
1326	15	50	Minnesota Vikings	4	2025-09-27 20:32:48.985147	4	0	f
1327	15	51	Washington Commanders	6	2025-09-27 20:32:48.986424	4	0	f
1328	15	52	Buffalo Bills	5	2025-09-27 20:32:48.987394	4	0	f
1329	15	53	Detroit Lions	7	2025-09-27 20:32:48.988459	4	7	f
1330	15	54	New England Patriots	12	2025-09-27 20:32:48.989438	4	12	f
1331	15	55	Los Angeles Chargers	15	2025-09-27 20:32:48.990498	4	0	f
1332	15	56	Philadelphia Eagles	11	2025-09-27 20:32:48.991633	4	11	f
1333	15	57	Tennessee Titans	13	2025-09-27 20:32:48.993303	4	0	f
1334	15	58	Indianapolis Colts	1	2025-09-27 20:32:48.994888	4	0	f
1335	15	59	San Francisco 49ers	9	2025-09-27 20:32:48.996535	4	0	f
1336	15	60	Baltimore Ravens	3	2025-09-27 20:32:48.997672	4	0	f
1337	15	61	Las Vegas Raiders	14	2025-09-27 20:32:48.998735	4	14	f
1338	15	62	Green Bay Packers	2	2025-09-27 20:32:49.00112	4	0	f
1339	15	63	New York Jets	10	2025-09-27 20:32:49.002197	4	0	f
1340	15	64	Denver Broncos	16	2025-09-27 20:32:49.003217	4	16	f
1341	13	50	Minnesota Vikings	9	2025-09-27 20:36:36.104542	4	0	f
1342	13	51	Atlanta Falcons	15	2025-09-27 20:36:36.105847	4	15	f
1343	13	52	Buffalo Bills	6	2025-09-27 20:36:36.106916	4	0	f
1344	13	53	Detroit Lions	3	2025-09-27 20:36:36.107921	4	3	f
1345	13	54	New England Patriots	2	2025-09-27 20:36:36.108942	4	2	f
1346	13	55	Los Angeles Chargers	12	2025-09-27 20:36:36.109931	4	0	f
1347	13	56	Tampa Bay Buccaneers	1	2025-09-27 20:36:36.110914	4	0	f
1348	13	57	Tennessee Titans	16	2025-09-27 20:36:36.11188	4	0	f
1349	13	58	Indianapolis Colts	11	2025-09-27 20:36:36.112859	4	0	f
1350	13	59	San Francisco 49ers	14	2025-09-27 20:36:36.113833	4	0	f
1351	13	60	Baltimore Ravens	4	2025-09-27 20:36:36.11481	4	0	f
1352	13	61	Las Vegas Raiders	10	2025-09-27 20:36:36.115769	4	10	f
1353	13	62	Green Bay Packers	7	2025-09-27 20:36:36.116723	4	0	f
1354	13	63	New York Jets	8	2025-09-27 20:36:36.117691	4	0	f
1355	13	64	Denver Broncos	13	2025-09-27 20:36:36.118442	4	13	f
1356	17	50	Pittsburgh Steelers	5	2025-09-28 04:08:30.772062	4	5	f
1357	17	51	Washington Commanders	8	2025-09-28 14:38:21.939332	4	0	f
1358	17	52	Buffalo Bills	9	2025-09-28 14:38:21.940416	4	0	f
1359	17	53	Cleveland Browns	10	2025-09-28 14:38:21.941201	4	0	f
1360	17	54	Carolina Panthers	6	2025-09-28 14:38:21.941955	4	0	f
1361	17	55	Los Angeles Chargers	12	2025-09-28 14:38:21.942705	4	0	f
1362	17	56	Tampa Bay Buccaneers	11	2025-09-28 14:38:21.943417	4	0	f
1363	17	57	Tennessee Titans	4	2025-09-28 14:38:21.944152	4	0	f
1364	17	58	Indianapolis Colts	7	2025-09-28 14:38:21.944883	4	0	f
1365	17	59	Jacksonville Jaguars	3	2025-09-28 14:38:21.945589	4	3	f
1366	17	60	Baltimore Ravens	2	2025-09-28 14:38:21.946265	4	0	f
1367	17	61	Las Vegas Raiders	1	2025-09-28 14:38:21.946966	4	1	f
1368	17	62	Green Bay Packers	14	2025-09-28 14:38:21.947678	4	0	f
1369	17	63	New York Jets	15	2025-09-28 14:38:21.948379	4	0	f
1370	17	64	Denver Broncos	13	2025-09-28 14:38:21.948963	4	13	f
1371	19	57	Tennessee Titans	11	2025-09-28 15:37:59.073342	4	0	f
1372	20	65	San Francisco 49ers	12	2025-10-02 21:05:20.3045	5	12	f
1373	14	65	Los Angeles Rams	5	2025-10-02 20:31:42.943716	5	0	f
1374	14	66	Minnesota Vikings	7	2025-10-03 22:03:13.357591	5	0	f
1375	14	67	Indianapolis Colts	12	2025-10-03 22:03:13.358878	5	12	f
1376	14	68	New Orleans Saints	4	2025-10-03 22:03:13.359828	5	4	f
1377	14	69	Dallas Cowboys	11	2025-10-03 22:03:13.360735	5	11	f
1378	14	70	Denver Broncos	1	2025-10-03 22:03:13.361592	5	1	f
1379	14	71	Carolina Panthers	8	2025-10-03 22:03:13.362391	5	8	f
1380	14	72	Houston Texans	3	2025-10-03 22:03:13.363172	5	3	f
1381	14	73	Arizona Cardinals	10	2025-10-03 22:03:13.363973	5	0	f
1382	14	74	Seattle Seahawks	6	2025-10-03 22:03:13.36478	5	0	f
1383	14	75	Detroit Lions	13	2025-10-03 22:03:13.365577	5	13	f
1384	14	76	Los Angeles Chargers	14	2025-10-03 22:03:13.366344	5	0	f
1385	14	77	New England Patriots	2	2025-10-03 22:03:13.367137	5	2	f
1386	14	78	Kansas City Chiefs	9	2025-10-03 22:03:13.367924	5	0	f
1387	23	65	San Francisco 49ers	10	2025-09-30 15:27:15.276183	5	10	f
1388	23	66	Minnesota Vikings	9	2025-09-30 15:27:15.277618	5	0	f
1389	23	67	Indianapolis Colts	3	2025-09-30 15:27:15.278734	5	3	f
1390	23	68	New York Giants	4	2025-09-30 15:27:15.27975	5	0	f
1391	23	69	New York Jets	5	2025-09-30 15:27:15.280715	5	0	f
1392	23	70	Denver Broncos	14	2025-09-30 15:27:15.281662	5	14	f
1393	23	71	Miami Dolphins	6	2025-09-30 15:27:15.282579	5	0	f
1394	23	72	Houston Texans	7	2025-09-30 15:27:15.283473	5	7	f
1395	23	73	Arizona Cardinals	8	2025-09-30 15:27:15.284323	5	0	f
1396	23	74	Seattle Seahawks	11	2025-09-30 15:27:15.28519	5	0	f
1397	23	75	Detroit Lions	12	2025-09-30 15:27:15.286068	5	12	f
1398	23	76	Los Angeles Chargers	1	2025-09-30 15:27:15.286928	5	0	f
1399	23	77	Buffalo Bills	13	2025-09-30 15:27:15.287773	5	0	f
1400	23	78	Kansas City Chiefs	2	2025-09-30 15:27:15.288605	5	0	f
1401	2	65	Los Angeles Rams	2	2025-09-30 17:17:29.026232	5	0	f
1402	2	66	Cleveland Browns	1	2025-09-30 17:17:29.027833	5	1	f
1403	2	67	Indianapolis Colts	7	2025-09-30 17:17:29.029032	5	7	f
1404	2	68	New York Giants	3	2025-09-30 17:17:29.030127	5	0	f
1405	2	69	Dallas Cowboys	13	2025-09-30 17:17:29.031215	5	13	f
1406	2	70	Denver Broncos	14	2025-09-30 17:17:29.032339	5	14	f
1407	2	71	Miami Dolphins	11	2025-09-30 17:17:29.033394	5	0	f
1408	2	72	Baltimore Ravens	8	2025-09-30 17:17:29.034424	5	0	f
1409	2	73	Tennessee Titans	5	2025-09-30 17:17:29.035456	5	5	f
1410	2	74	Tampa Bay Buccaneers	6	2025-09-30 17:17:29.036472	5	6	f
1411	2	75	Detroit Lions	12	2025-09-30 17:17:29.037478	5	12	f
1412	2	76	Los Angeles Chargers	10	2025-09-30 17:17:29.038516	5	0	f
1413	2	77	Buffalo Bills	4	2025-09-30 17:17:29.039524	5	0	f
1414	2	78	Kansas City Chiefs	9	2025-09-30 17:17:29.040298	5	0	f
1415	1	65	Los Angeles Rams	8	2025-09-30 20:01:04.660207	5	0	f
1416	1	66	Minnesota Vikings	7	2025-09-30 20:01:04.661673	5	0	f
1417	1	67	Indianapolis Colts	11	2025-09-30 20:01:04.66279	5	11	f
1418	1	68	New Orleans Saints	10	2025-09-30 20:01:04.663868	5	10	f
1419	1	69	Dallas Cowboys	9	2025-09-30 20:01:04.664898	5	9	f
1420	1	70	Denver Broncos	14	2025-09-30 20:01:04.665911	5	14	f
1421	1	71	Miami Dolphins	6	2025-09-30 20:01:04.666922	5	0	f
1422	1	72	Baltimore Ravens	1	2025-09-30 20:01:04.667931	5	0	f
1423	1	73	Arizona Cardinals	13	2025-09-30 20:01:04.668933	5	0	f
1424	1	74	Tampa Bay Buccaneers	5	2025-09-30 20:01:04.669925	5	5	f
1425	1	75	Detroit Lions	4	2025-09-30 20:01:04.670913	5	4	f
1426	1	76	Washington Commanders	3	2025-09-30 20:01:04.671915	5	3	f
1427	1	77	New England Patriots	2	2025-09-30 20:01:04.672912	5	2	f
1428	1	78	Kansas City Chiefs	12	2025-09-30 20:01:04.673658	5	0	f
1429	24	65	Los Angeles Rams	11	2025-09-30 21:14:21.806059	5	0	f
1430	24	66	Minnesota Vikings	8	2025-09-30 21:14:21.807338	5	0	f
1431	24	67	Indianapolis Colts	4	2025-09-30 21:14:21.80827	5	4	f
1432	24	68	New York Giants	12	2025-09-30 21:14:21.809156	5	0	f
1433	24	70	Philadelphia Eagles	7	2025-09-30 21:14:21.810038	5	0	f
1434	24	71	Carolina Panthers	6	2025-09-30 21:14:21.810892	5	6	f
1435	24	72	Baltimore Ravens	5	2025-09-30 21:14:21.81174	5	0	f
1436	24	73	Tennessee Titans	3	2025-09-30 21:14:21.812586	5	3	f
1437	24	74	Tampa Bay Buccaneers	10	2025-09-30 21:14:21.813427	5	10	f
1438	24	75	Detroit Lions	1	2025-09-30 21:14:21.814237	5	1	f
1439	24	76	Los Angeles Chargers	13	2025-09-30 21:14:21.81508	5	0	f
1440	24	77	Buffalo Bills	2	2025-09-30 21:14:21.815919	5	0	f
1441	24	78	Kansas City Chiefs	9	2025-09-30 21:14:21.816745	5	0	f
1442	15	65	Los Angeles Rams	4	2025-09-30 21:32:47.742759	5	0	f
1443	21	65	Los Angeles Rams	14	2025-09-30 21:54:35.865144	5	0	f
1444	21	66	Cleveland Browns	13	2025-09-30 21:54:35.866267	5	13	f
1445	21	67	Indianapolis Colts	12	2025-09-30 21:54:35.867125	5	12	f
1446	21	68	New York Giants	11	2025-09-30 21:54:35.867986	5	0	f
1447	21	69	Dallas Cowboys	10	2025-09-30 21:54:35.868824	5	10	f
1448	21	70	Philadelphia Eagles	6	2025-09-30 21:54:35.869647	5	0	f
1449	21	71	Miami Dolphins	1	2025-09-30 21:54:35.870573	5	0	f
1450	21	72	Houston Texans	7	2025-09-30 21:54:35.871394	5	7	f
1451	21	73	Tennessee Titans	5	2025-09-30 21:54:35.872183	5	5	f
1452	21	74	Tampa Bay Buccaneers	2	2025-09-30 21:54:35.873012	5	2	f
1453	21	75	Detroit Lions	4	2025-09-30 21:54:35.873862	5	4	f
1454	21	76	Los Angeles Chargers	9	2025-09-30 21:54:35.874686	5	0	f
1455	21	77	Buffalo Bills	3	2025-09-30 21:54:35.875496	5	0	f
1456	21	78	Kansas City Chiefs	8	2025-09-30 21:54:35.876095	5	0	f
1457	4	65	Los Angeles Rams	5	2025-10-01 03:08:45.37518	5	0	f
1458	4	66	Minnesota Vikings	8	2025-10-01 03:08:45.376491	5	0	f
1459	4	67	Indianapolis Colts	7	2025-10-01 03:08:45.377549	5	7	f
1460	4	68	New Orleans Saints	6	2025-10-01 03:08:45.37858	5	6	f
1461	4	69	New York Jets	9	2025-10-01 03:08:45.379547	5	0	f
1462	4	70	Denver Broncos	10	2025-10-01 03:08:45.380416	5	10	f
1463	4	71	Carolina Panthers	3	2025-10-01 03:08:45.381189	5	3	f
1464	4	72	Baltimore Ravens	4	2025-10-01 03:08:45.382023	5	0	f
1465	4	73	Arizona Cardinals	11	2025-10-01 03:08:45.382847	5	0	f
1466	4	74	Seattle Seahawks	12	2025-10-01 03:08:45.383644	5	0	f
1467	4	75	Detroit Lions	2	2025-10-01 03:08:45.384434	5	2	f
1468	4	76	Los Angeles Chargers	13	2025-10-01 03:08:45.385121	5	0	f
1469	4	77	Buffalo Bills	1	2025-10-01 03:08:45.385804	5	0	f
1470	4	78	Kansas City Chiefs	14	2025-10-01 03:08:45.386705	5	0	f
1471	12	65	Los Angeles Rams	10	2025-10-02 12:31:18.803434	5	0	f
1472	12	69	Dallas Cowboys	11	2025-10-05 07:12:17.781811	5	11	f
1473	12	70	Denver Broncos	14	2025-10-05 07:12:17.782636	5	14	f
1474	12	73	Arizona Cardinals	12	2025-10-05 07:12:17.784962	5	0	f
1475	12	78	Jacksonville Jaguars	9	2025-10-05 07:12:17.788245	5	9	f
1476	13	65	Los Angeles Rams	5	2025-10-01 21:29:51.587321	5	0	f
1477	8	65	Los Angeles Rams	7	2025-10-02 15:11:52.675993	5	0	f
1478	16	65	Los Angeles Rams	6	2025-10-02 01:32:05.9383	5	0	f
1479	16	66	Minnesota Vikings	7	2025-10-02 01:32:05.940009	5	0	f
1480	16	67	Indianapolis Colts	5	2025-10-02 01:32:05.941777	5	5	f
1481	16	68	New York Giants	14	2025-10-02 01:32:05.943044	5	0	f
1482	16	69	Dallas Cowboys	9	2025-10-02 01:32:05.944158	5	9	f
1483	16	70	Denver Broncos	8	2025-10-02 01:32:05.945528	5	8	f
1484	16	71	Carolina Panthers	13	2025-10-02 01:32:05.946708	5	13	f
1485	16	72	Baltimore Ravens	2	2025-10-02 01:32:05.947821	5	0	f
1486	16	73	Tennessee Titans	3	2025-10-02 01:32:05.94889	5	3	f
1487	16	74	Seattle Seahawks	10	2025-10-02 01:32:05.950029	5	0	f
1488	16	75	Cincinnati Bengals	1	2025-10-02 01:32:05.950964	5	0	f
1489	16	76	Washington Commanders	11	2025-10-02 01:32:05.951905	5	11	f
1490	16	77	Buffalo Bills	4	2025-10-02 01:32:05.952793	5	0	f
1491	16	78	Kansas City Chiefs	12	2025-10-02 01:32:05.953495	5	0	f
1492	18	65	Los Angeles Rams	10	2025-10-02 07:31:21.107913	5	0	f
1493	18	66	Cleveland Browns	8	2025-10-02 07:31:21.109217	5	8	f
1494	18	67	Indianapolis Colts	9	2025-10-02 07:31:21.11023	5	9	f
1495	18	68	New Orleans Saints	1	2025-10-02 07:31:21.111236	5	1	f
1496	18	69	Dallas Cowboys	7	2025-10-02 07:31:21.112238	5	7	f
1497	18	70	Philadelphia Eagles	12	2025-10-02 07:31:21.113271	5	0	f
1498	18	71	Carolina Panthers	6	2025-10-02 07:31:21.114476	5	6	f
1499	18	72	Baltimore Ravens	13	2025-10-02 07:31:21.115513	5	0	f
1500	18	73	Tennessee Titans	4	2025-10-02 07:31:21.116521	5	4	f
1501	18	74	Tampa Bay Buccaneers	5	2025-10-02 07:31:21.117507	5	5	f
1502	18	75	Detroit Lions	14	2025-10-02 07:31:21.118501	5	14	f
1503	18	76	Los Angeles Chargers	3	2025-10-02 07:31:21.119487	5	0	f
1504	18	77	New England Patriots	2	2025-10-02 07:31:21.120985	5	2	f
1505	18	78	Kansas City Chiefs	11	2025-10-02 07:31:21.121712	5	0	f
1506	19	65	Los Angeles Rams	5	2025-10-02 16:12:57.782631	5	0	f
1507	12	67	Las Vegas Raiders	8	2025-10-05 07:12:17.780046	5	0	f
1508	12	68	New Orleans Saints	7	2025-10-05 07:12:17.780939	5	7	f
1509	12	71	Miami Dolphins	5	2025-10-05 07:12:17.783449	5	0	f
1510	12	75	Detroit Lions	13	2025-10-05 07:12:17.786291	5	13	f
1511	12	77	New England Patriots	6	2025-10-05 07:12:17.787634	5	6	f
1512	8	66	Minnesota Vikings	10	2025-10-02 15:11:52.679049	5	0	f
1513	8	67	Indianapolis Colts	14	2025-10-02 15:11:52.679934	5	14	f
1514	8	68	New York Giants	11	2025-10-02 15:11:52.680741	5	0	f
1515	8	69	Dallas Cowboys	8	2025-10-02 15:11:52.68152	5	8	f
1516	8	70	Denver Broncos	2	2025-10-02 15:11:52.682238	5	2	f
1517	8	71	Carolina Panthers	12	2025-10-02 15:11:52.683142	5	12	f
1518	8	72	Baltimore Ravens	9	2025-10-02 15:11:52.68401	5	0	f
1519	8	73	Arizona Cardinals	6	2025-10-02 15:11:52.684845	5	0	f
1520	8	74	Tampa Bay Buccaneers	5	2025-10-02 15:11:52.685718	5	5	f
1521	8	75	Detroit Lions	13	2025-10-02 15:11:52.686509	5	13	f
1522	8	76	Washington Commanders	4	2025-10-02 15:11:52.687231	5	4	f
1523	8	77	New England Patriots	3	2025-10-02 15:11:52.687925	5	3	f
1524	8	78	Jacksonville Jaguars	1	2025-10-02 15:11:52.688616	5	1	f
1525	5	65	San Francisco 49ers	7	2025-10-02 15:35:17.768318	5	7	f
1526	19	66	Minnesota Vikings	10	2025-10-04 23:41:31.745061	5	0	f
1527	19	67	Indianapolis Colts	9	2025-10-05 15:09:14.069525	5	9	f
1528	19	68	New York Giants	4	2025-10-05 15:09:14.071019	5	0	f
1529	19	69	Dallas Cowboys	12	2025-10-05 15:09:14.072207	5	12	f
1530	19	70	Denver Broncos	6	2025-10-05 15:09:14.073313	5	6	f
1531	19	71	Miami Dolphins	7	2025-10-05 15:09:14.074394	5	0	f
1532	19	73	Tennessee Titans	14	2025-10-05 15:09:14.076491	5	14	f
1533	19	74	Seattle Seahawks	1	2025-10-05 15:09:14.077491	5	0	f
1534	19	77	Buffalo Bills	8	2025-10-05 23:44:49.842389	5	0	f
1535	19	78	Kansas City Chiefs	13	2025-10-05 23:44:49.843756	5	0	f
1536	9	65	Los Angeles Rams	14	2025-10-02 17:26:34.148832	5	0	f
1537	9	66	Minnesota Vikings	5	2025-10-02 17:26:34.150306	5	0	f
1538	9	67	Indianapolis Colts	4	2025-10-02 17:26:34.15149	5	4	f
1539	9	68	New York Giants	3	2025-10-02 17:26:34.152613	5	0	f
1540	9	69	Dallas Cowboys	10	2025-10-02 17:26:34.153668	5	10	f
1541	9	70	Philadelphia Eagles	6	2025-10-02 17:26:34.154587	5	0	f
1542	9	71	Carolina Panthers	11	2025-10-02 17:26:34.155455	5	11	f
1543	9	72	Houston Texans	13	2025-10-02 17:26:34.156287	5	13	f
1544	9	73	Arizona Cardinals	12	2025-10-02 17:26:34.157285	5	0	f
1545	9	74	Tampa Bay Buccaneers	7	2025-10-02 17:26:34.158332	5	7	f
1546	9	75	Cincinnati Bengals	2	2025-10-02 17:26:34.15914	5	0	f
1547	9	76	Los Angeles Chargers	9	2025-10-02 17:26:34.159942	5	0	f
1548	9	77	New England Patriots	1	2025-10-02 17:26:34.160742	5	1	f
1549	9	78	Kansas City Chiefs	8	2025-10-02 17:26:34.161537	5	0	f
1550	22	65	Los Angeles Rams	10	2025-10-02 20:28:38.824505	5	0	f
1551	22	66	Minnesota Vikings	9	2025-10-02 20:28:38.826042	5	0	f
1552	22	67	Indianapolis Colts	8	2025-10-02 20:28:38.827231	5	8	f
1553	22	68	New Orleans Saints	3	2025-10-02 20:28:38.82848	5	3	f
1554	22	69	Dallas Cowboys	12	2025-10-02 20:28:38.829547	5	12	f
1555	22	70	Denver Broncos	11	2025-10-02 20:28:38.830654	5	11	f
1556	22	71	Miami Dolphins	4	2025-10-02 20:28:38.831769	5	0	f
1557	22	72	Houston Texans	5	2025-10-02 20:28:38.832894	5	5	f
1558	22	73	Arizona Cardinals	6	2025-10-02 20:28:38.833828	5	0	f
1559	22	74	Tampa Bay Buccaneers	1	2025-10-02 20:28:38.83467	5	1	f
1560	22	75	Detroit Lions	14	2025-10-02 20:28:38.835484	5	14	f
1561	22	76	Los Angeles Chargers	7	2025-10-02 20:28:38.836301	5	0	f
1562	22	77	Buffalo Bills	13	2025-10-02 20:28:38.837246	5	0	f
1563	22	78	Jacksonville Jaguars	2	2025-10-02 20:28:38.838013	5	2	f
1564	26	65	Los Angeles Rams	5	2025-10-02 22:41:42.238939	5	0	f
1565	26	66	Minnesota Vikings	8	2025-10-02 22:41:42.240101	5	0	f
1566	26	67	Indianapolis Colts	7	2025-10-02 22:41:42.241056	5	7	f
1567	26	68	New York Giants	13	2025-10-02 22:41:42.241929	5	0	f
1568	26	69	Dallas Cowboys	4	2025-10-02 22:41:42.242768	5	4	f
1569	26	70	Philadelphia Eagles	1	2025-10-02 22:41:42.243709	5	0	f
1570	26	71	Miami Dolphins	9	2025-10-02 22:41:42.244571	5	0	f
1571	26	72	Baltimore Ravens	2	2025-10-02 22:41:42.245257	5	0	f
1572	26	73	Arizona Cardinals	3	2025-10-02 22:41:42.245954	5	0	f
1573	26	74	Tampa Bay Buccaneers	10	2025-10-02 22:41:42.246636	5	10	f
1574	26	75	Detroit Lions	11	2025-10-02 22:41:42.247324	5	11	f
1575	26	76	Los Angeles Chargers	6	2025-10-02 22:41:42.248022	5	0	f
1576	26	77	Buffalo Bills	12	2025-10-02 22:41:42.248711	5	0	f
1577	26	78	Kansas City Chiefs	14	2025-10-02 22:41:42.249201	5	0	f
1578	17	65	Los Angeles Rams	14	2025-10-03 00:05:07.358734	5	0	f
1579	17	68	New York Giants	12	2025-10-05 14:59:17.798609	5	0	f
1580	17	70	Denver Broncos	5	2025-10-05 14:59:17.80102	5	5	f
1581	17	72	Houston Texans	13	2025-10-05 14:59:17.803144	5	13	f
1582	17	73	Tennessee Titans	10	2025-10-05 14:59:17.804141	5	10	f
1583	17	74	Tampa Bay Buccaneers	3	2025-10-05 14:59:17.805093	5	3	f
1584	17	75	Detroit Lions	11	2025-10-05 14:59:17.806045	5	11	f
1585	17	76	Los Angeles Chargers	8	2025-10-05 14:59:17.807003	5	0	f
1586	17	77	Buffalo Bills	7	2025-10-05 14:59:17.807978	5	0	f
1587	10	65	San Francisco 49ers	8	2025-10-02 22:57:14.145287	5	8	f
1588	5	66	Minnesota Vikings	8	2025-10-03 00:54:16.925628	5	0	f
1589	5	67	Indianapolis Colts	14	2025-10-03 00:54:16.926861	5	14	f
1590	5	68	New Orleans Saints	10	2025-10-03 00:54:16.927881	5	10	f
1591	5	69	Dallas Cowboys	13	2025-10-03 00:54:16.928866	5	13	f
1592	5	70	Philadelphia Eagles	6	2025-10-03 00:54:16.929845	5	0	f
1593	5	71	Miami Dolphins	1	2025-10-03 00:54:16.930825	5	0	f
1594	5	72	Houston Texans	2	2025-10-03 00:54:16.931814	5	2	f
1595	5	73	Tennessee Titans	3	2025-10-03 00:54:16.932903	5	3	f
1596	5	74	Tampa Bay Buccaneers	12	2025-10-03 00:54:16.933941	5	12	f
1597	5	75	Detroit Lions	9	2025-10-03 00:54:16.934909	5	9	f
1598	5	76	Los Angeles Chargers	11	2025-10-03 00:54:16.935881	5	0	f
1599	5	77	New England Patriots	4	2025-10-03 00:54:16.936844	5	4	f
1600	5	78	Kansas City Chiefs	5	2025-10-03 00:54:16.937598	5	0	f
1601	12	66	Cleveland Browns	2	2025-10-05 07:12:17.778794	5	2	f
1602	12	72	Houston Texans	3	2025-10-05 07:12:17.784243	5	3	f
1603	12	74	Tampa Bay Buccaneers	1	2025-10-05 07:12:17.785627	5	1	f
1604	12	76	Washington Commanders	4	2025-10-05 07:12:17.786981	5	4	f
1605	10	66	Minnesota Vikings	11	2025-10-04 22:58:44.248656	5	0	f
1606	10	67	Las Vegas Raiders	2	2025-10-04 22:58:44.249779	5	0	f
1607	10	68	New Orleans Saints	1	2025-10-04 22:58:44.25055	5	1	f
1608	10	69	Dallas Cowboys	3	2025-10-04 22:58:44.251218	5	3	f
1609	10	70	Denver Broncos	14	2025-10-04 22:58:44.251956	5	14	f
1610	10	71	Miami Dolphins	10	2025-10-04 22:58:44.252796	5	0	f
1611	10	72	Houston Texans	4	2025-10-04 22:58:44.253532	5	4	f
1612	10	73	Arizona Cardinals	9	2025-10-04 22:58:44.254275	5	0	f
1613	10	74	Seattle Seahawks	13	2025-10-04 22:58:44.254998	5	0	f
1614	10	75	Detroit Lions	7	2025-10-04 22:58:44.255737	5	7	f
1615	10	76	Washington Commanders	6	2025-10-04 22:58:44.256448	5	6	f
1616	10	77	New England Patriots	12	2025-10-04 22:58:44.257143	5	12	f
1617	10	78	Jacksonville Jaguars	5	2025-10-04 22:58:44.257844	5	5	f
1618	15	66	Cleveland Browns	8	2025-10-04 23:00:10.397318	5	8	f
1619	15	67	Indianapolis Colts	6	2025-10-04 23:00:10.398253	5	6	f
1620	15	68	New York Giants	12	2025-10-04 23:00:10.39904	5	0	f
1621	15	69	Dallas Cowboys	9	2025-10-04 23:00:10.399759	5	9	f
1622	15	70	Denver Broncos	14	2025-10-04 23:00:10.400433	5	14	f
1623	15	71	Carolina Panthers	5	2025-10-04 23:00:10.401087	5	5	f
1624	15	72	Baltimore Ravens	10	2025-10-04 23:00:10.401759	5	0	f
1625	15	73	Arizona Cardinals	3	2025-10-04 23:00:10.402426	5	0	f
1626	15	74	Tampa Bay Buccaneers	2	2025-10-04 23:00:10.403067	5	2	f
1627	15	75	Detroit Lions	13	2025-10-04 23:00:10.403775	5	13	f
1628	15	76	Los Angeles Chargers	1	2025-10-04 23:00:10.404447	5	0	f
1629	15	77	Buffalo Bills	7	2025-10-04 23:00:10.405085	5	0	f
1630	15	78	Kansas City Chiefs	11	2025-10-04 23:00:10.405624	5	0	f
1631	13	66	Minnesota Vikings	3	2025-10-05 00:43:13.401987	5	0	f
1632	13	67	Las Vegas Raiders	2	2025-10-05 00:43:13.402952	5	0	f
1633	13	68	New York Giants	10	2025-10-05 00:43:13.403694	5	0	f
1634	13	69	New York Jets	1	2025-10-05 00:43:13.404421	5	0	f
1635	13	70	Denver Broncos	8	2025-10-05 00:43:13.405158	5	8	f
1636	13	71	Carolina Panthers	4	2025-10-05 00:43:13.405912	5	4	f
1637	13	72	Houston Texans	11	2025-10-05 00:43:13.406602	5	11	f
1638	13	73	Tennessee Titans	12	2025-10-05 00:43:13.407242	5	12	f
1639	13	74	Tampa Bay Buccaneers	14	2025-10-05 00:43:13.407917	5	14	f
1640	13	75	Detroit Lions	13	2025-10-05 00:43:13.408587	5	13	f
1641	13	76	Los Angeles Chargers	6	2025-10-05 00:43:13.409216	5	0	f
1642	13	77	New England Patriots	9	2025-10-05 00:43:13.409882	5	9	f
1643	13	78	Jacksonville Jaguars	7	2025-10-05 00:43:13.410382	5	7	f
1644	20	66	Minnesota Vikings	13	2025-10-05 05:38:23.398838	5	0	f
1645	20	67	Las Vegas Raiders	11	2025-10-05 05:38:23.400092	5	0	f
1646	20	68	New York Giants	3	2025-10-05 05:38:23.400935	5	0	f
1647	20	69	Dallas Cowboys	14	2025-10-05 05:38:23.401786	5	14	f
1648	20	70	Philadelphia Eagles	10	2025-10-05 05:38:23.402767	5	0	f
1649	20	75	Detroit Lions	4	2025-10-05 05:38:23.407749	5	4	f
1650	20	71	Carolina Panthers	1	2025-10-05 05:38:23.404153	5	1	f
1651	20	72	Houston Texans	5	2025-10-05 05:38:23.405186	5	5	f
1652	20	73	Arizona Cardinals	9	2025-10-05 05:38:23.406201	5	0	f
1653	20	74	Tampa Bay Buccaneers	2	2025-10-05 05:38:23.407203	5	2	f
1654	20	76	Los Angeles Chargers	6	2025-10-05 05:38:23.409247	5	0	f
1655	20	77	New England Patriots	8	2025-10-05 05:38:23.409956	5	8	f
1656	20	78	Jacksonville Jaguars	7	2025-10-05 05:38:23.410492	5	7	f
1657	17	66	Cleveland Browns	4	2025-10-05 13:02:13.815374	5	4	f
1658	25	67	Indianapolis Colts	1	2025-10-05 13:53:37.214599	5	1	f
1659	25	68	New Orleans Saints	11	2025-10-05 13:53:37.215976	5	11	f
1660	25	69	Dallas Cowboys	6	2025-10-05 13:53:37.216991	5	6	f
1661	25	70	Denver Broncos	9	2025-10-05 13:53:37.217886	5	9	f
1662	25	71	Miami Dolphins	2	2025-10-05 13:53:37.218772	5	0	f
1663	25	72	Baltimore Ravens	10	2025-10-05 13:53:37.219619	5	0	f
1664	25	73	Tennessee Titans	5	2025-10-05 13:53:37.220514	5	5	f
1665	25	74	Tampa Bay Buccaneers	4	2025-10-05 13:53:37.221395	5	4	f
1666	25	75	Cincinnati Bengals	7	2025-10-05 13:53:37.222179	5	0	f
1667	25	76	Los Angeles Chargers	8	2025-10-05 13:53:37.222971	5	0	f
1668	25	77	New England Patriots	3	2025-10-05 13:53:37.223847	5	3	f
1669	25	78	Kansas City Chiefs	12	2025-10-05 13:53:37.225076	5	0	f
1670	17	67	Indianapolis Colts	9	2025-10-05 14:59:17.797731	5	9	f
1671	17	69	New York Jets	6	2025-10-05 14:59:17.800428	5	0	f
1672	17	71	Carolina Panthers	1	2025-10-05 14:59:17.802569	5	1	f
1673	17	78	Jacksonville Jaguars	2	2025-10-05 14:59:17.809196	5	2	f
1674	19	72	Houston Texans	11	2025-10-05 15:09:14.075437	5	11	f
1675	19	75	Cincinnati Bengals	3	2025-10-05 15:09:14.078515	5	0	f
1676	19	76	Los Angeles Chargers	2	2025-10-05 15:09:14.079519	5	0	f
1677	1	79	Philadelphia Eagles	7	2025-10-07 13:12:09.833277	6	0	f
1678	1	80	Denver Broncos	15	2025-10-07 13:12:09.834337	6	0	f
1679	1	81	Indianapolis Colts	14	2025-10-07 13:12:09.835242	6	0	f
1680	1	82	Los Angeles Chargers	13	2025-10-07 13:12:09.836107	6	0	f
1681	1	83	Pittsburgh Steelers	5	2025-10-07 13:12:09.836875	6	5	f
1682	1	84	Tampa Bay Buccaneers	6	2025-10-07 13:12:09.837599	6	6	f
1683	1	85	Dallas Cowboys	12	2025-10-07 13:12:09.838314	6	0	f
1684	1	86	Jacksonville Jaguars	11	2025-10-07 13:12:09.839046	6	0	f
1685	1	87	Los Angeles Rams	3	2025-10-07 13:12:09.839807	6	3	f
1686	1	88	Las Vegas Raiders	4	2025-10-07 13:12:09.840663	6	4	f
1687	1	89	Green Bay Packers	1	2025-10-07 13:12:09.841488	6	0	f
1688	1	90	New England Patriots	2	2025-10-07 13:12:09.842226	6	2	f
1689	1	91	Detroit Lions	10	2025-10-07 13:12:09.842998	6	0	f
1690	1	92	Buffalo Bills	8	2025-10-07 13:12:09.843958	6	0	f
1691	1	93	Washington Commanders	9	2025-10-07 13:12:09.844582	6	0	f
1692	14	79	Philadelphia Eagles	9	2025-10-09 14:57:13.08864	6	0	f
1693	14	80	Denver Broncos	7	2025-10-11 17:12:27.001002	6	0	f
1694	14	81	Indianapolis Colts	15	2025-10-11 17:12:27.002577	6	0	f
1695	14	82	Los Angeles Chargers	2	2025-10-11 17:12:27.003611	6	0	f
1696	14	83	Pittsburgh Steelers	13	2025-10-11 17:12:27.004506	6	13	f
1697	14	84	San Francisco 49ers	3	2025-10-11 17:12:27.005414	6	0	f
1698	14	85	Carolina Panthers	8	2025-10-11 17:12:27.006422	6	8	f
1699	14	86	Seattle Seahawks	12	2025-10-11 17:12:27.007114	6	12	f
1700	14	87	Los Angeles Rams	1	2025-10-11 17:12:27.007783	6	1	f
1701	14	88	Las Vegas Raiders	10	2025-10-11 17:12:27.008609	6	10	f
1702	14	89	Green Bay Packers	5	2025-10-11 17:12:27.009279	6	0	f
1703	14	90	New England Patriots	6	2025-10-11 17:12:27.009946	6	6	f
1704	14	91	Detroit Lions	11	2025-10-11 17:12:27.010702	6	0	f
1705	14	92	Buffalo Bills	4	2025-10-11 17:12:27.011521	6	0	f
1706	14	93	Washington Commanders	14	2025-10-11 17:12:27.012295	6	0	f
1707	12	79	Philadelphia Eagles	9	2025-10-09 14:32:45.302704	6	0	f
1708	12	80	Denver Broncos	10	2025-10-12 02:09:23.572208	6	0	f
1709	12	81	Indianapolis Colts	5	2025-10-12 02:09:23.573429	6	0	f
1710	12	82	Miami Dolphins	1	2025-10-12 02:09:23.574235	6	1	f
1711	12	83	Pittsburgh Steelers	6	2025-10-12 02:09:23.575017	6	6	f
1712	12	84	San Francisco 49ers	3	2025-10-12 02:09:23.575759	6	0	f
1713	12	85	Dallas Cowboys	13	2025-10-12 02:09:23.57647	6	0	f
1714	12	86	Seattle Seahawks	7	2025-10-12 02:09:23.577122	6	7	f
1715	12	87	Los Angeles Rams	8	2025-10-12 02:09:23.577858	6	8	f
1716	12	88	Las Vegas Raiders	4	2025-10-12 02:09:23.5787	6	4	f
1717	12	89	Green Bay Packers	2	2025-10-12 02:09:23.579416	6	0	f
1718	12	90	New England Patriots	12	2025-10-12 02:09:23.580137	6	12	f
1719	12	91	Detroit Lions	11	2025-10-12 02:09:23.58089	6	0	f
1720	12	92	Buffalo Bills	14	2025-10-12 02:09:23.581561	6	0	f
1721	12	93	Washington Commanders	15	2025-10-12 02:09:23.58219	6	0	f
1722	8	79	New York Giants	6	2025-10-09 05:48:34.082538	6	6	f
1723	13	79	New York Giants	5	2025-10-09 02:06:50.596172	6	5	f
1724	2	79	New York Giants	1	2025-10-10 00:06:26.951217	6	1	f
1725	2	80	Denver Broncos	15	2025-10-10 00:06:26.952975	6	0	f
1726	2	81	Indianapolis Colts	2	2025-10-10 00:06:26.954296	6	0	f
1727	2	82	Miami Dolphins	5	2025-10-10 00:06:26.95528	6	5	f
1728	2	83	Pittsburgh Steelers	8	2025-10-10 00:06:26.956875	6	8	f
1729	2	84	San Francisco 49ers	3	2025-10-10 00:06:26.958257	6	0	f
1730	2	85	Dallas Cowboys	10	2025-10-10 00:06:26.959527	6	0	f
1731	2	86	Jacksonville Jaguars	12	2025-10-10 00:06:26.960758	6	0	f
1732	2	87	Los Angeles Rams	11	2025-10-10 00:06:26.961863	6	11	f
1733	2	88	Tennessee Titans	4	2025-10-10 00:06:26.962887	6	0	f
1734	2	89	Green Bay Packers	9	2025-10-10 00:06:26.963694	6	0	f
1735	2	90	New Orleans Saints	7	2025-10-10 00:06:26.964535	6	0	f
1736	2	91	Detroit Lions	6	2025-10-10 00:06:26.965328	6	0	f
1737	2	92	Atlanta Falcons	13	2025-10-10 00:06:26.966123	6	13	f
1738	2	93	Washington Commanders	14	2025-10-10 00:06:26.966976	6	0	f
1739	21	79	New York Giants	15	2025-10-08 18:06:26.784197	6	15	f
1740	21	80	Denver Broncos	14	2025-10-08 18:06:26.785335	6	0	f
1741	21	81	Indianapolis Colts	13	2025-10-08 18:06:26.786199	6	0	f
1742	21	82	Los Angeles Chargers	12	2025-10-08 18:06:26.787014	6	0	f
1743	21	83	Pittsburgh Steelers	11	2025-10-08 18:06:26.787776	6	11	f
1744	21	84	Tampa Bay Buccaneers	10	2025-10-08 18:06:26.788503	6	10	f
1745	21	85	Dallas Cowboys	9	2025-10-08 18:06:26.789206	6	0	f
1746	21	86	Jacksonville Jaguars	8	2025-10-08 18:06:26.789927	6	0	f
1747	21	87	Los Angeles Rams	7	2025-10-08 18:06:26.790667	6	7	f
1748	21	88	Tennessee Titans	6	2025-10-08 18:06:26.791327	6	0	f
1749	21	89	Cincinnati Bengals	5	2025-10-08 18:06:26.792062	6	5	f
1750	21	90	New England Patriots	4	2025-10-08 18:06:26.792764	6	4	f
1751	21	91	Detroit Lions	3	2025-10-08 18:06:26.79349	6	0	f
1752	21	92	Buffalo Bills	2	2025-10-08 18:06:26.794218	6	0	f
1753	21	93	Washington Commanders	1	2025-10-08 18:06:26.794777	6	0	f
1754	23	79	Philadelphia Eagles	3	2025-10-08 20:52:33.455551	6	0	f
1755	23	80	Denver Broncos	15	2025-10-08 20:52:33.456744	6	0	f
1756	23	81	Indianapolis Colts	14	2025-10-08 20:52:33.457661	6	0	f
1757	23	82	Los Angeles Chargers	12	2025-10-08 20:52:33.458559	6	0	f
1758	23	83	Pittsburgh Steelers	5	2025-10-08 20:52:33.459457	6	5	f
1759	23	84	San Francisco 49ers	13	2025-10-08 20:52:33.460302	6	0	f
1760	23	85	Carolina Panthers	9	2025-10-08 20:52:33.461156	6	9	f
1761	23	86	Seattle Seahawks	8	2025-10-08 20:52:33.462018	6	8	f
1762	23	87	Los Angeles Rams	7	2025-10-08 20:52:33.462891	6	7	f
1763	23	88	Tennessee Titans	1	2025-10-08 20:52:33.463733	6	0	f
1764	23	89	Green Bay Packers	4	2025-10-08 20:52:33.464537	6	0	f
1765	23	90	New England Patriots	11	2025-10-08 20:52:33.465186	6	11	f
1766	23	91	Detroit Lions	6	2025-10-08 20:52:33.465868	6	0	f
1767	23	92	Buffalo Bills	10	2025-10-08 20:52:33.466557	6	0	f
1768	23	93	Chicago Bears	2	2025-10-08 20:52:33.467047	6	2	f
1769	22	79	New York Giants	4	2025-10-09 02:04:49.43864	6	4	f
1770	22	80	Denver Broncos	11	2025-10-09 02:04:49.440097	6	0	f
1771	22	81	Indianapolis Colts	6	2025-10-09 02:04:49.441189	6	0	f
1772	22	82	Los Angeles Chargers	3	2025-10-09 02:04:49.442252	6	0	f
1773	22	83	Pittsburgh Steelers	8	2025-10-09 02:04:49.443277	6	8	f
1774	22	85	Dallas Cowboys	7	2025-10-09 02:04:49.450314	6	0	f
1775	22	86	Seattle Seahawks	1	2025-10-09 02:04:49.452151	6	1	f
1776	22	87	Los Angeles Rams	5	2025-10-09 02:04:49.454719	6	5	f
1777	22	88	Las Vegas Raiders	9	2025-10-09 02:04:49.456936	6	9	f
1778	22	89	Cincinnati Bengals	10	2025-10-09 02:04:49.45928	6	10	f
1779	22	90	New England Patriots	13	2025-10-09 02:04:49.463061	6	13	f
1780	22	91	Detroit Lions	14	2025-10-09 02:04:49.464038	6	0	f
1781	22	92	Buffalo Bills	15	2025-10-09 02:04:49.464977	6	0	f
1782	22	93	Washington Commanders	12	2025-10-09 02:04:49.465915	6	0	f
1783	22	84	Tampa Bay Buccaneers	2	2025-10-09 02:04:49.449404	6	2	f
1784	24	79	Philadelphia Eagles	15	2025-10-09 02:49:41.222347	6	0	f
1785	24	80	New York Jets	5	2025-10-09 02:49:41.223647	6	5	f
1786	24	81	Indianapolis Colts	7	2025-10-09 02:49:41.224613	6	0	f
1787	24	82	Los Angeles Chargers	2	2025-10-09 02:49:41.225488	6	0	f
1788	24	83	Pittsburgh Steelers	3	2025-10-09 02:49:41.226328	6	3	f
1789	24	84	Tampa Bay Buccaneers	14	2025-10-09 02:49:41.227191	6	14	f
1790	24	85	Dallas Cowboys	13	2025-10-09 02:49:41.228013	6	0	f
1791	24	86	Jacksonville Jaguars	8	2025-10-09 02:49:41.228802	6	0	f
1792	24	87	Los Angeles Rams	6	2025-10-09 02:49:41.229579	6	6	f
1793	24	88	Tennessee Titans	4	2025-10-09 02:49:41.230299	6	0	f
1794	24	89	Green Bay Packers	1	2025-10-09 02:49:41.231026	6	0	f
1795	24	90	New England Patriots	10	2025-10-09 02:49:41.231703	6	10	f
1796	24	91	Detroit Lions	12	2025-10-09 02:49:41.23235	6	0	f
1797	24	92	Buffalo Bills	11	2025-10-09 02:49:41.233019	6	0	f
1798	24	93	Washington Commanders	9	2025-10-09 02:49:41.233696	6	0	f
1799	8	80	Denver Broncos	9	2025-10-09 05:48:34.083821	6	0	f
1800	8	81	Indianapolis Colts	12	2025-10-09 05:48:34.08483	6	0	f
1801	8	82	Los Angeles Chargers	8	2025-10-09 05:48:34.085736	6	0	f
1802	8	83	Cleveland Browns	5	2025-10-09 05:48:34.086432	6	0	f
1803	8	84	Tampa Bay Buccaneers	4	2025-10-09 05:48:34.087084	6	4	f
1804	8	85	Carolina Panthers	2	2025-10-09 05:48:34.087752	6	2	f
1805	8	86	Seattle Seahawks	11	2025-10-09 05:48:34.088422	6	11	f
1806	8	87	Los Angeles Rams	15	2025-10-09 05:48:34.089049	6	15	f
1807	8	88	Las Vegas Raiders	3	2025-10-09 05:48:34.089708	6	3	f
1808	8	89	Cincinnati Bengals	7	2025-10-09 05:48:34.090514	6	7	f
1809	8	90	New England Patriots	13	2025-10-09 05:48:34.091309	6	13	f
1810	8	91	Detroit Lions	14	2025-10-09 05:48:34.092096	6	0	f
1811	8	92	Buffalo Bills	1	2025-10-09 05:48:34.092965	6	0	f
1812	8	93	Washington Commanders	10	2025-10-09 05:48:34.093929	6	0	f
1813	9	79	Philadelphia Eagles	9	2025-10-09 15:37:22.840477	6	0	f
1814	9	80	Denver Broncos	10	2025-10-09 15:37:22.841964	6	0	f
1815	9	81	Arizona Cardinals	11	2025-10-09 15:37:22.843528	6	11	f
1816	9	82	Los Angeles Chargers	13	2025-10-09 15:37:22.844662	6	0	f
1817	9	83	Cleveland Browns	5	2025-10-09 15:37:22.845688	6	0	f
1818	9	84	San Francisco 49ers	6	2025-10-09 15:37:22.846681	6	0	f
1819	9	85	Dallas Cowboys	14	2025-10-09 15:37:22.847621	6	0	f
1820	9	86	Seattle Seahawks	8	2025-10-09 15:37:22.848572	6	8	f
1821	9	87	Los Angeles Rams	12	2025-10-09 15:37:22.849521	6	12	f
1822	9	88	Tennessee Titans	2	2025-10-09 15:37:22.850434	6	0	f
1823	9	89	Cincinnati Bengals	3	2025-10-09 15:37:22.851319	6	3	f
1824	9	90	New Orleans Saints	1	2025-10-09 15:37:22.852315	6	0	f
1825	9	91	Detroit Lions	4	2025-10-09 15:37:22.85328	6	0	f
1826	9	92	Buffalo Bills	15	2025-10-09 15:37:22.854261	6	0	f
1827	9	93	Washington Commanders	7	2025-10-09 15:37:22.855241	6	0	f
1828	16	79	Philadelphia Eagles	4	2025-10-09 16:25:01.057178	6	0	f
1829	16	80	Denver Broncos	5	2025-10-09 16:25:01.058232	6	0	f
1830	16	81	Indianapolis Colts	6	2025-10-09 16:25:01.059038	6	0	f
1831	16	82	Los Angeles Chargers	10	2025-10-09 16:25:01.059783	6	0	f
1832	16	83	Pittsburgh Steelers	8	2025-10-09 16:25:01.060495	6	8	f
1833	16	84	Tampa Bay Buccaneers	14	2025-10-09 16:25:01.061157	6	14	f
1834	16	85	Dallas Cowboys	13	2025-10-09 16:25:01.061855	6	0	f
1835	16	86	Jacksonville Jaguars	15	2025-10-09 16:25:01.062545	6	0	f
1836	16	87	Baltimore Ravens	2	2025-10-09 16:25:01.063241	6	0	f
1837	16	88	Las Vegas Raiders	7	2025-10-09 16:25:01.06394	6	7	f
1838	16	89	Green Bay Packers	3	2025-10-09 16:25:01.064734	6	0	f
1839	16	90	New England Patriots	11	2025-10-09 16:25:01.065534	6	11	f
1840	16	91	Detroit Lions	1	2025-10-09 16:25:01.066236	6	0	f
1841	16	92	Buffalo Bills	9	2025-10-09 16:25:01.067144	6	0	f
1842	16	93	Washington Commanders	12	2025-10-09 16:25:01.067893	6	0	f
1843	5	79	Philadelphia Eagles	10	2025-10-09 20:46:26.414948	6	0	f
1844	5	80	Denver Broncos	15	2025-10-09 20:46:26.417027	6	0	f
1845	5	81	Indianapolis Colts	7	2025-10-09 20:46:26.418479	6	0	f
1846	5	82	Los Angeles Chargers	8	2025-10-09 20:46:26.419546	6	0	f
1847	5	83	Pittsburgh Steelers	14	2025-10-09 20:46:26.420952	6	14	f
1848	5	84	Tampa Bay Buccaneers	2	2025-10-09 20:46:26.421979	6	2	f
1849	5	85	Carolina Panthers	3	2025-10-09 20:46:26.422998	6	3	f
1850	5	86	Seattle Seahawks	6	2025-10-09 20:46:26.424041	6	6	f
1851	5	87	Los Angeles Rams	13	2025-10-09 20:46:26.425308	6	13	f
1852	5	88	Las Vegas Raiders	9	2025-10-09 20:46:26.426603	6	9	f
1853	5	89	Cincinnati Bengals	1	2025-10-09 20:46:26.427956	6	1	f
1854	5	90	New England Patriots	12	2025-10-09 20:46:26.42903	6	12	f
1855	5	91	Detroit Lions	4	2025-10-09 20:46:26.430214	6	0	f
1856	5	92	Buffalo Bills	11	2025-10-09 20:46:26.431699	6	0	f
1857	5	93	Washington Commanders	5	2025-10-09 20:46:26.43269	6	0	f
1858	26	79	Philadelphia Eagles	6	2025-10-09 21:35:36.719536	6	0	f
1859	4	79	Philadelphia Eagles	15	2025-10-09 21:55:29.593305	6	0	f
1860	4	80	Denver Broncos	14	2025-10-09 21:55:29.594536	6	0	f
1861	4	81	Indianapolis Colts	13	2025-10-09 21:55:29.595497	6	0	f
1862	4	82	Los Angeles Chargers	12	2025-10-09 21:55:29.596434	6	0	f
1863	4	83	Pittsburgh Steelers	11	2025-10-09 21:55:29.597305	6	11	f
1864	4	84	Tampa Bay Buccaneers	10	2025-10-09 21:55:29.598152	6	10	f
1865	4	85	Dallas Cowboys	9	2025-10-09 21:55:29.59898	6	0	f
1866	4	86	Seattle Seahawks	8	2025-10-09 21:55:29.599829	6	8	f
1867	4	87	Los Angeles Rams	7	2025-10-09 21:55:29.600672	6	7	f
1868	4	88	Las Vegas Raiders	6	2025-10-09 21:55:29.601527	6	6	f
1869	4	89	Green Bay Packers	5	2025-10-09 21:55:29.602335	6	0	f
1870	4	90	New Orleans Saints	4	2025-10-09 21:55:29.603187	6	0	f
1871	4	91	Detroit Lions	3	2025-10-09 21:55:29.604016	6	0	f
1872	4	92	Buffalo Bills	2	2025-10-09 21:55:29.604872	6	0	f
1873	4	93	Washington Commanders	1	2025-10-09 21:55:29.605562	6	0	f
1874	10	79	Philadelphia Eagles	7	2025-10-09 22:53:50.512187	6	0	f
1875	19	79	New York Giants	5	2025-10-09 23:10:39.212954	6	5	f
1876	17	79	New York Giants	1	2025-10-09 23:10:54.408684	6	1	f
1877	15	79	Philadelphia Eagles	4	2025-10-09 23:48:20.572893	6	0	f
1878	20	79	Philadelphia Eagles	8	2025-10-09 23:54:43.540097	6	0	f
1879	18	79	Philadelphia Eagles	10	2025-10-09 23:54:43.540097	6	0	f
1880	18	80	New York Jets	2	2025-10-10 07:06:22.536164	6	2	f
1881	18	81	Indianapolis Colts	3	2025-10-10 07:06:22.537174	6	0	f
1882	18	82	Miami Dolphins	4	2025-10-10 07:06:22.53793	6	4	f
1883	18	83	Pittsburgh Steelers	5	2025-10-10 07:06:22.538657	6	5	f
1884	18	84	Tampa Bay Buccaneers	1	2025-10-10 07:06:22.539376	6	1	f
1885	18	85	Dallas Cowboys	15	2025-10-10 07:06:22.540107	6	0	f
1886	18	86	Jacksonville Jaguars	6	2025-10-10 07:06:22.540849	6	0	f
1887	18	87	Los Angeles Rams	7	2025-10-10 07:06:22.541549	6	7	f
1888	18	88	Las Vegas Raiders	8	2025-10-10 07:06:22.542204	6	8	f
1889	18	89	Cincinnati Bengals	14	2025-10-10 07:06:22.542905	6	14	f
1890	18	90	New England Patriots	12	2025-10-10 07:06:22.543585	6	12	f
1891	18	91	Kansas City Chiefs	11	2025-10-10 07:06:22.544225	6	11	f
1892	18	92	Buffalo Bills	13	2025-10-10 07:06:22.544913	6	0	f
1893	18	93	Chicago Bears	9	2025-10-10 07:06:22.545473	6	9	f
1894	20	80	Denver Broncos	15	2025-10-10 17:27:42.973877	6	0	f
1895	20	81	Indianapolis Colts	14	2025-10-10 17:27:42.974997	6	0	f
1896	20	82	Los Angeles Chargers	7	2025-10-10 17:27:42.975815	6	0	f
1897	20	83	Pittsburgh Steelers	13	2025-10-10 17:27:42.97658	6	13	f
1898	20	84	Tampa Bay Buccaneers	12	2025-10-10 17:27:42.977292	6	12	f
1899	20	85	Dallas Cowboys	11	2025-10-10 17:27:42.97802	6	0	f
1900	20	86	Jacksonville Jaguars	10	2025-10-10 17:27:42.978762	6	0	f
1901	20	87	Baltimore Ravens	1	2025-10-10 17:27:42.979446	6	0	f
1902	20	88	Tennessee Titans	2	2025-10-10 17:27:42.980104	6	0	f
1903	20	89	Green Bay Packers	3	2025-10-10 17:27:42.980841	6	0	f
1904	20	90	New England Patriots	9	2025-10-10 17:27:42.981526	6	9	f
1905	20	91	Detroit Lions	6	2025-10-10 17:27:42.982215	6	0	f
1906	20	92	Buffalo Bills	5	2025-10-10 17:27:42.982992	6	0	f
1907	20	93	Chicago Bears	4	2025-10-10 17:27:42.983773	6	4	f
1908	10	80	Denver Broncos	15	2025-10-11 22:40:46.328182	6	0	f
1909	10	81	Indianapolis Colts	10	2025-10-11 22:40:46.329415	6	0	f
1910	10	82	Miami Dolphins	9	2025-10-11 22:40:46.33057	6	9	f
1911	10	83	Cleveland Browns	8	2025-10-11 22:40:46.331498	6	0	f
1912	10	84	Tampa Bay Buccaneers	1	2025-10-11 22:40:46.332259	6	1	f
1913	10	85	Carolina Panthers	6	2025-10-11 22:40:46.333097	6	6	f
1914	10	86	Seattle Seahawks	5	2025-10-11 22:40:46.333925	6	5	f
1915	10	87	Los Angeles Rams	2	2025-10-11 22:40:46.334739	6	2	f
1916	10	88	Tennessee Titans	4	2025-10-11 22:40:46.335463	6	0	f
1917	10	89	Cincinnati Bengals	14	2025-10-11 22:40:46.336146	6	14	f
1918	10	90	New England Patriots	3	2025-10-11 22:40:46.336962	6	3	f
1919	10	91	Detroit Lions	13	2025-10-11 22:40:46.337682	6	0	f
1920	10	92	Buffalo Bills	12	2025-10-11 22:40:46.338349	6	0	f
1921	10	93	Washington Commanders	11	2025-10-11 22:40:46.338935	6	0	f
1922	26	80	Denver Broncos	8	2025-10-12 02:18:51.917311	6	0	f
1923	26	81	Indianapolis Colts	10	2025-10-12 02:18:51.918574	6	0	f
1924	26	82	Los Angeles Chargers	3	2025-10-12 02:18:51.919476	6	0	f
1925	26	83	Cleveland Browns	1	2025-10-12 02:18:51.920234	6	0	f
1926	26	84	Tampa Bay Buccaneers	11	2025-10-12 02:18:51.921022	6	11	f
1927	26	85	Dallas Cowboys	9	2025-10-12 02:18:51.921791	6	0	f
1928	26	86	Jacksonville Jaguars	13	2025-10-12 02:18:51.922609	6	0	f
1929	26	87	Los Angeles Rams	14	2025-10-12 02:18:51.92333	6	14	f
1930	26	88	Tennessee Titans	4	2025-10-12 02:18:51.924072	6	0	f
1931	26	89	Green Bay Packers	2	2025-10-12 02:18:51.924868	6	0	f
1932	26	90	New England Patriots	15	2025-10-12 02:18:51.925633	6	15	f
1933	26	91	Kansas City Chiefs	5	2025-10-12 02:18:51.926306	6	5	f
1934	26	92	Buffalo Bills	7	2025-10-12 02:18:51.927007	6	0	f
1935	26	93	Washington Commanders	12	2025-10-12 02:18:51.927706	6	0	f
1936	13	80	Denver Broncos	15	2025-10-12 02:45:12.943421	6	0	f
1937	13	81	Indianapolis Colts	12	2025-10-12 02:45:12.944746	6	0	f
1938	13	82	Miami Dolphins	3	2025-10-12 02:45:12.945678	6	3	f
1939	13	83	Pittsburgh Steelers	6	2025-10-12 02:45:12.946563	6	6	f
1940	13	84	Tampa Bay Buccaneers	2	2025-10-12 02:45:12.94739	6	2	f
1941	13	85	Dallas Cowboys	1	2025-10-12 02:45:12.948197	6	0	f
1942	13	86	Seattle Seahawks	7	2025-10-12 02:45:12.949043	6	7	f
1943	13	87	Los Angeles Rams	13	2025-10-12 02:45:12.949882	6	13	f
1944	13	88	Las Vegas Raiders	4	2025-10-12 02:45:12.950707	6	4	f
1945	13	89	Cincinnati Bengals	10	2025-10-12 02:45:12.951516	6	10	f
1946	13	90	New England Patriots	9	2025-10-12 02:45:12.952313	6	9	f
1947	13	91	Detroit Lions	14	2025-10-12 02:45:12.953122	6	0	f
1948	13	92	Buffalo Bills	8	2025-10-12 02:45:12.953933	6	0	f
1949	13	93	Washington Commanders	11	2025-10-12 02:45:12.954752	6	0	f
1950	15	80	Denver Broncos	13	2025-10-12 05:24:32.040555	6	0	f
1951	15	81	Indianapolis Colts	12	2025-10-12 05:24:32.041813	6	0	f
1952	15	82	Los Angeles Chargers	10	2025-10-12 05:24:32.042742	6	0	f
1953	15	83	Cleveland Browns	5	2025-10-12 05:24:32.043622	6	0	f
1954	15	84	Tampa Bay Buccaneers	8	2025-10-12 05:24:32.04454	6	8	f
1955	15	85	Dallas Cowboys	3	2025-10-12 05:24:32.045492	6	0	f
1956	15	86	Jacksonville Jaguars	6	2025-10-12 05:24:32.046394	6	0	f
1957	15	87	Los Angeles Rams	1	2025-10-12 05:24:32.047213	6	1	f
1958	15	88	Tennessee Titans	2	2025-10-12 05:24:32.048055	6	0	f
1959	15	89	Cincinnati Bengals	7	2025-10-12 05:24:32.048869	6	7	f
1960	15	90	New England Patriots	11	2025-10-12 05:24:32.049693	6	11	f
1961	15	91	Detroit Lions	15	2025-10-12 05:24:32.05051	6	0	f
1962	15	92	Buffalo Bills	14	2025-10-12 05:24:32.051302	6	0	f
1963	15	93	Washington Commanders	9	2025-10-12 05:24:32.051944	6	0	f
1964	19	81	Indianapolis Colts	11	2025-10-12 16:54:46.129035	6	0	f
1965	19	82	Los Angeles Chargers	9	2025-10-12 16:54:46.130649	6	0	f
1966	19	83	Cleveland Browns	10	2025-10-12 16:54:46.131873	6	0	f
1967	19	84	Tampa Bay Buccaneers	12	2025-10-12 16:54:46.132918	6	12	f
1968	19	85	Carolina Panthers	8	2025-10-12 16:54:46.134232	6	8	f
1969	19	86	Seattle Seahawks	13	2025-10-12 16:54:46.135438	6	13	f
1970	19	87	Baltimore Ravens	4	2025-10-12 16:54:46.136773	6	0	f
1971	19	88	Tennessee Titans	3	2025-10-12 16:54:46.138146	6	0	f
1972	19	89	Cincinnati Bengals	7	2025-10-12 16:54:46.13915	6	7	f
1973	19	90	New England Patriots	2	2025-10-12 16:54:46.140146	6	2	f
1974	19	91	Detroit Lions	14	2025-10-12 16:54:46.141111	6	0	f
1975	19	92	Buffalo Bills	6	2025-10-12 16:54:46.142099	6	0	f
1976	19	93	Chicago Bears	1	2025-10-12 16:54:46.143188	6	1	f
1977	17	81	Indianapolis Colts	12	2025-10-12 16:55:57.060264	6	0	f
1978	17	82	Los Angeles Chargers	6	2025-10-12 16:55:57.061752	6	0	f
1979	17	83	Cleveland Browns	5	2025-10-12 16:55:57.063021	6	0	f
1980	17	84	Tampa Bay Buccaneers	14	2025-10-12 16:55:57.064122	6	14	f
1981	17	85	Dallas Cowboys	7	2025-10-12 16:55:57.065258	6	0	f
1982	17	86	Seattle Seahawks	10	2025-10-12 16:55:57.066296	6	10	f
1983	17	87	Los Angeles Rams	11	2025-10-12 16:55:57.068287	6	11	f
1984	17	88	Tennessee Titans	9	2025-10-12 17:50:47.390029	6	0	f
1985	17	89	Green Bay Packers	2	2025-10-12 17:50:47.391327	6	0	f
1986	17	90	New England Patriots	13	2025-10-12 17:50:47.392301	6	13	f
1987	17	91	Detroit Lions	8	2025-10-12 17:50:47.393295	6	0	f
1988	17	92	Buffalo Bills	4	2025-10-12 17:50:47.394276	6	0	f
1989	17	93	Washington Commanders	3	2025-10-12 17:50:47.39529	6	0	f
1990	24	94	Pittsburgh Steelers	7	2025-10-14 13:10:22.079647	7	0	f
1991	24	95	Los Angeles Rams	13	2025-10-14 13:10:22.080782	7	13	f
1992	24	96	Chicago Bears	8	2025-10-14 13:10:22.081492	7	8	f
1993	24	97	Cleveland Browns	9	2025-10-14 13:10:22.082145	7	9	f
1994	24	98	Tennessee Titans	2	2025-10-14 13:10:22.082877	7	0	f
1995	24	99	Kansas City Chiefs	1	2025-10-14 13:10:22.083571	7	1	f
1996	24	100	Philadelphia Eagles	10	2025-10-14 13:10:22.084349	7	10	f
1997	24	101	Carolina Panthers	6	2025-10-14 13:10:22.08504	7	6	f
1998	24	102	Denver Broncos	3	2025-10-14 13:10:22.086048	7	0	f
1999	24	103	Indianapolis Colts	15	2025-10-14 13:10:22.086788	7	15	f
2000	24	104	Dallas Cowboys	4	2025-10-14 13:10:22.087521	7	4	f
2001	24	105	Green Bay Packers	12	2025-10-14 13:10:22.088475	7	0	f
2002	24	106	Atlanta Falcons	11	2025-10-14 13:10:22.089254	7	0	f
2003	24	107	Detroit Lions	14	2025-10-14 13:10:22.089955	7	14	f
2004	24	108	Seattle Seahawks	5	2025-10-14 13:10:22.090704	7	5	f
2005	1	94	Pittsburgh Steelers	5	2025-10-14 16:36:05.946534	7	0	f
2006	1	95	Los Angeles Rams	11	2025-10-14 16:36:05.947604	7	11	f
2007	1	96	New Orleans Saints	6	2025-10-14 16:36:05.94847	7	0	f
2008	1	97	Cleveland Browns	4	2025-10-14 16:36:05.949163	7	4	f
2009	1	98	New England Patriots	3	2025-10-14 16:36:05.949939	7	3	f
2010	1	99	Kansas City Chiefs	2	2025-10-14 16:36:05.950656	7	2	f
2011	1	100	Philadelphia Eagles	7	2025-10-14 16:36:05.951625	7	7	f
2012	1	101	Carolina Panthers	8	2025-10-14 16:36:05.952302	7	8	f
2013	1	103	Indianapolis Colts	9	2025-10-14 16:36:05.953823	7	9	f
2014	1	104	Washington Commanders	10	2025-10-14 16:36:05.954567	7	0	f
2015	1	105	Arizona Cardinals	12	2025-10-14 16:36:05.955231	7	12	f
2016	1	106	San Francisco 49ers	13	2025-10-14 16:36:05.955889	7	13	f
2017	1	107	Detroit Lions	14	2025-10-14 16:36:05.956534	7	14	f
2018	1	108	Seattle Seahawks	1	2025-10-14 16:36:05.95715	7	1	f
2019	1	102	Denver Broncos	15	2025-10-14 16:36:05.953383	7	0	f
2020	12	94	Pittsburgh Steelers	9	2025-10-15 15:06:44.491652	7	0	f
2021	12	101	New York Jets	7	2025-10-17 06:41:31.441402	7	0	f
2022	12	103	Indianapolis Colts	2	2025-10-17 06:41:31.442808	7	2	f
2023	14	94	Pittsburgh Steelers	11	2025-10-15 19:22:52.122727	7	0	f
2024	14	95	Los Angeles Rams	14	2025-10-17 20:37:11.213812	7	14	f
2025	14	96	Chicago Bears	7	2025-10-17 20:37:11.215685	7	7	f
2026	14	97	Cleveland Browns	6	2025-10-17 20:37:11.216824	7	6	f
2027	14	98	New England Patriots	10	2025-10-17 20:37:11.218241	7	10	f
2028	14	99	Kansas City Chiefs	1	2025-10-17 20:37:11.219288	7	1	f
2029	14	100	Philadelphia Eagles	5	2025-10-17 20:37:11.221339	7	5	f
2030	14	101	Carolina Panthers	2	2025-10-17 20:37:11.222425	7	2	f
2031	14	102	Denver Broncos	12	2025-10-17 20:37:11.227702	7	0	f
2032	14	103	Los Angeles Chargers	13	2025-10-17 20:37:11.232021	7	0	f
2033	14	104	Washington Commanders	4	2025-10-17 20:37:11.239287	7	0	f
2034	14	105	Arizona Cardinals	8	2025-10-17 20:37:11.241272	7	8	f
2035	14	106	San Francisco 49ers	3	2025-10-17 20:37:11.243278	7	3	f
2036	14	107	Detroit Lions	9	2025-10-20 01:35:01.812203	7	9	f
2037	14	108	Seattle Seahawks	15	2025-10-20 01:35:01.813532	7	15	f
2038	13	94	Pittsburgh Steelers	4	2025-10-16 14:12:04.101438	7	0	f
2039	12	95	Jacksonville Jaguars	4	2025-10-17 06:41:31.434292	7	0	f
2040	12	102	Denver Broncos	13	2025-10-17 06:41:31.442102	7	0	f
2041	12	107	Tampa Bay Buccaneers	12	2025-10-17 06:41:31.445728	7	0	f
2042	12	108	Seattle Seahawks	6	2025-10-17 06:41:31.446429	7	6	f
2043	8	94	Cincinnati Bengals	9	2025-10-15 21:21:21.617908	7	9	f
2044	2	94	Pittsburgh Steelers	4	2025-10-15 19:23:35.865109	7	0	f
2045	2	95	Los Angeles Rams	3	2025-10-15 19:23:35.866269	7	3	f
2046	2	96	New Orleans Saints	2	2025-10-19 15:20:54.92759	7	0	f
2047	2	97	Cleveland Browns	1	2025-10-19 15:20:54.928854	7	1	f
2048	2	98	Tennessee Titans	5	2025-10-19 15:20:54.929786	7	0	f
2049	2	99	Las Vegas Raiders	10	2025-10-19 15:20:54.930669	7	0	f
2050	2	100	Minnesota Vikings	6	2025-10-19 15:20:54.931481	7	0	f
2051	2	101	Carolina Panthers	8	2025-10-19 15:20:54.932149	7	8	f
2052	2	102	Denver Broncos	11	2025-10-19 15:20:54.93287	7	0	f
2053	2	103	Indianapolis Colts	14	2025-10-19 15:20:54.93357	7	14	f
2054	2	104	Dallas Cowboys	9	2025-10-19 15:20:54.934275	7	9	f
2055	2	105	Green Bay Packers	15	2025-10-19 15:20:54.934959	7	0	f
2056	2	106	San Francisco 49ers	7	2025-10-19 15:20:54.935665	7	7	f
2057	2	107	Detroit Lions	13	2025-10-19 15:20:54.9363	7	13	f
2058	2	108	Seattle Seahawks	12	2025-10-19 15:20:54.936986	7	12	f
2059	8	96	Chicago Bears	10	2025-10-15 21:21:21.61985	7	10	f
2060	8	97	Cleveland Browns	8	2025-10-15 21:21:21.620625	7	8	f
2061	8	98	New England Patriots	15	2025-10-15 21:21:21.62142	7	15	f
2062	8	99	Las Vegas Raiders	5	2025-10-15 21:21:21.622114	7	0	f
2063	8	100	Minnesota Vikings	11	2025-10-15 21:21:21.622807	7	0	f
2064	8	101	Carolina Panthers	14	2025-10-15 21:21:21.623504	7	14	f
2065	8	102	New York Giants	3	2025-10-15 21:21:21.624219	7	3	f
2066	8	103	Indianapolis Colts	7	2025-10-15 21:21:21.624967	7	7	f
2067	8	104	Washington Commanders	13	2025-10-15 21:21:21.625653	7	0	f
2068	8	105	Green Bay Packers	6	2025-10-15 21:21:21.626319	7	0	f
2069	8	106	Atlanta Falcons	4	2025-10-15 21:21:21.627099	7	0	f
2070	8	107	Tampa Bay Buccaneers	1	2025-10-15 21:21:21.627941	7	0	f
2071	8	108	Seattle Seahawks	12	2025-10-15 21:21:21.62876	7	12	f
2072	8	95	Jacksonville Jaguars	2	2025-10-15 21:21:21.619019	7	0	f
2073	21	94	Pittsburgh Steelers	15	2025-10-15 22:42:06.15686	7	0	f
2074	21	95	Los Angeles Rams	14	2025-10-15 22:42:06.158617	7	14	f
2075	21	96	Chicago Bears	13	2025-10-15 22:42:06.159842	7	13	f
2076	21	97	Miami Dolphins	6	2025-10-15 22:42:06.16115	7	0	f
2077	21	98	New England Patriots	12	2025-10-15 22:42:06.16245	7	12	f
2078	21	99	Las Vegas Raiders	11	2025-10-15 22:42:06.163547	7	0	f
2079	21	100	Philadelphia Eagles	10	2025-10-15 22:42:06.16465	7	10	f
2080	21	101	Carolina Panthers	9	2025-10-15 22:42:06.165599	7	9	f
2081	21	102	New York Giants	8	2025-10-15 22:42:06.166273	7	8	f
2082	21	103	Indianapolis Colts	7	2025-10-15 22:42:06.167001	7	7	f
2083	21	104	Washington Commanders	5	2025-10-15 22:42:06.168514	7	0	f
2084	21	105	Green Bay Packers	4	2025-10-15 22:42:06.169522	7	0	f
2085	21	106	Atlanta Falcons	3	2025-10-15 22:42:06.170501	7	0	f
2086	21	107	Tampa Bay Buccaneers	2	2025-10-15 22:42:06.171498	7	0	f
2087	21	108	Seattle Seahawks	1	2025-10-15 22:42:06.172604	7	1	f
2088	9	94	Cincinnati Bengals	9	2025-10-15 23:34:59.837377	7	9	f
2089	9	95	Los Angeles Rams	3	2025-10-15 23:34:59.838771	7	3	f
2090	9	96	Chicago Bears	7	2025-10-15 23:34:59.83987	7	7	f
2091	9	97	Cleveland Browns	11	2025-10-15 23:34:59.840877	7	11	f
2092	9	98	New England Patriots	15	2025-10-15 23:34:59.841873	7	15	f
2093	9	99	Las Vegas Raiders	10	2025-10-15 23:34:59.842883	7	0	f
2094	9	100	Philadelphia Eagles	13	2025-10-15 23:34:59.843878	7	13	f
2095	9	101	New York Jets	1	2025-10-15 23:34:59.844854	7	0	f
2096	9	102	New York Giants	5	2025-10-15 23:34:59.845814	7	5	f
2097	9	103	Indianapolis Colts	8	2025-10-15 23:34:59.846898	7	8	f
2098	9	104	Dallas Cowboys	12	2025-10-15 23:34:59.847888	7	12	f
2099	9	105	Arizona Cardinals	6	2025-10-15 23:34:59.848834	7	6	f
2100	9	106	Atlanta Falcons	4	2025-10-15 23:34:59.849793	7	0	f
2101	9	107	Detroit Lions	2	2025-10-15 23:34:59.85074	7	2	f
2102	9	108	Seattle Seahawks	14	2025-10-15 23:34:59.851711	7	14	f
2103	23	94	Pittsburgh Steelers	6	2025-10-16 00:12:07.742862	7	0	f
2104	23	95	Los Angeles Rams	3	2025-10-16 00:12:07.744023	7	3	f
2105	23	96	Chicago Bears	4	2025-10-16 00:12:07.744869	7	4	f
2106	23	97	Miami Dolphins	5	2025-10-16 00:12:07.745644	7	0	f
2107	23	98	New England Patriots	7	2025-10-16 00:12:07.746342	7	7	f
2108	23	99	Kansas City Chiefs	8	2025-10-16 00:12:07.747109	7	8	f
2109	23	100	Philadelphia Eagles	14	2025-10-16 00:12:07.747984	7	14	f
2110	23	101	New York Jets	10	2025-10-16 00:12:07.748771	7	0	f
2111	23	102	Denver Broncos	15	2025-10-16 00:12:07.749544	7	0	f
2112	23	103	Indianapolis Colts	13	2025-10-16 00:12:07.750226	7	13	f
2113	23	104	Dallas Cowboys	12	2025-10-16 00:12:07.750939	7	12	f
2114	23	105	Green Bay Packers	11	2025-10-16 00:12:07.751668	7	0	f
2115	23	106	Atlanta Falcons	9	2025-10-16 00:12:07.752424	7	0	f
2116	23	107	Tampa Bay Buccaneers	2	2025-10-16 00:12:07.753148	7	0	f
2117	23	108	Seattle Seahawks	1	2025-10-16 00:12:07.753729	7	1	f
2118	4	94	Pittsburgh Steelers	10	2025-10-16 10:03:21.704864	7	0	f
2119	4	95	Jacksonville Jaguars	5	2025-10-16 10:03:21.706079	7	0	f
2120	4	96	New Orleans Saints	6	2025-10-16 10:03:21.706934	7	0	f
2121	4	97	Miami Dolphins	4	2025-10-16 10:03:21.707711	7	0	f
2122	4	98	New England Patriots	8	2025-10-16 10:03:21.708503	7	8	f
2123	4	99	Las Vegas Raiders	3	2025-10-16 10:03:21.70924	7	0	f
2124	4	100	Philadelphia Eagles	11	2025-10-16 10:03:21.709993	7	11	f
2125	4	101	Carolina Panthers	9	2025-10-16 10:03:21.710793	7	9	f
2126	4	102	Denver Broncos	15	2025-10-16 10:03:21.711546	7	0	f
2127	4	103	Indianapolis Colts	2	2025-10-16 10:03:21.712262	7	2	f
2128	4	104	Washington Commanders	12	2025-10-16 10:03:21.712987	7	0	f
2129	4	105	Green Bay Packers	7	2025-10-16 10:03:21.713677	7	0	f
2130	4	106	San Francisco 49ers	14	2025-10-16 10:03:21.714641	7	14	f
2131	4	107	Detroit Lions	13	2025-10-16 10:03:21.715607	7	13	f
2132	4	108	Seattle Seahawks	1	2025-10-16 10:03:21.716184	7	1	f
2133	5	94	Cincinnati Bengals	7	2025-10-16 18:15:35.233021	7	7	f
2134	18	94	Pittsburgh Steelers	10	2025-10-16 21:42:22.932162	7	0	f
2135	15	94	Pittsburgh Steelers	4	2025-10-16 22:09:26.095099	7	0	f
2136	26	94	Pittsburgh Steelers	6	2025-10-16 22:15:40.265147	7	0	f
2137	22	94	Cincinnati Bengals	7	2025-10-16 22:25:33.734676	7	7	f
2138	22	95	Jacksonville Jaguars	4	2025-10-16 22:25:33.736077	7	0	f
2139	22	96	Chicago Bears	15	2025-10-16 22:25:33.737163	7	15	f
2140	22	97	Cleveland Browns	9	2025-10-16 22:25:33.73808	7	9	f
2141	22	98	New England Patriots	14	2025-10-16 22:25:33.73911	7	14	f
2142	22	99	Las Vegas Raiders	8	2025-10-16 22:25:33.739922	7	0	f
2143	22	100	Philadelphia Eagles	13	2025-10-16 22:25:33.740928	7	13	f
2144	22	101	Carolina Panthers	2	2025-10-16 22:25:33.741931	7	2	f
2145	22	102	Denver Broncos	11	2025-10-16 22:25:33.743052	7	0	f
2146	22	103	Indianapolis Colts	1	2025-10-16 22:25:33.743913	7	1	f
2147	22	104	Washington Commanders	6	2025-10-16 22:25:33.744881	7	0	f
2148	22	105	Green Bay Packers	12	2025-10-16 22:25:33.745874	7	0	f
2149	22	106	San Francisco 49ers	10	2025-10-16 22:25:33.746774	7	10	f
2150	22	107	Detroit Lions	3	2025-10-16 22:25:33.747626	7	3	f
2151	22	108	Seattle Seahawks	5	2025-10-16 22:25:33.748602	7	5	f
2152	10	94	Cincinnati Bengals	10	2025-10-16 22:46:08.671282	7	10	f
2153	17	94	Pittsburgh Steelers	1	2025-10-16 23:07:14.142462	7	0	f
2154	19	94	Pittsburgh Steelers	5	2025-10-16 23:07:33.964386	7	0	f
2155	16	94	Cincinnati Bengals	4	2025-10-16 23:51:19.442482	7	4	f
2156	16	95	Jacksonville Jaguars	7	2025-10-16 23:51:19.443841	7	0	f
2157	16	96	Chicago Bears	10	2025-10-16 23:51:19.444683	7	10	f
2158	16	97	Cleveland Browns	14	2025-10-16 23:51:19.445666	7	14	f
2159	16	98	New England Patriots	8	2025-10-16 23:51:19.446609	7	8	f
2160	16	99	Las Vegas Raiders	1	2025-10-16 23:51:19.447547	7	0	f
2161	16	100	Minnesota Vikings	6	2025-10-16 23:51:19.448459	7	0	f
2162	16	101	New York Jets	2	2025-10-16 23:51:19.44919	7	0	f
2163	16	102	Denver Broncos	9	2025-10-16 23:51:19.449906	7	0	f
2164	16	103	Indianapolis Colts	3	2025-10-16 23:51:19.450614	7	3	f
2165	16	104	Washington Commanders	15	2025-10-16 23:51:19.451296	7	0	f
2166	16	105	Arizona Cardinals	5	2025-10-16 23:51:19.452021	7	5	f
2167	16	106	San Francisco 49ers	12	2025-10-16 23:51:19.452747	7	12	f
2168	16	107	Detroit Lions	11	2025-10-16 23:51:19.453492	7	11	f
2169	16	108	Seattle Seahawks	13	2025-10-16 23:51:19.454034	7	13	f
2170	5	95	Los Angeles Rams	2	2025-10-17 00:38:35.037904	7	2	f
2171	5	96	Chicago Bears	11	2025-10-17 00:38:35.03922	7	11	f
2172	5	97	Cleveland Browns	13	2025-10-17 00:38:35.04022	7	13	f
2173	5	98	Tennessee Titans	1	2025-10-17 00:38:35.041153	7	0	f
2174	5	99	Kansas City Chiefs	3	2025-10-17 00:38:35.042126	7	3	f
2175	5	100	Philadelphia Eagles	12	2025-10-17 00:38:35.04303	7	12	f
2176	5	101	Carolina Panthers	14	2025-10-17 00:38:35.043917	7	14	f
2177	5	102	Denver Broncos	5	2025-10-17 00:38:35.04477	7	0	f
2178	5	103	Indianapolis Colts	15	2025-10-17 00:38:35.045617	7	15	f
2179	5	104	Washington Commanders	9	2025-10-17 00:38:35.046459	7	0	f
2180	5	105	Green Bay Packers	10	2025-10-17 00:38:35.047285	7	0	f
2181	5	106	San Francisco 49ers	6	2025-10-17 00:38:35.048147	7	6	f
2182	5	107	Detroit Lions	4	2025-10-17 00:38:35.048992	7	4	f
2183	5	108	Seattle Seahawks	8	2025-10-17 00:38:35.049657	7	8	f
2184	12	96	Chicago Bears	8	2025-10-17 06:41:31.436995	7	8	f
2185	12	97	Cleveland Browns	3	2025-10-17 06:41:31.43839	7	3	f
2186	12	98	New England Patriots	14	2025-10-17 06:41:31.439301	7	14	f
2187	12	99	Kansas City Chiefs	11	2025-10-17 06:41:31.440147	7	11	f
2188	12	100	Minnesota Vikings	5	2025-10-17 06:41:31.440942	7	0	f
2189	12	104	Washington Commanders	15	2025-10-17 06:41:31.443838	7	0	f
2190	12	105	Green Bay Packers	10	2025-10-17 06:41:31.444584	7	0	f
2191	12	106	Atlanta Falcons	1	2025-10-17 06:41:31.445332	7	0	f
2192	13	95	Los Angeles Rams	3	2025-10-18 01:43:16.072076	7	3	f
2193	13	96	New Orleans Saints	5	2025-10-18 01:43:16.073179	7	0	f
2194	13	97	Miami Dolphins	11	2025-10-18 01:43:16.074	7	0	f
2195	13	98	Tennessee Titans	6	2025-10-18 01:43:16.074731	7	0	f
2196	13	99	Las Vegas Raiders	12	2025-10-18 01:43:16.075453	7	0	f
2197	13	100	Minnesota Vikings	10	2025-10-18 01:43:16.076133	7	0	f
2198	13	101	Carolina Panthers	13	2025-10-18 01:43:16.076886	7	13	f
2199	13	102	Denver Broncos	15	2025-10-18 01:43:16.077621	7	0	f
2200	13	103	Los Angeles Chargers	2	2025-10-18 01:43:16.078248	7	0	f
2201	13	104	Washington Commanders	9	2025-10-18 01:43:16.078909	7	0	f
2202	13	105	Arizona Cardinals	7	2025-10-18 01:43:16.079612	7	7	f
2203	13	106	San Francisco 49ers	1	2025-10-18 01:43:16.080233	7	1	f
2204	13	107	Tampa Bay Buccaneers	14	2025-10-20 02:28:26.803851	7	0	f
2205	13	108	Seattle Seahawks	8	2025-10-20 02:28:26.805281	7	8	f
2206	15	95	Jacksonville Jaguars	15	2025-10-18 23:28:30.883016	7	0	f
2207	15	96	Chicago Bears	8	2025-10-19 15:05:22.790861	7	8	f
2208	15	97	Cleveland Browns	1	2025-10-19 15:05:22.792228	7	1	f
2209	15	98	New England Patriots	14	2025-10-19 15:05:22.793225	7	14	f
2210	15	99	Las Vegas Raiders	3	2025-10-19 15:05:22.794116	7	0	f
2211	15	100	Philadelphia Eagles	2	2025-10-19 15:05:22.79497	7	2	f
2212	15	101	Carolina Panthers	13	2025-10-19 15:05:22.795812	7	13	f
2213	15	102	Denver Broncos	12	2025-10-19 15:05:22.796633	7	0	f
2214	15	103	Indianapolis Colts	10	2025-10-19 15:05:22.797441	7	10	f
2215	15	104	Dallas Cowboys	6	2025-10-19 15:05:22.798228	7	6	f
2216	15	105	Arizona Cardinals	5	2025-10-19 15:05:22.799044	7	5	f
2217	15	106	San Francisco 49ers	9	2025-10-19 15:05:22.79987	7	9	f
2218	15	107	Tampa Bay Buccaneers	7	2025-10-19 15:05:22.800679	7	0	f
2219	15	108	Seattle Seahawks	11	2025-10-19 15:05:22.801476	7	11	f
2220	19	95	Los Angeles Rams	6	2025-10-19 02:06:31.488769	7	6	f
2221	17	95	Los Angeles Rams	2	2025-10-19 02:08:29.83719	7	2	f
2222	20	95	Jacksonville Jaguars	9	2025-10-19 03:15:47.837682	7	0	f
2223	20	96	New Orleans Saints	4	2025-10-19 03:15:47.838984	7	0	f
2224	20	98	New England Patriots	6	2025-10-19 03:15:47.841009	7	6	f
2225	20	99	Las Vegas Raiders	2	2025-10-19 03:15:47.842107	7	0	f
2226	20	102	New York Giants	14	2025-10-19 03:15:47.845246	7	14	f
2227	20	104	Dallas Cowboys	13	2025-10-19 03:15:47.847603	7	13	f
2228	20	107	Tampa Bay Buccaneers	10	2025-10-19 03:15:47.850704	7	0	f
2229	20	108	Seattle Seahawks	1	2025-10-19 03:15:47.851593	7	1	f
2230	20	97	Miami Dolphins	5	2025-10-19 03:15:47.839904	7	0	f
2231	20	101	Carolina Panthers	3	2025-10-19 03:15:47.844218	7	3	f
2232	20	100	Philadelphia Eagles	11	2025-10-19 03:15:47.843175	7	11	f
2233	20	103	Los Angeles Chargers	12	2025-10-19 03:15:47.846828	7	0	f
2234	20	105	Arizona Cardinals	7	2025-10-19 03:15:47.849148	7	7	f
2235	20	106	San Francisco 49ers	8	2025-10-19 03:15:47.850185	7	8	f
2236	26	95	Los Angeles Rams	7	2025-10-19 04:45:26.789263	7	7	f
2237	18	95	Los Angeles Rams	5	2025-10-19 08:58:53.347554	7	5	f
2238	18	96	Chicago Bears	1	2025-10-19 08:58:53.348696	7	1	f
2239	18	97	Miami Dolphins	15	2025-10-19 08:58:53.349653	7	0	f
2240	18	98	New England Patriots	2	2025-10-19 08:58:53.350534	7	2	f
2241	18	99	Las Vegas Raiders	14	2025-10-19 08:58:53.351386	7	0	f
2242	18	100	Minnesota Vikings	3	2025-10-19 08:58:53.352212	7	0	f
2243	18	101	Carolina Panthers	13	2025-10-19 08:58:53.353039	7	13	f
2244	18	102	New York Giants	4	2025-10-19 08:58:53.353796	7	4	f
2245	18	103	Indianapolis Colts	12	2025-10-19 08:58:53.354539	7	12	f
2246	18	104	Dallas Cowboys	11	2025-10-19 08:58:53.355535	7	11	f
2247	18	105	Green Bay Packers	9	2025-10-19 08:58:53.35644	7	0	f
2248	18	106	Atlanta Falcons	8	2025-10-19 08:58:53.357139	7	0	f
2249	18	107	Detroit Lions	7	2025-10-19 08:58:53.357849	7	7	f
2250	18	108	Seattle Seahawks	6	2025-10-19 08:58:53.358505	7	6	f
2251	10	95	Los Angeles Rams	3	2025-10-19 10:28:16.87039	7	3	f
2252	17	96	New Orleans Saints	7	2025-10-19 13:58:44.032716	7	0	f
2253	17	97	Cleveland Browns	3	2025-10-19 13:58:44.033769	7	3	f
2254	17	98	New England Patriots	12	2025-10-19 13:58:44.034531	7	12	f
2255	17	99	Kansas City Chiefs	6	2025-10-19 13:58:44.03521	7	6	f
2256	17	100	Philadelphia Eagles	10	2025-10-19 13:58:44.03594	7	10	f
2257	17	101	Carolina Panthers	9	2025-10-19 13:58:44.036641	7	9	f
2258	17	102	New York Giants	11	2025-10-19 13:58:44.037282	7	11	f
2259	17	103	Indianapolis Colts	13	2025-10-19 13:58:44.037974	7	13	f
2260	17	104	Dallas Cowboys	4	2025-10-19 13:58:44.038638	7	4	f
2261	17	105	Green Bay Packers	15	2025-10-19 13:58:44.039266	7	0	f
2262	17	106	Atlanta Falcons	5	2025-10-19 13:58:44.039954	7	0	f
2263	17	107	Tampa Bay Buccaneers	8	2025-10-19 13:58:44.040628	7	0	f
2264	17	108	Seattle Seahawks	14	2025-10-19 13:58:44.041283	7	14	f
2265	26	96	Chicago Bears	8	2025-10-19 14:48:54.464683	7	8	f
2266	26	97	Miami Dolphins	4	2025-10-19 14:48:54.465862	7	0	f
2267	26	98	New England Patriots	10	2025-10-19 14:48:54.466672	7	10	f
2268	26	99	Kansas City Chiefs	1	2025-10-19 14:48:54.467548	7	1	f
2269	26	100	Philadelphia Eagles	5	2025-10-19 14:48:54.468498	7	5	f
2270	26	101	Carolina Panthers	11	2025-10-19 14:48:54.469257	7	11	f
2271	26	102	New York Giants	2	2025-10-19 14:48:54.470047	7	2	f
2272	26	103	Indianapolis Colts	15	2025-10-19 14:48:54.470754	7	15	f
2273	26	104	Washington Commanders	14	2025-10-19 14:48:54.471505	7	0	f
2274	26	105	Green Bay Packers	13	2025-10-19 14:48:54.472393	7	0	f
2275	26	106	Atlanta Falcons	9	2025-10-19 14:48:54.473252	7	0	f
2276	26	107	Tampa Bay Buccaneers	12	2025-10-19 14:48:54.474123	7	0	f
2277	26	108	Seattle Seahawks	3	2025-10-19 14:48:54.474743	7	3	f
2278	19	96	New Orleans Saints	4	2025-10-19 14:54:39.208862	7	0	f
2279	19	97	Cleveland Browns	8	2025-10-19 14:54:39.210232	7	8	f
2280	19	98	New England Patriots	7	2025-10-19 14:54:39.211191	7	7	f
2281	19	99	Kansas City Chiefs	10	2025-10-19 14:54:39.212176	7	10	f
2282	19	100	Philadelphia Eagles	14	2025-10-19 14:54:39.213178	7	14	f
2283	19	101	Carolina Panthers	1	2025-10-19 14:54:39.21417	7	1	f
2284	19	102	Denver Broncos	11	2025-10-19 14:54:39.215153	7	0	f
2285	19	103	Indianapolis Colts	13	2025-10-19 14:54:39.216154	7	13	f
2286	19	104	Dallas Cowboys	9	2025-10-19 14:54:39.217057	7	9	f
2287	19	105	Green Bay Packers	12	2025-10-19 14:54:39.21809	7	0	f
2288	19	106	Atlanta Falcons	3	2025-10-19 14:54:39.218946	7	0	f
2289	19	107	Tampa Bay Buccaneers	2	2025-10-19 14:54:39.220013	7	0	f
2290	19	108	Seattle Seahawks	15	2025-10-19 14:54:39.220735	7	15	f
2291	10	96	New Orleans Saints	14	2025-10-19 14:55:08.598837	7	0	f
2292	10	97	Cleveland Browns	2	2025-10-19 14:55:08.599884	7	2	f
2293	10	98	New England Patriots	8	2025-10-19 14:55:08.600678	7	8	f
2294	10	99	Las Vegas Raiders	9	2025-10-19 14:55:08.601415	7	0	f
2295	10	100	Philadelphia Eagles	11	2025-10-19 14:55:08.602107	7	11	f
2296	10	101	Carolina Panthers	7	2025-10-19 14:55:08.602833	7	7	f
2297	10	102	Denver Broncos	15	2025-10-19 14:55:08.603556	7	0	f
2298	10	103	Indianapolis Colts	13	2025-10-19 14:55:08.604296	7	13	f
2299	10	104	Dallas Cowboys	6	2025-10-19 14:55:08.605212	7	6	f
2300	10	105	Green Bay Packers	5	2025-10-19 14:55:08.605924	7	0	f
2301	10	106	San Francisco 49ers	4	2025-10-19 14:55:08.606625	7	4	f
2302	10	107	Tampa Bay Buccaneers	1	2025-10-19 14:55:08.607279	7	0	f
2303	10	108	Seattle Seahawks	12	2025-10-19 14:55:08.60783	7	12	f
2304	12	109	Los Angeles Chargers	13	2025-10-22 14:46:55.555527	8	13	f
2305	12	112	Cleveland Browns	8	2025-10-25 21:27:35.131305	8	0	f
2306	12	116	San Francisco 49ers	9	2025-10-25 21:27:35.134445	8	0	f
2307	12	118	Denver Broncos	11	2025-10-25 21:27:35.136017	8	11	f
2308	12	120	Pittsburgh Steelers	3	2025-10-25 21:27:35.137482	8	0	f
2309	22	109	Los Angeles Chargers	7	2025-10-21 15:29:27.254165	8	7	f
2310	22	110	Atlanta Falcons	3	2025-10-21 15:29:27.256071	8	0	f
2311	22	111	Cincinnati Bengals	4	2025-10-21 15:29:27.257235	8	0	f
2312	22	112	Cleveland Browns	2	2025-10-21 15:29:27.258333	8	0	f
2313	22	113	New York Giants	6	2025-10-21 15:29:27.259421	8	0	f
2314	22	114	Buffalo Bills	13	2025-10-21 15:29:27.260582	8	13	f
2315	22	115	Baltimore Ravens	10	2025-10-21 15:29:27.261802	8	10	f
2316	22	116	San Francisco 49ers	8	2025-10-21 15:29:27.262924	8	0	f
2317	22	117	Tampa Bay Buccaneers	12	2025-10-21 15:29:27.264603	8	12	f
2318	22	118	Denver Broncos	11	2025-10-21 15:29:27.265638	8	11	f
2319	22	119	Indianapolis Colts	5	2025-10-21 15:29:27.266633	8	5	f
2320	22	120	Green Bay Packers	9	2025-10-21 15:29:27.269081	8	9	f
2321	22	121	Kansas City Chiefs	1	2025-10-21 15:29:27.270108	8	1	f
2322	1	109	Los Angeles Chargers	8	2025-10-21 15:59:54.078052	8	8	f
2323	1	110	Atlanta Falcons	5	2025-10-21 15:59:54.079097	8	0	f
2324	1	111	Cincinnati Bengals	4	2025-10-21 15:59:54.079982	8	0	f
2325	1	112	New England Patriots	10	2025-10-21 15:59:54.080798	8	10	f
2326	1	113	Philadelphia Eagles	9	2025-10-21 15:59:54.081606	8	9	f
2327	1	114	Buffalo Bills	7	2025-10-21 15:59:54.082463	8	7	f
2328	1	115	Baltimore Ravens	6	2025-10-21 15:59:54.08324	8	6	f
2329	1	116	San Francisco 49ers	3	2025-10-21 15:59:54.083971	8	0	f
2330	1	117	Tampa Bay Buccaneers	11	2025-10-21 15:59:54.084715	8	11	f
2331	1	118	Denver Broncos	13	2025-10-21 15:59:54.085412	8	13	f
2332	1	119	Indianapolis Colts	2	2025-10-21 15:59:54.08611	8	2	f
2333	1	120	Green Bay Packers	1	2025-10-21 15:59:54.087032	8	1	f
2334	1	121	Kansas City Chiefs	12	2025-10-21 15:59:54.08767	8	12	f
2335	4	109	Los Angeles Chargers	10	2025-10-22 03:49:42.466952	8	10	f
2336	4	110	Atlanta Falcons	7	2025-10-22 03:49:42.46817	8	0	f
2337	4	111	Cincinnati Bengals	5	2025-10-22 03:49:42.469067	8	0	f
2338	4	112	New England Patriots	3	2025-10-22 03:49:42.469852	8	3	f
2339	4	113	Philadelphia Eagles	8	2025-10-22 03:49:42.470617	8	8	f
2340	4	114	Buffalo Bills	11	2025-10-22 03:49:42.471319	8	11	f
2341	4	115	Chicago Bears	9	2025-10-22 03:49:42.472061	8	0	f
2342	4	116	San Francisco 49ers	12	2025-10-22 03:49:42.472894	8	0	f
2343	4	117	Tampa Bay Buccaneers	4	2025-10-22 03:49:42.473721	8	4	f
2344	4	118	Denver Broncos	13	2025-10-22 03:49:42.474531	8	13	f
2345	4	119	Indianapolis Colts	2	2025-10-22 03:49:42.475331	8	2	f
2346	4	120	Green Bay Packers	6	2025-10-22 03:49:42.476155	8	6	f
2347	4	121	Washington Commanders	1	2025-10-22 03:49:42.476811	8	0	f
2348	14	109	Los Angeles Chargers	6	2025-10-23 19:24:45.910575	8	6	f
2349	14	110	Atlanta Falcons	13	2025-10-26 16:58:57.154483	8	0	f
2350	14	111	Cincinnati Bengals	11	2025-10-26 16:58:57.156416	8	0	f
2351	14	112	New England Patriots	10	2025-10-26 16:58:57.15765	8	10	f
2352	14	113	New York Giants	1	2025-10-26 16:58:57.158786	8	0	f
2353	14	114	Carolina Panthers	3	2025-10-26 16:58:57.159872	8	0	f
2354	14	115	Chicago Bears	8	2025-10-26 16:58:57.160953	8	0	f
2355	14	116	San Francisco 49ers	4	2025-10-26 16:58:57.16198	8	0	f
2356	14	117	Tampa Bay Buccaneers	9	2025-10-26 16:58:57.162999	8	9	f
2357	14	118	Denver Broncos	5	2025-10-26 16:58:57.164011	8	5	f
2358	14	119	Indianapolis Colts	12	2025-10-26 16:58:57.165015	8	12	f
2359	14	120	Green Bay Packers	2	2025-10-26 16:58:57.166022	8	2	f
2360	14	121	Kansas City Chiefs	7	2025-10-26 16:58:57.167064	8	7	f
2361	12	110	Atlanta Falcons	6	2025-10-25 21:27:35.129296	8	0	f
2362	12	111	Cincinnati Bengals	12	2025-10-25 21:27:35.130467	8	0	f
2363	12	113	Philadelphia Eagles	4	2025-10-25 21:27:35.13215	8	4	f
2364	12	114	Buffalo Bills	5	2025-10-25 21:27:35.132923	8	5	f
2365	12	115	Chicago Bears	7	2025-10-25 21:27:35.1337	8	0	f
2366	12	117	Tampa Bay Buccaneers	10	2025-10-25 21:27:35.135238	8	10	f
2367	12	119	Tennessee Titans	2	2025-10-25 21:27:35.136725	8	0	f
2368	12	121	Washington Commanders	1	2025-10-25 21:27:35.138183	8	0	f
2369	13	109	Minnesota Vikings	5	2025-10-22 17:43:44.021257	8	0	f
2370	24	109	Los Angeles Chargers	9	2025-10-22 19:06:27.279388	8	9	f
2371	24	110	Atlanta Falcons	7	2025-10-22 19:06:27.280864	8	0	f
2372	24	111	New York Jets	8	2025-10-22 19:06:27.283504	8	8	f
2373	24	112	New England Patriots	6	2025-10-22 19:06:27.285022	8	6	f
2374	24	113	New York Giants	3	2025-10-22 19:06:27.286529	8	0	f
2375	24	114	Buffalo Bills	11	2025-10-22 19:06:27.28793	8	11	f
2376	24	115	Chicago Bears	4	2025-10-22 19:06:27.290878	8	0	f
2377	24	116	San Francisco 49ers	12	2025-10-22 19:06:27.294105	8	0	f
2378	24	117	Tampa Bay Buccaneers	13	2025-10-22 19:06:27.295069	8	13	f
2379	24	118	Dallas Cowboys	10	2025-10-22 19:06:27.296002	8	0	f
2380	24	119	Tennessee Titans	1	2025-10-22 19:06:27.296861	8	0	f
2381	24	120	Pittsburgh Steelers	5	2025-10-22 19:06:27.297773	8	0	f
2382	24	121	Kansas City Chiefs	2	2025-10-22 19:06:27.298708	8	2	f
2383	21	109	Los Angeles Chargers	13	2025-10-22 23:09:37.314305	8	13	f
2384	21	110	Atlanta Falcons	6	2025-10-22 23:09:37.320117	8	0	f
2385	21	111	Cincinnati Bengals	7	2025-10-22 23:09:37.324566	8	0	f
2386	21	112	New England Patriots	8	2025-10-22 23:09:37.325721	8	8	f
2387	21	113	New York Giants	9	2025-10-22 23:09:37.326894	8	0	f
2388	21	114	Buffalo Bills	5	2025-10-22 23:09:37.328263	8	5	f
2389	21	115	Chicago Bears	10	2025-10-22 23:09:37.329389	8	0	f
2390	21	116	San Francisco 49ers	11	2025-10-22 23:09:37.330515	8	0	f
2391	21	117	Tampa Bay Buccaneers	12	2025-10-22 23:09:37.331639	8	12	f
2392	21	118	Denver Broncos	3	2025-10-22 23:09:37.332918	8	3	f
2393	21	119	Tennessee Titans	4	2025-10-22 23:09:37.334293	8	0	f
2394	21	120	Pittsburgh Steelers	2	2025-10-22 23:09:37.335241	8	0	f
2395	21	121	Kansas City Chiefs	1	2025-10-22 23:09:37.33612	8	1	f
2396	23	110	Atlanta Falcons	3	2025-10-23 00:16:45.649932	8	0	f
2397	23	111	Cincinnati Bengals	2	2025-10-23 00:16:45.650889	8	0	f
2398	23	112	Cleveland Browns	1	2025-10-23 00:16:45.651779	8	0	f
2399	23	113	Philadelphia Eagles	6	2025-10-23 00:16:45.652655	8	6	f
2400	23	114	Buffalo Bills	12	2025-10-23 00:16:45.65351	8	12	f
2401	23	115	Chicago Bears	7	2025-10-23 00:16:45.654327	8	0	f
2402	23	116	Houston Texans	11	2025-10-23 00:16:45.655178	8	11	f
2403	23	117	Tampa Bay Buccaneers	5	2025-10-23 00:16:45.65601	8	5	f
2404	23	118	Denver Broncos	13	2025-10-23 00:16:45.656893	8	13	f
2405	23	119	Indianapolis Colts	4	2025-10-23 00:16:45.657724	8	4	f
2406	23	120	Green Bay Packers	9	2025-10-23 00:16:45.658551	8	9	f
2407	23	121	Washington Commanders	8	2025-10-23 00:16:45.659377	8	0	f
2408	23	109	Minnesota Vikings	10	2025-10-23 00:16:45.64913	8	0	f
2409	18	109	Minnesota Vikings	5	2025-10-23 03:29:26.594887	8	0	f
2410	8	109	Minnesota Vikings	7	2025-10-23 04:24:46.924779	8	0	f
2411	8	110	Atlanta Falcons	12	2025-10-23 04:24:46.926408	8	0	f
2412	8	111	Cincinnati Bengals	10	2025-10-23 04:24:46.927699	8	0	f
2413	8	112	New England Patriots	13	2025-10-23 04:24:46.928808	8	13	f
2414	8	113	New York Giants	5	2025-10-23 04:24:46.929954	8	0	f
2415	8	114	Carolina Panthers	6	2025-10-23 04:24:46.931038	8	0	f
2416	8	115	Chicago Bears	4	2025-10-23 04:24:46.932033	8	0	f
2417	8	116	San Francisco 49ers	1	2025-10-23 04:24:46.933054	8	0	f
2418	8	117	Tampa Bay Buccaneers	11	2025-10-23 04:24:46.934075	8	11	f
2419	8	118	Denver Broncos	8	2025-10-23 04:24:46.935043	8	8	f
2420	8	119	Indianapolis Colts	9	2025-10-23 04:24:46.935986	8	9	f
2421	8	120	Green Bay Packers	2	2025-10-23 04:24:46.936915	8	2	f
2422	8	121	Washington Commanders	3	2025-10-23 04:24:46.937836	8	0	f
2423	2	109	Minnesota Vikings	3	2025-10-23 10:23:45.514335	8	0	f
2424	2	110	Atlanta Falcons	2	2025-10-23 10:23:45.515508	8	0	f
2425	2	111	Cincinnati Bengals	11	2025-10-23 10:23:45.516314	8	0	f
2426	2	112	Cleveland Browns	4	2025-10-23 10:23:45.517138	8	0	f
2427	2	113	New York Giants	6	2025-10-23 10:23:45.517922	8	0	f
2428	2	114	Buffalo Bills	5	2025-10-23 10:23:45.518641	8	5	f
2429	2	115	Baltimore Ravens	8	2025-10-23 10:23:45.519384	8	8	f
2430	2	116	Houston Texans	9	2025-10-23 10:23:45.520141	8	9	f
2431	2	117	Tampa Bay Buccaneers	12	2025-10-23 10:23:45.52095	8	12	f
2432	2	118	Denver Broncos	13	2025-10-23 10:23:45.521819	8	13	f
2433	2	119	Indianapolis Colts	1	2025-10-23 10:23:45.522714	8	1	f
2434	2	120	Green Bay Packers	10	2025-10-23 10:23:45.523438	8	10	f
2435	2	121	Kansas City Chiefs	7	2025-10-23 10:23:45.524092	8	7	f
2436	9	109	Los Angeles Chargers	10	2025-10-23 15:44:06.625775	8	10	f
2437	9	110	Atlanta Falcons	11	2025-10-23 15:44:06.627323	8	0	f
2438	9	111	New York Jets	1	2025-10-23 15:44:06.628654	8	1	f
2439	9	112	Cleveland Browns	2	2025-10-23 15:44:06.629804	8	0	f
2440	9	113	New York Giants	4	2025-10-23 15:44:06.63091	8	0	f
2441	9	114	Buffalo Bills	7	2025-10-23 15:44:06.632014	8	7	f
2442	9	115	Baltimore Ravens	3	2025-10-23 15:44:06.633114	8	3	f
2443	9	116	San Francisco 49ers	12	2025-10-23 15:44:06.634225	8	0	f
2444	9	117	Tampa Bay Buccaneers	13	2025-10-23 15:44:06.63531	8	13	f
2445	9	118	Dallas Cowboys	6	2025-10-23 15:44:06.636335	8	0	f
2446	9	119	Indianapolis Colts	9	2025-10-23 15:44:06.637385	8	9	f
2447	9	120	Green Bay Packers	5	2025-10-23 15:44:06.63842	8	5	f
2448	9	121	Washington Commanders	8	2025-10-23 15:44:06.639227	8	0	f
2449	20	109	Los Angeles Chargers	2	2025-10-23 16:06:33.365582	8	2	f
2450	20	110	Miami Dolphins	1	2025-10-26 13:59:47.070082	8	1	f
2451	20	111	Cincinnati Bengals	3	2025-10-26 13:59:47.07146	8	0	f
2452	5	109	Los Angeles Chargers	9	2025-10-23 18:05:48.188964	8	9	f
2453	5	110	Atlanta Falcons	12	2025-10-23 18:05:48.190639	8	0	f
2454	5	111	New York Jets	1	2025-10-23 18:05:48.191972	8	1	f
2455	5	112	New England Patriots	10	2025-10-23 18:05:48.193255	8	10	f
2456	5	113	Philadelphia Eagles	5	2025-10-23 18:05:48.194473	8	5	f
2457	5	114	Buffalo Bills	13	2025-10-23 18:05:48.195654	8	13	f
2458	5	115	Baltimore Ravens	2	2025-10-23 18:05:48.196907	8	2	f
2459	5	116	San Francisco 49ers	8	2025-10-23 18:05:48.198028	8	0	f
2460	5	117	Tampa Bay Buccaneers	6	2025-10-23 18:05:48.199103	8	6	f
2461	5	118	Denver Broncos	3	2025-10-23 18:05:48.200233	8	3	f
2462	5	119	Indianapolis Colts	7	2025-10-23 18:05:48.201377	8	7	f
2463	5	120	Pittsburgh Steelers	11	2025-10-23 18:05:48.202516	8	0	f
2464	5	121	Washington Commanders	4	2025-10-23 18:05:48.203421	8	0	f
2465	15	109	Los Angeles Chargers	4	2025-10-23 22:35:58.874407	8	4	f
2466	10	109	Minnesota Vikings	7	2025-10-23 23:56:55.466569	8	0	f
2467	17	109	Los Angeles Chargers	1	2025-10-23 22:56:51.957856	8	1	f
2468	16	109	Los Angeles Chargers	10	2025-10-23 22:56:58.80163	8	10	f
2469	16	110	Atlanta Falcons	9	2025-10-23 22:56:58.802576	8	0	f
2470	16	111	Cincinnati Bengals	13	2025-10-23 22:56:58.803349	8	0	f
2471	16	112	Cleveland Browns	8	2025-10-23 22:56:58.804153	8	0	f
2472	16	113	New York Giants	3	2025-10-23 22:56:58.804867	8	0	f
2473	16	114	Carolina Panthers	2	2025-10-23 22:56:58.805657	8	0	f
2474	16	115	Baltimore Ravens	12	2025-10-23 22:56:58.806471	8	12	f
2475	16	116	Houston Texans	1	2025-10-23 22:56:58.807159	8	1	f
2476	16	117	Tampa Bay Buccaneers	11	2025-10-23 22:56:58.80794	8	11	f
2477	16	118	Denver Broncos	7	2025-10-23 22:56:58.808639	8	7	f
2478	16	119	Indianapolis Colts	5	2025-10-23 22:56:58.809413	8	5	f
2479	16	120	Pittsburgh Steelers	6	2025-10-23 22:56:58.810145	8	0	f
2480	16	121	Washington Commanders	4	2025-10-23 22:56:58.81072	8	0	f
2481	19	109	Los Angeles Chargers	4	2025-10-23 23:27:48.09227	8	4	f
2482	26	109	Los Angeles Chargers	8	2025-10-23 23:47:26.976083	8	8	f
2483	20	113	New York Giants	11	2025-10-26 13:59:47.073039	8	0	f
2484	20	114	Carolina Panthers	10	2025-10-26 13:59:47.074115	8	0	f
2485	20	116	San Francisco 49ers	13	2025-10-26 13:59:47.075963	8	0	f
2486	20	118	Dallas Cowboys	12	2025-10-26 13:59:47.077557	8	0	f
2487	20	112	New England Patriots	9	2025-10-26 13:59:47.072172	8	9	f
2488	20	115	Chicago Bears	8	2025-10-26 13:59:47.075057	8	0	f
2489	20	117	Tampa Bay Buccaneers	7	2025-10-26 13:59:47.076806	8	7	f
2490	20	119	Indianapolis Colts	4	2025-10-26 13:59:47.078236	8	4	f
2491	20	120	Pittsburgh Steelers	5	2025-10-26 13:59:47.079121	8	0	f
2492	20	121	Washington Commanders	6	2025-10-26 13:59:47.079883	8	0	f
2493	18	110	Atlanta Falcons	7	2025-10-26 01:54:48.473596	8	0	f
2494	18	111	Cincinnati Bengals	8	2025-10-26 01:54:48.474609	8	0	f
2495	18	112	New England Patriots	4	2025-10-26 01:54:48.475348	8	4	f
2496	18	113	Philadelphia Eagles	6	2025-10-26 01:54:48.47614	8	6	f
2497	18	114	Buffalo Bills	3	2025-10-26 01:54:48.476871	8	3	f
2498	18	115	Chicago Bears	9	2025-10-26 01:54:48.477812	8	0	f
2499	18	116	San Francisco 49ers	10	2025-10-26 01:54:48.478742	8	0	f
2500	18	117	Tampa Bay Buccaneers	11	2025-10-26 01:54:48.479658	8	11	f
2501	18	118	Dallas Cowboys	2	2025-10-26 01:54:48.480336	8	0	f
2502	18	119	Indianapolis Colts	12	2025-10-26 01:54:48.481057	8	12	f
2503	18	120	Green Bay Packers	1	2025-10-26 01:54:48.481763	8	1	f
2504	18	121	Kansas City Chiefs	13	2025-10-26 01:54:48.482285	8	13	f
2505	13	110	Atlanta Falcons	9	2025-10-26 14:24:05.24071	8	0	f
2506	13	111	Cincinnati Bengals	7	2025-10-26 14:24:05.241983	8	0	f
2507	13	112	Cleveland Browns	1	2025-10-26 14:24:05.242918	8	0	f
2508	13	113	New York Giants	3	2025-10-26 14:24:05.243803	8	0	f
2509	13	114	Buffalo Bills	8	2025-10-26 14:24:05.244658	8	8	f
2510	13	115	Chicago Bears	10	2025-10-26 14:24:05.245517	8	0	f
2511	13	116	San Francisco 49ers	13	2025-10-26 14:24:05.246331	8	0	f
2512	13	117	Tampa Bay Buccaneers	12	2025-10-26 14:24:05.247172	8	12	f
2513	13	118	Denver Broncos	11	2025-10-26 14:24:05.248013	8	11	f
2514	13	119	Indianapolis Colts	6	2025-10-26 14:24:05.24884	8	6	f
2515	13	120	Green Bay Packers	2	2025-10-26 14:24:05.249676	8	2	f
2516	13	121	Kansas City Chiefs	4	2025-10-26 14:24:05.250411	8	4	f
2517	15	110	Atlanta Falcons	5	2025-10-26 06:41:57.775905	8	0	f
2518	15	111	Cincinnati Bengals	9	2025-10-26 06:41:57.777263	8	0	f
2519	15	112	New England Patriots	11	2025-10-26 06:41:57.778378	8	11	f
2520	15	113	New York Giants	1	2025-10-26 06:41:57.779469	8	0	f
2521	15	114	Buffalo Bills	10	2025-10-26 06:41:57.780569	8	10	f
2522	15	115	Chicago Bears	3	2025-10-26 06:41:57.781754	8	0	f
2523	15	116	San Francisco 49ers	7	2025-10-26 06:41:57.782849	8	0	f
2524	15	117	Tampa Bay Buccaneers	12	2025-10-26 06:41:57.783974	8	12	f
2525	15	118	Denver Broncos	13	2025-10-26 06:41:57.785068	8	13	f
2526	15	119	Indianapolis Colts	8	2025-10-26 06:41:57.786161	8	8	f
2527	15	120	Green Bay Packers	6	2025-10-26 06:41:57.787247	8	6	f
2528	15	121	Kansas City Chiefs	2	2025-10-26 06:41:57.788088	8	2	f
2529	10	110	Atlanta Falcons	6	2025-10-26 14:24:48.922271	8	0	f
2530	10	111	Cincinnati Bengals	5	2025-10-26 14:24:48.923915	8	0	f
2531	10	112	Cleveland Browns	9	2025-10-26 14:24:48.925054	8	0	f
2532	10	113	New York Giants	13	2025-10-26 14:24:48.92599	8	0	f
2533	10	114	Buffalo Bills	4	2025-10-26 14:24:48.926887	8	4	f
2534	10	115	Chicago Bears	12	2025-10-26 14:24:48.927779	8	0	f
2535	10	116	San Francisco 49ers	3	2025-10-26 14:24:48.928697	8	0	f
2536	10	117	Tampa Bay Buccaneers	10	2025-10-26 14:24:48.929645	8	10	f
2537	10	118	Denver Broncos	11	2025-10-26 14:24:48.930646	8	11	f
2538	10	119	Tennessee Titans	2	2025-10-26 14:24:48.931526	8	0	f
2539	10	120	Green Bay Packers	8	2025-10-26 23:40:03.097551	8	8	f
2540	10	121	Kansas City Chiefs	1	2025-10-26 23:40:03.098674	8	1	f
2541	26	110	Atlanta Falcons	2	2025-10-26 14:29:06.153643	8	0	f
2542	26	111	Cincinnati Bengals	5	2025-10-26 14:29:06.155316	8	0	f
2543	26	112	New England Patriots	11	2025-10-26 14:29:06.156441	8	11	f
2544	26	113	New York Giants	3	2025-10-26 14:29:06.157504	8	0	f
2545	26	114	Buffalo Bills	13	2025-10-26 14:29:06.15857	8	13	f
2546	26	115	Baltimore Ravens	6	2025-10-26 14:29:06.159972	8	6	f
2547	26	116	San Francisco 49ers	10	2025-10-26 14:29:06.161576	8	0	f
2548	26	117	Tampa Bay Buccaneers	12	2025-10-26 14:29:06.162848	8	12	f
2549	26	118	Dallas Cowboys	7	2025-10-26 14:29:06.164524	8	0	f
2550	26	119	Indianapolis Colts	1	2025-10-26 14:29:06.165712	8	1	f
2551	26	120	Green Bay Packers	9	2025-10-26 14:29:06.167006	8	9	f
2552	26	121	Kansas City Chiefs	4	2025-10-26 14:29:06.168204	8	4	f
2553	17	110	Atlanta Falcons	9	2025-10-26 16:08:10.953569	8	0	f
2554	17	111	New York Jets	2	2025-10-26 16:08:10.954894	8	2	f
2555	17	112	New England Patriots	13	2025-10-26 16:08:10.955964	8	13	f
2556	17	113	New York Giants	3	2025-10-26 16:08:10.95695	8	0	f
2557	17	114	Buffalo Bills	8	2025-10-26 16:08:10.957901	8	8	f
2558	17	115	Chicago Bears	10	2025-10-26 16:08:10.958837	8	0	f
2559	17	116	San Francisco 49ers	6	2025-10-26 16:08:10.959774	8	0	f
2560	17	117	Tampa Bay Buccaneers	11	2025-10-26 16:08:10.960719	8	11	f
2561	17	118	Denver Broncos	4	2025-10-26 16:08:10.961685	8	4	f
2562	17	119	Indianapolis Colts	7	2025-10-26 16:08:10.962596	8	7	f
2563	17	120	Pittsburgh Steelers	5	2025-10-26 16:08:10.963522	8	0	f
2564	17	121	Kansas City Chiefs	12	2025-10-26 16:08:10.9646	8	12	f
2565	19	110	Atlanta Falcons	5	2025-10-26 16:14:32.117118	8	0	f
2566	19	111	Cincinnati Bengals	7	2025-10-26 16:14:32.118339	8	0	f
2567	19	112	Cleveland Browns	6	2025-10-26 16:14:32.119307	8	0	f
2568	19	113	Philadelphia Eagles	10	2025-10-26 16:14:32.120232	8	10	f
2569	19	114	Buffalo Bills	3	2025-10-26 16:14:32.121128	8	3	f
2570	19	115	Baltimore Ravens	2	2025-10-26 16:14:32.12212	8	2	f
2571	19	116	San Francisco 49ers	12	2025-10-26 16:14:32.122999	8	0	f
2572	19	117	Tampa Bay Buccaneers	13	2025-10-26 16:14:32.123892	8	13	f
2573	19	118	Denver Broncos	9	2025-10-26 16:14:32.12476	8	9	f
2574	19	119	Indianapolis Colts	1	2025-10-26 16:14:32.125622	8	1	f
2575	19	120	Green Bay Packers	11	2025-10-26 16:14:32.126481	8	11	f
2576	19	121	Washington Commanders	8	2025-10-26 16:14:32.127168	8	0	f
2577	1	122	Baltimore Ravens	8	2025-10-28 13:58:45.024704	9	8	f
2578	1	123	Chicago Bears	5	2025-10-28 13:58:45.026218	9	5	f
2579	1	124	Detroit Lions	11	2025-10-28 13:58:45.027183	9	0	f
2580	1	125	Green Bay Packers	4	2025-10-28 13:58:45.028109	9	0	f
2581	1	126	Los Angeles Chargers	1	2025-10-28 13:58:45.028983	9	0	f
2582	1	127	New England Patriots	9	2025-10-28 13:58:45.029851	9	0	f
2583	1	128	San Francisco 49ers	6	2025-10-28 13:58:45.030709	9	6	f
2584	1	129	Indianapolis Colts	10	2025-10-28 13:58:45.031628	9	0	f
2585	1	130	Denver Broncos	14	2025-10-28 13:58:45.032482	9	14	f
2586	1	131	Jacksonville Jaguars	3	2025-11-02 20:35:27.445936	9	0	f
2587	1	132	Los Angeles Rams	7	2025-11-02 20:35:27.447286	9	7	f
2588	1	133	Kansas City Chiefs	12	2025-11-02 20:35:27.448318	9	0	f
2589	1	134	Washington Commanders	2	2025-11-03 01:11:42.602689	9	0	f
2590	1	135	Dallas Cowboys	13	2025-11-03 01:11:42.603757	9	0	f
2591	14	122	Baltimore Ravens	8	2025-10-30 12:14:31.997805	9	8	f
2592	14	123	Chicago Bears	4	2025-11-01 17:55:09.892567	9	4	f
2593	14	124	Detroit Lions	13	2025-11-01 17:55:09.893853	9	0	f
2594	14	125	Carolina Panthers	5	2025-11-01 17:55:09.894819	9	5	f
2595	14	126	Los Angeles Chargers	6	2025-11-01 17:55:09.895737	9	0	f
2596	14	127	New England Patriots	9	2025-11-01 17:55:09.89663	9	0	f
2597	14	128	San Francisco 49ers	3	2025-11-01 17:55:09.897503	9	3	f
2598	14	129	Indianapolis Colts	14	2025-11-01 17:55:09.898345	9	0	f
2599	14	130	Denver Broncos	1	2025-11-01 17:55:09.899216	9	1	f
2600	14	131	Jacksonville Jaguars	2	2025-11-01 17:55:09.90009	9	0	f
2601	14	132	Los Angeles Rams	7	2025-11-01 17:55:09.900961	9	7	f
2602	14	133	Kansas City Chiefs	11	2025-11-01 17:55:09.901852	9	0	f
2603	14	134	Seattle Seahawks	10	2025-11-01 17:55:09.902721	9	10	f
2604	14	135	Dallas Cowboys	12	2025-11-01 17:55:09.903574	9	0	f
2605	23	122	Baltimore Ravens	9	2025-10-28 20:10:47.226019	9	9	f
2606	23	123	Cincinnati Bengals	3	2025-10-28 20:10:47.227449	9	0	f
2607	23	124	Detroit Lions	12	2025-10-28 20:10:47.228467	9	0	f
2608	23	125	Carolina Panthers	6	2025-10-28 20:10:47.229241	9	6	f
2609	23	126	Los Angeles Chargers	11	2025-10-28 20:10:47.230399	9	0	f
2610	23	127	Atlanta Falcons	10	2025-10-28 20:10:47.231386	9	10	f
2611	23	128	San Francisco 49ers	1	2025-10-28 20:10:47.232387	9	1	f
2612	23	129	Pittsburgh Steelers	4	2025-10-28 20:10:47.233243	9	4	f
2613	23	130	Denver Broncos	14	2025-10-28 20:10:47.234168	9	14	f
2614	23	131	Jacksonville Jaguars	2	2025-10-28 20:10:47.234957	9	0	f
2615	23	132	Los Angeles Rams	7	2025-10-28 20:10:47.235745	9	7	f
2616	23	133	Buffalo Bills	13	2025-10-28 20:10:47.236576	9	13	f
2617	23	134	Seattle Seahawks	8	2025-10-28 20:10:47.237561	9	8	f
2618	23	135	Dallas Cowboys	5	2025-10-28 20:10:47.238278	9	0	f
2619	12	122	Baltimore Ravens	12	2025-10-30 03:05:03.114713	9	12	f
2620	12	123	Cincinnati Bengals	5	2025-11-02 00:44:56.110302	9	0	f
2621	12	127	New England Patriots	8	2025-11-02 00:44:56.115172	9	0	f
2622	12	130	Denver Broncos	13	2025-11-02 00:44:56.118283	9	13	f
2623	12	133	Buffalo Bills	3	2025-11-02 00:44:56.121315	9	3	f
2624	12	124	Detroit Lions	11	2025-11-02 00:44:56.111807	9	0	f
2625	12	125	Green Bay Packers	7	2025-11-02 00:44:56.112975	9	0	f
2626	12	126	Los Angeles Chargers	14	2025-11-02 00:44:56.114112	9	0	f
2627	12	128	San Francisco 49ers	6	2025-11-02 00:44:56.116208	9	6	f
2628	12	129	Pittsburgh Steelers	1	2025-11-02 00:44:56.117247	9	1	f
2629	12	131	Jacksonville Jaguars	10	2025-11-02 00:44:56.119293	9	0	f
2630	12	132	Los Angeles Rams	2	2025-11-02 00:44:56.120306	9	2	f
2631	12	134	Seattle Seahawks	4	2025-11-02 00:44:56.122338	9	4	f
2632	12	135	Dallas Cowboys	9	2025-11-02 00:44:56.123374	9	0	f
2633	13	122	Miami Dolphins	6	2025-10-29 15:02:56.866352	9	0	f
2634	17	122	Baltimore Ravens	14	2025-10-30 22:48:52.315895	9	14	f
2635	17	123	Chicago Bears	6	2025-11-02 15:11:40.316229	9	6	f
2636	17	124	Detroit Lions	12	2025-11-02 15:11:40.317429	9	0	f
2637	17	125	Carolina Panthers	5	2025-11-02 15:11:40.318223	9	5	f
2638	17	126	Los Angeles Chargers	4	2025-11-02 15:11:40.318994	9	0	f
2639	17	127	New England Patriots	8	2025-11-02 15:11:40.319782	9	0	f
2640	17	128	San Francisco 49ers	10	2025-11-02 15:11:40.320812	9	10	f
2641	17	129	Indianapolis Colts	9	2025-11-02 15:11:40.321624	9	0	f
2642	17	130	Denver Broncos	13	2025-11-02 15:11:40.322339	9	13	f
2643	17	131	Las Vegas Raiders	1	2025-11-02 15:11:40.323043	9	1	f
2644	17	132	Los Angeles Rams	7	2025-11-02 15:11:40.32378	9	7	f
2645	17	133	Buffalo Bills	2	2025-11-02 15:11:40.324456	9	2	f
2646	17	134	Seattle Seahawks	11	2025-11-02 15:11:40.325101	9	11	f
2647	17	135	Dallas Cowboys	3	2025-11-04 00:03:33.177746	9	0	f
2648	24	122	Miami Dolphins	4	2025-10-30 02:25:27.482121	9	0	f
2649	24	123	Chicago Bears	6	2025-10-30 02:25:27.483538	9	6	f
2650	24	124	Detroit Lions	3	2025-10-30 02:25:27.48461	9	0	f
2651	24	125	Green Bay Packers	2	2025-10-30 02:25:27.485682	9	0	f
2652	24	126	Los Angeles Chargers	5	2025-10-30 02:25:27.486694	9	0	f
2653	24	127	New England Patriots	8	2025-10-30 02:25:27.4877	9	0	f
2654	24	128	San Francisco 49ers	10	2025-10-30 02:25:27.488713	9	10	f
2655	24	129	Indianapolis Colts	14	2025-10-30 02:25:27.491079	9	0	f
2656	24	130	Denver Broncos	11	2025-10-30 02:25:27.49309	9	11	f
2657	24	131	Jacksonville Jaguars	7	2025-10-30 02:25:27.494142	9	0	f
2658	24	132	Los Angeles Rams	1	2025-10-30 02:25:27.495494	9	1	f
2659	24	133	Buffalo Bills	13	2025-10-30 02:25:27.496394	9	13	f
2660	24	134	Seattle Seahawks	12	2025-10-30 02:25:27.497383	9	12	f
2661	24	135	Dallas Cowboys	9	2025-10-30 02:25:27.498338	9	0	f
2662	2	122	Miami Dolphins	1	2025-10-30 12:27:29.085083	9	0	f
2663	2	123	Chicago Bears	9	2025-10-30 12:27:29.086149	9	9	f
2664	2	124	Minnesota Vikings	11	2025-10-30 12:27:29.086964	9	11	f
2665	2	125	Carolina Panthers	2	2025-10-30 12:27:29.087723	9	2	f
2666	2	126	Tennessee Titans	3	2025-10-30 12:27:29.088469	9	3	f
2667	2	127	New England Patriots	13	2025-10-30 12:27:29.089183	9	0	f
2668	2	128	San Francisco 49ers	7	2025-10-30 12:27:29.089896	9	7	f
2669	2	129	Pittsburgh Steelers	4	2025-10-30 12:27:29.090646	9	4	f
2670	2	130	Denver Broncos	14	2025-10-30 12:27:29.091333	9	14	f
2671	2	131	Las Vegas Raiders	6	2025-10-30 12:27:29.092069	9	6	f
2672	2	132	New Orleans Saints	5	2025-10-30 12:27:29.0928	9	0	f
2673	2	133	Kansas City Chiefs	12	2025-10-30 12:27:29.093496	9	0	f
2674	2	134	Washington Commanders	8	2025-10-30 12:27:29.094248	9	0	f
2675	2	135	Dallas Cowboys	10	2025-10-30 12:27:29.094814	9	0	f
2676	21	122	Miami Dolphins	4	2025-10-30 14:37:40.183592	9	0	f
2677	21	123	Cincinnati Bengals	3	2025-10-30 14:37:40.184672	9	0	f
2678	21	124	Detroit Lions	7	2025-10-30 14:37:40.185485	9	0	f
2679	21	125	Carolina Panthers	6	2025-10-30 14:37:40.186221	9	6	f
2680	21	126	Tennessee Titans	5	2025-10-30 14:37:40.186926	9	5	f
2681	21	127	New England Patriots	2	2025-10-30 14:37:40.187652	9	0	f
2682	21	128	San Francisco 49ers	1	2025-10-30 14:37:40.188322	9	1	f
2683	21	129	Indianapolis Colts	12	2025-10-30 14:37:40.189025	9	0	f
2684	21	130	Denver Broncos	13	2025-10-30 14:37:40.189726	9	13	f
2685	21	131	Jacksonville Jaguars	11	2025-10-30 14:37:40.19043	9	0	f
2686	21	132	New Orleans Saints	10	2025-10-30 14:37:40.1912	9	0	f
2687	21	133	Buffalo Bills	9	2025-10-30 14:37:40.19193	9	9	f
2688	21	134	Washington Commanders	8	2025-10-30 14:37:40.192638	9	0	f
2689	21	135	Dallas Cowboys	14	2025-10-30 14:37:40.19329	9	0	f
2690	16	122	Miami Dolphins	13	2025-10-30 15:30:01.743036	9	0	f
2691	16	123	Cincinnati Bengals	7	2025-10-30 15:30:01.744273	9	0	f
2692	16	124	Detroit Lions	4	2025-10-30 15:30:01.745275	9	0	f
2693	16	125	Green Bay Packers	2	2025-10-30 15:30:01.746287	9	0	f
2694	16	126	Los Angeles Chargers	6	2025-10-30 15:30:01.747198	9	0	f
2695	16	127	New England Patriots	11	2025-10-30 15:30:01.748101	9	0	f
2696	16	128	San Francisco 49ers	12	2025-10-30 15:30:01.749002	9	12	f
2697	16	129	Indianapolis Colts	3	2025-10-30 15:30:01.74989	9	0	f
2698	16	130	Denver Broncos	14	2025-10-30 15:30:01.750761	9	14	f
2699	16	131	Las Vegas Raiders	5	2025-10-30 15:30:01.751674	9	5	f
2700	16	132	New Orleans Saints	10	2025-10-30 15:30:01.752576	9	0	f
2701	16	133	Kansas City Chiefs	8	2025-10-30 15:30:01.753449	9	0	f
2702	16	134	Seattle Seahawks	9	2025-10-30 15:30:01.754283	9	9	f
2703	16	135	Arizona Cardinals	1	2025-10-30 15:30:01.754961	9	1	f
2704	4	122	Miami Dolphins	3	2025-10-30 15:44:08.721804	9	0	f
2705	4	123	Chicago Bears	5	2025-10-30 15:44:08.723235	9	5	f
2706	4	124	Detroit Lions	7	2025-10-30 15:44:08.724458	9	0	f
2707	4	125	Carolina Panthers	2	2025-10-30 15:44:08.725488	9	2	f
2708	4	126	Los Angeles Chargers	8	2025-10-30 15:44:08.726504	9	0	f
2709	4	127	Atlanta Falcons	9	2025-10-30 15:44:08.727518	9	9	f
2710	4	128	San Francisco 49ers	10	2025-10-30 15:44:08.728546	9	10	f
2711	4	129	Indianapolis Colts	12	2025-10-30 15:44:08.729555	9	0	f
2712	4	130	Denver Broncos	14	2025-10-30 15:44:08.730557	9	14	f
2713	4	131	Jacksonville Jaguars	1	2025-10-30 15:44:08.731561	9	0	f
2714	4	132	New Orleans Saints	4	2025-10-30 15:44:08.732605	9	0	f
2715	4	133	Buffalo Bills	13	2025-10-30 15:44:08.733704	9	13	f
2716	4	134	Seattle Seahawks	6	2025-10-30 15:44:08.734712	9	6	f
2717	4	135	Dallas Cowboys	11	2025-10-30 15:44:08.735717	9	0	f
2718	8	122	Baltimore Ravens	11	2025-10-30 22:39:25.175903	9	11	f
2719	9	122	Baltimore Ravens	5	2025-10-30 20:11:15.922538	9	5	f
2720	9	123	Cincinnati Bengals	4	2025-10-30 20:11:15.923916	9	0	f
2721	9	124	Detroit Lions	6	2025-10-30 20:11:15.924969	9	0	f
2722	9	125	Carolina Panthers	2	2025-10-30 20:11:15.925933	9	2	f
2723	9	126	Los Angeles Chargers	12	2025-10-30 20:11:15.926839	9	0	f
2724	9	127	Atlanta Falcons	8	2025-10-30 20:11:15.927716	9	8	f
2725	9	128	San Francisco 49ers	14	2025-10-30 20:11:15.928689	9	14	f
2726	9	129	Indianapolis Colts	13	2025-10-30 20:11:15.92954	9	0	f
2727	9	130	Houston Texans	3	2025-10-30 20:11:15.930348	9	0	f
2728	9	131	Jacksonville Jaguars	9	2025-10-30 20:11:15.93134	9	0	f
2729	9	132	Los Angeles Rams	7	2025-10-30 20:11:15.932243	9	7	f
2730	9	134	Seattle Seahawks	11	2025-10-30 20:11:15.934071	9	11	f
2731	9	135	Arizona Cardinals	1	2025-10-30 20:11:15.93491	9	1	f
2732	9	133	Buffalo Bills	10	2025-10-30 20:11:15.933558	9	10	f
2733	18	122	Miami Dolphins	10	2025-10-30 20:34:48.82512	9	0	f
2734	15	122	Baltimore Ravens	3	2025-10-30 22:35:53.274475	9	3	f
2735	8	123	Chicago Bears	8	2025-10-30 22:39:25.177407	9	8	f
2736	8	124	Minnesota Vikings	6	2025-10-30 22:39:25.178215	9	6	f
2737	8	125	Carolina Panthers	2	2025-10-30 22:39:25.179026	9	2	f
2738	8	126	Los Angeles Chargers	14	2025-10-30 22:39:25.179809	9	0	f
2739	8	127	New England Patriots	9	2025-10-30 22:39:25.180608	9	0	f
2740	8	128	San Francisco 49ers	12	2025-10-30 22:39:25.181311	9	12	f
2741	8	129	Indianapolis Colts	7	2025-10-30 22:39:25.182051	9	0	f
2742	8	130	Denver Broncos	5	2025-10-30 22:39:25.182785	9	5	f
2743	8	131	Jacksonville Jaguars	10	2025-10-30 22:39:25.183549	9	0	f
2744	8	132	Los Angeles Rams	1	2025-10-30 22:39:25.184312	9	1	f
2745	8	133	Buffalo Bills	4	2025-10-30 22:39:25.185046	9	4	f
2746	8	134	Seattle Seahawks	13	2025-10-30 22:39:25.185761	9	13	f
2747	8	135	Arizona Cardinals	3	2025-10-30 22:39:25.186292	9	3	f
2748	5	122	Baltimore Ravens	14	2025-10-30 22:52:18.951491	9	14	f
2749	10	122	Baltimore Ravens	10	2025-10-31 00:13:23.271927	9	10	f
2750	19	122	Miami Dolphins	4	2025-10-30 23:19:18.344312	9	0	f
2751	22	123	Chicago Bears	7	2025-10-31 14:50:44.350178	9	7	f
2752	22	124	Detroit Lions	10	2025-10-31 14:50:44.351568	9	0	f
2753	22	125	Green Bay Packers	2	2025-10-31 14:50:44.352695	9	0	f
2754	22	126	Los Angeles Chargers	13	2025-10-31 14:50:44.353786	9	0	f
2755	22	127	New England Patriots	9	2025-10-31 14:50:44.354894	9	0	f
2756	22	128	San Francisco 49ers	8	2025-10-31 14:50:44.355984	9	8	f
2757	22	129	Pittsburgh Steelers	3	2025-10-31 14:50:44.357089	9	3	f
2758	22	130	Denver Broncos	11	2025-10-31 14:50:44.358604	9	11	f
2759	22	131	Las Vegas Raiders	1	2025-10-31 14:50:44.359702	9	1	f
2760	22	132	Los Angeles Rams	12	2025-10-31 14:50:44.360798	9	12	f
2761	22	133	Kansas City Chiefs	4	2025-10-31 14:50:44.361949	9	0	f
2762	22	134	Seattle Seahawks	6	2025-10-31 14:50:44.363015	9	6	f
2763	22	135	Dallas Cowboys	5	2025-10-31 14:50:44.363854	9	0	f
2764	5	123	Chicago Bears	10	2025-10-31 15:18:29.885204	9	10	f
2765	5	124	Detroit Lions	13	2025-10-31 15:18:29.886276	9	0	f
2766	5	125	Green Bay Packers	1	2025-10-31 15:18:29.887054	9	0	f
2767	5	126	Los Angeles Chargers	11	2025-10-31 15:18:29.8878	9	0	f
2768	5	127	New England Patriots	12	2025-10-31 15:18:29.88855	9	0	f
2769	5	128	San Francisco 49ers	9	2025-10-31 15:18:29.889231	9	9	f
2770	5	129	Indianapolis Colts	6	2025-10-31 15:18:29.889941	9	0	f
2771	5	130	Houston Texans	5	2025-10-31 15:18:29.890639	9	0	f
2772	5	131	Las Vegas Raiders	3	2025-10-31 15:18:29.89132	9	3	f
2773	5	132	Los Angeles Rams	2	2025-10-31 15:18:29.892027	9	2	f
2774	5	133	Kansas City Chiefs	4	2025-10-31 15:18:29.892715	9	0	f
2775	5	134	Seattle Seahawks	7	2025-10-31 15:18:29.893512	9	7	f
2776	5	135	Dallas Cowboys	8	2025-10-31 15:18:29.894187	9	0	f
2777	10	123	Chicago Bears	6	2025-11-01 11:31:12.300217	9	6	f
2778	10	124	Detroit Lions	7	2025-11-01 11:31:12.301307	9	0	f
2779	10	125	Carolina Panthers	1	2025-11-01 11:31:12.302182	9	1	f
2780	10	126	Los Angeles Chargers	2	2025-11-01 11:31:12.302988	9	0	f
2781	10	127	New England Patriots	11	2025-11-01 11:31:12.303817	9	0	f
2782	10	128	San Francisco 49ers	8	2025-11-01 11:31:12.304578	9	8	f
2783	10	129	Indianapolis Colts	3	2025-11-01 11:31:12.305385	9	0	f
2784	10	130	Denver Broncos	14	2025-11-01 11:31:12.306094	9	14	f
2785	10	131	Jacksonville Jaguars	4	2025-11-01 11:31:12.306818	9	0	f
2786	10	132	Los Angeles Rams	5	2025-11-01 11:31:12.307569	9	5	f
2787	10	133	Buffalo Bills	9	2025-11-01 11:31:12.308331	9	9	f
2788	10	134	Seattle Seahawks	12	2025-11-01 11:31:12.309048	9	12	f
2789	10	135	Dallas Cowboys	13	2025-11-01 11:31:12.309608	9	0	f
2790	19	123	Cincinnati Bengals	1	2025-11-02 03:35:47.678853	9	0	f
2791	19	124	Detroit Lions	8	2025-11-02 03:35:47.680173	9	0	f
2792	19	125	Green Bay Packers	9	2025-11-02 03:35:47.681272	9	0	f
2793	19	126	Los Angeles Chargers	2	2025-11-02 03:35:47.682389	9	0	f
2794	19	127	New England Patriots	6	2025-11-02 03:35:47.683461	9	0	f
2795	19	128	San Francisco 49ers	3	2025-11-02 03:35:47.684525	9	3	f
2796	19	129	Indianapolis Colts	12	2025-11-02 03:35:47.685583	9	0	f
2797	19	130	Denver Broncos	13	2025-11-02 03:35:47.686659	9	13	f
2798	19	131	Jacksonville Jaguars	10	2025-11-02 03:35:47.687719	9	0	f
2799	19	132	Los Angeles Rams	11	2025-11-02 03:35:47.688779	9	11	f
2800	19	133	Kansas City Chiefs	5	2025-11-02 03:35:47.689834	9	0	f
2801	19	134	Seattle Seahawks	14	2025-11-02 03:35:47.690896	9	14	f
2802	19	135	Dallas Cowboys	7	2025-11-02 03:35:47.691723	9	0	f
2803	18	123	Cincinnati Bengals	1	2025-11-02 04:56:40.029171	9	0	f
2804	18	124	Minnesota Vikings	2	2025-11-02 04:56:40.030729	9	2	f
2805	18	125	Green Bay Packers	3	2025-11-02 04:56:40.031912	9	0	f
2806	18	126	Los Angeles Chargers	4	2025-11-02 04:56:40.033054	9	0	f
2807	18	127	Atlanta Falcons	5	2025-11-02 04:56:40.03397	9	5	f
2808	18	128	San Francisco 49ers	14	2025-11-02 04:56:40.034818	9	14	f
2809	18	129	Pittsburgh Steelers	13	2025-11-02 04:56:40.035637	9	13	f
2810	18	130	Denver Broncos	7	2025-11-02 04:56:40.036446	9	7	f
2811	18	131	Jacksonville Jaguars	6	2025-11-02 04:56:40.037341	9	0	f
2812	18	132	Los Angeles Rams	12	2025-11-02 04:56:40.038162	9	12	f
2813	18	133	Kansas City Chiefs	11	2025-11-02 04:56:40.039162	9	0	f
2814	18	134	Seattle Seahawks	9	2025-11-02 04:56:40.040113	9	9	f
2815	18	135	Dallas Cowboys	8	2025-11-02 04:56:40.040866	9	0	f
2816	26	123	Chicago Bears	12	2025-11-02 05:28:12.243006	9	12	f
2817	26	124	Detroit Lions	5	2025-11-02 05:28:12.244047	9	0	f
2818	26	125	Green Bay Packers	1	2025-11-02 05:28:12.244801	9	0	f
2819	26	126	Los Angeles Chargers	11	2025-11-02 05:28:12.24552	9	0	f
2820	26	127	New England Patriots	13	2025-11-02 05:28:12.24621	9	0	f
2821	26	128	New York Giants	6	2025-11-02 05:28:12.246953	9	0	f
2822	26	129	Indianapolis Colts	7	2025-11-02 05:28:12.247665	9	0	f
2823	26	130	Denver Broncos	10	2025-11-02 05:28:12.248381	9	10	f
2824	26	131	Jacksonville Jaguars	2	2025-11-02 05:28:12.249097	9	0	f
2825	26	132	Los Angeles Rams	3	2025-11-02 05:28:12.249807	9	3	f
2826	26	133	Kansas City Chiefs	9	2025-11-02 05:28:12.250508	9	0	f
2827	26	134	Seattle Seahawks	4	2025-11-02 05:28:12.251185	9	4	f
2828	26	135	Dallas Cowboys	8	2025-11-02 05:28:12.251898	9	0	f
2829	15	123	Cincinnati Bengals	4	2025-11-02 14:16:07.510205	9	0	f
2830	15	124	Detroit Lions	2	2025-11-02 14:16:07.51172	9	0	f
2831	15	125	Carolina Panthers	1	2025-11-02 14:16:07.512827	9	1	f
2832	15	126	Tennessee Titans	6	2025-11-02 14:16:07.513944	9	6	f
2833	15	127	New England Patriots	12	2025-11-02 14:16:07.515015	9	0	f
2834	15	128	San Francisco 49ers	7	2025-11-02 14:16:07.516084	9	7	f
2835	15	129	Indianapolis Colts	13	2025-11-02 14:16:07.517127	9	0	f
2836	15	130	Denver Broncos	14	2025-11-02 14:16:07.518203	9	14	f
2837	15	131	Jacksonville Jaguars	11	2025-11-02 14:16:07.519272	9	0	f
2838	15	132	New Orleans Saints	5	2025-11-02 14:16:07.520338	9	0	f
2839	15	133	Buffalo Bills	10	2025-11-02 14:16:07.521423	9	10	f
2840	15	134	Seattle Seahawks	9	2025-11-02 14:16:07.522486	9	9	f
2841	15	135	Dallas Cowboys	8	2025-11-02 14:16:07.523309	9	0	f
2842	13	123	Chicago Bears	5	2025-11-02 16:06:03.499542	9	5	f
2843	13	124	Detroit Lions	10	2025-11-02 16:06:03.500555	9	0	f
2844	13	125	Green Bay Packers	4	2025-11-02 16:06:03.50125	9	0	f
2845	13	126	Tennessee Titans	3	2025-11-02 16:06:03.501978	9	3	f
2846	13	127	Atlanta Falcons	11	2025-11-02 16:06:03.502714	9	11	f
2847	13	128	San Francisco 49ers	9	2025-11-02 16:06:03.503462	9	9	f
2848	13	129	Indianapolis Colts	12	2025-11-02 16:06:03.504397	9	0	f
2849	13	130	Denver Broncos	14	2025-11-02 16:06:03.505155	9	14	f
2850	13	131	Jacksonville Jaguars	13	2025-11-02 16:06:03.505873	9	0	f
2851	13	132	New Orleans Saints	8	2025-11-02 16:06:03.506646	9	0	f
2852	13	133	Buffalo Bills	1	2025-11-02 16:06:03.507437	9	1	f
2853	13	134	Seattle Seahawks	2	2025-11-02 16:06:03.508388	9	2	f
2854	13	135	Dallas Cowboys	7	2025-11-02 16:06:03.509237	9	0	f
2855	20	124	Minnesota Vikings	6	2025-11-02 17:37:49.175549	9	6	f
2856	20	127	Atlanta Falcons	12	2025-11-02 17:37:49.179343	9	12	f
2857	20	128	San Francisco 49ers	4	2025-11-02 17:37:49.180525	9	4	f
2858	20	130	Denver Broncos	13	2025-11-02 17:37:49.182705	9	13	f
2859	20	131	Jacksonville Jaguars	10	2025-11-02 17:37:49.183802	9	0	f
2860	20	133	Buffalo Bills	8	2025-11-02 17:37:49.185976	9	8	f
2861	20	135	Dallas Cowboys	11	2025-11-02 17:37:49.188295	9	0	f
2862	20	123	Chicago Bears	1	2025-11-02 17:37:49.173952	9	1	f
2863	20	125	Green Bay Packers	2	2025-11-02 17:37:49.176852	9	0	f
2864	20	126	Tennessee Titans	3	2025-11-02 17:37:49.178105	9	3	f
2865	20	129	Indianapolis Colts	9	2025-11-02 17:37:49.181644	9	0	f
2866	20	132	Los Angeles Rams	5	2025-11-02 17:37:49.1849	9	5	f
2867	20	134	Seattle Seahawks	7	2025-11-02 17:37:49.187221	9	7	f
2868	1	136	Denver Broncos	14	2025-11-06 04:53:15.996196	10	0	f
2869	1	137	Indianapolis Colts	10	2025-11-06 04:53:15.997847	10	0	f
2870	1	138	Chicago Bears	5	2025-11-06 04:53:15.999204	10	5	f
2871	1	139	Buffalo Bills	4	2025-11-06 04:53:16.000434	10	0	f
2872	1	140	Baltimore Ravens	11	2025-11-06 04:53:16.0016	10	11	f
2873	1	141	New York Jets	6	2025-11-06 04:53:16.002702	10	6	f
2874	1	142	New England Patriots	9	2025-11-06 04:53:16.003774	10	9	f
2875	1	143	Carolina Panthers	3	2025-11-06 04:53:16.004858	10	0	f
2876	1	144	Jacksonville Jaguars	7	2025-11-06 04:53:16.005951	10	0	f
2877	1	145	Seattle Seahawks	8	2025-11-06 04:53:16.00703	10	8	f
2878	1	146	Los Angeles Rams	12	2025-11-06 04:53:16.00811	10	12	f
2879	1	147	Detroit Lions	13	2025-11-06 04:53:16.009552	10	13	f
2880	1	148	Los Angeles Chargers	2	2025-11-06 04:53:16.010614	10	2	f
2881	1	149	Philadelphia Eagles	1	2025-11-06 04:53:16.011687	10	0	f
2882	22	136	Denver Broncos	11	2025-11-05 21:08:47.030658	10	0	f
2883	22	137	Indianapolis Colts	13	2025-11-05 21:08:47.031891	10	0	f
2884	22	138	Chicago Bears	4	2025-11-05 21:08:47.032834	10	4	f
2885	22	139	Buffalo Bills	14	2025-11-05 21:08:47.033678	10	0	f
2886	22	140	Baltimore Ravens	3	2025-11-05 21:08:47.034658	10	3	f
2887	22	141	New York Jets	2	2025-11-05 21:08:47.035629	10	2	f
2888	22	142	Tampa Bay Buccaneers	5	2025-11-05 21:08:47.036466	10	0	f
2889	22	143	Carolina Panthers	10	2025-11-05 21:08:47.037288	10	0	f
2890	22	144	Houston Texans	1	2025-11-05 21:08:47.038083	10	1	f
2891	22	145	Arizona Cardinals	7	2025-11-05 21:08:47.038867	10	0	f
2892	22	146	Los Angeles Rams	9	2025-11-05 21:08:47.039596	10	9	f
2893	22	147	Detroit Lions	8	2025-11-05 21:08:47.04039	10	8	f
2894	22	148	Los Angeles Chargers	12	2025-11-05 21:08:47.041252	10	12	f
2895	22	149	Green Bay Packers	6	2025-11-05 21:08:47.042026	10	0	f
2896	14	136	Las Vegas Raiders	5	2025-11-06 18:01:13.953926	10	5	f
2897	14	137	Indianapolis Colts	4	2025-11-08 16:21:16.986504	10	0	f
2898	14	138	Chicago Bears	11	2025-11-08 16:21:16.987824	10	11	f
2899	14	139	Buffalo Bills	14	2025-11-08 16:21:16.988872	10	0	f
2900	14	140	Baltimore Ravens	3	2025-11-08 16:21:16.989859	10	3	f
2901	14	141	Cleveland Browns	6	2025-11-08 16:21:16.990804	10	0	f
2902	14	142	Tampa Bay Buccaneers	8	2025-11-08 16:21:16.991733	10	0	f
2903	14	143	Carolina Panthers	9	2025-11-08 16:21:16.992762	10	0	f
2904	14	144	Jacksonville Jaguars	1	2025-11-08 16:21:16.99372	10	0	f
2905	14	145	Seattle Seahawks	10	2025-11-08 16:21:16.994671	10	10	f
2906	14	146	Los Angeles Rams	13	2025-11-08 16:21:16.995604	10	13	f
2907	14	147	Detroit Lions	12	2025-11-08 16:21:16.996539	10	12	f
2908	14	148	Los Angeles Chargers	2	2025-11-08 16:21:16.997463	10	2	f
2909	14	149	Philadelphia Eagles	7	2025-11-08 16:21:16.998397	10	0	f
2910	13	136	Denver Broncos	8	2025-11-05 14:02:42.311909	10	0	f
2911	12	136	Denver Broncos	14	2025-11-05 22:26:22.156093	10	0	f
2912	2	136	Denver Broncos	14	2025-11-05 21:50:54.70558	10	0	f
2913	2	137	Indianapolis Colts	2	2025-11-05 21:50:54.706729	10	0	f
2914	2	138	Chicago Bears	3	2025-11-05 21:50:54.707556	10	3	f
2915	2	139	Buffalo Bills	4	2025-11-05 21:50:54.708312	10	0	f
2916	2	140	Minnesota Vikings	7	2025-11-05 21:50:54.709047	10	0	f
2917	2	141	Cleveland Browns	9	2025-11-05 21:50:54.70979	10	0	f
2918	2	142	Tampa Bay Buccaneers	8	2025-11-05 21:50:54.710526	10	0	f
2919	2	143	Carolina Panthers	1	2025-11-05 21:50:54.711265	10	0	f
2920	2	144	Houston Texans	11	2025-11-05 21:50:54.712076	10	11	f
2921	2	145	Arizona Cardinals	6	2025-11-05 21:50:54.712916	10	0	f
2922	2	146	San Francisco 49ers	12	2025-11-05 21:50:54.713765	10	0	f
2923	2	147	Washington Commanders	13	2025-11-05 21:50:54.714541	10	0	f
2924	2	148	Los Angeles Chargers	5	2025-11-05 21:50:54.71526	10	5	f
2925	2	149	Green Bay Packers	10	2025-11-05 21:50:54.715808	10	0	f
2926	12	138	Chicago Bears	9	2025-11-08 00:31:52.397643	10	9	f
2927	12	141	Cleveland Browns	11	2025-11-08 00:31:52.402846	10	0	f
2928	12	144	Jacksonville Jaguars	8	2025-11-08 00:31:52.406309	10	0	f
2929	12	146	Los Angeles Rams	12	2025-11-08 00:31:52.408468	10	12	f
2930	12	147	Detroit Lions	7	2025-11-08 00:31:52.40947	10	7	f
2931	12	148	Pittsburgh Steelers	10	2025-11-08 00:31:52.410471	10	0	f
2932	12	149	Green Bay Packers	6	2025-11-08 00:31:52.411442	10	0	f
2933	16	136	Denver Broncos	14	2025-11-06 02:24:24.447848	10	0	f
2934	16	137	Indianapolis Colts	10	2025-11-06 02:24:24.449531	10	0	f
2935	16	138	Chicago Bears	8	2025-11-06 02:24:24.450679	10	8	f
2936	16	139	Miami Dolphins	13	2025-11-06 02:24:24.451486	10	13	f
2937	16	140	Baltimore Ravens	6	2025-11-06 02:24:24.452323	10	6	f
2938	16	141	New York Jets	1	2025-11-06 02:24:24.453152	10	1	f
2939	16	142	Tampa Bay Buccaneers	3	2025-11-06 02:24:24.453904	10	0	f
2940	16	143	Carolina Panthers	9	2025-11-06 02:24:24.454683	10	0	f
2941	16	144	Houston Texans	2	2025-11-06 02:24:24.455426	10	2	f
2942	16	145	Seattle Seahawks	11	2025-11-06 02:24:24.456174	10	11	f
2943	16	146	Los Angeles Rams	7	2025-11-06 02:24:24.456904	10	7	f
2944	16	147	Detroit Lions	12	2025-11-06 02:24:24.457639	10	12	f
2945	16	148	Los Angeles Chargers	5	2025-11-06 02:24:24.458396	10	5	f
2946	16	149	Green Bay Packers	4	2025-11-06 02:24:24.459066	10	0	f
2947	9	136	Las Vegas Raiders	3	2025-11-06 14:38:42.319256	10	3	f
2948	9	137	Indianapolis Colts	6	2025-11-06 14:38:42.320247	10	0	f
2949	9	138	Chicago Bears	7	2025-11-06 14:38:42.320987	10	7	f
2950	9	139	Buffalo Bills	14	2025-11-06 14:38:42.321939	10	0	f
2951	9	140	Baltimore Ravens	5	2025-11-06 14:38:42.32271	10	5	f
2952	9	141	Cleveland Browns	8	2025-11-06 14:38:42.323467	10	0	f
2953	9	142	Tampa Bay Buccaneers	4	2025-11-06 14:38:42.324204	10	0	f
2954	9	143	Carolina Panthers	11	2025-11-06 14:38:42.3249	10	0	f
2955	9	144	Jacksonville Jaguars	2	2025-11-06 14:38:42.325659	10	0	f
2956	9	145	Arizona Cardinals	1	2025-11-06 14:38:42.326648	10	0	f
2957	9	146	Los Angeles Rams	9	2025-11-06 14:38:42.327611	10	9	f
2958	9	147	Detroit Lions	10	2025-11-06 14:38:42.328549	10	10	f
2959	9	148	Los Angeles Chargers	13	2025-11-06 14:38:42.329464	10	13	f
2960	9	149	Philadelphia Eagles	12	2025-11-06 14:38:42.33016	10	0	f
2961	5	136	Las Vegas Raiders	5	2025-11-06 18:12:20.084136	10	5	f
2962	18	136	Denver Broncos	14	2025-11-06 19:59:08.347175	10	0	f
2963	10	136	Denver Broncos	14	2025-11-06 23:20:28.188913	10	0	f
2964	26	136	Denver Broncos	3	2025-11-06 23:24:23.473817	10	0	f
2965	15	137	Indianapolis Colts	10	2025-11-09 13:48:05.202277	10	0	f
2966	15	136	Denver Broncos	14	2025-11-07 00:09:27.180134	10	0	f
2967	17	136	Denver Broncos	1	2025-11-07 00:01:08.770573	10	0	f
2968	8	136	Denver Broncos	5	2025-11-07 00:36:18.647042	10	0	f
2969	8	137	Indianapolis Colts	10	2025-11-07 00:36:18.648627	10	0	f
2970	8	138	Chicago Bears	14	2025-11-07 00:36:18.649906	10	14	f
2971	8	139	Buffalo Bills	9	2025-11-07 00:36:18.651138	10	0	f
2972	8	140	Minnesota Vikings	7	2025-11-07 00:36:18.652319	10	0	f
2973	8	141	Cleveland Browns	8	2025-11-07 00:36:18.65338	10	0	f
2974	8	142	New England Patriots	1	2025-11-07 00:36:18.654356	10	1	f
2975	8	143	Carolina Panthers	12	2025-11-07 00:36:18.655358	10	0	f
2976	8	144	Jacksonville Jaguars	6	2025-11-07 00:36:18.656489	10	0	f
2977	8	145	Seattle Seahawks	11	2025-11-07 00:36:18.657613	10	11	f
2978	8	146	Los Angeles Rams	2	2025-11-07 00:36:18.658665	10	2	f
2979	8	147	Detroit Lions	13	2025-11-07 00:36:18.659722	10	13	f
2980	8	148	Los Angeles Chargers	3	2025-11-07 00:36:18.660871	10	3	f
2981	8	149	Green Bay Packers	4	2025-11-07 00:36:18.662127	10	0	f
2982	19	136	Las Vegas Raiders	5	2025-11-07 01:00:41.989655	10	5	f
2983	5	137	Indianapolis Colts	6	2025-11-07 16:32:47.881275	10	0	f
2984	5	138	Chicago Bears	9	2025-11-07 16:32:47.882583	10	9	f
2985	5	139	Buffalo Bills	10	2025-11-07 16:32:47.883578	10	0	f
2986	5	140	Baltimore Ravens	11	2025-11-07 16:32:47.884452	10	11	f
2987	5	141	Cleveland Browns	13	2025-11-07 16:32:47.885244	10	0	f
2988	5	142	Tampa Bay Buccaneers	12	2025-11-07 16:32:47.885965	10	0	f
2989	5	143	Carolina Panthers	14	2025-11-07 16:32:47.886724	10	0	f
2990	5	144	Jacksonville Jaguars	4	2025-11-07 16:32:47.887438	10	0	f
2991	5	145	Arizona Cardinals	1	2025-11-07 16:32:47.888185	10	0	f
2992	5	146	Los Angeles Rams	2	2025-11-07 16:32:47.889	10	2	f
2993	5	147	Detroit Lions	8	2025-11-07 16:32:47.889736	10	8	f
2994	5	148	Los Angeles Chargers	3	2025-11-07 16:32:47.89045	10	3	f
2995	5	149	Philadelphia Eagles	7	2025-11-07 16:32:47.890992	10	0	f
2996	18	137	Indianapolis Colts	1	2025-11-07 17:50:50.20924	10	0	f
2997	18	138	Chicago Bears	8	2025-11-07 17:50:50.210474	10	8	f
2998	18	139	Buffalo Bills	7	2025-11-07 17:50:50.211391	10	0	f
2999	18	140	Baltimore Ravens	6	2025-11-07 17:50:50.212281	10	6	f
3000	18	141	Cleveland Browns	5	2025-11-07 17:50:50.213196	10	0	f
3001	18	142	Tampa Bay Buccaneers	13	2025-11-07 17:50:50.214041	10	0	f
3002	18	143	New Orleans Saints	12	2025-11-07 17:50:50.214865	10	12	f
3003	18	144	Houston Texans	4	2025-11-07 17:50:50.215781	10	4	f
3004	18	145	Arizona Cardinals	3	2025-11-07 17:50:50.216676	10	0	f
3005	18	146	San Francisco 49ers	2	2025-11-07 17:50:50.217576	10	0	f
3006	18	147	Detroit Lions	9	2025-11-07 17:50:50.218426	10	9	f
3007	18	148	Pittsburgh Steelers	11	2025-11-07 17:50:50.219279	10	0	f
3008	18	149	Philadelphia Eagles	10	2025-11-07 17:50:50.219921	10	0	f
3009	12	137	Atlanta Falcons	5	2025-11-08 00:31:52.396524	10	5	f
3010	12	139	Buffalo Bills	13	2025-11-08 00:31:52.400733	10	0	f
3011	12	140	Baltimore Ravens	4	2025-11-08 00:31:52.402045	10	4	f
3012	12	142	New England Patriots	3	2025-11-08 00:31:52.40451	10	3	f
3013	12	143	Carolina Panthers	2	2025-11-08 00:31:52.405645	10	0	f
3014	12	145	Arizona Cardinals	1	2025-11-08 00:31:52.407827	10	0	f
3015	4	137	Indianapolis Colts	13	2025-11-08 10:43:22.355188	10	0	f
3016	4	138	Chicago Bears	6	2025-11-08 10:43:22.356654	10	6	f
3017	4	139	Buffalo Bills	12	2025-11-08 10:43:22.357758	10	0	f
3018	4	140	Baltimore Ravens	9	2025-11-08 10:43:22.358803	10	9	f
3019	4	141	New York Jets	3	2025-11-08 10:43:22.359767	10	3	f
3020	4	142	Tampa Bay Buccaneers	10	2025-11-08 10:43:22.36073	10	0	f
3021	4	143	Carolina Panthers	5	2025-11-08 10:43:22.361687	10	0	f
3022	4	144	Houston Texans	11	2025-11-08 10:43:22.362622	10	11	f
3023	4	145	Seattle Seahawks	7	2025-11-08 10:43:22.363614	10	7	f
3024	4	146	San Francisco 49ers	4	2025-11-08 10:43:22.364627	10	0	f
3025	4	147	Detroit Lions	2	2025-11-08 10:43:22.365554	10	2	f
3026	4	148	Pittsburgh Steelers	1	2025-11-08 10:43:22.366476	10	0	f
3027	4	149	Philadelphia Eagles	8	2025-11-08 10:43:22.367395	10	0	f
3028	20	137	Atlanta Falcons	13	2025-11-08 14:17:18.519772	10	13	f
3029	20	138	New York Giants	1	2025-11-08 14:17:18.521194	10	0	f
3030	20	139	Miami Dolphins	9	2025-11-08 14:17:18.521965	10	9	f
3031	20	140	Minnesota Vikings	2	2025-11-08 14:17:18.522752	10	0	f
3032	20	141	Cleveland Browns	3	2025-11-08 14:17:18.523488	10	0	f
3033	20	142	Tampa Bay Buccaneers	7	2025-11-08 14:17:18.524282	10	0	f
3034	20	143	Carolina Panthers	11	2025-11-08 14:17:18.524996	10	0	f
3035	20	144	Houston Texans	12	2025-11-08 14:17:18.525928	10	12	f
3036	20	145	Arizona Cardinals	10	2025-11-08 14:17:18.526685	10	0	f
3037	20	146	Los Angeles Rams	6	2025-11-08 14:17:18.527646	10	6	f
3038	20	147	Detroit Lions	4	2025-11-08 14:17:18.528399	10	4	f
3039	20	148	Pittsburgh Steelers	8	2025-11-08 14:17:18.529225	10	0	f
3040	20	149	Green Bay Packers	5	2025-11-08 14:17:18.530406	10	0	f
3041	10	137	Atlanta Falcons	5	2025-11-09 14:04:36.088743	10	5	f
3042	10	138	Chicago Bears	8	2025-11-09 14:04:36.095352	10	8	f
3043	10	139	Buffalo Bills	13	2025-11-09 14:04:36.096342	10	0	f
3044	10	140	Baltimore Ravens	11	2025-11-09 14:04:36.097333	10	11	f
3045	10	141	Cleveland Browns	4	2025-11-09 14:04:36.098185	10	0	f
3046	10	142	Tampa Bay Buccaneers	3	2025-11-09 14:04:36.098961	10	0	f
3047	10	143	Carolina Panthers	10	2025-11-09 14:04:36.099754	10	0	f
3048	10	144	Jacksonville Jaguars	7	2025-11-09 14:04:36.100602	10	0	f
3049	10	145	Seattle Seahawks	9	2025-11-09 14:04:36.101521	10	9	f
3050	10	146	Los Angeles Rams	2	2025-11-09 14:04:36.102363	10	2	f
3051	10	147	Detroit Lions	12	2025-11-09 14:04:36.103158	10	12	f
3052	10	148	Pittsburgh Steelers	6	2025-11-09 14:04:36.104069	10	0	f
3053	10	149	Green Bay Packers	1	2025-11-09 14:04:36.104913	10	0	f
3054	13	137	Atlanta Falcons	1	2025-11-09 05:26:52.942193	10	1	f
3055	13	138	Chicago Bears	3	2025-11-09 05:26:52.943614	10	3	f
3056	13	139	Buffalo Bills	9	2025-11-09 05:26:52.944721	10	0	f
3057	13	140	Minnesota Vikings	5	2025-11-09 05:26:52.945734	10	0	f
3058	13	141	New York Jets	2	2025-11-09 05:26:52.946715	10	2	f
3059	13	142	Tampa Bay Buccaneers	10	2025-11-09 05:26:52.947673	10	0	f
3060	13	143	New Orleans Saints	6	2025-11-09 05:26:52.948604	10	6	f
3061	13	144	Jacksonville Jaguars	11	2025-11-09 05:26:52.949523	10	0	f
3062	13	145	Arizona Cardinals	4	2025-11-09 05:26:52.95043	10	0	f
3063	13	146	San Francisco 49ers	7	2025-11-09 05:26:52.951485	10	0	f
3064	13	147	Detroit Lions	12	2025-11-09 05:26:52.952615	10	12	f
3065	13	148	Pittsburgh Steelers	13	2025-11-09 05:26:52.953615	10	0	f
3066	13	149	Philadelphia Eagles	14	2025-11-09 05:26:52.95463	10	0	f
3067	19	137	Indianapolis Colts	6	2025-11-09 08:04:06.142997	10	0	f
3068	17	137	Indianapolis Colts	14	2025-11-09 08:04:58.201833	10	0	f
3069	15	138	Chicago Bears	7	2025-11-09 13:48:05.204487	10	7	f
3070	15	139	Buffalo Bills	6	2025-11-09 13:48:05.207632	10	0	f
3071	15	140	Baltimore Ravens	11	2025-11-09 13:48:05.211246	10	11	f
3072	15	141	Cleveland Browns	8	2025-11-09 13:48:05.212895	10	0	f
3073	15	142	Tampa Bay Buccaneers	5	2025-11-09 13:48:05.214187	10	0	f
3074	15	143	Carolina Panthers	13	2025-11-09 13:48:05.215632	10	0	f
3075	15	144	Jacksonville Jaguars	4	2025-11-09 13:48:05.216915	10	0	f
3076	15	145	Seattle Seahawks	12	2025-11-09 13:48:05.218121	10	12	f
3077	15	146	San Francisco 49ers	3	2025-11-09 13:48:05.219224	10	0	f
3078	15	147	Detroit Lions	9	2025-11-09 13:48:05.22028	10	9	f
3079	15	148	Pittsburgh Steelers	2	2025-11-09 13:48:05.221496	10	0	f
3080	15	149	Green Bay Packers	1	2025-11-09 13:48:05.222609	10	0	f
3081	26	137	Indianapolis Colts	9	2025-11-09 14:09:24.403976	10	0	f
3082	17	138	Chicago Bears	10	2025-11-09 17:02:47.642758	10	10	f
3083	17	139	Buffalo Bills	13	2025-11-09 17:02:47.644078	10	0	f
3084	17	140	Baltimore Ravens	8	2025-11-09 17:02:47.645418	10	8	f
3085	17	141	Cleveland Browns	2	2025-11-09 17:02:47.646654	10	0	f
3086	17	142	Tampa Bay Buccaneers	4	2025-11-09 17:02:47.647528	10	0	f
3087	17	143	Carolina Panthers	12	2025-11-09 17:02:47.648626	10	0	f
3088	17	144	Houston Texans	3	2025-11-09 17:02:47.649451	10	3	f
3089	17	145	Seattle Seahawks	11	2025-11-09 17:02:47.650292	10	11	f
3090	17	146	Los Angeles Rams	9	2025-11-09 17:02:47.651252	10	9	f
3091	17	147	Detroit Lions	6	2025-11-09 17:02:47.652407	10	6	f
3092	17	148	Los Angeles Chargers	5	2025-11-09 17:02:47.653628	10	5	f
3093	17	149	Green Bay Packers	7	2025-11-09 17:02:47.654478	10	0	f
3094	19	138	New York Giants	1	2025-11-09 17:52:04.158216	10	0	f
3095	19	139	Buffalo Bills	2	2025-11-09 17:52:04.159229	10	0	f
3096	19	140	Baltimore Ravens	3	2025-11-09 17:52:04.159933	10	3	f
3097	19	141	Cleveland Browns	11	2025-11-09 17:52:04.160832	10	0	f
3098	19	142	Tampa Bay Buccaneers	12	2025-11-09 17:52:04.16169	10	0	f
3099	19	143	New Orleans Saints	13	2025-11-09 17:52:04.162505	10	13	f
3100	19	144	Jacksonville Jaguars	4	2025-11-09 17:52:04.163306	10	0	f
3101	19	145	Seattle Seahawks	14	2025-11-09 17:52:04.164032	10	14	f
3102	19	146	Los Angeles Rams	10	2025-11-09 17:52:04.164723	10	10	f
3103	19	147	Detroit Lions	9	2025-11-09 17:52:04.165423	10	9	f
3104	19	148	Los Angeles Chargers	8	2025-11-09 17:52:04.16611	10	8	f
3105	19	149	Philadelphia Eagles	7	2025-11-09 17:52:04.166922	10	0	f
3106	26	138	New York Giants	4	2025-11-09 17:56:20.181651	10	0	f
3107	26	139	Buffalo Bills	6	2025-11-09 17:56:20.182744	10	0	f
3108	26	140	Baltimore Ravens	7	2025-11-09 17:56:20.183542	10	7	f
3109	26	141	Cleveland Browns	10	2025-11-09 17:56:20.184298	10	0	f
3110	26	142	Tampa Bay Buccaneers	2	2025-11-09 17:56:20.185045	10	0	f
3111	26	143	Carolina Panthers	5	2025-11-09 17:56:20.185802	10	0	f
3112	26	144	Houston Texans	1	2025-11-09 17:56:20.186526	10	1	f
3113	26	145	Seattle Seahawks	13	2025-11-09 17:56:20.187641	10	13	f
3114	26	146	Los Angeles Rams	11	2025-11-09 17:56:20.188456	10	11	f
3115	26	147	Detroit Lions	14	2025-11-09 17:56:20.189229	10	14	f
3116	26	148	Los Angeles Chargers	12	2025-11-09 17:56:20.189971	10	12	f
3117	26	149	Philadelphia Eagles	8	2025-11-09 17:56:20.190576	10	0	f
3118	23	149	Philadelphia Eagles	1	2025-11-10 02:07:56.302391	10	0	f
3119	20	150	New York Jets	3	2025-11-13 03:42:55.347305	11	0	f
3120	21	150	New York Jets	7	2025-11-11 15:27:52.068072	11	0	f
3121	21	151	Miami Dolphins	6	2025-11-11 15:27:52.06949	11	6	f
3122	21	152	Atlanta Falcons	8	2025-11-11 15:27:52.070604	11	0	f
3123	21	153	Tampa Bay Buccaneers	9	2025-11-11 15:27:52.071756	11	0	f
3124	21	154	Houston Texans	10	2025-11-11 15:27:52.07288	11	0	f
3125	21	155	Chicago Bears	11	2025-11-11 15:27:52.073971	11	11	f
3126	21	156	New York Giants	4	2025-11-11 15:27:52.075109	11	4	f
3127	21	157	Cincinnati Bengals	12	2025-11-11 15:27:52.076219	11	0	f
3128	21	158	Los Angeles Chargers	13	2025-11-11 15:27:52.077369	11	0	f
3129	21	159	Seattle Seahawks	14	2025-11-11 15:27:52.078474	11	14	f
3130	21	160	San Francisco 49ers	15	2025-11-11 15:27:52.079547	11	15	f
3131	21	161	Baltimore Ravens	5	2025-11-11 15:27:52.080631	11	0	f
3132	21	162	Denver Broncos	1	2025-11-11 15:27:52.081715	11	1	f
3133	21	163	Detroit Lions	2	2025-11-11 15:27:52.082821	11	0	f
3134	21	164	Dallas Cowboys	3	2025-11-11 15:27:52.083724	11	3	f
3135	1	150	New York Jets	2	2025-11-11 16:35:40.245945	11	0	f
3136	1	151	Miami Dolphins	7	2025-11-11 16:35:40.247314	11	7	f
3137	1	152	Atlanta Falcons	6	2025-11-11 16:35:40.248337	11	0	f
3138	1	153	Buffalo Bills	8	2025-11-11 16:35:40.249349	11	8	f
3139	1	154	Houston Texans	5	2025-11-11 16:35:40.250186	11	0	f
3140	1	155	Minnesota Vikings	3	2025-11-11 16:35:40.250977	11	0	f
3141	1	156	Green Bay Packers	4	2025-11-11 16:35:40.25187	11	0	f
3142	1	157	Pittsburgh Steelers	9	2025-11-11 16:35:40.252811	11	9	f
3143	1	158	Los Angeles Chargers	10	2025-11-11 16:35:40.253707	11	0	f
3144	1	159	Los Angeles Rams	11	2025-11-11 16:35:40.254508	11	0	f
3145	1	160	Arizona Cardinals	12	2025-11-11 16:35:40.255275	11	0	f
3146	1	161	Baltimore Ravens	1	2025-11-11 16:35:40.25603	11	0	f
3147	1	162	Denver Broncos	15	2025-11-11 16:35:40.256748	11	15	f
3148	1	163	Detroit Lions	14	2025-11-11 16:35:40.257497	11	0	f
3149	1	164	Dallas Cowboys	13	2025-11-11 16:35:40.258123	11	13	f
3150	12	150	New England Patriots	8	2025-11-13 01:34:33.484471	11	8	f
3151	12	151	Miami Dolphins	2	2025-11-13 01:34:33.485715	11	2	f
3152	12	155	Chicago Bears	14	2025-11-13 01:34:33.489186	11	14	f
3153	12	158	Los Angeles Chargers	11	2025-11-13 01:34:33.491828	11	0	f
3154	12	160	San Francisco 49ers	13	2025-11-13 01:34:33.49379	11	13	f
3155	12	162	Denver Broncos	15	2025-11-13 01:34:33.495476	11	15	f
3156	12	163	Detroit Lions	10	2025-11-13 01:34:33.4962	11	0	f
3157	12	164	Dallas Cowboys	6	2025-11-13 01:34:33.496939	11	6	f
3158	14	150	New England Patriots	10	2025-11-13 16:27:31.6183	11	10	f
3159	14	151	Miami Dolphins	13	2025-11-15 22:24:32.99599	11	13	f
3160	14	152	Atlanta Falcons	7	2025-11-15 22:24:32.998037	11	0	f
3161	14	153	Buffalo Bills	5	2025-11-15 22:24:32.99932	11	5	f
3162	14	154	Houston Texans	2	2025-11-15 22:24:33.000512	11	0	f
3163	14	155	Chicago Bears	6	2025-11-15 22:24:33.001794	11	6	f
3164	14	156	Green Bay Packers	11	2025-11-15 22:24:33.003327	11	0	f
3165	14	157	Cincinnati Bengals	4	2025-11-15 22:24:33.004556	11	0	f
3166	14	158	Los Angeles Chargers	15	2025-11-15 22:24:33.005652	11	0	f
3167	14	159	Seattle Seahawks	1	2025-11-15 22:24:33.006792	11	1	f
3168	14	160	San Francisco 49ers	14	2025-11-15 22:24:33.007842	11	14	f
3169	14	161	Cleveland Browns	8	2025-11-15 22:24:33.008854	11	8	f
3170	14	162	Kansas City Chiefs	12	2025-11-15 22:24:33.010218	11	0	f
3171	14	163	Philadelphia Eagles	3	2025-11-15 22:24:33.011551	11	3	f
3172	14	164	Dallas Cowboys	9	2025-11-15 22:24:33.012649	11	9	f
3173	22	150	New England Patriots	15	2025-11-13 15:39:03.049736	11	15	f
3174	22	151	Miami Dolphins	7	2025-11-13 15:39:03.051239	11	7	f
3175	22	152	Atlanta Falcons	5	2025-11-13 15:39:03.052372	11	0	f
3176	22	153	Buffalo Bills	6	2025-11-13 15:39:03.053461	11	6	f
3177	22	154	Tennessee Titans	3	2025-11-13 15:39:03.054704	11	3	f
3178	22	155	Minnesota Vikings	2	2025-11-13 15:39:03.055759	11	0	f
3179	22	156	Green Bay Packers	10	2025-11-13 15:39:03.056555	11	0	f
3180	22	157	Cincinnati Bengals	8	2025-11-13 15:39:03.057436	11	0	f
3181	22	158	Los Angeles Chargers	4	2025-11-13 15:39:03.058355	11	0	f
3182	22	159	Los Angeles Rams	1	2025-11-13 15:39:03.059466	11	0	f
3183	22	160	San Francisco 49ers	14	2025-11-13 15:39:03.060399	11	14	f
3184	22	161	Cleveland Browns	9	2025-11-13 15:39:03.061323	11	9	f
3185	22	162	Denver Broncos	11	2025-11-13 15:39:03.062302	11	11	f
3186	22	163	Detroit Lions	13	2025-11-13 15:39:03.063197	11	0	f
3187	22	164	Dallas Cowboys	12	2025-11-13 15:39:03.064175	11	12	f
3188	12	152	Atlanta Falcons	12	2025-11-13 01:34:33.487131	11	0	f
3189	12	153	Buffalo Bills	4	2025-11-13 01:34:33.487954	11	4	f
3190	12	154	Houston Texans	9	2025-11-13 01:34:33.488747	11	0	f
3191	12	156	Green Bay Packers	5	2025-11-13 01:34:33.490271	11	0	f
3192	12	157	Cincinnati Bengals	1	2025-11-13 01:34:33.491221	11	0	f
3193	12	159	Seattle Seahawks	7	2025-11-13 01:34:33.493179	11	7	f
3194	12	161	Baltimore Ravens	3	2025-11-13 01:34:33.495053	11	0	f
3195	20	151	Miami Dolphins	9	2025-11-13 03:42:55.349573	11	9	f
3196	20	152	Carolina Panthers	10	2025-11-13 03:42:55.351711	11	10	f
3197	20	153	Tampa Bay Buccaneers	8	2025-11-13 03:42:55.352982	11	0	f
3198	20	155	Chicago Bears	11	2025-11-13 03:42:55.354875	11	11	f
3199	20	156	New York Giants	5	2025-11-13 03:42:55.356282	11	5	f
3200	20	157	Pittsburgh Steelers	7	2025-11-13 03:42:55.357149	11	7	f
3201	20	158	Jacksonville Jaguars	1	2025-11-13 03:42:55.357913	11	1	f
3202	20	159	Los Angeles Rams	6	2025-11-13 03:42:55.35868	11	0	f
3203	20	160	San Francisco 49ers	12	2025-11-13 03:42:55.359482	11	12	f
3204	20	162	Kansas City Chiefs	13	2025-11-13 03:42:55.360665	11	0	f
3205	20	163	Detroit Lions	14	2025-11-16 22:46:55.275877	11	0	f
3206	20	164	Dallas Cowboys	15	2025-11-16 22:46:55.277405	11	15	f
3207	13	150	New York Jets	12	2025-11-13 12:36:57.688675	11	0	f
3208	2	150	New England Patriots	7	2025-11-14 01:12:41.716177	11	7	f
3209	2	151	Miami Dolphins	1	2025-11-14 01:12:41.717474	11	1	f
3210	2	152	Carolina Panthers	8	2025-11-14 01:12:41.718407	11	8	f
3211	2	153	Buffalo Bills	14	2025-11-14 01:12:41.719255	11	14	f
3212	2	154	Houston Texans	15	2025-11-14 01:12:41.720104	11	0	f
3213	2	155	Minnesota Vikings	9	2025-11-14 01:12:41.720976	11	0	f
3214	2	156	New York Giants	3	2025-11-14 01:12:41.721902	11	3	f
3215	2	157	Pittsburgh Steelers	2	2025-11-14 01:12:41.722906	11	2	f
3216	2	158	Jacksonville Jaguars	10	2025-11-14 01:12:41.723939	11	10	f
3217	2	159	Seattle Seahawks	4	2025-11-14 01:12:41.724928	11	4	f
3218	2	160	San Francisco 49ers	13	2025-11-14 01:12:41.725908	11	13	f
3219	2	161	Cleveland Browns	5	2025-11-14 01:12:41.726788	11	5	f
3220	2	162	Denver Broncos	11	2025-11-14 01:12:41.727635	11	11	f
3221	2	163	Detroit Lions	6	2025-11-14 01:12:41.728487	11	0	f
3222	2	164	Dallas Cowboys	12	2025-11-14 01:12:41.729306	11	12	f
3223	5	150	New England Patriots	14	2025-11-13 14:18:01.867245	11	14	f
3224	5	151	Miami Dolphins	15	2025-11-13 14:18:01.868286	11	15	f
3225	5	152	Atlanta Falcons	12	2025-11-13 14:18:01.868981	11	0	f
3226	5	153	Tampa Bay Buccaneers	13	2025-11-13 14:18:01.869726	11	0	f
3227	5	154	Houston Texans	9	2025-11-13 14:18:01.870451	11	0	f
3228	5	155	Chicago Bears	8	2025-11-13 14:18:01.87118	11	8	f
3229	5	156	Green Bay Packers	1	2025-11-13 14:18:01.871869	11	0	f
3230	5	157	Cincinnati Bengals	2	2025-11-13 14:18:01.872622	11	0	f
3231	5	158	Los Angeles Chargers	11	2025-11-13 14:18:01.873332	11	0	f
3232	5	159	Los Angeles Rams	7	2025-11-13 14:18:01.873995	11	0	f
3233	5	160	San Francisco 49ers	10	2025-11-13 14:18:01.874721	11	10	f
3234	5	161	Cleveland Browns	3	2025-11-13 14:18:01.875485	11	3	f
3235	5	162	Kansas City Chiefs	4	2025-11-13 14:18:01.876205	11	0	f
3236	5	163	Philadelphia Eagles	5	2025-11-13 14:18:01.876888	11	5	f
3237	5	164	Dallas Cowboys	6	2025-11-13 14:18:01.877611	11	6	f
3238	9	150	New York Jets	3	2025-11-13 15:06:39.622467	11	0	f
3239	9	151	Miami Dolphins	2	2025-11-13 15:06:39.62349	11	2	f
3240	9	152	Carolina Panthers	4	2025-11-13 15:06:39.624281	11	4	f
3241	9	153	Buffalo Bills	8	2025-11-13 15:06:39.625046	11	8	f
3242	9	154	Houston Texans	6	2025-11-13 15:06:39.625759	11	0	f
3243	9	155	Minnesota Vikings	9	2025-11-13 15:06:39.626545	11	0	f
3244	9	156	Green Bay Packers	13	2025-11-13 15:06:39.627306	11	0	f
3245	9	157	Pittsburgh Steelers	10	2025-11-13 15:06:39.628	11	10	f
3246	9	158	Los Angeles Chargers	15	2025-11-13 15:06:39.628728	11	0	f
3247	9	159	Seattle Seahawks	7	2025-11-13 15:06:39.629454	11	7	f
3248	9	160	Arizona Cardinals	1	2025-11-13 15:06:39.630189	11	0	f
3249	9	161	Baltimore Ravens	11	2025-11-13 15:06:39.630901	11	0	f
3250	9	162	Denver Broncos	5	2025-11-13 15:06:39.631729	11	5	f
3251	9	163	Detroit Lions	12	2025-11-13 15:06:39.632545	11	0	f
3252	9	164	Dallas Cowboys	14	2025-11-13 15:06:39.633207	11	14	f
3253	10	150	New England Patriots	10	2025-11-14 01:04:46.951816	11	10	f
3254	19	150	New York Jets	9	2025-11-13 22:53:47.033813	11	0	f
3255	15	150	New York Jets	2	2025-11-13 23:06:11.285564	11	0	f
3256	17	150	New England Patriots	1	2025-11-13 23:31:22.163374	11	1	f
3257	16	150	New England Patriots	1	2025-11-13 23:53:43.553636	11	1	f
3258	16	151	Miami Dolphins	12	2025-11-13 23:53:43.55477	11	12	f
3259	16	152	Atlanta Falcons	9	2025-11-13 23:53:43.555626	11	0	f
3260	16	153	Buffalo Bills	5	2025-11-13 23:53:43.556431	11	5	f
3261	16	154	Tennessee Titans	3	2025-11-13 23:53:43.557205	11	3	f
3262	16	155	Minnesota Vikings	11	2025-11-13 23:53:43.557946	11	0	f
3263	16	156	Green Bay Packers	4	2025-11-13 23:53:43.558726	11	0	f
3264	16	157	Cincinnati Bengals	6	2025-11-13 23:53:43.559459	11	0	f
3265	16	158	Los Angeles Chargers	10	2025-11-13 23:53:43.560188	11	0	f
3266	16	159	Los Angeles Rams	13	2025-11-13 23:53:43.56095	11	0	f
3267	16	160	San Francisco 49ers	14	2025-11-13 23:53:43.561688	11	14	f
3268	16	161	Cleveland Browns	2	2025-11-13 23:53:43.562452	11	2	f
3269	16	162	Denver Broncos	8	2025-11-13 23:53:43.563324	11	8	f
3270	16	163	Philadelphia Eagles	15	2025-11-13 23:53:43.564236	11	15	f
3271	16	164	Dallas Cowboys	7	2025-11-13 23:53:43.564813	11	7	f
3272	26	150	New England Patriots	4	2025-11-14 00:06:46.515682	11	4	f
3273	18	150	New York Jets	10	2025-11-14 00:48:45.67509	11	0	f
3274	8	150	New England Patriots	10	2025-11-14 01:06:32.963459	11	10	f
3275	8	151	Miami Dolphins	9	2025-11-14 01:06:32.964659	11	9	f
3276	8	152	Carolina Panthers	8	2025-11-14 01:06:32.965511	11	8	f
3277	8	153	Buffalo Bills	2	2025-11-14 01:06:32.96637	11	2	f
3278	8	154	Houston Texans	15	2025-11-14 01:06:32.967182	11	0	f
3279	8	155	Chicago Bears	7	2025-11-14 01:06:32.968028	11	7	f
3280	8	156	Green Bay Packers	3	2025-11-14 01:06:32.968833	11	0	f
3281	8	157	Cincinnati Bengals	1	2025-11-14 01:06:32.969652	11	0	f
3282	8	158	Los Angeles Chargers	14	2025-11-14 01:06:32.970522	11	0	f
3283	8	159	Seattle Seahawks	11	2025-11-14 01:06:32.971357	11	11	f
3284	8	160	San Francisco 49ers	12	2025-11-14 01:06:32.972215	11	12	f
3285	8	161	Baltimore Ravens	13	2025-11-14 01:06:32.97303	11	0	f
3286	8	162	Denver Broncos	6	2025-11-14 01:06:32.973824	11	6	f
3287	8	163	Detroit Lions	5	2025-11-14 01:06:32.974664	11	0	f
3288	8	164	Dallas Cowboys	4	2025-11-14 01:06:32.975478	11	4	f
3289	4	151	Miami Dolphins	14	2025-11-14 01:36:52.087256	11	14	f
3290	4	152	Carolina Panthers	13	2025-11-14 01:36:52.088379	11	13	f
3291	4	153	Buffalo Bills	12	2025-11-14 01:36:52.089264	11	12	f
3292	4	154	Houston Texans	11	2025-11-14 01:36:52.09015	11	0	f
3293	4	155	Chicago Bears	10	2025-11-14 01:36:52.090996	11	10	f
3294	4	156	Green Bay Packers	9	2025-11-14 01:36:52.091825	11	0	f
3295	4	157	Pittsburgh Steelers	8	2025-11-14 01:36:52.092609	11	8	f
3296	4	158	Jacksonville Jaguars	7	2025-11-14 01:36:52.09336	11	7	f
3297	4	159	Seattle Seahawks	6	2025-11-14 01:36:52.094139	11	6	f
3298	4	160	San Francisco 49ers	5	2025-11-14 01:36:52.094861	11	5	f
3299	4	161	Baltimore Ravens	4	2025-11-14 01:36:52.095594	11	0	f
3300	4	162	Denver Broncos	3	2025-11-14 01:36:52.096532	11	3	f
3301	4	163	Philadelphia Eagles	2	2025-11-14 01:36:52.097329	11	2	f
3302	4	164	Dallas Cowboys	1	2025-11-14 01:36:52.097945	11	1	f
3303	23	150	New York Jets	6	2025-11-14 16:58:20.245029	11	0	f
3304	23	151	Miami Dolphins	3	2025-11-14 16:58:20.245033	11	3	f
3305	23	152	Atlanta Falcons	5	2025-11-14 16:58:20.245036	11	0	f
3306	23	153	Buffalo Bills	13	2025-11-14 16:58:20.245038	11	13	f
3307	23	154	Houston Texans	1	2025-11-14 16:58:20.245039	11	0	f
3308	23	155	Minnesota Vikings	7	2025-11-14 16:58:20.245039	11	0	f
3309	23	156	Green Bay Packers	10	2025-11-14 16:58:20.24504	11	0	f
3310	23	157	Pittsburgh Steelers	11	2025-11-14 16:58:20.245041	11	11	f
3311	23	158	Los Angeles Chargers	8	2025-11-14 16:58:20.245042	11	0	f
3312	23	159	Los Angeles Rams	4	2025-11-14 16:58:20.245043	11	0	f
3313	23	160	San Francisco 49ers	12	2025-11-14 16:58:20.245044	11	12	f
3314	23	161	Baltimore Ravens	2	2025-11-14 16:58:20.245044	11	0	f
3315	23	162	Denver Broncos	15	2025-11-14 16:58:20.245045	11	15	f
3316	23	163	Philadelphia Eagles	9	2025-11-14 16:58:20.245046	11	9	f
3317	23	164	Dallas Cowboys	14	2025-11-14 16:58:20.245047	11	14	f
3318	17	151	Washington Commanders	2	2025-11-15 13:37:00.343636	11	0	f
3319	17	152	Carolina Panthers	10	2025-11-16 16:14:51.982429	11	10	f
3320	17	153	Tampa Bay Buccaneers	3	2025-11-16 16:14:51.98346	11	0	f
3321	17	154	Tennessee Titans	11	2025-11-16 16:14:51.984211	11	11	f
3322	17	155	Chicago Bears	9	2025-11-16 16:14:51.984911	11	9	f
3323	17	156	New York Giants	6	2025-11-16 16:14:51.985647	11	6	f
3324	17	157	Cincinnati Bengals	13	2025-11-16 16:14:51.986397	11	0	f
3325	17	158	Los Angeles Chargers	15	2025-11-16 16:14:51.98712	11	0	f
3326	17	159	Seattle Seahawks	4	2025-11-16 16:14:51.987812	11	4	f
3327	17	160	San Francisco 49ers	7	2025-11-16 16:14:51.988518	11	7	f
3328	17	161	Baltimore Ravens	14	2025-11-16 16:14:51.989226	11	0	f
3329	17	162	Denver Broncos	5	2025-11-16 16:14:51.989911	11	5	f
3330	17	163	Detroit Lions	12	2025-11-16 16:14:51.990622	11	0	f
3331	17	164	Dallas Cowboys	8	2025-11-16 16:14:51.991337	11	8	f
3332	13	151	Miami Dolphins	5	2025-11-16 02:04:14.697801	11	5	f
3333	13	152	Atlanta Falcons	4	2025-11-16 02:04:14.699472	11	0	f
3334	13	153	Tampa Bay Buccaneers	3	2025-11-16 02:04:14.700808	11	0	f
3335	13	154	Tennessee Titans	10	2025-11-16 02:04:14.702114	11	10	f
3336	13	155	Chicago Bears	9	2025-11-16 02:04:14.703337	11	9	f
3337	13	156	New York Giants	8	2025-11-16 02:04:14.704509	11	8	f
3338	13	157	Cincinnati Bengals	2	2025-11-16 02:04:14.705672	11	0	f
3339	13	158	Jacksonville Jaguars	1	2025-11-16 02:04:14.706842	11	1	f
3340	13	159	Los Angeles Rams	14	2025-11-16 02:04:14.708215	11	0	f
3341	13	160	San Francisco 49ers	6	2025-11-16 02:04:14.709364	11	6	f
3342	13	161	Baltimore Ravens	7	2025-11-16 02:04:14.710501	11	0	f
3343	13	162	Denver Broncos	15	2025-11-16 02:04:14.711644	11	15	f
3344	13	163	Detroit Lions	11	2025-11-16 02:04:14.712794	11	0	f
3345	13	164	Dallas Cowboys	13	2025-11-16 02:04:14.7137	11	13	f
3346	18	151	Miami Dolphins	11	2025-11-16 06:31:18.612094	11	11	f
3347	18	152	Carolina Panthers	12	2025-11-16 06:31:18.61343	11	12	f
3348	18	153	Tampa Bay Buccaneers	1	2025-11-16 06:31:18.614568	11	0	f
3349	18	154	Tennessee Titans	2	2025-11-16 06:31:18.615703	11	2	f
3350	18	155	Minnesota Vikings	9	2025-11-16 06:31:18.616783	11	0	f
3351	18	156	New York Giants	8	2025-11-16 06:31:18.617598	11	8	f
3352	18	157	Cincinnati Bengals	7	2025-11-16 06:31:18.618362	11	0	f
3353	18	158	Jacksonville Jaguars	6	2025-11-16 06:31:18.619107	11	6	f
3354	18	159	Los Angeles Rams	13	2025-11-16 06:31:18.619809	11	0	f
3355	18	160	San Francisco 49ers	14	2025-11-16 06:31:18.620536	11	14	f
3356	18	161	Baltimore Ravens	4	2025-11-16 06:31:18.621261	11	0	f
3357	18	162	Denver Broncos	5	2025-11-16 06:31:18.622034	11	5	f
3358	18	163	Philadelphia Eagles	3	2025-11-16 06:31:18.622772	11	3	f
3359	18	164	Dallas Cowboys	15	2025-11-16 06:31:18.623372	11	15	f
3360	26	151	Washington Commanders	5	2025-11-16 07:09:32.33821	11	0	f
3361	26	152	Atlanta Falcons	2	2025-11-16 07:09:32.339249	11	0	f
3362	26	153	Tampa Bay Buccaneers	9	2025-11-16 07:09:32.339956	11	0	f
3363	26	154	Houston Texans	3	2025-11-16 07:09:32.340816	11	0	f
3364	26	155	Chicago Bears	6	2025-11-16 07:09:32.341765	11	6	f
3365	26	156	Green Bay Packers	11	2025-11-16 07:09:32.34254	11	0	f
3366	26	158	Los Angeles Chargers	14	2025-11-16 07:09:32.34404	11	0	f
3367	26	159	Los Angeles Rams	12	2025-11-16 07:09:32.344718	11	0	f
3368	26	160	San Francisco 49ers	1	2025-11-16 07:09:32.34546	11	1	f
3369	26	161	Baltimore Ravens	15	2025-11-16 07:09:32.346176	11	0	f
3370	26	162	Kansas City Chiefs	10	2025-11-16 07:09:32.346858	11	0	f
3371	26	163	Philadelphia Eagles	13	2025-11-16 07:09:32.347557	11	13	f
3372	26	164	Dallas Cowboys	8	2025-11-16 07:09:32.348253	11	8	f
3373	26	157	Pittsburgh Steelers	7	2025-11-16 07:09:32.343304	11	7	f
3374	10	151	Miami Dolphins	5	2025-11-16 11:15:44.63182	11	5	f
3375	19	151	Miami Dolphins	8	2025-11-16 12:57:16.871107	11	8	f
3376	15	151	Miami Dolphins	6	2025-11-16 14:27:43.666488	11	6	f
3377	15	152	Carolina Panthers	9	2025-11-16 14:35:35.661771	11	9	f
3378	15	153	Tampa Bay Buccaneers	10	2025-11-16 14:35:35.663032	11	0	f
3379	15	154	Tennessee Titans	5	2025-11-16 14:35:35.663855	11	5	f
3380	15	155	Chicago Bears	13	2025-11-16 14:35:35.664668	11	13	f
3381	15	156	New York Giants	3	2025-11-16 14:35:35.665453	11	3	f
3382	15	157	Pittsburgh Steelers	4	2025-11-16 14:35:35.666262	11	4	f
3383	15	158	Los Angeles Chargers	14	2025-11-16 14:35:35.667052	11	0	f
3384	15	159	Seattle Seahawks	11	2025-11-16 14:35:35.667799	11	11	f
3385	15	160	San Francisco 49ers	8	2025-11-16 14:35:35.668695	11	8	f
3386	15	161	Baltimore Ravens	7	2025-11-16 14:35:35.669508	11	0	f
3387	15	162	Denver Broncos	15	2025-11-16 14:35:35.670291	11	15	f
3388	15	163	Detroit Lions	1	2025-11-16 14:35:35.671066	11	0	f
3389	15	164	Dallas Cowboys	12	2025-11-16 14:35:35.671686	11	12	f
3390	10	152	Carolina Panthers	1	2025-11-16 16:55:57.370518	11	1	f
3391	10	153	Tampa Bay Buccaneers	9	2025-11-16 16:55:57.37155	11	0	f
3392	10	154	Tennessee Titans	6	2025-11-16 16:55:57.372361	11	6	f
3393	10	155	Chicago Bears	11	2025-11-16 16:55:57.37317	11	11	f
3394	10	156	Green Bay Packers	2	2025-11-16 16:55:57.373904	11	0	f
3395	10	157	Cincinnati Bengals	14	2025-11-16 16:55:57.374628	11	0	f
3396	10	158	Jacksonville Jaguars	3	2025-11-16 16:55:57.375354	11	3	f
3397	10	159	Seattle Seahawks	7	2025-11-16 16:55:57.376063	11	7	f
3398	10	160	San Francisco 49ers	12	2025-11-16 16:55:57.376741	11	12	f
3399	10	161	Baltimore Ravens	4	2025-11-16 16:55:57.377437	11	0	f
3400	10	162	Denver Broncos	15	2025-11-16 16:55:57.378157	11	15	f
3401	10	163	Detroit Lions	8	2025-11-16 16:55:57.378834	11	0	f
3402	10	164	Dallas Cowboys	13	2025-11-16 16:55:57.379733	11	13	f
3403	19	152	Carolina Panthers	2	2025-11-16 17:00:31.128494	11	2	f
3404	19	153	Tampa Bay Buccaneers	10	2025-11-16 17:00:31.129648	11	0	f
3405	19	154	Houston Texans	1	2025-11-16 17:00:31.130572	11	0	f
3406	19	155	Chicago Bears	11	2025-11-16 17:00:31.131564	11	11	f
3407	19	156	Green Bay Packers	3	2025-11-16 17:00:31.132444	11	0	f
3408	19	157	Pittsburgh Steelers	7	2025-11-16 17:00:31.133233	11	7	f
3409	19	158	Los Angeles Chargers	13	2025-11-16 17:00:31.133981	11	0	f
3410	19	159	Seattle Seahawks	6	2025-11-16 17:00:31.134732	11	6	f
3411	19	160	San Francisco 49ers	15	2025-11-16 17:00:31.135618	11	15	f
3412	19	161	Baltimore Ravens	12	2025-11-16 17:00:31.136708	11	0	f
3413	19	162	Denver Broncos	5	2025-11-16 17:00:31.137862	11	5	f
3414	19	163	Detroit Lions	4	2025-11-16 17:00:31.139075	11	0	f
3415	19	164	Dallas Cowboys	14	2025-11-16 17:00:31.139743	11	14	f
3416	1	165	Buffalo Bills	8	2025-11-18 14:13:06.507136	12	0	f
3417	1	166	Pittsburgh Steelers	3	2025-11-18 14:13:06.508957	12	3	f
3418	1	167	New England Patriots	12	2025-11-18 14:13:06.510303	12	0	f
3419	1	168	Detroit Lions	14	2025-11-18 14:13:06.511622	12	0	f
3420	1	169	Minnesota Vikings	2	2025-11-18 14:13:06.512971	12	0	f
3421	1	170	Tennessee Titans	4	2025-11-18 14:13:06.514351	12	4	f
3422	1	171	Indianapolis Colts	5	2025-11-18 14:13:06.515497	12	5	f
3423	1	172	Baltimore Ravens	6	2025-11-18 14:13:06.516947	12	0	f
3424	1	173	Las Vegas Raiders	7	2025-11-18 14:13:06.518066	12	0	f
3425	1	174	Arizona Cardinals	1	2025-11-18 14:13:06.519158	12	0	f
3426	1	175	Philadelphia Eagles	11	2025-11-18 14:13:06.520246	12	0	f
3427	1	176	New Orleans Saints	9	2025-11-18 14:13:06.521377	12	0	f
3428	1	177	Los Angeles Rams	10	2025-11-18 14:13:06.522683	12	10	f
3429	1	178	San Francisco 49ers	13	2025-11-18 14:13:06.52362	12	13	f
3430	12	165	Buffalo Bills	10	2025-11-20 11:13:49.585575	12	0	f
3431	12	166	Pittsburgh Steelers	9	2025-11-23 15:17:01.774161	12	9	f
3432	12	174	Arizona Cardinals	3	2025-11-23 15:17:01.782783	12	0	f
3433	12	175	Philadelphia Eagles	8	2025-11-23 15:17:01.783827	12	0	f
3434	12	176	Atlanta Falcons	1	2025-11-23 15:17:01.784849	12	1	f
3435	14	165	Houston Texans	8	2025-11-20 23:31:43.454552	12	8	f
3436	14	166	Chicago Bears	12	2025-11-23 12:33:40.790528	12	0	f
3437	14	167	New England Patriots	10	2025-11-23 12:33:40.7922	12	0	f
3438	14	168	Detroit Lions	14	2025-11-23 12:33:40.793091	12	0	f
3439	14	169	Minnesota Vikings	4	2025-11-23 12:33:40.793911	12	0	f
3440	14	170	Seattle Seahawks	13	2025-11-23 12:33:40.79487	12	0	f
3441	14	171	Indianapolis Colts	6	2025-11-23 12:33:40.795647	12	6	f
3442	14	172	Baltimore Ravens	7	2025-11-23 12:33:40.796385	12	0	f
3443	14	173	Las Vegas Raiders	1	2025-11-23 12:33:40.797145	12	0	f
3444	14	174	Jacksonville Jaguars	11	2025-11-23 12:33:40.797863	12	11	f
3445	14	175	Philadelphia Eagles	5	2025-11-23 12:33:40.798608	12	0	f
3446	14	176	Atlanta Falcons	9	2025-11-23 12:33:40.799325	12	9	f
3447	14	177	Tampa Bay Buccaneers	2	2025-11-23 12:33:40.799994	12	0	f
3448	14	178	San Francisco 49ers	3	2025-11-23 12:33:40.800702	12	3	f
3449	23	165	Buffalo Bills	14	2025-11-19 00:21:46.086317	12	0	f
3450	23	166	Pittsburgh Steelers	10	2025-11-19 00:21:46.087418	12	10	f
3451	23	167	New England Patriots	13	2025-11-19 00:21:46.088168	12	0	f
3452	23	168	Detroit Lions	11	2025-11-19 00:21:46.088866	12	0	f
3453	23	169	Minnesota Vikings	8	2025-11-19 00:21:46.08958	12	0	f
3454	23	170	Seattle Seahawks	9	2025-11-19 00:21:46.090304	12	0	f
3455	23	171	Indianapolis Colts	7	2025-11-19 00:21:46.091054	12	7	f
3456	23	172	Baltimore Ravens	6	2025-11-19 00:21:46.091931	12	0	f
3457	23	173	Las Vegas Raiders	5	2025-11-19 00:21:46.092662	12	0	f
3458	23	174	Arizona Cardinals	3	2025-11-19 00:21:46.093368	12	0	f
3459	23	175	Philadelphia Eagles	12	2025-11-19 00:21:46.09408	12	0	f
3460	23	176	Atlanta Falcons	4	2025-11-19 00:21:46.094805	12	4	f
3461	23	177	Los Angeles Rams	2	2025-11-19 00:21:46.095517	12	2	f
3462	23	178	San Francisco 49ers	1	2025-11-19 00:21:46.096239	12	1	f
3463	4	165	Houston Texans	5	2025-11-19 10:58:38.604415	12	5	f
3464	4	166	Pittsburgh Steelers	4	2025-11-19 10:58:38.605784	12	4	f
3465	4	167	New England Patriots	7	2025-11-19 10:58:38.606863	12	0	f
3466	4	168	Detroit Lions	3	2025-11-19 10:58:38.607966	12	0	f
3467	4	169	Green Bay Packers	2	2025-11-19 10:58:38.609118	12	2	f
3468	4	170	Tennessee Titans	6	2025-11-19 10:58:38.610227	12	6	f
3469	4	171	Indianapolis Colts	8	2025-11-19 10:58:38.611321	12	8	f
3470	4	172	New York Jets	1	2025-11-19 10:58:38.612334	12	1	f
3471	4	173	Las Vegas Raiders	9	2025-11-19 10:58:38.613376	12	0	f
3472	4	174	Jacksonville Jaguars	10	2025-11-19 10:58:38.614398	12	10	f
3473	4	175	Philadelphia Eagles	12	2025-11-19 10:58:38.615461	12	0	f
3474	4	176	Atlanta Falcons	11	2025-11-19 10:58:38.616567	12	11	f
3475	4	177	Tampa Bay Buccaneers	13	2025-11-19 10:58:38.617662	12	0	f
3476	4	178	San Francisco 49ers	14	2025-11-19 10:58:38.618355	12	14	f
3477	22	165	Buffalo Bills	7	2025-11-19 17:46:36.663387	12	0	f
3478	22	166	Chicago Bears	5	2025-11-19 17:46:36.664615	12	0	f
3479	22	167	New England Patriots	11	2025-11-19 17:46:36.665541	12	0	f
3480	22	168	Detroit Lions	12	2025-11-19 17:46:36.666373	12	0	f
3481	22	169	Green Bay Packers	8	2025-11-19 17:46:36.66721	12	8	f
3482	22	170	Seattle Seahawks	13	2025-11-19 17:46:36.667993	12	0	f
3483	22	171	Kansas City Chiefs	4	2025-11-19 17:46:36.668782	12	0	f
3484	22	172	Baltimore Ravens	14	2025-11-19 17:46:36.66958	12	0	f
3485	22	173	Las Vegas Raiders	3	2025-11-19 17:46:36.670366	12	0	f
3486	22	174	Jacksonville Jaguars	2	2025-11-19 17:46:36.671172	12	2	f
3487	22	175	Philadelphia Eagles	6	2025-11-19 17:46:36.671947	12	0	f
3488	22	176	Atlanta Falcons	1	2025-11-19 17:46:36.672741	12	1	f
3489	22	177	Los Angeles Rams	9	2025-11-19 17:46:36.673528	12	9	f
3490	22	178	San Francisco 49ers	10	2025-11-19 17:46:36.674158	12	10	f
3491	8	165	Buffalo Bills	9	2025-11-20 14:24:00.494847	12	0	f
3492	8	166	Pittsburgh Steelers	1	2025-11-20 14:24:00.496374	12	1	f
3493	8	167	New England Patriots	14	2025-11-20 14:24:00.497478	12	0	f
3494	8	168	Detroit Lions	13	2025-11-20 14:24:00.498263	12	0	f
3495	8	169	Green Bay Packers	10	2025-11-20 14:24:00.499068	12	10	f
3496	8	170	Seattle Seahawks	12	2025-11-20 14:24:00.499956	12	0	f
3497	8	171	Indianapolis Colts	8	2025-11-20 14:24:00.500726	12	8	f
3498	8	172	Baltimore Ravens	11	2025-11-20 14:24:00.501463	12	0	f
3499	8	173	Las Vegas Raiders	2	2025-11-20 14:24:00.502211	12	0	f
3500	8	174	Jacksonville Jaguars	7	2025-11-20 14:24:00.502904	12	7	f
3501	8	175	Philadelphia Eagles	6	2025-11-20 14:24:00.503612	12	0	f
3502	8	176	New Orleans Saints	3	2025-11-20 14:24:00.504335	12	0	f
3503	8	177	Tampa Bay Buccaneers	5	2025-11-20 14:24:00.505033	12	0	f
3504	8	178	Carolina Panthers	4	2025-11-20 14:24:00.505747	12	0	f
3505	20	165	Buffalo Bills	14	2025-11-20 00:29:47.497619	12	0	f
3506	20	166	Pittsburgh Steelers	9	2025-11-23 07:29:08.080502	12	9	f
3507	20	168	New York Giants	8	2025-11-23 07:29:08.083179	12	8	f
3508	20	169	Minnesota Vikings	2	2025-11-23 07:29:08.084227	12	0	f
3509	20	172	New York Jets	10	2025-11-23 07:29:08.087604	12	10	f
3510	21	165	Buffalo Bills	10	2025-11-20 10:34:37.863692	12	0	f
3511	21	166	Chicago Bears	11	2025-11-20 10:34:37.865216	12	0	f
3512	21	167	Cincinnati Bengals	12	2025-11-20 10:34:37.866495	12	12	f
3513	21	168	Detroit Lions	6	2025-11-20 10:34:37.867582	12	0	f
3514	21	169	Minnesota Vikings	13	2025-11-20 10:34:37.868653	12	0	f
3515	21	170	Seattle Seahawks	9	2025-11-20 10:34:37.869649	12	0	f
3516	21	171	Kansas City Chiefs	8	2025-11-20 10:34:37.870622	12	0	f
3517	21	172	Baltimore Ravens	7	2025-11-20 10:34:37.871606	12	0	f
3518	21	173	Las Vegas Raiders	5	2025-11-20 10:34:37.872556	12	0	f
3519	21	174	Jacksonville Jaguars	14	2025-11-20 10:34:37.873488	12	14	f
3520	21	175	Philadelphia Eagles	4	2025-11-20 10:34:37.874417	12	0	f
3521	21	176	Atlanta Falcons	3	2025-11-20 10:34:37.875346	12	3	f
3522	21	177	Tampa Bay Buccaneers	1	2025-11-20 10:34:37.876277	12	0	f
3523	21	178	Carolina Panthers	2	2025-11-20 10:34:37.877198	12	0	f
3524	12	173	Cleveland Browns	4	2025-11-23 15:17:01.781599	12	4	f
3525	16	165	Buffalo Bills	8	2025-11-20 20:53:48.127614	12	0	f
3526	16	166	Chicago Bears	9	2025-11-20 20:53:48.128672	12	0	f
3527	16	167	Cincinnati Bengals	3	2025-11-20 20:53:48.129482	12	3	f
3528	16	168	New York Giants	2	2025-11-20 20:53:48.130305	12	2	f
3529	16	169	Minnesota Vikings	4	2025-11-20 20:53:48.131092	12	0	f
3530	16	170	Tennessee Titans	1	2025-11-20 20:53:48.131864	12	1	f
3531	16	171	Kansas City Chiefs	10	2025-11-20 20:53:48.132689	12	0	f
3532	16	172	Baltimore Ravens	5	2025-11-20 20:53:48.133454	12	0	f
3533	16	173	Las Vegas Raiders	11	2025-11-20 20:53:48.134208	12	0	f
3534	16	174	Jacksonville Jaguars	13	2025-11-20 20:53:48.134923	12	13	f
3535	16	175	Philadelphia Eagles	12	2025-11-20 20:53:48.135706	12	0	f
3536	16	176	New Orleans Saints	14	2025-11-20 20:53:48.136481	12	0	f
3537	16	177	Los Angeles Rams	7	2025-11-20 20:53:48.13729	12	7	f
3538	16	178	San Francisco 49ers	6	2025-11-20 20:53:48.137887	12	6	f
3539	2	165	Buffalo Bills	4	2025-11-20 20:55:51.57887	12	0	f
3540	2	166	Chicago Bears	6	2025-11-21 15:01:43.867188	12	0	f
3541	2	167	Cincinnati Bengals	1	2025-11-21 15:01:43.868492	12	1	f
3542	2	168	New York Giants	2	2025-11-21 15:01:43.869466	12	2	f
3543	2	169	Green Bay Packers	10	2025-11-21 15:01:43.870368	12	10	f
3544	2	170	Tennessee Titans	7	2025-11-21 15:01:43.871236	12	7	f
3545	2	171	Kansas City Chiefs	9	2025-11-21 15:01:43.872049	12	0	f
3546	2	172	Baltimore Ravens	3	2025-11-21 15:01:43.872806	12	0	f
3547	2	173	Cleveland Browns	8	2025-11-21 15:01:43.873567	12	8	f
3548	2	174	Arizona Cardinals	5	2025-11-21 15:01:43.87432	12	0	f
3549	2	175	Dallas Cowboys	12	2025-11-21 15:01:43.87506	12	12	f
3550	2	176	Atlanta Falcons	13	2025-11-21 15:01:43.875775	12	13	f
3551	2	177	Los Angeles Rams	14	2025-11-21 15:01:43.876476	12	14	f
3552	2	178	San Francisco 49ers	11	2025-11-21 15:01:43.877191	12	11	f
3553	18	165	Buffalo Bills	14	2025-11-20 22:36:23.812965	12	0	f
3554	9	165	Houston Texans	6	2025-11-20 22:57:20.713657	12	6	f
3555	9	166	Chicago Bears	4	2025-11-20 22:57:20.714635	12	0	f
3556	9	167	Cincinnati Bengals	2	2025-11-20 22:57:20.715491	12	2	f
3557	9	168	Detroit Lions	12	2025-11-20 22:57:20.71625	12	0	f
3558	9	169	Green Bay Packers	5	2025-11-20 22:57:20.717189	12	5	f
3559	9	170	Seattle Seahawks	14	2025-11-20 22:57:20.717945	12	0	f
3560	9	171	Indianapolis Colts	10	2025-11-20 22:57:20.718788	12	10	f
3561	9	172	New York Jets	3	2025-11-20 22:57:20.71957	12	3	f
3562	9	173	Cleveland Browns	7	2025-11-20 22:57:20.720568	12	7	f
3563	9	174	Arizona Cardinals	8	2025-11-20 22:57:20.721383	12	0	f
3564	9	175	Philadelphia Eagles	9	2025-11-20 22:57:20.72215	12	0	f
3565	9	176	Atlanta Falcons	1	2025-11-20 22:57:20.722889	12	1	f
3566	9	177	Tampa Bay Buccaneers	11	2025-11-20 22:57:20.723878	12	0	f
3567	9	178	San Francisco 49ers	13	2025-11-20 22:57:20.724737	12	13	f
3568	13	165	Buffalo Bills	8	2025-11-20 22:57:47.756461	12	0	f
3569	19	165	Buffalo Bills	5	2025-11-20 23:00:49.788402	12	0	f
3570	15	165	Buffalo Bills	4	2025-11-20 23:05:32.006732	12	0	f
3571	17	165	Buffalo Bills	1	2025-11-20 23:10:57.430953	12	0	f
3572	17	166	Chicago Bears	11	2025-11-23 15:51:38.883245	12	0	f
3573	17	167	New England Patriots	13	2025-11-23 15:51:38.884908	12	0	f
3574	17	168	Detroit Lions	12	2025-11-23 15:51:38.886277	12	0	f
3575	17	169	Minnesota Vikings	6	2025-11-23 15:51:38.887472	12	0	f
3576	17	170	Seattle Seahawks	14	2025-11-23 15:51:38.888659	12	0	f
3577	17	171	Indianapolis Colts	2	2025-11-23 15:51:38.88951	12	2	f
3578	17	172	Baltimore Ravens	10	2025-11-23 15:51:38.890339	12	0	f
3579	17	173	Cleveland Browns	3	2025-11-23 15:51:38.89126	12	3	f
3580	17	174	Jacksonville Jaguars	8	2025-11-23 15:51:38.892143	12	8	f
3581	17	175	Philadelphia Eagles	9	2025-11-23 15:51:38.89292	12	0	f
3582	17	176	New Orleans Saints	7	2025-11-23 15:51:38.893711	12	0	f
3583	17	177	Tampa Bay Buccaneers	4	2025-11-23 15:51:38.894442	12	0	f
3584	17	178	Carolina Panthers	5	2025-11-23 15:51:38.895254	12	0	f
3585	10	165	Houston Texans	11	2025-11-21 01:11:01.02025	12	11	f
3586	5	165	Houston Texans	2	2025-11-21 00:58:48.872922	12	2	f
3587	26	165	Buffalo Bills	5	2025-11-21 00:32:32.220422	12	0	f
3588	5	166	Chicago Bears	13	2025-11-21 00:58:48.874416	12	0	f
3589	5	167	New England Patriots	4	2025-11-21 00:58:48.875502	12	0	f
3590	5	168	Detroit Lions	6	2025-11-21 00:58:48.876582	12	0	f
3591	5	169	Minnesota Vikings	3	2025-11-21 00:58:48.877593	12	0	f
3592	5	170	Seattle Seahawks	11	2025-11-21 00:58:48.878758	12	0	f
3593	5	171	Indianapolis Colts	7	2025-11-21 00:58:48.879648	12	7	f
3594	5	172	Baltimore Ravens	9	2025-11-21 00:58:48.880449	12	0	f
3595	5	173	Las Vegas Raiders	1	2025-11-21 00:58:48.881264	12	0	f
3596	5	174	Jacksonville Jaguars	8	2025-11-21 00:58:48.882112	12	8	f
3597	5	175	Dallas Cowboys	5	2025-11-21 00:58:48.88286	12	5	f
3598	5	176	Atlanta Falcons	14	2025-11-21 00:58:48.883605	12	14	f
3599	5	177	Tampa Bay Buccaneers	12	2025-11-21 00:58:48.884338	12	0	f
3600	5	178	San Francisco 49ers	10	2025-11-21 00:58:48.885073	12	10	f
3601	12	167	New England Patriots	7	2025-11-23 15:17:01.775723	12	0	f
3602	12	168	Detroit Lions	11	2025-11-23 15:17:01.776758	12	0	f
3603	12	169	Green Bay Packers	12	2025-11-23 15:17:01.777591	12	12	f
3604	12	170	Seattle Seahawks	14	2025-11-23 15:17:01.778542	12	0	f
3605	12	171	Indianapolis Colts	5	2025-11-23 15:17:01.779683	12	5	f
3606	12	172	Baltimore Ravens	2	2025-11-23 15:17:01.780667	12	0	f
3607	12	177	Tampa Bay Buccaneers	13	2025-11-23 15:17:01.785612	12	0	f
3608	12	178	San Francisco 49ers	6	2025-11-23 15:17:01.786421	12	6	f
3609	10	166	Chicago Bears	7	2025-11-23 15:58:11.817424	12	0	f
3610	10	167	New England Patriots	9	2025-11-23 15:58:11.818977	12	0	f
3611	10	168	Detroit Lions	12	2025-11-23 15:58:11.820195	12	0	f
3612	10	169	Green Bay Packers	5	2025-11-23 15:58:11.821287	12	5	f
3613	10	170	Tennessee Titans	4	2025-11-23 15:58:11.822414	12	4	f
3614	10	171	Kansas City Chiefs	13	2025-11-23 15:58:11.823541	12	0	f
3615	10	172	Baltimore Ravens	14	2025-11-23 15:58:11.824677	12	0	f
3616	10	173	Las Vegas Raiders	1	2025-11-23 15:58:11.825738	12	0	f
3617	10	174	Arizona Cardinals	2	2025-11-23 15:58:11.826709	12	0	f
3618	10	175	Dallas Cowboys	10	2025-11-23 15:58:11.827663	12	10	f
3619	10	176	New Orleans Saints	3	2025-11-23 15:58:11.828646	12	0	f
3620	10	177	Tampa Bay Buccaneers	6	2025-11-23 15:58:11.82962	12	0	f
3621	10	178	San Francisco 49ers	8	2025-11-23 15:58:11.830556	12	8	f
3622	15	166	Chicago Bears	11	2025-11-23 17:35:00.813433	12	0	f
3623	15	167	New England Patriots	14	2025-11-23 17:35:00.816364	12	0	f
3624	15	168	Detroit Lions	2	2025-11-23 17:35:00.817716	12	0	f
3625	15	169	Minnesota Vikings	1	2025-11-23 17:35:00.819218	12	0	f
3626	15	170	Seattle Seahawks	3	2025-11-23 17:35:00.820573	12	0	f
3627	15	171	Indianapolis Colts	9	2025-11-23 17:35:00.821897	12	9	f
3628	15	172	New York Jets	5	2025-11-23 17:35:00.823097	12	5	f
3629	15	173	Cleveland Browns	8	2025-11-23 17:35:00.824213	12	8	f
3630	15	174	Jacksonville Jaguars	12	2025-11-23 17:35:00.825355	12	12	f
3631	15	175	Philadelphia Eagles	10	2025-11-23 17:35:00.826439	12	0	f
3632	15	176	New Orleans Saints	13	2025-11-23 17:35:00.827465	12	0	f
3633	15	177	Tampa Bay Buccaneers	7	2025-11-23 17:35:00.828512	12	0	f
3634	15	178	San Francisco 49ers	6	2025-11-23 17:35:00.829588	12	6	f
3635	18	166	Chicago Bears	5	2025-11-23 05:46:46.161681	12	0	f
3636	18	167	Cincinnati Bengals	4	2025-11-23 05:46:46.163294	12	4	f
3637	18	168	Detroit Lions	3	2025-11-23 05:46:46.16453	12	0	f
3638	18	169	Minnesota Vikings	2	2025-11-23 05:46:46.165754	12	0	f
3639	18	170	Tennessee Titans	7	2025-11-23 05:46:46.166953	12	7	f
3640	18	171	Kansas City Chiefs	6	2025-11-23 05:46:46.168224	12	0	f
3641	18	172	Baltimore Ravens	13	2025-11-23 05:46:46.169405	12	0	f
3642	18	173	Las Vegas Raiders	12	2025-11-23 05:46:46.170555	12	0	f
3643	18	174	Jacksonville Jaguars	8	2025-11-23 05:46:46.171533	12	8	f
3644	18	175	Dallas Cowboys	9	2025-11-23 05:46:46.172372	12	9	f
3645	18	176	New Orleans Saints	10	2025-11-23 05:46:46.173164	12	0	f
3646	18	177	Tampa Bay Buccaneers	11	2025-11-23 05:46:46.173889	12	0	f
3647	18	178	Carolina Panthers	1	2025-11-23 05:46:46.174525	12	0	f
3648	20	167	New England Patriots	12	2025-11-23 07:29:08.08247	12	0	f
3649	20	170	Seattle Seahawks	1	2025-11-23 07:29:08.085853	12	0	f
3650	20	171	Indianapolis Colts	6	2025-11-23 07:29:08.086991	12	6	f
3651	20	173	Las Vegas Raiders	5	2025-11-23 07:29:08.088983	12	0	f
3652	20	174	Jacksonville Jaguars	7	2025-11-23 07:29:08.090064	12	7	f
3653	20	175	Dallas Cowboys	3	2025-11-23 07:29:08.091045	12	3	f
3654	20	176	New Orleans Saints	4	2025-11-23 07:29:08.092038	12	0	f
3655	20	177	Los Angeles Rams	13	2025-11-23 07:29:08.093221	12	13	f
3656	20	178	San Francisco 49ers	11	2025-11-23 07:29:08.094033	12	11	f
3657	13	166	Chicago Bears	4	2025-11-23 14:20:24.136916	12	0	f
3658	13	167	Cincinnati Bengals	2	2025-11-23 14:20:24.136919	12	2	f
3659	13	168	New York Giants	5	2025-11-23 14:20:24.136921	12	5	f
3660	13	169	Green Bay Packers	6	2025-11-23 14:20:24.136922	12	6	f
3661	13	170	Seattle Seahawks	9	2025-11-23 14:20:24.136923	12	0	f
3662	13	171	Kansas City Chiefs	1	2025-11-23 14:20:24.136923	12	0	f
3663	13	172	Baltimore Ravens	3	2025-11-23 14:20:24.136924	12	0	f
3664	13	173	Cleveland Browns	7	2025-11-23 14:20:24.136924	12	7	f
3665	13	174	Arizona Cardinals	10	2025-11-23 14:20:24.136925	12	0	f
3666	13	175	Philadelphia Eagles	11	2025-11-23 14:20:24.136925	12	0	f
3667	13	176	Atlanta Falcons	12	2025-11-23 14:20:24.136926	12	12	f
3668	13	177	Tampa Bay Buccaneers	13	2025-11-23 14:20:24.136927	12	0	f
3669	13	178	Carolina Panthers	14	2025-11-23 14:20:24.136927	12	0	f
3670	19	166	Pittsburgh Steelers	3	2025-11-23 15:32:05.457402	12	3	f
3671	19	167	New England Patriots	4	2025-11-23 15:32:05.458943	12	0	f
3672	19	168	Detroit Lions	6	2025-11-23 15:32:05.460266	12	0	f
3673	19	169	Minnesota Vikings	7	2025-11-23 15:32:05.461486	12	0	f
3674	19	170	Seattle Seahawks	12	2025-11-23 15:32:05.462686	12	0	f
3675	19	171	Indianapolis Colts	9	2025-11-23 15:32:05.463786	12	9	f
3676	19	172	New York Jets	8	2025-11-23 15:32:05.464831	12	8	f
3677	19	173	Cleveland Browns	1	2025-11-23 15:32:05.465981	12	1	f
3678	19	174	Jacksonville Jaguars	14	2025-11-23 15:32:05.467183	12	14	f
3679	19	175	Philadelphia Eagles	13	2025-11-23 15:32:05.468345	12	0	f
3680	19	176	Atlanta Falcons	10	2025-11-23 15:32:05.46974	12	10	f
3681	19	177	Tampa Bay Buccaneers	2	2025-11-23 15:32:05.470952	12	0	f
3682	19	178	Carolina Panthers	11	2025-11-23 15:32:05.471902	12	0	f
3683	26	166	Chicago Bears	3	2025-11-23 15:56:29.357883	12	0	f
3684	26	167	New England Patriots	8	2025-11-23 15:56:29.359037	12	0	f
3685	26	168	Detroit Lions	2	2025-11-23 15:56:29.359911	12	0	f
3686	26	169	Green Bay Packers	10	2025-11-23 15:56:29.360738	12	10	f
3687	26	170	Seattle Seahawks	1	2025-11-23 15:56:29.361551	12	0	f
3688	26	171	Kansas City Chiefs	12	2025-11-23 15:56:29.362333	12	0	f
3689	26	172	Baltimore Ravens	4	2025-11-23 15:56:29.363074	12	0	f
3690	26	173	Cleveland Browns	11	2025-11-23 15:56:29.36379	12	11	f
3691	26	174	Jacksonville Jaguars	6	2025-11-23 15:56:29.364603	12	6	f
3692	26	175	Philadelphia Eagles	13	2025-11-23 15:56:29.365389	12	0	f
3693	26	176	Atlanta Falcons	7	2025-11-23 15:56:29.366142	12	7	f
3694	26	177	Los Angeles Rams	9	2025-11-23 15:56:29.366847	12	9	f
3695	26	178	San Francisco 49ers	14	2025-11-23 15:56:29.36762	12	14	f
3696	1	179	Detroit Lions	11	2025-11-25 14:55:52.220281	13	0	f
3697	1	180	Kansas City Chiefs	12	2025-11-25 14:55:52.221908	13	0	f
3698	1	181	Baltimore Ravens	6	2025-11-25 14:55:52.223199	13	0	f
3699	1	182	Philadelphia Eagles	13	2025-11-25 14:55:52.224374	13	0	f
3700	1	183	San Francisco 49ers	7	2025-11-25 14:55:52.225517	13	7	f
3701	1	184	Jacksonville Jaguars	10	2025-11-25 14:55:52.226689	13	10	f
3702	1	185	Indianapolis Colts	14	2025-11-25 14:55:52.227782	13	0	f
3703	1	186	Miami Dolphins	5	2025-11-25 14:55:52.228865	13	0	f
3704	1	187	Atlanta Falcons	4	2025-11-25 14:55:52.229934	13	0	f
3705	1	188	Tampa Bay Buccaneers	8	2025-11-25 14:55:52.230975	13	0	f
3706	1	189	Los Angeles Rams	3	2025-11-25 14:55:52.232036	13	0	f
3707	1	190	Seattle Seahawks	2	2025-11-25 14:55:52.233073	13	2	f
3708	1	192	Los Angeles Chargers	1	2025-11-25 14:55:52.235387	13	1	f
3709	1	193	Denver Broncos	16	2025-11-25 14:55:52.236501	13	0	f
3710	1	194	New England Patriots	15	2025-11-25 14:55:52.237528	13	15	f
3711	1	191	Buffalo Bills	9	2025-11-25 14:55:52.234665	13	9	f
3712	21	179	Detroit Lions	5	2025-11-25 21:46:09.444293	13	0	f
3713	21	180	Dallas Cowboys	6	2025-11-25 21:46:09.446818	13	6	f
3714	21	181	Cincinnati Bengals	7	2025-11-25 21:46:09.448035	13	7	f
3715	21	182	Chicago Bears	8	2025-11-25 21:46:09.449202	13	8	f
3716	21	183	San Francisco 49ers	9	2025-11-25 21:46:09.450366	13	9	f
3717	21	184	Jacksonville Jaguars	10	2025-11-25 21:46:09.451422	13	10	f
3718	21	185	Indianapolis Colts	11	2025-11-25 21:46:09.452382	13	0	f
3719	21	186	Miami Dolphins	13	2025-11-25 21:46:09.453408	13	0	f
3720	21	187	Atlanta Falcons	12	2025-11-25 21:46:09.454407	13	0	f
3721	21	188	Tampa Bay Buccaneers	14	2025-11-25 21:46:09.455422	13	0	f
3722	21	189	Carolina Panthers	4	2025-11-25 21:46:09.456419	13	4	f
3723	21	190	Seattle Seahawks	3	2025-11-25 21:46:09.457502	13	3	f
3724	21	191	Buffalo Bills	15	2025-11-25 21:46:09.458471	13	15	f
3725	21	192	Los Angeles Chargers	2	2025-11-25 21:46:09.459421	13	2	f
3726	21	193	Denver Broncos	16	2025-11-25 21:46:09.460431	13	0	f
3727	21	194	New England Patriots	1	2025-11-25 21:46:09.461835	13	1	f
3728	14	179	Detroit Lions	12	2025-11-26 23:47:33.214061	13	0	f
3729	14	180	Kansas City Chiefs	9	2025-11-27 20:47:21.733273	13	0	f
3730	14	181	Cincinnati Bengals	4	2025-11-27 20:47:21.734801	13	4	f
3731	14	182	Philadelphia Eagles	10	2025-11-28 15:11:06.075795	13	0	f
3732	14	183	Cleveland Browns	8	2025-11-29 04:00:48.419429	13	0	f
3733	14	184	Tennessee Titans	2	2025-11-29 04:00:48.420616	13	0	f
3734	14	185	Houston Texans	13	2025-11-29 04:00:48.42149	13	13	f
3735	14	186	Miami Dolphins	14	2025-11-29 04:00:48.422288	13	0	f
3736	14	187	Atlanta Falcons	11	2025-11-29 04:00:48.423078	13	0	f
3737	14	188	Tampa Bay Buccaneers	7	2025-11-29 04:00:48.423806	13	0	f
3738	14	189	Los Angeles Rams	5	2025-11-29 04:00:48.424594	13	0	f
3739	14	190	Seattle Seahawks	16	2025-11-29 04:00:48.425329	13	16	f
3740	14	191	Buffalo Bills	3	2025-11-29 04:00:48.426127	13	3	f
3741	14	192	Los Angeles Chargers	6	2025-11-29 04:00:48.42683	13	6	f
3742	14	193	Denver Broncos	15	2025-11-29 04:00:48.427539	13	0	f
3743	14	194	New England Patriots	1	2025-11-29 04:00:48.428256	13	1	f
3744	12	179	Green Bay Packers	11	2025-11-26 14:20:41.309277	13	11	f
3745	12	180	Dallas Cowboys	10	2025-11-26 14:20:41.310745	13	10	f
3746	12	181	Cincinnati Bengals	9	2025-11-26 14:20:41.311834	13	9	f
3747	12	182	Chicago Bears	8	2025-11-26 14:20:41.312849	13	8	f
3748	12	185	Houston Texans	12	2025-11-29 12:03:43.085736	13	12	f
3749	12	187	Atlanta Falcons	13	2025-11-29 12:03:43.088212	13	0	f
3750	12	193	Denver Broncos	16	2025-11-29 12:03:43.094334	13	0	f
3751	2	179	Detroit Lions	5	2025-11-27 13:13:17.07227	13	0	f
3752	2	180	Dallas Cowboys	2	2025-11-27 13:13:17.073654	13	2	f
3753	2	181	Cincinnati Bengals	10	2025-11-27 13:13:17.074681	13	10	f
3754	2	182	Philadelphia Eagles	1	2025-11-27 13:13:17.075679	13	0	f
3755	2	183	San Francisco 49ers	14	2025-11-27 13:13:17.076579	13	14	f
3756	2	184	Tennessee Titans	13	2025-11-27 13:13:17.077477	13	0	f
3757	2	185	Indianapolis Colts	9	2025-11-27 13:13:17.078614	13	0	f
3758	2	186	New Orleans Saints	3	2025-11-27 13:13:17.079452	13	3	f
3759	2	187	New York Jets	12	2025-11-27 13:13:17.08024	13	12	f
3760	2	188	Tampa Bay Buccaneers	11	2025-11-27 13:13:17.080979	13	0	f
3761	2	189	Los Angeles Rams	4	2025-11-27 13:13:17.081798	13	0	f
3762	2	190	Minnesota Vikings	6	2025-11-27 13:13:17.082667	13	0	f
3763	2	191	Buffalo Bills	8	2025-11-27 13:13:17.083423	13	8	f
3764	2	192	Las Vegas Raiders	7	2025-11-27 13:13:17.084191	13	0	f
3765	2	193	Denver Broncos	16	2025-11-27 13:13:17.0849	13	0	f
3766	2	194	New England Patriots	15	2025-11-27 13:13:17.085642	13	15	f
3767	13	179	Detroit Lions	6	2025-11-27 11:45:53.917421	13	0	f
3768	13	180	Kansas City Chiefs	7	2025-11-27 11:45:53.918912	13	0	f
3769	13	181	Cincinnati Bengals	8	2025-11-27 11:45:53.920039	13	8	f
3770	12	183	San Francisco 49ers	1	2025-11-29 12:03:43.082863	13	1	f
3771	12	184	Jacksonville Jaguars	2	2025-11-29 12:03:43.084495	13	2	f
3772	12	186	Miami Dolphins	7	2025-11-29 12:03:43.086982	13	0	f
3773	12	188	Tampa Bay Buccaneers	6	2025-11-29 12:03:43.089315	13	0	f
3774	12	189	Los Angeles Rams	4	2025-11-29 12:03:43.090393	13	0	f
3775	12	190	Seattle Seahawks	14	2025-11-29 12:03:43.091435	13	14	f
3776	12	191	Pittsburgh Steelers	5	2025-11-29 12:03:43.092312	13	0	f
3777	12	192	Los Angeles Chargers	3	2025-11-29 12:03:43.09331	13	3	f
3778	12	194	New England Patriots	15	2025-11-29 12:03:43.095283	13	15	f
3779	23	179	Detroit Lions	4	2025-11-26 15:20:32.111238	13	0	f
3780	23	180	Dallas Cowboys	5	2025-11-26 15:20:32.11277	13	5	f
3781	23	181	Baltimore Ravens	7	2025-11-26 15:20:32.114173	13	0	f
3782	23	182	Philadelphia Eagles	10	2025-11-26 15:20:32.115368	13	0	f
3783	23	183	San Francisco 49ers	9	2025-11-26 15:20:32.11646	13	9	f
3784	23	184	Jacksonville Jaguars	11	2025-11-26 15:20:32.117561	13	11	f
3785	23	185	Indianapolis Colts	1	2025-11-26 15:20:32.118602	13	0	f
3786	23	186	Miami Dolphins	3	2025-11-26 15:20:32.119594	13	0	f
3787	23	187	Atlanta Falcons	8	2025-11-26 15:20:32.120655	13	0	f
3788	23	188	Tampa Bay Buccaneers	6	2025-11-26 15:20:32.121635	13	0	f
3789	23	189	Los Angeles Rams	12	2025-11-26 15:20:32.122627	13	0	f
3790	23	190	Seattle Seahawks	13	2025-11-26 15:20:32.12356	13	13	f
3791	23	191	Buffalo Bills	14	2025-11-26 15:20:32.124507	13	14	f
3792	23	192	Las Vegas Raiders	15	2025-11-26 15:20:32.125482	13	0	f
3793	23	193	Denver Broncos	16	2025-11-26 15:20:32.126506	13	0	f
3794	23	194	New York Giants	2	2025-11-26 15:20:32.127449	13	0	f
3795	20	179	Detroit Lions	10	2025-11-26 15:53:54.889151	13	0	f
3796	20	180	Dallas Cowboys	16	2025-11-26 15:53:54.890567	13	16	f
3797	20	181	Baltimore Ravens	12	2025-11-26 15:53:54.891806	13	0	f
3798	20	182	Philadelphia Eagles	14	2025-11-26 15:53:54.892747	13	0	f
3799	20	183	Cleveland Browns	4	2025-11-30 16:34:05.954125	13	0	f
3800	20	186	Miami Dolphins	1	2025-11-30 16:34:05.957905	13	0	f
3801	20	187	Atlanta Falcons	2	2025-11-30 16:34:05.958817	13	0	f
3802	20	193	Denver Broncos	13	2025-11-30 19:43:51.908666	13	0	f
3803	20	194	New York Giants	11	2025-12-01 02:21:38.040122	13	0	f
3804	20	191	Pittsburgh Steelers	7	2025-11-30 19:43:51.905987	13	0	f
3805	20	192	Las Vegas Raiders	3	2025-11-30 19:43:51.907314	13	0	f
3806	20	185	Houston Texans	5	2025-11-30 16:34:05.956834	13	5	f
3807	20	184	Jacksonville Jaguars	15	2025-11-30 16:34:05.955672	13	15	f
3808	20	188	Tampa Bay Buccaneers	6	2025-11-30 16:34:05.959581	13	0	f
3809	20	189	Los Angeles Rams	8	2025-11-30 16:34:05.96031	13	0	f
3810	20	190	Minnesota Vikings	9	2025-11-30 19:43:51.904298	13	0	f
3811	22	179	Green Bay Packers	2	2025-11-26 15:55:29.050852	13	2	f
3812	22	180	Kansas City Chiefs	13	2025-11-26 15:55:29.052347	13	0	f
3813	22	181	Cincinnati Bengals	7	2025-11-26 15:55:29.053417	13	7	f
3814	22	182	Chicago Bears	3	2025-11-26 15:55:29.054388	13	3	f
3815	22	183	Cleveland Browns	4	2025-11-26 15:55:29.055524	13	0	f
3816	22	184	Tennessee Titans	1	2025-11-26 15:55:29.056494	13	0	f
3817	22	185	Houston Texans	10	2025-11-26 15:55:29.057424	13	10	f
3818	22	186	Miami Dolphins	14	2025-11-26 15:55:29.058608	13	0	f
3819	22	187	New York Jets	5	2025-11-26 15:55:29.059716	13	5	f
3820	22	188	Tampa Bay Buccaneers	15	2025-11-26 15:55:29.060801	13	0	f
3821	22	189	Carolina Panthers	9	2025-11-26 15:55:29.061658	13	9	f
3822	22	190	Seattle Seahawks	16	2025-11-26 15:55:29.062559	13	16	f
3823	22	191	Buffalo Bills	8	2025-11-26 15:55:29.063469	13	8	f
3824	22	192	Los Angeles Chargers	12	2025-11-26 15:55:29.064459	13	12	f
3825	22	193	Denver Broncos	11	2025-11-26 15:55:29.065286	13	0	f
3826	22	194	New England Patriots	6	2025-11-26 15:55:29.065979	13	6	f
3827	5	179	Detroit Lions	13	2025-11-26 22:49:20.887229	13	0	f
3828	5	180	Kansas City Chiefs	1	2025-11-26 22:49:20.888767	13	0	f
3829	5	181	Cincinnati Bengals	2	2025-11-26 22:49:20.889952	13	2	f
3830	5	182	Chicago Bears	3	2025-11-26 22:49:20.89106	13	3	f
3831	5	183	Cleveland Browns	4	2025-11-26 22:49:20.892064	13	0	f
3832	5	184	Jacksonville Jaguars	6	2025-11-26 22:49:20.893024	13	6	f
3833	5	185	Indianapolis Colts	8	2025-11-26 22:49:20.893967	13	0	f
3834	5	186	Miami Dolphins	12	2025-11-26 22:49:20.894902	13	0	f
3835	5	187	Atlanta Falcons	10	2025-11-26 22:49:20.895836	13	0	f
3836	5	188	Tampa Bay Buccaneers	9	2025-11-26 22:49:20.896762	13	0	f
3837	5	189	Carolina Panthers	5	2025-11-26 22:49:20.897686	13	5	f
3838	5	190	Seattle Seahawks	16	2025-11-26 22:49:20.898615	13	16	f
3839	5	191	Buffalo Bills	15	2025-11-26 22:49:20.899539	13	15	f
3840	5	192	Los Angeles Chargers	11	2025-11-26 22:49:20.900452	13	11	f
3841	5	193	Denver Broncos	14	2025-11-26 22:49:20.901352	13	0	f
3842	5	194	New York Giants	7	2025-11-26 22:49:20.902267	13	0	f
3843	8	179	Detroit Lions	8	2025-11-27 00:08:13.919247	13	0	f
3844	8	180	Dallas Cowboys	12	2025-11-27 21:01:08.335941	13	12	f
3845	8	181	Cincinnati Bengals	5	2025-11-27 21:01:08.337656	13	5	f
3846	8	182	Chicago Bears	13	2025-11-27 21:01:08.338657	13	13	f
3847	8	183	San Francisco 49ers	7	2025-11-27 21:01:08.339726	13	7	f
3848	8	184	Jacksonville Jaguars	16	2025-11-27 21:01:08.34058	13	16	f
3849	8	185	Houston Texans	9	2025-11-27 21:01:08.341787	13	9	f
3850	8	186	Miami Dolphins	15	2025-11-27 21:01:08.342598	13	0	f
3851	8	187	Atlanta Falcons	14	2025-11-27 21:01:08.343746	13	0	f
3852	8	188	Arizona Cardinals	1	2025-11-27 21:01:08.344597	13	1	f
3853	8	189	Carolina Panthers	10	2025-11-27 21:01:08.34538	13	10	f
3854	8	190	Minnesota Vikings	4	2025-11-27 21:01:08.346348	13	0	f
3855	8	191	Buffalo Bills	3	2025-11-27 21:01:08.347305	13	3	f
3856	8	192	Los Angeles Chargers	11	2025-11-27 21:01:08.348211	13	11	f
3857	8	193	Denver Broncos	6	2025-11-27 21:01:08.349254	13	0	f
3858	8	194	New England Patriots	2	2025-11-27 21:01:08.350111	13	2	f
3859	16	179	Detroit Lions	12	2025-11-27 01:08:17.736442	13	0	f
3860	16	180	Kansas City Chiefs	4	2025-11-27 01:08:17.737829	13	0	f
3861	16	181	Baltimore Ravens	8	2025-11-27 01:08:17.738906	13	0	f
3862	16	182	Chicago Bears	6	2025-11-27 01:08:17.739792	13	6	f
3863	16	183	San Francisco 49ers	13	2025-11-27 01:08:17.740635	13	13	f
3864	16	184	Tennessee Titans	5	2025-11-27 01:08:17.741408	13	0	f
3865	16	185	Indianapolis Colts	14	2025-11-27 01:08:17.742197	13	0	f
3866	16	186	Miami Dolphins	7	2025-11-27 01:08:17.742913	13	0	f
3867	16	187	Atlanta Falcons	15	2025-11-27 01:08:17.743644	13	0	f
3868	16	188	Tampa Bay Buccaneers	16	2025-11-27 01:08:17.744421	13	0	f
3869	16	189	Carolina Panthers	1	2025-11-27 01:08:17.745173	13	1	f
3870	16	190	Minnesota Vikings	2	2025-11-27 01:08:17.745902	13	0	f
3871	16	191	Buffalo Bills	11	2025-11-27 01:08:17.746631	13	11	f
3872	16	192	Los Angeles Chargers	3	2025-11-27 01:08:17.747442	13	3	f
3873	16	193	Denver Broncos	9	2025-11-27 01:08:17.748226	13	0	f
3874	16	194	New England Patriots	10	2025-11-27 01:08:17.748797	13	10	f
3875	10	179	Detroit Lions	16	2025-11-27 02:01:32.844277	13	0	f
3876	10	180	Dallas Cowboys	15	2025-11-27 02:01:32.845469	13	15	f
3877	10	181	Cincinnati Bengals	14	2025-11-27 02:01:32.846392	13	14	f
3878	13	182	Chicago Bears	9	2025-11-27 11:45:53.921442	13	9	f
3879	9	179	Detroit Lions	6	2025-11-27 14:17:10.552703	13	0	f
3880	9	180	Kansas City Chiefs	9	2025-11-27 14:17:10.554442	13	0	f
3881	9	181	Cincinnati Bengals	12	2025-11-27 14:17:10.555973	13	12	f
3882	9	182	Chicago Bears	4	2025-11-27 14:17:10.557151	13	4	f
3883	9	183	Cleveland Browns	3	2025-11-27 14:17:10.558324	13	0	f
3884	9	184	Tennessee Titans	8	2025-11-27 14:17:10.55936	13	0	f
3885	9	185	Indianapolis Colts	10	2025-11-27 14:17:10.560579	13	0	f
3886	9	186	Miami Dolphins	5	2025-11-27 14:17:10.561579	13	0	f
3887	9	187	Atlanta Falcons	14	2025-11-27 14:17:10.562392	13	0	f
3888	9	188	Arizona Cardinals	7	2025-11-27 14:17:10.56316	13	7	f
3889	9	189	Los Angeles Rams	13	2025-11-27 14:17:10.563989	13	0	f
3890	9	190	Minnesota Vikings	1	2025-11-27 14:17:10.564792	13	0	f
3891	9	191	Buffalo Bills	16	2025-11-27 14:17:10.565567	13	16	f
3892	9	193	Denver Broncos	15	2025-11-27 14:17:10.567381	13	0	f
3893	9	194	New York Giants	2	2025-11-27 14:17:10.568256	13	0	f
3894	9	192	Los Angeles Chargers	11	2025-11-27 14:17:10.56683	13	11	f
3895	18	179	Green Bay Packers	5	2025-11-27 14:25:01.614479	13	5	f
3896	18	180	Dallas Cowboys	10	2025-11-27 14:25:01.616051	13	10	f
3897	18	181	Baltimore Ravens	16	2025-11-27 14:25:01.61727	13	0	f
3898	18	182	Chicago Bears	6	2025-11-27 14:25:01.618422	13	6	f
3899	19	179	Detroit Lions	5	2025-11-27 14:30:35.507314	13	0	f
3900	19	180	Kansas City Chiefs	16	2025-11-27 14:30:35.508831	13	0	f
3901	19	181	Baltimore Ravens	15	2025-11-27 14:30:35.510079	13	0	f
3902	19	182	Philadelphia Eagles	14	2025-11-27 14:30:35.51162	13	0	f
3903	4	179	Detroit Lions	5	2025-11-27 14:46:38.307114	13	0	f
3904	4	180	Dallas Cowboys	7	2025-11-27 14:46:38.308254	13	7	f
3905	4	181	Cincinnati Bengals	8	2025-11-27 14:46:38.309086	13	8	f
3906	4	182	Chicago Bears	9	2025-11-28 14:00:45.65647	13	9	f
3907	17	179	Detroit Lions	3	2025-11-27 16:04:40.78057	13	0	f
3908	17	180	Dallas Cowboys	1	2025-11-27 16:04:40.782307	13	1	f
3909	17	181	Cincinnati Bengals	7	2025-11-27 16:04:40.78369	13	7	f
3910	17	182	Chicago Bears	8	2025-11-27 16:04:40.784898	13	8	f
3911	15	181	Cincinnati Bengals	6	2025-11-28 00:25:54.090489	13	6	f
3912	26	181	Cincinnati Bengals	14	2025-11-28 01:03:14.43914	13	14	f
3913	4	183	San Francisco 49ers	4	2025-11-28 14:00:45.659184	13	4	f
3914	4	184	Jacksonville Jaguars	10	2025-11-28 14:00:45.660793	13	10	f
3915	4	185	Houston Texans	11	2025-11-28 14:00:45.662384	13	11	f
3916	4	186	Miami Dolphins	2	2025-11-28 14:00:45.663752	13	0	f
3917	4	187	Atlanta Falcons	3	2025-11-28 14:00:45.664989	13	0	f
3918	4	188	Tampa Bay Buccaneers	6	2025-11-28 14:00:45.666406	13	0	f
3919	4	189	Los Angeles Rams	1	2025-11-28 14:00:45.667809	13	0	f
3920	4	190	Minnesota Vikings	12	2025-11-28 14:00:45.669167	13	0	f
3921	4	191	Buffalo Bills	13	2025-11-28 14:00:45.670508	13	13	f
3922	4	192	Las Vegas Raiders	14	2025-11-28 14:00:45.671868	13	0	f
3923	4	193	Denver Broncos	15	2025-11-28 14:00:45.673158	13	0	f
3924	4	194	New York Giants	16	2025-11-28 14:00:45.674229	13	0	f
3925	15	182	Chicago Bears	8	2025-11-28 15:29:25.8648	13	8	f
3926	10	182	Chicago Bears	13	2025-11-28 16:38:14.378271	13	13	f
3927	10	193	Denver Broncos	12	2025-11-30 16:55:46.278875	13	0	f
3928	13	183	Cleveland Browns	13	2025-11-30 04:50:01.428879	13	0	f
3929	13	184	Tennessee Titans	14	2025-11-30 04:50:01.430283	13	0	f
3930	13	185	Houston Texans	2	2025-11-30 04:50:01.431711	13	2	f
3931	13	186	Miami Dolphins	15	2025-11-30 04:50:01.433092	13	0	f
3932	13	187	Atlanta Falcons	3	2025-11-30 04:50:01.433919	13	0	f
3933	13	188	Tampa Bay Buccaneers	4	2025-11-30 04:50:01.434719	13	0	f
3934	13	189	Los Angeles Rams	5	2025-11-30 04:50:01.435541	13	0	f
3935	13	190	Seattle Seahawks	12	2025-11-30 04:50:01.436337	13	12	f
3936	13	191	Buffalo Bills	11	2025-11-30 04:50:01.437213	13	11	f
3937	13	192	Las Vegas Raiders	10	2025-11-30 04:50:01.437946	13	0	f
3938	13	193	Denver Broncos	16	2025-11-30 04:50:01.438715	13	0	f
3939	13	194	New York Giants	1	2025-11-30 04:50:01.439345	13	0	f
3940	18	183	San Francisco 49ers	12	2025-11-30 11:56:07.91676	13	12	f
3941	18	184	Tennessee Titans	11	2025-11-30 11:56:07.91797	13	0	f
3942	18	185	Houston Texans	9	2025-11-30 11:56:07.918969	13	9	f
3943	18	186	Miami Dolphins	13	2025-11-30 11:56:07.919909	13	0	f
3944	18	187	Atlanta Falcons	15	2025-11-30 11:56:07.920852	13	0	f
3945	18	188	Tampa Bay Buccaneers	2	2025-11-30 11:56:07.921824	13	0	f
3946	18	189	Carolina Panthers	3	2025-11-30 11:56:07.923035	13	3	f
3947	18	190	Minnesota Vikings	4	2025-11-30 11:56:07.924418	13	0	f
3948	18	191	Buffalo Bills	7	2025-11-30 11:56:07.925637	13	7	f
3949	18	192	Las Vegas Raiders	1	2025-11-30 11:56:07.926841	13	0	f
3950	18	193	Denver Broncos	14	2025-11-30 11:56:07.928146	13	0	f
3951	18	194	New York Giants	8	2025-11-30 11:56:07.929209	13	0	f
3952	26	183	Cleveland Browns	12	2025-11-30 13:50:05.260149	13	0	f
3953	26	184	Jacksonville Jaguars	6	2025-11-30 13:50:05.261636	13	6	f
3954	26	185	Houston Texans	7	2025-11-30 13:50:05.262926	13	7	f
3955	26	186	Miami Dolphins	2	2025-11-30 13:50:05.264164	13	0	f
3956	26	187	Atlanta Falcons	8	2025-11-30 13:50:05.265325	13	0	f
3957	26	188	Tampa Bay Buccaneers	9	2025-11-30 13:50:05.266262	13	0	f
3958	26	189	Los Angeles Rams	1	2025-11-30 13:50:05.267347	13	0	f
3959	26	190	Seattle Seahawks	10	2025-11-30 13:50:05.268442	13	10	f
3960	26	191	Buffalo Bills	11	2025-11-30 13:50:05.269421	13	11	f
3961	26	192	Los Angeles Chargers	3	2025-11-30 13:50:05.270304	13	3	f
3962	26	193	Denver Broncos	4	2025-11-30 13:50:05.271169	13	0	f
3963	26	194	New England Patriots	5	2025-11-30 13:50:05.272075	13	5	f
3964	15	183	San Francisco 49ers	9	2025-11-30 14:53:57.716167	13	9	f
3965	15	184	Jacksonville Jaguars	11	2025-11-30 14:53:57.718076	13	11	f
3966	15	185	Houston Texans	2	2025-11-30 14:53:57.719518	13	2	f
3967	15	186	Miami Dolphins	3	2025-11-30 14:53:57.720829	13	0	f
3968	15	187	Atlanta Falcons	10	2025-11-30 14:53:57.722096	13	0	f
3969	15	188	Tampa Bay Buccaneers	13	2025-11-30 14:53:57.723302	13	0	f
3970	15	189	Los Angeles Rams	4	2025-11-30 14:53:57.72441	13	0	f
3971	15	190	Seattle Seahawks	5	2025-11-30 14:53:57.725511	13	5	f
3972	15	191	Buffalo Bills	12	2025-11-30 14:53:57.726586	13	12	f
3973	15	192	Las Vegas Raiders	7	2025-11-30 14:53:57.727631	13	0	f
3974	15	193	Denver Broncos	14	2025-11-30 14:53:57.729684	13	0	f
3975	15	194	New York Giants	1	2025-11-30 14:53:57.731087	13	0	f
3976	17	183	Cleveland Browns	5	2025-11-30 15:36:45.159295	13	0	f
3977	17	184	Jacksonville Jaguars	9	2025-11-30 15:36:45.160859	13	9	f
3978	17	185	Indianapolis Colts	11	2025-11-30 15:36:45.161991	13	0	f
3979	17	186	New Orleans Saints	6	2025-11-30 15:36:45.16284	13	6	f
3980	17	187	Atlanta Falcons	2	2025-11-30 15:36:45.163653	13	0	f
3981	17	188	Tampa Bay Buccaneers	10	2025-11-30 15:36:45.164402	13	0	f
3982	17	189	Los Angeles Rams	16	2025-11-30 15:36:45.16513	13	0	f
3983	17	190	Seattle Seahawks	15	2025-11-30 15:36:45.165833	13	15	f
3984	17	191	Buffalo Bills	4	2025-11-30 15:36:45.166554	13	4	f
3985	17	192	Los Angeles Chargers	12	2025-11-30 15:36:45.167383	13	12	f
3986	17	193	Denver Broncos	14	2025-11-30 15:36:45.168234	13	0	f
3987	17	194	New England Patriots	13	2025-11-30 15:36:45.168925	13	13	f
3988	10	183	San Francisco 49ers	7	2025-11-30 16:55:46.264747	13	7	f
3989	10	184	Jacksonville Jaguars	10	2025-11-30 16:55:46.2667	13	10	f
3990	10	185	Houston Texans	11	2025-11-30 16:55:46.26833	13	11	f
3991	10	186	Miami Dolphins	4	2025-11-30 16:55:46.269813	13	0	f
3992	10	187	Atlanta Falcons	6	2025-11-30 16:55:46.271124	13	0	f
3993	10	188	Tampa Bay Buccaneers	5	2025-11-30 16:55:46.272667	13	0	f
3994	10	189	Los Angeles Rams	3	2025-11-30 16:55:46.274248	13	0	f
3995	10	190	Seattle Seahawks	2	2025-11-30 16:55:46.275455	13	2	f
3996	10	191	Pittsburgh Steelers	9	2025-11-30 16:55:46.276602	13	0	f
3997	10	192	Los Angeles Chargers	1	2025-11-30 16:55:46.2779	13	1	f
3998	10	194	New York Giants	8	2025-11-30 16:55:46.279968	13	0	f
3999	19	183	San Francisco 49ers	9	2025-11-30 17:04:08.781627	13	9	f
4000	19	184	Jacksonville Jaguars	6	2025-11-30 17:04:08.783179	13	6	f
4001	19	185	Indianapolis Colts	10	2025-11-30 17:04:08.784312	13	0	f
4002	19	186	New Orleans Saints	8	2025-11-30 17:04:08.788079	13	8	f
4003	19	187	Atlanta Falcons	7	2025-11-30 17:04:08.789253	13	0	f
4004	19	188	Tampa Bay Buccaneers	11	2025-11-30 17:04:08.790548	13	0	f
4005	19	189	Los Angeles Rams	4	2025-11-30 17:04:08.791674	13	0	f
4006	19	190	Minnesota Vikings	13	2025-11-30 17:04:08.792842	13	0	f
4007	19	191	Buffalo Bills	3	2025-11-30 17:04:08.793893	13	3	f
4008	19	192	Las Vegas Raiders	2	2025-11-30 17:04:08.795083	13	0	f
4009	19	193	Denver Broncos	12	2025-11-30 17:04:08.796149	13	0	f
4010	19	194	New York Giants	1	2025-11-30 17:04:08.79722	13	0	f
4011	12	195	Dallas Cowboys	9	2025-12-02 14:41:18.827223	14	0	f
4012	12	196	Seattle Seahawks	13	2025-12-07 12:10:18.298958	14	13	f
4013	12	197	Cleveland Browns	10	2025-12-07 12:10:18.300352	14	0	f
4014	12	198	Green Bay Packers	3	2025-12-07 12:10:18.301413	14	3	f
4015	12	199	Washington Commanders	4	2025-12-07 12:10:18.302445	14	0	f
4016	12	200	Miami Dolphins	8	2025-12-07 12:10:18.30343	14	8	f
4017	12	201	Tampa Bay Buccaneers	1	2025-12-07 12:10:18.304386	14	0	f
4018	12	202	Jacksonville Jaguars	11	2025-12-07 12:10:18.305337	14	11	f
4019	12	203	Pittsburgh Steelers	7	2025-12-07 12:10:18.306298	14	7	f
4020	12	204	Denver Broncos	12	2025-12-07 12:10:18.307268	14	0	f
4021	12	205	Buffalo Bills	2	2025-12-07 12:10:18.308208	14	0	f
4022	12	206	Arizona Cardinals	6	2025-12-07 12:10:18.309158	14	0	f
4023	12	207	Houston Texans	5	2025-12-07 12:10:18.310095	14	5	f
4024	12	208	Philadelphia Eagles	14	2025-12-07 12:10:18.310991	14	0	f
4025	1	195	Detroit Lions	13	2025-12-02 16:03:41.351805	14	13	f
4026	1	196	Seattle Seahawks	6	2025-12-02 16:03:41.353267	14	6	f
4027	1	197	Cleveland Browns	7	2025-12-02 16:03:41.354398	14	0	f
4028	1	198	Green Bay Packers	8	2025-12-02 16:03:41.35545	14	8	f
4029	1	199	Washington Commanders	9	2025-12-02 16:03:41.356395	14	0	f
4030	1	200	Miami Dolphins	5	2025-12-02 16:03:41.357319	14	5	f
4031	1	201	Tampa Bay Buccaneers	4	2025-12-02 16:03:41.358208	14	0	f
4032	1	202	Indianapolis Colts	10	2025-12-02 16:03:41.359086	14	0	f
4033	1	203	Baltimore Ravens	3	2025-12-02 16:03:41.359964	14	0	f
4034	1	204	Denver Broncos	14	2025-12-02 16:03:41.360818	14	0	f
4035	1	205	Buffalo Bills	2	2025-12-02 16:03:41.361644	14	0	f
4036	1	206	Los Angeles Rams	1	2025-12-02 16:03:41.362523	14	1	f
4037	1	207	Kansas City Chiefs	11	2025-12-02 16:03:41.363334	14	0	f
4038	1	208	Philadelphia Eagles	12	2025-12-02 16:03:41.363986	14	0	f
4039	14	195	Dallas Cowboys	13	2025-12-04 22:41:41.096816	14	0	f
4040	14	196	Seattle Seahawks	14	2025-12-06 22:30:28.494425	14	14	f
4041	14	197	Cleveland Browns	12	2025-12-06 22:30:28.49599	14	0	f
4042	14	198	Green Bay Packers	8	2025-12-06 22:30:28.497594	14	8	f
4043	14	199	Washington Commanders	10	2025-12-06 22:30:28.49915	14	0	f
4044	14	200	New York Jets	9	2025-12-06 22:30:28.500229	14	0	f
4045	14	201	Tampa Bay Buccaneers	6	2025-12-06 22:30:28.501359	14	0	f
4046	14	202	Jacksonville Jaguars	11	2025-12-06 22:30:28.502442	14	11	f
4047	14	203	Baltimore Ravens	1	2025-12-06 22:30:28.503388	14	0	f
4048	14	204	Denver Broncos	2	2025-12-06 22:30:28.504336	14	0	f
4049	14	205	Cincinnati Bengals	5	2025-12-06 22:30:28.505299	14	5	f
4050	14	206	Los Angeles Rams	7	2025-12-06 22:30:28.50622	14	7	f
4051	14	207	Houston Texans	3	2025-12-06 22:30:28.507253	14	3	f
4052	14	208	Philadelphia Eagles	4	2025-12-06 22:30:28.508155	14	0	f
4053	2	195	Dallas Cowboys	5	2025-12-02 21:52:07.585417	14	0	f
4054	20	195	Dallas Cowboys	14	2025-12-03 05:39:09.088884	14	0	f
4055	20	208	Philadelphia Eagles	9	2025-12-03 05:39:09.099122	14	0	f
4056	20	204	Las Vegas Raiders	11	2025-12-03 05:39:09.096203	14	11	f
4057	20	200	Miami Dolphins	12	2025-12-03 05:39:09.093277	14	12	f
4058	20	201	Tampa Bay Buccaneers	4	2025-12-03 05:39:09.093998	14	0	f
4059	20	202	Indianapolis Colts	3	2025-12-03 05:39:09.09475	14	0	f
4060	20	203	Baltimore Ravens	13	2025-12-03 05:39:09.095479	14	0	f
4061	20	205	Cincinnati Bengals	1	2025-12-03 05:39:09.096916	14	1	f
4062	20	206	Los Angeles Rams	2	2025-12-03 05:39:09.097651	14	2	f
4063	20	207	Kansas City Chiefs	5	2025-12-03 05:39:09.098409	14	0	f
4064	20	196	Seattle Seahawks	8	2025-12-03 05:39:09.090102	14	8	f
4065	20	197	Cleveland Browns	7	2025-12-03 05:39:09.090943	14	0	f
4066	20	198	Green Bay Packers	6	2025-12-03 05:39:09.091752	14	6	f
4067	20	199	Washington Commanders	10	2025-12-03 05:39:09.092535	14	0	f
4068	13	195	Dallas Cowboys	5	2025-12-03 14:01:19.796454	14	0	f
4069	13	196	Seattle Seahawks	9	2025-12-06 23:45:07.322426	14	9	f
4070	13	197	Cleveland Browns	8	2025-12-06 23:45:07.32351	14	0	f
4071	13	198	Chicago Bears	11	2025-12-06 23:45:07.324321	14	0	f
4072	13	199	Washington Commanders	14	2025-12-06 23:45:07.325177	14	0	f
4073	13	200	Miami Dolphins	7	2025-12-06 23:45:07.32598	14	7	f
4074	13	201	New Orleans Saints	12	2025-12-06 23:45:07.326796	14	12	f
4075	13	202	Jacksonville Jaguars	13	2025-12-06 23:45:07.327588	14	13	f
4076	13	203	Baltimore Ravens	6	2025-12-06 23:45:07.328479	14	0	f
4077	13	204	Denver Broncos	10	2025-12-06 23:45:07.329336	14	0	f
4078	13	205	Cincinnati Bengals	4	2025-12-06 23:45:07.330248	14	4	f
4079	13	206	Arizona Cardinals	3	2025-12-06 23:45:07.331139	14	0	f
4080	13	207	Houston Texans	2	2025-12-06 23:45:07.331983	14	2	f
4081	13	208	Philadelphia Eagles	1	2025-12-06 23:45:07.332838	14	0	f
4082	8	195	Dallas Cowboys	7	2025-12-03 18:30:59.844386	14	0	f
4083	8	196	Seattle Seahawks	10	2025-12-03 18:30:59.846022	14	10	f
4084	8	197	Cleveland Browns	8	2025-12-03 18:30:59.847176	14	0	f
4085	8	198	Chicago Bears	9	2025-12-03 18:30:59.848303	14	0	f
4086	8	199	Washington Commanders	6	2025-12-03 18:30:59.849321	14	0	f
4087	8	200	Miami Dolphins	11	2025-12-03 18:30:59.850315	14	11	f
4088	8	201	Tampa Bay Buccaneers	5	2025-12-03 18:30:59.85129	14	0	f
4089	8	202	Jacksonville Jaguars	12	2025-12-03 18:30:59.852317	14	12	f
4090	8	203	Pittsburgh Steelers	1	2025-12-03 18:30:59.853276	14	1	f
4091	8	204	Las Vegas Raiders	4	2025-12-03 18:30:59.854243	14	4	f
4092	8	205	Cincinnati Bengals	2	2025-12-03 18:30:59.855179	14	2	f
4093	8	206	Los Angeles Rams	14	2025-12-03 18:30:59.856156	14	14	f
4094	8	207	Houston Texans	13	2025-12-03 18:30:59.857097	14	13	f
4095	8	208	Los Angeles Chargers	3	2025-12-03 18:30:59.85807	14	3	f
4096	21	195	Detroit Lions	5	2025-12-04 02:14:28.382303	14	5	f
4097	21	196	Atlanta Falcons	6	2025-12-04 02:14:28.383611	14	0	f
4098	21	197	Cleveland Browns	7	2025-12-04 02:14:28.384545	14	0	f
4099	21	198	Chicago Bears	8	2025-12-04 02:14:28.385432	14	0	f
4100	21	199	Washington Commanders	9	2025-12-04 02:14:28.386425	14	0	f
4101	21	200	Miami Dolphins	10	2025-12-04 02:14:28.38742	14	10	f
4102	21	201	New Orleans Saints	11	2025-12-04 02:14:28.388286	14	11	f
4103	21	202	Indianapolis Colts	12	2025-12-04 02:14:28.389169	14	0	f
4104	21	203	Baltimore Ravens	13	2025-12-04 02:14:28.390129	14	0	f
4105	21	204	Las Vegas Raiders	4	2025-12-04 02:14:28.390854	14	4	f
4106	21	205	Cincinnati Bengals	3	2025-12-04 02:14:28.391613	14	3	f
4107	21	206	Arizona Cardinals	2	2025-12-04 02:14:28.39251	14	0	f
4108	21	207	Houston Texans	1	2025-12-04 02:14:28.393269	14	1	f
4109	21	208	Philadelphia Eagles	14	2025-12-04 02:14:28.394111	14	0	f
4110	16	195	Detroit Lions	12	2025-12-04 02:30:08.977589	14	12	f
4111	16	196	Seattle Seahawks	8	2025-12-04 02:30:08.979043	14	8	f
4112	16	197	Tennessee Titans	2	2025-12-04 02:30:08.980287	14	2	f
4113	16	198	Green Bay Packers	7	2025-12-04 02:30:08.981426	14	7	f
4114	16	199	Minnesota Vikings	3	2025-12-04 02:30:08.98247	14	3	f
4115	16	200	Miami Dolphins	13	2025-12-04 02:30:08.983273	14	13	f
4116	16	201	Tampa Bay Buccaneers	5	2025-12-04 02:30:08.984411	14	0	f
4117	16	202	Jacksonville Jaguars	4	2025-12-04 02:30:08.985426	14	4	f
4118	16	203	Baltimore Ravens	11	2025-12-04 02:30:08.986612	14	0	f
4119	16	204	Denver Broncos	6	2025-12-04 02:30:08.987422	14	0	f
4120	16	205	Buffalo Bills	9	2025-12-04 02:30:08.98855	14	0	f
4121	16	206	Arizona Cardinals	1	2025-12-04 02:30:08.989698	14	0	f
4122	16	207	Kansas City Chiefs	10	2025-12-04 02:30:08.991046	14	0	f
4123	16	208	Philadelphia Eagles	14	2025-12-04 02:30:08.991859	14	0	f
4124	4	195	Detroit Lions	10	2025-12-04 10:45:15.629276	14	10	f
4125	4	196	Seattle Seahawks	4	2025-12-04 10:45:15.630562	14	4	f
4126	4	197	Cleveland Browns	3	2025-12-04 10:45:15.631437	14	0	f
4127	4	198	Green Bay Packers	7	2025-12-04 10:45:15.632308	14	7	f
4128	4	199	Washington Commanders	6	2025-12-04 10:45:15.633172	14	0	f
4129	4	200	Miami Dolphins	5	2025-12-04 10:45:15.633914	14	5	f
4130	4	201	Tampa Bay Buccaneers	8	2025-12-04 10:45:15.634697	14	0	f
4131	4	202	Indianapolis Colts	11	2025-12-04 10:45:15.635694	14	0	f
4132	4	203	Baltimore Ravens	12	2025-12-04 10:45:15.636795	14	0	f
4133	4	204	Denver Broncos	14	2025-12-04 10:45:15.637915	14	0	f
4134	4	205	Buffalo Bills	13	2025-12-04 10:45:15.639093	14	0	f
4135	4	206	Los Angeles Rams	9	2025-12-04 10:45:15.640202	14	9	f
4136	4	207	Houston Texans	1	2025-12-04 10:45:15.641317	14	1	f
4137	4	208	Philadelphia Eagles	2	2025-12-04 10:45:15.642436	14	0	f
4138	23	195	Detroit Lions	5	2025-12-04 14:17:11.01632	14	5	f
4139	23	196	Seattle Seahawks	10	2025-12-04 14:17:11.017666	14	10	f
4140	23	197	Cleveland Browns	6	2025-12-04 14:17:11.018725	14	0	f
4141	23	198	Green Bay Packers	7	2025-12-04 14:17:11.019669	14	7	f
4142	23	199	Washington Commanders	2	2025-12-04 14:17:11.020601	14	0	f
4143	23	200	Miami Dolphins	3	2025-12-04 14:17:11.021446	14	3	f
4144	23	201	Tampa Bay Buccaneers	4	2025-12-04 14:17:11.022352	14	0	f
4145	23	202	Indianapolis Colts	9	2025-12-04 14:17:11.023276	14	0	f
4146	23	203	Pittsburgh Steelers	1	2025-12-04 14:17:11.024149	14	1	f
4147	23	204	Denver Broncos	14	2025-12-04 14:17:11.024943	14	0	f
4148	23	205	Buffalo Bills	12	2025-12-04 14:17:11.025799	14	0	f
4149	23	206	Los Angeles Rams	13	2025-12-04 14:17:11.02665	14	13	f
4150	23	207	Houston Texans	11	2025-12-04 14:17:11.027513	14	11	f
4151	23	208	Philadelphia Eagles	8	2025-12-04 14:17:11.028254	14	0	f
4152	5	195	Dallas Cowboys	6	2025-12-04 17:17:03.409895	14	0	f
4153	5	196	Seattle Seahawks	14	2025-12-04 17:17:03.412322	14	14	f
4154	5	197	Cleveland Browns	12	2025-12-04 17:17:03.413657	14	0	f
4155	5	198	Green Bay Packers	10	2025-12-04 17:17:03.414989	14	10	f
4156	5	199	Washington Commanders	11	2025-12-04 17:17:03.416297	14	0	f
4157	5	200	Miami Dolphins	13	2025-12-04 17:17:03.417528	14	13	f
4158	5	201	New Orleans Saints	3	2025-12-04 17:17:03.418757	14	3	f
4159	5	202	Indianapolis Colts	5	2025-12-04 17:17:03.419967	14	0	f
4160	5	203	Pittsburgh Steelers	2	2025-12-04 17:17:03.421185	14	2	f
4161	5	204	Las Vegas Raiders	1	2025-12-04 17:17:03.422334	14	1	f
4162	5	205	Cincinnati Bengals	4	2025-12-04 17:17:03.423479	14	4	f
4163	5	206	Los Angeles Rams	7	2025-12-04 17:17:03.424649	14	7	f
4164	5	207	Houston Texans	8	2025-12-04 17:17:03.425782	14	8	f
4165	5	208	Philadelphia Eagles	9	2025-12-04 17:17:03.426671	14	0	f
4166	19	195	Detroit Lions	5	2025-12-04 19:16:45.766528	14	5	f
4167	9	195	Dallas Cowboys	6	2025-12-04 20:55:23.026431	14	0	f
4168	9	196	Atlanta Falcons	2	2025-12-04 20:55:23.02793	14	0	f
4169	9	197	Cleveland Browns	12	2025-12-04 20:55:23.029179	14	0	f
4170	9	198	Chicago Bears	4	2025-12-04 20:55:23.030304	14	0	f
4171	9	199	Washington Commanders	7	2025-12-04 20:55:23.03135	14	0	f
4172	9	200	Miami Dolphins	10	2025-12-04 20:55:23.032365	14	10	f
4173	9	201	Tampa Bay Buccaneers	3	2025-12-04 20:55:23.033409	14	0	f
4174	9	202	Jacksonville Jaguars	8	2025-12-04 20:55:23.034458	14	8	f
4175	9	203	Pittsburgh Steelers	9	2025-12-04 20:55:23.035465	14	9	f
4176	9	204	Denver Broncos	11	2025-12-04 20:55:23.036474	14	0	f
4177	9	205	Cincinnati Bengals	5	2025-12-04 20:55:23.037445	14	5	f
4178	9	206	Arizona Cardinals	1	2025-12-04 20:55:23.038432	14	0	f
4179	9	207	Houston Texans	13	2025-12-04 20:55:23.039411	14	13	f
4180	9	208	Philadelphia Eagles	14	2025-12-04 20:55:23.040192	14	0	f
4181	22	195	Dallas Cowboys	8	2025-12-04 22:13:07.110414	14	0	f
4182	22	196	Seattle Seahawks	12	2025-12-04 22:13:07.111762	14	12	f
4183	22	197	Cleveland Browns	13	2025-12-04 22:13:07.112833	14	0	f
4184	22	198	Green Bay Packers	5	2025-12-04 22:13:07.113881	14	5	f
4185	22	199	Washington Commanders	6	2025-12-04 22:13:07.114903	14	0	f
4186	22	200	New York Jets	4	2025-12-04 22:13:07.115946	14	0	f
4187	22	201	New Orleans Saints	11	2025-12-04 22:13:07.117	14	11	f
4188	22	202	Jacksonville Jaguars	3	2025-12-04 22:13:07.118095	14	3	f
4189	22	203	Pittsburgh Steelers	2	2025-12-04 22:13:07.119133	14	2	f
4190	22	204	Las Vegas Raiders	7	2025-12-04 22:13:07.120151	14	7	f
4191	22	205	Cincinnati Bengals	10	2025-12-04 22:13:07.121175	14	10	f
4192	22	206	Los Angeles Rams	14	2025-12-04 22:13:07.122215	14	14	f
4193	22	207	Houston Texans	1	2025-12-04 22:13:07.123255	14	1	f
4194	22	208	Philadelphia Eagles	9	2025-12-04 22:13:07.124091	14	0	f
4195	15	195	Detroit Lions	4	2025-12-04 22:33:20.477631	14	4	f
4196	17	195	Dallas Cowboys	1	2025-12-04 22:38:21.902911	14	0	f
4197	10	195	Dallas Cowboys	3	2025-12-05 00:59:29.793276	14	0	f
4198	18	195	Detroit Lions	14	2025-12-05 00:35:10.4425	14	14	f
4199	18	196	Seattle Seahawks	10	2025-12-06 18:34:47.832519	14	10	f
4200	18	197	Cleveland Browns	1	2025-12-06 18:34:47.834195	14	0	f
4201	18	198	Chicago Bears	9	2025-12-06 18:34:47.835461	14	0	f
4202	18	199	Washington Commanders	13	2025-12-06 18:34:47.836547	14	0	f
4203	18	200	New York Jets	2	2025-12-06 18:34:47.837433	14	0	f
4204	18	201	Tampa Bay Buccaneers	8	2025-12-06 18:34:47.838596	14	0	f
4205	18	202	Jacksonville Jaguars	7	2025-12-06 18:34:47.839783	14	7	f
4206	18	203	Baltimore Ravens	11	2025-12-06 18:34:47.840934	14	0	f
4207	18	204	Las Vegas Raiders	6	2025-12-06 18:34:47.841782	14	6	f
4208	18	205	Cincinnati Bengals	5	2025-12-06 18:34:47.842587	14	5	f
4209	18	206	Los Angeles Rams	4	2025-12-06 18:34:47.84341	14	4	f
4210	18	207	Kansas City Chiefs	12	2025-12-06 18:34:47.84426	14	0	f
4211	18	208	Philadelphia Eagles	3	2025-12-06 18:34:47.844874	14	0	f
4212	10	196	Atlanta Falcons	6	2025-12-07 15:21:43.794975	14	0	f
4213	10	197	Cleveland Browns	5	2025-12-07 15:21:43.79629	14	0	f
4214	10	198	Chicago Bears	10	2025-12-07 15:21:43.797218	14	0	f
4215	10	199	Washington Commanders	4	2025-12-07 15:21:43.798102	14	0	f
4216	10	200	New York Jets	2	2025-12-07 15:21:43.798894	14	0	f
4217	10	201	Tampa Bay Buccaneers	7	2025-12-07 15:21:43.799695	14	0	f
4218	10	202	Jacksonville Jaguars	8	2025-12-07 15:21:43.800456	14	8	f
4219	10	203	Pittsburgh Steelers	9	2025-12-07 15:21:43.801185	14	9	f
4220	10	204	Denver Broncos	14	2025-12-07 15:21:43.801894	14	0	f
4221	10	205	Cincinnati Bengals	13	2025-12-07 15:21:43.802618	14	13	f
4222	10	206	Arizona Cardinals	1	2025-12-07 15:21:43.803334	14	0	f
4223	10	207	Houston Texans	12	2025-12-07 15:21:43.804107	14	12	f
4224	10	208	Philadelphia Eagles	11	2025-12-07 15:21:43.804849	14	0	f
4225	2	196	Seattle Seahawks	8	2025-12-07 14:51:37.946997	14	8	f
4226	2	197	Cleveland Browns	2	2025-12-07 14:51:37.9487	14	0	f
4227	2	198	Green Bay Packers	9	2025-12-07 14:51:37.950058	14	9	f
4228	2	199	Minnesota Vikings	10	2025-12-07 14:51:37.951438	14	10	f
4229	2	200	Miami Dolphins	7	2025-12-07 14:51:37.95278	14	7	f
4230	2	201	New Orleans Saints	1	2025-12-07 14:51:37.953961	14	1	f
4231	2	202	Indianapolis Colts	11	2025-12-07 14:51:37.955136	14	0	f
4232	2	203	Baltimore Ravens	12	2025-12-07 14:51:37.956268	14	0	f
4233	2	204	Denver Broncos	14	2025-12-07 14:51:37.957397	14	0	f
4234	2	205	Cincinnati Bengals	3	2025-12-07 14:51:37.958545	14	3	f
4235	2	206	Arizona Cardinals	6	2025-12-07 14:51:37.9597	14	0	f
4236	2	207	Kansas City Chiefs	4	2025-12-08 01:00:39.122992	14	0	f
4237	2	208	Philadelphia Eagles	13	2025-12-08 01:00:39.124351	14	0	f
4238	26	196	Seattle Seahawks	6	2025-12-07 15:40:39.818412	14	6	f
4239	26	197	Cleveland Browns	7	2025-12-07 15:40:39.819885	14	0	f
4240	26	198	Chicago Bears	3	2025-12-07 15:40:39.821253	14	0	f
4241	26	199	Washington Commanders	1	2025-12-07 15:40:39.822457	14	0	f
4242	26	200	Miami Dolphins	8	2025-12-07 15:40:39.823445	14	8	f
4243	26	201	Tampa Bay Buccaneers	10	2025-12-07 15:40:39.824411	14	0	f
4244	26	202	Indianapolis Colts	11	2025-12-07 15:40:39.825348	14	0	f
4245	26	203	Baltimore Ravens	5	2025-12-07 15:40:39.826309	14	0	f
4246	26	204	Denver Broncos	4	2025-12-07 15:40:39.827522	14	0	f
4247	26	205	Buffalo Bills	12	2025-12-07 15:40:39.828658	14	0	f
4248	26	206	Los Angeles Rams	13	2025-12-07 15:40:39.829863	14	13	f
4249	26	207	Kansas City Chiefs	2	2025-12-07 15:40:39.83073	14	0	f
4250	26	208	Philadelphia Eagles	9	2025-12-07 15:40:39.831375	14	0	f
4251	19	196	Seattle Seahawks	11	2025-12-07 16:12:59.567283	14	11	f
4252	19	197	Cleveland Browns	1	2025-12-07 16:12:59.568747	14	0	f
4253	19	198	Chicago Bears	12	2025-12-07 16:12:59.569695	14	0	f
4254	19	199	Washington Commanders	13	2025-12-07 16:12:59.57056	14	0	f
4255	19	200	New York Jets	4	2025-12-07 16:12:59.571366	14	0	f
4256	19	201	Tampa Bay Buccaneers	14	2025-12-07 16:12:59.572159	14	0	f
4257	19	202	Indianapolis Colts	10	2025-12-07 16:12:59.572996	14	0	f
4258	19	203	Baltimore Ravens	2	2025-12-07 16:12:59.573811	14	0	f
4259	19	204	Denver Broncos	9	2025-12-07 16:12:59.574586	14	0	f
4260	19	205	Buffalo Bills	3	2025-12-07 16:12:59.575354	14	0	f
4261	19	206	Los Angeles Rams	8	2025-12-07 16:12:59.576131	14	8	f
4262	19	207	Houston Texans	6	2025-12-07 16:12:59.576869	14	6	f
4263	19	208	Los Angeles Chargers	7	2025-12-07 16:12:59.577487	14	7	f
4264	17	196	Seattle Seahawks	13	2025-12-07 17:18:53.659931	14	13	f
4265	17	197	Cleveland Browns	12	2025-12-07 17:18:53.661107	14	0	f
4266	17	198	Chicago Bears	2	2025-12-07 17:18:53.661968	14	0	f
4267	17	199	Washington Commanders	3	2025-12-07 17:18:53.662777	14	0	f
4268	17	200	New York Jets	4	2025-12-07 17:18:53.663563	14	0	f
4269	17	201	Tampa Bay Buccaneers	11	2025-12-07 17:18:53.66432	14	0	f
4270	17	202	Indianapolis Colts	10	2025-12-07 17:18:53.665066	14	0	f
4271	17	203	Baltimore Ravens	5	2025-12-07 17:18:53.665794	14	0	f
4272	17	204	Denver Broncos	6	2025-12-07 17:18:53.666521	14	0	f
4273	17	205	Buffalo Bills	7	2025-12-07 17:18:53.667249	14	0	f
4274	17	206	Los Angeles Rams	14	2025-12-07 17:18:53.667945	14	14	f
4275	17	207	Houston Texans	9	2025-12-07 17:18:53.668689	14	9	f
4276	17	208	Los Angeles Chargers	8	2025-12-07 17:18:53.669412	14	8	f
4277	15	196	Seattle Seahawks	13	2025-12-07 17:24:47.426062	14	13	f
4278	15	197	Cleveland Browns	8	2025-12-07 17:24:47.42734	14	0	f
4279	15	198	Chicago Bears	9	2025-12-07 17:24:47.4283	14	0	f
4280	15	199	Washington Commanders	12	2025-12-07 17:24:47.429164	14	0	f
4281	15	200	Miami Dolphins	1	2025-12-07 17:24:47.429963	14	1	f
4282	15	201	Tampa Bay Buccaneers	10	2025-12-07 17:24:47.430774	14	0	f
4283	15	202	Indianapolis Colts	11	2025-12-07 17:24:47.43155	14	0	f
4284	15	203	Baltimore Ravens	2	2025-12-07 17:24:47.432358	14	0	f
4285	15	204	Denver Broncos	14	2025-12-07 17:24:47.433279	14	0	f
4286	15	205	Cincinnati Bengals	3	2025-12-07 17:24:47.434263	14	3	f
4287	15	206	Los Angeles Rams	6	2025-12-07 17:24:47.435178	14	6	f
4288	15	207	Houston Texans	7	2025-12-07 17:24:47.436091	14	7	f
4289	15	208	Philadelphia Eagles	5	2025-12-07 17:24:47.436732	14	0	f
4290	22	209	Tampa Bay Buccaneers	14	2025-12-11 17:41:15.450461	15	0	f
4291	22	210	Chicago Bears	15	2025-12-11 17:41:15.452368	15	15	f
4292	22	211	Baltimore Ravens	7	2025-12-11 17:41:15.453605	15	7	f
4293	22	212	Los Angeles Chargers	4	2025-12-11 17:41:15.454746	15	4	f
4294	22	213	Buffalo Bills	3	2025-12-11 17:41:15.455867	15	3	f
4295	22	214	New York Giants	1	2025-12-11 17:41:15.456795	15	0	f
4296	22	215	Las Vegas Raiders	2	2025-12-11 17:41:15.457609	15	0	f
4297	22	216	Jacksonville Jaguars	10	2025-12-11 17:41:15.458412	15	10	f
4298	22	217	Houston Texans	16	2025-12-11 17:41:15.459197	15	16	f
4299	22	218	Denver Broncos	11	2025-12-11 17:41:15.460245	15	11	f
4300	22	219	Detroit Lions	8	2025-12-11 17:41:15.461276	15	0	f
4301	22	220	Carolina Panthers	6	2025-12-11 17:41:15.46231	15	0	f
4302	22	221	San Francisco 49ers	13	2025-12-11 17:41:15.463172	15	13	f
4303	22	222	Seattle Seahawks	9	2025-12-11 17:41:15.464125	15	0	f
4304	22	223	Minnesota Vikings	5	2025-12-11 17:41:15.465041	15	5	f
4305	22	224	Pittsburgh Steelers	12	2025-12-11 17:41:15.465916	15	12	f
4306	12	209	Tampa Bay Buccaneers	10	2025-12-10 11:35:49.651088	15	0	f
4307	12	211	Cincinnati Bengals	11	2025-12-12 17:18:26.919595	15	0	f
4308	12	212	Kansas City Chiefs	9	2025-12-12 17:18:26.920488	15	0	f
4309	12	213	Buffalo Bills	12	2025-12-12 17:18:26.921272	15	12	f
4310	12	214	New York Giants	13	2025-12-12 17:18:26.922038	15	0	f
4311	12	218	Denver Broncos	16	2025-12-12 17:18:26.925764	15	16	f
4312	12	219	Los Angeles Rams	14	2025-12-12 17:18:26.926536	15	14	f
4313	12	220	Carolina Panthers	7	2025-12-12 17:18:26.92744	15	0	f
4314	12	224	Pittsburgh Steelers	15	2025-12-12 17:18:26.930548	15	15	f
4315	2	209	Tampa Bay Buccaneers	3	2025-12-09 18:11:41.798065	15	0	f
4316	2	210	Cleveland Browns	1	2025-12-14 15:55:26.285758	15	0	f
4317	2	211	Baltimore Ravens	14	2025-12-14 15:55:26.287048	15	14	f
4318	2	212	Kansas City Chiefs	2	2025-12-14 15:55:26.288061	15	0	f
4319	2	213	New England Patriots	5	2025-12-14 15:55:26.289054	15	0	f
4320	2	214	New York Giants	13	2025-12-14 15:55:26.289908	15	0	f
4321	2	215	Las Vegas Raiders	4	2025-12-14 15:55:26.290771	15	0	f
4322	2	216	Jacksonville Jaguars	15	2025-12-14 15:55:26.291595	15	15	f
4323	2	217	Houston Texans	6	2025-12-14 15:55:26.292465	15	6	f
4324	2	218	Denver Broncos	16	2025-12-14 15:55:26.293252	15	16	f
4325	2	219	Detroit Lions	7	2025-12-14 15:55:26.293962	15	0	f
4326	2	220	Carolina Panthers	10	2025-12-14 15:55:26.29471	15	0	f
4327	2	221	Tennessee Titans	8	2025-12-14 15:55:26.295451	15	0	f
4328	2	222	Indianapolis Colts	9	2025-12-14 15:55:26.296185	15	9	f
4329	2	223	Dallas Cowboys	12	2025-12-14 15:55:26.296902	15	0	f
4330	2	224	Pittsburgh Steelers	11	2025-12-14 15:55:26.297901	15	11	f
4331	1	209	Tampa Bay Buccaneers	7	2025-12-09 21:50:26.781626	15	0	f
4332	1	210	Chicago Bears	11	2025-12-09 21:50:26.78338	15	11	f
4333	1	211	Baltimore Ravens	10	2025-12-09 21:50:26.784768	15	10	f
4334	1	212	Kansas City Chiefs	12	2025-12-09 21:50:26.786169	15	0	f
4335	1	213	New England Patriots	13	2025-12-09 21:50:26.787487	15	0	f
4336	1	214	Washington Commanders	6	2025-12-09 21:50:26.788711	15	6	f
4337	1	215	Philadelphia Eagles	8	2025-12-09 21:50:26.789747	15	8	f
4338	1	216	Jacksonville Jaguars	5	2025-12-09 21:50:26.790988	15	5	f
4339	1	217	Houston Texans	9	2025-12-09 21:50:26.792224	15	9	f
4340	1	218	Denver Broncos	16	2025-12-09 21:50:26.793403	15	16	f
4341	1	219	Detroit Lions	15	2025-12-09 21:50:26.794424	15	0	f
4342	1	220	Carolina Panthers	4	2025-12-09 21:50:26.795279	15	0	f
4343	1	221	San Francisco 49ers	3	2025-12-09 21:50:26.796137	15	3	f
4344	1	222	Seattle Seahawks	1	2025-12-09 21:50:26.796925	15	0	f
4345	1	223	Dallas Cowboys	2	2025-12-09 21:50:26.797847	15	0	f
4346	1	224	Pittsburgh Steelers	14	2025-12-09 21:50:26.798506	15	14	f
4347	23	209	Tampa Bay Buccaneers	9	2025-12-09 23:36:35.413633	15	0	f
4348	23	210	Chicago Bears	8	2025-12-09 23:36:35.41572	15	8	f
4349	23	211	Cincinnati Bengals	1	2025-12-09 23:36:35.417202	15	0	f
4350	23	212	Los Angeles Chargers	15	2025-12-09 23:36:35.418556	15	15	f
4351	23	213	Buffalo Bills	13	2025-12-09 23:36:35.419853	15	13	f
4352	23	214	Washington Commanders	11	2025-12-09 23:36:35.421111	15	11	f
4353	23	215	Philadelphia Eagles	10	2025-12-09 23:36:35.422284	15	10	f
4354	23	216	Jacksonville Jaguars	14	2025-12-09 23:36:35.423425	15	14	f
4355	23	217	Houston Texans	7	2025-12-09 23:36:35.424572	15	7	f
4356	23	218	Denver Broncos	16	2025-12-09 23:36:35.425701	15	16	f
4357	23	219	Detroit Lions	12	2025-12-09 23:36:35.426557	15	0	f
4358	23	220	Carolina Panthers	6	2025-12-09 23:36:35.427321	15	0	f
4359	23	221	San Francisco 49ers	5	2025-12-09 23:36:35.428115	15	5	f
4360	23	222	Indianapolis Colts	4	2025-12-09 23:36:35.429114	15	4	f
4361	23	223	Minnesota Vikings	3	2025-12-09 23:36:35.429898	15	3	f
4362	23	224	Miami Dolphins	2	2025-12-09 23:36:35.4307	15	0	f
4363	14	209	Tampa Bay Buccaneers	8	2025-12-11 17:13:08.985218	15	0	f
4364	14	210	Chicago Bears	2	2025-12-14 13:37:54.087438	15	2	f
4365	14	211	Cincinnati Bengals	7	2025-12-14 13:37:54.088639	15	0	f
4366	14	212	Los Angeles Chargers	4	2025-12-14 13:37:54.089552	15	4	f
4367	14	213	New England Patriots	10	2025-12-14 13:37:54.090555	15	0	f
4368	14	214	New York Giants	6	2025-12-14 13:37:54.091471	15	0	f
4369	14	215	Philadelphia Eagles	14	2025-12-14 13:37:54.092354	15	14	f
4370	14	216	Jacksonville Jaguars	13	2025-12-14 13:37:54.093212	15	13	f
4371	14	217	Houston Texans	11	2025-12-14 13:37:54.094076	15	11	f
4372	14	218	Green Bay Packers	9	2025-12-14 13:37:54.095046	15	0	f
4373	14	219	Los Angeles Rams	16	2025-12-14 13:37:54.096213	15	16	f
4374	14	220	Carolina Panthers	15	2025-12-14 13:37:54.097364	15	0	f
4375	14	221	San Francisco 49ers	5	2025-12-14 13:37:54.098484	15	5	f
4376	14	222	Seattle Seahawks	12	2025-12-14 13:37:54.099693	15	0	f
4377	14	223	Dallas Cowboys	3	2025-12-14 13:37:54.100875	15	0	f
4378	14	224	Miami Dolphins	1	2025-12-14 13:37:54.101926	15	0	f
4379	12	210	Chicago Bears	3	2025-12-12 17:18:26.918439	15	3	f
4380	12	215	Philadelphia Eagles	6	2025-12-12 17:18:26.922843	15	6	f
4381	12	216	Jacksonville Jaguars	5	2025-12-12 17:18:26.923822	15	5	f
4382	12	217	Houston Texans	8	2025-12-12 17:18:26.924919	15	8	f
4383	12	221	San Francisco 49ers	1	2025-12-12 17:18:26.928312	15	1	f
4384	12	222	Seattle Seahawks	2	2025-12-12 17:18:26.929094	15	0	f
4385	12	223	Minnesota Vikings	4	2025-12-12 17:18:26.929798	15	4	f
4386	16	209	Atlanta Falcons	6	2025-12-11 03:14:56.015067	15	6	f
4387	16	210	Chicago Bears	9	2025-12-11 03:14:56.018023	15	9	f
4388	16	211	Baltimore Ravens	14	2025-12-11 03:14:56.0194	15	14	f
4389	16	212	Los Angeles Chargers	5	2025-12-11 03:14:56.020633	15	5	f
4390	16	213	New England Patriots	15	2025-12-11 03:14:56.021924	15	0	f
4391	16	214	New York Giants	16	2025-12-11 03:14:56.023268	15	0	f
4392	16	215	Las Vegas Raiders	4	2025-12-11 03:14:56.024549	15	0	f
4393	16	216	New York Jets	3	2025-12-11 03:14:56.025811	15	0	f
4394	16	217	Houston Texans	8	2025-12-11 03:14:56.027613	15	8	f
4395	16	218	Denver Broncos	7	2025-12-11 03:14:56.028844	15	7	f
4396	16	219	Los Angeles Rams	12	2025-12-11 03:14:56.029986	15	12	f
4397	16	220	New Orleans Saints	13	2025-12-11 03:14:56.031119	15	13	f
4398	16	221	Tennessee Titans	1	2025-12-11 03:14:56.032115	15	0	f
4399	16	222	Seattle Seahawks	10	2025-12-11 03:14:56.033156	15	0	f
4400	16	223	Dallas Cowboys	11	2025-12-11 03:14:56.033951	15	0	f
4401	16	224	Miami Dolphins	2	2025-12-11 03:14:56.034672	15	0	f
4402	13	209	Tampa Bay Buccaneers	5	2025-12-11 14:41:49.4666	15	0	f
4403	20	209	Tampa Bay Buccaneers	14	2025-12-11 15:38:18.569856	15	0	f
4404	9	209	Tampa Bay Buccaneers	13	2025-12-11 16:56:40.298114	15	0	f
4405	9	210	Cleveland Browns	14	2025-12-11 16:56:40.299282	15	0	f
4406	9	211	Baltimore Ravens	4	2025-12-11 16:56:40.300169	15	4	f
4407	9	212	Los Angeles Chargers	5	2025-12-11 16:56:40.301048	15	5	f
4408	9	213	Buffalo Bills	6	2025-12-11 16:56:40.301838	15	6	f
4409	9	214	New York Giants	16	2025-12-11 16:56:40.302637	15	0	f
4410	9	215	Philadelphia Eagles	7	2025-12-11 16:56:40.303407	15	7	f
4411	9	216	Jacksonville Jaguars	8	2025-12-11 16:56:40.304168	15	8	f
4412	9	217	Arizona Cardinals	3	2025-12-11 16:56:40.304941	15	0	f
4413	9	218	Denver Broncos	9	2025-12-11 16:56:40.305698	15	9	f
4414	9	219	Detroit Lions	10	2025-12-11 16:56:40.306499	15	0	f
4415	9	220	Carolina Panthers	15	2025-12-11 16:56:40.307318	15	0	f
4416	9	221	San Francisco 49ers	11	2025-12-11 16:56:40.308085	15	11	f
4417	9	222	Seattle Seahawks	12	2025-12-11 16:56:40.308825	15	0	f
4418	9	223	Dallas Cowboys	1	2025-12-11 16:56:40.309598	15	0	f
4419	9	224	Miami Dolphins	2	2025-12-11 16:56:40.310224	15	0	f
4420	5	209	Tampa Bay Buccaneers	16	2025-12-11 18:14:51.196598	15	0	f
4421	5	210	Chicago Bears	6	2025-12-11 18:14:51.197746	15	6	f
4422	5	211	Baltimore Ravens	14	2025-12-11 18:14:51.198648	15	14	f
4423	5	212	Kansas City Chiefs	9	2025-12-11 18:14:51.199444	15	0	f
4424	5	213	Buffalo Bills	12	2025-12-11 18:14:51.200278	15	12	f
4425	5	214	New York Giants	8	2025-12-11 18:14:51.201093	15	0	f
4426	5	215	Philadelphia Eagles	5	2025-12-11 18:14:51.201816	15	5	f
4427	5	216	Jacksonville Jaguars	4	2025-12-11 18:14:51.202557	15	4	f
4428	5	217	Arizona Cardinals	1	2025-12-11 18:14:51.203319	15	0	f
4429	5	218	Denver Broncos	10	2025-12-11 18:14:51.204182	15	10	f
4430	5	219	Detroit Lions	11	2025-12-11 18:14:51.204896	15	0	f
4431	5	220	Carolina Panthers	13	2025-12-11 18:14:51.205617	15	0	f
4432	5	221	San Francisco 49ers	3	2025-12-11 18:14:51.206344	15	3	f
4433	5	222	Indianapolis Colts	2	2025-12-11 18:14:51.207069	15	2	f
4434	5	223	Dallas Cowboys	7	2025-12-11 18:14:51.207767	15	0	f
4435	5	224	Pittsburgh Steelers	15	2025-12-11 18:14:51.208479	15	15	f
4436	19	209	Tampa Bay Buccaneers	16	2025-12-11 22:48:32.26288	15	0	f
4437	8	209	Tampa Bay Buccaneers	10	2025-12-11 22:51:42.350325	15	0	f
4438	8	210	Chicago Bears	13	2025-12-11 22:51:42.351841	15	13	f
4439	8	211	Cincinnati Bengals	9	2025-12-11 22:51:42.352988	15	0	f
4440	8	212	Los Angeles Chargers	11	2025-12-11 22:51:42.354114	15	11	f
4441	8	213	New England Patriots	3	2025-12-11 22:51:42.355185	15	0	f
4442	8	214	New York Giants	4	2025-12-11 22:51:42.356254	15	0	f
4443	8	215	Las Vegas Raiders	7	2025-12-11 22:51:42.357301	15	0	f
4444	8	216	Jacksonville Jaguars	16	2025-12-11 22:51:42.358382	15	16	f
4445	8	217	Houston Texans	14	2025-12-11 22:51:42.359448	15	14	f
4446	8	218	Denver Broncos	1	2025-12-11 22:51:42.360473	15	1	f
4447	8	219	Detroit Lions	2	2025-12-11 22:51:42.361514	15	0	f
4448	8	220	Carolina Panthers	6	2025-12-11 22:51:42.362554	15	0	f
4449	8	221	San Francisco 49ers	15	2025-12-11 22:51:42.363574	15	15	f
4450	8	222	Indianapolis Colts	8	2025-12-11 22:51:42.364589	15	8	f
4451	8	223	Dallas Cowboys	12	2025-12-11 22:51:42.365623	15	0	f
4452	8	224	Pittsburgh Steelers	5	2025-12-11 22:51:42.366459	15	5	f
4453	15	209	Tampa Bay Buccaneers	4	2025-12-11 23:25:11.044113	15	0	f
4454	10	209	Tampa Bay Buccaneers	8	2025-12-11 23:27:47.108209	15	0	f
4455	18	209	Tampa Bay Buccaneers	16	2025-12-12 00:20:18.859735	15	0	f
4456	26	209	Tampa Bay Buccaneers	8	2025-12-12 00:45:50.43672	15	0	f
4457	4	209	Tampa Bay Buccaneers	10	2025-12-12 01:05:32.026778	15	0	f
4458	4	210	Chicago Bears	6	2025-12-12 01:05:32.031817	15	6	f
4459	4	211	Cincinnati Bengals	3	2025-12-12 01:05:32.03328	15	0	f
4460	4	212	Kansas City Chiefs	5	2025-12-12 01:05:32.035927	15	0	f
4461	4	213	Buffalo Bills	11	2025-12-12 01:05:32.037602	15	11	f
4462	4	214	New York Giants	7	2025-12-12 01:05:32.039894	15	0	f
4463	4	215	Las Vegas Raiders	2	2025-12-12 01:05:32.041241	15	0	f
4464	4	216	New York Jets	4	2025-12-12 01:05:32.043602	15	0	f
4465	4	217	Arizona Cardinals	8	2025-12-12 01:05:32.044836	15	0	f
4466	4	218	Denver Broncos	16	2025-12-12 01:05:32.046056	15	16	f
4467	4	219	Detroit Lions	9	2025-12-12 01:05:32.049027	15	0	f
4468	4	220	Carolina Panthers	12	2025-12-12 01:05:32.050483	15	0	f
4469	4	221	San Francisco 49ers	13	2025-12-12 01:05:32.051856	15	13	f
4470	4	222	Indianapolis Colts	14	2025-12-12 01:05:32.053405	15	14	f
4471	4	223	Dallas Cowboys	1	2025-12-12 01:05:32.054862	15	0	f
4472	4	224	Pittsburgh Steelers	15	2025-12-12 01:05:32.055792	15	15	f
4473	17	209	Tampa Bay Buccaneers	16	2025-12-12 01:10:48.977905	15	0	f
4474	18	210	Cleveland Browns	8	2025-12-14 12:58:35.941719	15	0	f
4475	18	211	Baltimore Ravens	15	2025-12-14 12:58:35.943206	15	15	f
4476	18	212	Kansas City Chiefs	9	2025-12-14 12:58:35.94432	15	0	f
4477	18	213	Buffalo Bills	10	2025-12-14 12:58:35.945347	15	10	f
4478	18	214	New York Giants	7	2025-12-14 12:58:35.946354	15	0	f
4479	18	215	Philadelphia Eagles	11	2025-12-14 12:58:35.947334	15	11	f
4480	18	216	Jacksonville Jaguars	12	2025-12-14 12:58:35.948296	15	12	f
4481	18	217	Houston Texans	5	2025-12-14 12:58:35.949241	15	5	f
4482	18	218	Green Bay Packers	13	2025-12-14 12:58:35.950198	15	0	f
4483	18	219	Detroit Lions	1	2025-12-14 12:58:35.951145	15	0	f
4484	18	220	Carolina Panthers	2	2025-12-14 12:58:35.952129	15	0	f
4485	18	221	Tennessee Titans	3	2025-12-14 12:58:35.953073	15	0	f
4486	18	222	Indianapolis Colts	4	2025-12-14 12:58:35.95399	15	4	f
4487	18	223	Minnesota Vikings	6	2025-12-14 12:58:35.955044	15	6	f
4488	18	224	Pittsburgh Steelers	14	2025-12-14 12:58:35.956119	15	14	f
4489	15	210	Chicago Bears	13	2025-12-14 15:34:40.973241	15	13	f
4490	15	211	Cincinnati Bengals	14	2025-12-14 15:34:40.974461	15	0	f
4491	15	212	Los Angeles Chargers	12	2025-12-14 15:34:40.975345	15	12	f
4492	15	213	Buffalo Bills	15	2025-12-14 15:34:40.976196	15	15	f
4493	15	214	New York Giants	10	2025-12-14 15:34:40.976968	15	0	f
4494	15	215	Las Vegas Raiders	1	2025-12-14 15:34:40.977765	15	0	f
4495	15	216	New York Jets	5	2025-12-14 15:34:40.978574	15	0	f
4496	15	217	Houston Texans	11	2025-12-14 15:34:40.979353	15	11	f
4497	15	218	Denver Broncos	16	2025-12-14 15:34:40.980148	15	16	f
4498	15	219	Detroit Lions	8	2025-12-14 15:34:40.9809	15	0	f
4499	15	220	Carolina Panthers	7	2025-12-14 15:34:40.981722	15	0	f
4500	15	221	Tennessee Titans	6	2025-12-14 15:34:40.982524	15	0	f
4501	15	222	Indianapolis Colts	2	2025-12-14 15:34:40.983343	15	2	f
4502	15	223	Minnesota Vikings	3	2025-12-15 01:05:51.813077	15	3	f
4503	15	224	Pittsburgh Steelers	9	2025-12-15 01:05:51.814472	15	9	f
4504	17	210	Cleveland Browns	10	2025-12-14 16:44:42.145268	15	0	f
4505	17	211	Baltimore Ravens	3	2025-12-14 16:44:42.146614	15	3	f
4506	17	212	Los Angeles Chargers	4	2025-12-14 16:44:42.14764	15	4	f
4507	17	213	Buffalo Bills	2	2025-12-14 16:44:42.148614	15	2	f
4508	17	214	New York Giants	5	2025-12-14 16:44:42.149573	15	0	f
4509	17	215	Las Vegas Raiders	9	2025-12-14 16:44:42.150536	15	0	f
4510	17	216	Jacksonville Jaguars	7	2025-12-14 16:44:42.151479	15	7	f
4511	17	217	Houston Texans	12	2025-12-14 16:44:42.152441	15	12	f
4512	17	218	Denver Broncos	1	2025-12-14 16:44:42.153397	15	1	f
4513	17	219	Detroit Lions	6	2025-12-14 16:44:42.154336	15	0	f
4514	17	220	Carolina Panthers	14	2025-12-14 16:44:42.155299	15	0	f
4515	17	221	San Francisco 49ers	11	2025-12-14 16:44:42.156234	15	11	f
4516	17	222	Seattle Seahawks	15	2025-12-14 16:44:42.157163	15	0	f
4517	17	223	Minnesota Vikings	8	2025-12-14 16:44:42.158087	15	8	f
4518	17	224	Pittsburgh Steelers	13	2025-12-14 16:44:42.159023	15	13	f
4519	10	210	Cleveland Browns	11	2025-12-14 16:36:45.578759	15	0	f
4520	10	211	Cincinnati Bengals	6	2025-12-14 16:36:45.579922	15	0	f
4521	10	212	Los Angeles Chargers	13	2025-12-14 16:36:45.580764	15	13	f
4522	10	213	Buffalo Bills	12	2025-12-14 16:36:45.581585	15	12	f
4523	10	214	New York Giants	7	2025-12-14 16:36:45.582355	15	0	f
4524	10	215	Las Vegas Raiders	2	2025-12-14 16:36:45.583118	15	0	f
4525	10	216	Jacksonville Jaguars	5	2025-12-14 16:36:45.583829	15	5	f
4526	10	217	Houston Texans	3	2025-12-14 16:36:45.584587	15	3	f
4527	10	218	Denver Broncos	16	2025-12-14 16:36:45.585328	15	16	f
4528	10	219	Detroit Lions	14	2025-12-14 16:36:45.586063	15	0	f
4529	10	220	Carolina Panthers	10	2025-12-14 16:36:45.586778	15	0	f
4530	10	221	San Francisco 49ers	1	2025-12-14 16:36:45.587506	15	1	f
4531	10	222	Indianapolis Colts	4	2025-12-14 16:36:45.588278	15	4	f
4532	10	223	Minnesota Vikings	9	2025-12-14 16:36:45.589102	15	9	f
4533	10	224	Pittsburgh Steelers	15	2025-12-14 16:36:45.589835	15	15	f
4534	26	210	Chicago Bears	5	2025-12-14 16:52:04.381346	15	5	f
4535	26	211	Baltimore Ravens	1	2025-12-14 16:52:04.382554	15	1	f
4536	26	212	Kansas City Chiefs	2	2025-12-14 16:52:04.3835	15	0	f
4537	26	213	New England Patriots	11	2025-12-14 16:52:04.384368	15	0	f
4538	26	214	New York Giants	12	2025-12-14 16:52:04.385179	15	0	f
4539	26	215	Philadelphia Eagles	3	2025-12-14 16:52:04.385976	15	3	f
4540	26	216	Jacksonville Jaguars	4	2025-12-14 16:52:04.386888	15	4	f
4541	26	217	Houston Texans	13	2025-12-14 16:52:04.387728	15	13	f
4542	26	218	Green Bay Packers	14	2025-12-14 16:52:04.388503	15	0	f
4543	26	219	Detroit Lions	10	2025-12-14 16:52:04.389261	15	0	f
4544	26	220	Carolina Panthers	6	2025-12-14 16:52:04.389999	15	0	f
4545	26	221	San Francisco 49ers	15	2025-12-14 16:52:04.390791	15	15	f
4546	26	222	Seattle Seahawks	9	2025-12-14 16:52:04.39159	15	0	f
4547	26	223	Dallas Cowboys	16	2025-12-14 16:52:04.392343	15	0	f
4548	26	224	Pittsburgh Steelers	7	2025-12-14 16:52:04.392932	15	7	f
4549	19	210	Chicago Bears	12	2025-12-14 16:52:08.228939	15	12	f
4550	19	211	Baltimore Ravens	1	2025-12-14 16:52:08.230571	15	1	f
4551	19	212	Los Angeles Chargers	5	2025-12-14 16:52:08.231797	15	5	f
4552	19	213	Buffalo Bills	6	2025-12-14 16:52:08.232893	15	6	f
4553	19	214	New York Giants	13	2025-12-14 16:52:08.23372	15	0	f
4554	19	215	Philadelphia Eagles	4	2025-12-14 16:52:08.234545	15	4	f
4555	19	216	Jacksonville Jaguars	11	2025-12-14 16:52:08.235443	15	11	f
4556	19	217	Houston Texans	15	2025-12-14 16:52:08.236254	15	15	f
4557	19	218	Denver Broncos	3	2025-12-14 16:52:08.237038	15	3	f
4558	19	219	Detroit Lions	14	2025-12-14 16:52:08.238246	15	0	f
4559	19	220	Carolina Panthers	2	2025-12-14 16:52:08.239396	15	0	f
4560	19	221	Tennessee Titans	10	2025-12-14 16:52:08.240641	15	0	f
4561	19	222	Seattle Seahawks	7	2025-12-14 16:52:08.24183	15	0	f
4562	19	223	Dallas Cowboys	8	2025-12-14 16:52:08.243092	15	0	f
4563	19	224	Pittsburgh Steelers	9	2025-12-14 16:52:08.2441	15	9	f
4564	13	210	Cleveland Browns	1	2025-12-14 17:04:26.183794	15	0	f
4565	13	211	Cincinnati Bengals	2	2025-12-14 17:04:26.185488	15	0	f
4566	13	212	Los Angeles Chargers	3	2025-12-14 17:04:26.186801	15	3	f
4567	13	213	Buffalo Bills	4	2025-12-14 17:04:26.187966	15	4	f
4568	13	214	New York Giants	15	2025-12-14 17:04:26.189047	15	0	f
4569	13	215	Las Vegas Raiders	6	2025-12-14 17:04:26.190152	15	0	f
4570	13	216	Jacksonville Jaguars	7	2025-12-14 17:04:26.191132	15	7	f
4571	13	217	Houston Texans	8	2025-12-14 17:04:26.19216	15	8	f
4572	13	218	Denver Broncos	16	2025-12-14 17:04:26.193241	15	16	f
4573	13	219	Detroit Lions	9	2025-12-14 17:04:26.194225	15	0	f
4574	13	220	Carolina Panthers	10	2025-12-14 17:04:26.195344	15	0	f
4575	13	221	San Francisco 49ers	11	2025-12-14 17:04:26.1964	15	11	f
4576	13	222	Seattle Seahawks	12	2025-12-14 17:04:26.197761	15	0	f
4577	13	223	Dallas Cowboys	13	2025-12-14 17:04:26.198888	15	0	f
4578	13	224	Miami Dolphins	14	2025-12-14 17:04:26.199728	15	0	f
4579	20	218	Green Bay Packers	6	2025-12-14 21:02:52.647232	15	0	f
4580	20	219	Detroit Lions	7	2025-12-14 21:02:52.648722	15	0	f
4581	20	220	Carolina Panthers	5	2025-12-14 21:02:52.649993	15	0	f
4582	20	221	San Francisco 49ers	1	2025-12-14 21:02:52.651289	15	1	f
4583	20	222	Seattle Seahawks	2	2025-12-14 21:02:52.652849	15	0	f
4584	20	223	Dallas Cowboys	4	2025-12-14 21:02:52.653945	15	0	f
4585	20	224	Pittsburgh Steelers	3	2025-12-14 21:02:52.654836	15	3	f
4586	14	225	Los Angeles Rams	16	2025-12-18 13:48:37.364893	16	16	f
4587	14	226	Chicago Bears	13	2025-12-20 18:20:05.263987	16	13	f
4588	14	227	Philadelphia Eagles	10	2025-12-20 18:20:05.26608	16	10	f
4589	14	228	Buffalo Bills	11	2025-12-20 18:20:05.267586	16	0	f
4590	14	229	Los Angeles Chargers	12	2025-12-20 18:20:05.269	16	12	f
4591	14	230	Kansas City Chiefs	6	2025-12-20 18:20:05.270403	16	0	f
4592	14	231	New Orleans Saints	15	2025-12-20 18:20:05.271649	16	15	f
4593	14	232	New York Giants	3	2025-12-20 18:20:05.272633	16	3	f
4594	14	233	Tampa Bay Buccaneers	7	2025-12-20 18:20:05.273578	16	0	f
4595	14	234	New England Patriots	5	2025-12-20 18:20:05.274593	16	5	f
4596	14	235	Denver Broncos	14	2025-12-20 18:20:05.275765	16	0	f
4597	14	236	Arizona Cardinals	2	2025-12-20 18:20:05.276925	16	0	f
4598	14	237	Detroit Lions	9	2025-12-20 18:20:05.278149	16	0	f
4599	14	238	Houston Texans	4	2025-12-20 18:20:05.279344	16	0	f
4600	14	239	Cincinnati Bengals	8	2025-12-20 18:20:05.280512	16	8	f
4601	14	240	San Francisco 49ers	1	2025-12-20 18:20:05.28172	16	1	f
4602	12	226	Green Bay Packers	12	2025-12-17 20:56:09.28877	16	0	f
4603	12	229	Los Angeles Chargers	14	2025-12-17 20:56:09.292733	16	14	f
4604	12	232	Minnesota Vikings	4	2025-12-17 20:56:09.29603	16	0	f
4605	12	239	Cincinnati Bengals	13	2025-12-17 20:56:09.303317	16	13	f
4606	12	240	San Francisco 49ers	8	2025-12-17 20:56:09.30429	16	8	f
4607	1	225	Los Angeles Rams	5	2025-12-16 22:03:33.250815	16	5	f
4608	1	226	Green Bay Packers	6	2025-12-16 22:03:33.252342	16	0	f
4609	1	227	Philadelphia Eagles	12	2025-12-16 22:03:33.253535	16	12	f
4610	1	228	Buffalo Bills	13	2025-12-16 22:03:33.254675	16	0	f
4611	1	229	Los Angeles Chargers	11	2025-12-16 22:03:33.255766	16	11	f
4612	1	230	Tennessee Titans	10	2025-12-16 22:03:33.256819	16	10	f
4613	1	231	New Orleans Saints	9	2025-12-16 22:03:33.257987	16	9	f
4614	1	232	Minnesota Vikings	8	2025-12-16 22:03:33.259105	16	0	f
4615	1	233	Tampa Bay Buccaneers	7	2025-12-16 22:03:33.260132	16	0	f
4616	1	234	New England Patriots	4	2025-12-16 22:03:33.261154	16	4	f
4617	1	235	Denver Broncos	16	2025-12-16 22:03:33.262258	16	0	f
4618	1	236	Atlanta Falcons	3	2025-12-16 22:03:33.263284	16	3	f
4619	1	237	Detroit Lions	14	2025-12-16 22:03:33.264309	16	0	f
4620	1	238	Houston Texans	2	2025-12-16 22:03:33.265326	16	0	f
4621	1	239	Cincinnati Bengals	1	2025-12-16 22:03:33.26637	16	1	f
4622	1	240	San Francisco 49ers	15	2025-12-16 22:03:33.267234	16	15	f
4623	4	225	Los Angeles Rams	10	2025-12-17 01:42:26.485736	16	10	f
4624	4	226	Chicago Bears	5	2025-12-17 01:42:26.487174	16	5	f
4625	4	227	Philadelphia Eagles	6	2025-12-17 01:42:26.488534	16	6	f
4626	4	228	Buffalo Bills	9	2025-12-17 01:42:26.48978	16	0	f
4627	4	229	Dallas Cowboys	2	2025-12-17 01:42:26.490677	16	0	f
4628	4	230	Kansas City Chiefs	4	2025-12-17 01:42:26.49171	16	0	f
4629	4	231	New Orleans Saints	7	2025-12-17 01:42:26.492789	16	7	f
4630	4	232	New York Giants	1	2025-12-17 01:42:26.493909	16	1	f
4631	4	233	Tampa Bay Buccaneers	8	2025-12-17 01:42:26.495153	16	0	f
4632	4	234	Baltimore Ravens	11	2025-12-17 01:42:26.496375	16	0	f
4633	4	235	Denver Broncos	16	2025-12-17 01:42:26.497597	16	0	f
4634	4	236	Arizona Cardinals	3	2025-12-17 01:42:26.498804	16	0	f
4635	4	237	Pittsburgh Steelers	12	2025-12-17 01:42:26.500078	16	12	f
4636	4	238	Houston Texans	13	2025-12-17 01:42:26.501306	16	0	f
4637	4	239	Cincinnati Bengals	14	2025-12-17 01:42:26.502473	16	14	f
4638	4	240	Indianapolis Colts	15	2025-12-17 01:42:26.503317	16	0	f
4639	12	225	Los Angeles Rams	10	2025-12-17 20:56:09.285999	16	10	f
4640	12	227	Philadelphia Eagles	11	2025-12-17 20:56:09.290707	16	11	f
4641	12	228	Buffalo Bills	1	2025-12-17 20:56:09.291984	16	0	f
4642	12	230	Kansas City Chiefs	6	2025-12-17 20:56:09.294273	16	0	f
4643	12	231	New Orleans Saints	5	2025-12-17 20:56:09.295359	16	5	f
4644	12	233	Tampa Bay Buccaneers	9	2025-12-17 20:56:09.297455	16	0	f
4645	12	234	New England Patriots	15	2025-12-17 20:56:09.298535	16	15	f
4646	12	235	Denver Broncos	16	2025-12-17 20:56:09.29958	16	0	f
4647	12	236	Atlanta Falcons	7	2025-12-17 20:56:09.300632	16	7	f
4648	12	237	Pittsburgh Steelers	3	2025-12-17 20:56:09.301653	16	3	f
4649	12	238	Houston Texans	2	2025-12-17 20:56:09.302663	16	0	f
4650	13	225	Los Angeles Rams	10	2025-12-18 03:57:56.021119	16	10	f
4651	5	225	Los Angeles Rams	8	2025-12-18 16:49:06.702559	16	8	f
4652	5	226	Chicago Bears	12	2025-12-18 16:49:06.704062	16	12	f
4653	5	227	Philadelphia Eagles	5	2025-12-18 16:49:06.705371	16	5	f
4654	5	228	Buffalo Bills	4	2025-12-18 16:49:06.706665	16	0	f
4655	5	229	Dallas Cowboys	2	2025-12-18 16:49:06.707728	16	0	f
4656	5	230	Kansas City Chiefs	6	2025-12-18 16:49:06.708651	16	0	f
4657	5	231	New Orleans Saints	16	2025-12-18 16:49:06.709606	16	16	f
4658	5	232	Minnesota Vikings	7	2025-12-18 16:49:06.710478	16	0	f
4659	5	233	Tampa Bay Buccaneers	3	2025-12-18 16:49:06.71144	16	0	f
4660	5	234	New England Patriots	15	2025-12-18 16:49:06.712286	16	15	f
4661	5	235	Denver Broncos	10	2025-12-18 16:49:06.713094	16	0	f
4662	5	236	Arizona Cardinals	1	2025-12-18 16:49:06.713872	16	0	f
4663	5	237	Detroit Lions	13	2025-12-18 16:49:06.715141	16	0	f
4664	5	238	Las Vegas Raiders	9	2025-12-18 16:49:06.716631	16	9	f
4665	5	239	Cincinnati Bengals	11	2025-12-18 16:49:06.717751	16	11	f
4666	5	240	Indianapolis Colts	14	2025-12-18 16:49:06.718622	16	0	f
4667	20	225	Los Angeles Rams	1	2025-12-18 16:54:21.132906	16	1	f
4668	20	226	Chicago Bears	16	2025-12-18 16:54:21.133964	16	16	f
4669	20	227	Philadelphia Eagles	15	2025-12-18 16:54:21.134772	16	15	f
4670	20	228	Buffalo Bills	2	2025-12-21 15:31:16.295822	16	0	f
4671	20	229	Dallas Cowboys	11	2025-12-21 15:31:16.297131	16	0	f
4672	20	230	Kansas City Chiefs	3	2025-12-21 15:31:16.298115	16	0	f
4673	20	231	New Orleans Saints	4	2025-12-21 15:31:16.298942	16	4	f
4674	20	232	Minnesota Vikings	12	2025-12-21 15:31:16.299773	16	0	f
4675	20	233	Carolina Panthers	6	2025-12-21 15:31:16.300593	16	6	f
4676	20	234	New England Patriots	14	2025-12-21 15:31:16.301448	16	14	f
4677	20	235	Jacksonville Jaguars	7	2025-12-21 15:31:16.302266	16	7	f
4678	20	236	Atlanta Falcons	8	2025-12-21 15:31:16.303061	16	8	f
4679	20	237	Pittsburgh Steelers	9	2025-12-21 15:31:16.303843	16	9	f
4680	20	238	Las Vegas Raiders	10	2025-12-21 15:31:16.304627	16	10	f
4681	20	239	Miami Dolphins	5	2025-12-21 15:31:16.305436	16	0	f
4682	20	240	San Francisco 49ers	13	2025-12-21 15:31:16.306377	16	13	f
4683	2	225	Seattle Seahawks	5	2025-12-18 17:35:10.057228	16	0	f
4684	2	226	Chicago Bears	1	2025-12-18 17:35:10.0587	16	1	f
4685	2	227	Philadelphia Eagles	2	2025-12-18 17:35:10.059798	16	2	f
4686	2	228	Buffalo Bills	6	2025-12-18 17:35:10.060824	16	0	f
4687	2	229	Dallas Cowboys	7	2025-12-18 17:35:10.061791	16	0	f
4688	2	230	Tennessee Titans	4	2025-12-18 17:35:10.062673	16	4	f
4689	2	231	New Orleans Saints	9	2025-12-18 17:35:10.063561	16	9	f
4690	2	232	Minnesota Vikings	12	2025-12-18 17:35:10.064434	16	0	f
4691	2	233	Tampa Bay Buccaneers	8	2025-12-18 17:35:10.065566	16	0	f
4692	2	234	New England Patriots	3	2025-12-18 17:35:10.066755	16	3	f
4693	2	235	Denver Broncos	16	2025-12-18 17:35:10.06783	16	0	f
4694	2	236	Atlanta Falcons	10	2025-12-18 17:35:10.068832	16	10	f
4695	2	237	Pittsburgh Steelers	11	2025-12-18 17:35:10.07009	16	11	f
4696	2	238	Houston Texans	14	2025-12-18 17:35:10.071264	16	0	f
4697	2	239	Miami Dolphins	15	2025-12-18 17:35:10.072437	16	0	f
4698	2	240	San Francisco 49ers	13	2025-12-18 17:35:10.073357	16	13	f
4699	16	225	Seattle Seahawks	16	2025-12-18 21:24:58.998333	16	0	f
4700	16	226	Chicago Bears	2	2025-12-18 21:24:58.999909	16	2	f
4701	16	227	Washington Commanders	4	2025-12-18 21:24:59.001197	16	0	f
4702	16	228	Buffalo Bills	6	2025-12-18 21:24:59.002375	16	0	f
4703	16	229	Los Angeles Chargers	1	2025-12-18 21:24:59.00349	16	1	f
4704	16	230	Tennessee Titans	3	2025-12-18 21:24:59.004569	16	3	f
4705	16	231	New Orleans Saints	9	2025-12-18 21:24:59.005633	16	9	f
4706	16	232	Minnesota Vikings	12	2025-12-18 21:24:59.00666	16	0	f
4707	16	233	Tampa Bay Buccaneers	13	2025-12-18 21:24:59.007685	16	0	f
4708	16	234	Baltimore Ravens	10	2025-12-18 21:24:59.0087	16	0	f
4709	16	235	Denver Broncos	11	2025-12-18 21:24:59.009735	16	0	f
4710	16	236	Atlanta Falcons	14	2025-12-18 21:24:59.010747	16	14	f
4711	16	237	Pittsburgh Steelers	5	2025-12-18 21:24:59.011761	16	5	f
4712	16	238	Houston Texans	7	2025-12-18 21:24:59.012778	16	0	f
4713	16	239	Cincinnati Bengals	15	2025-12-18 21:24:59.013811	16	15	f
4714	16	240	San Francisco 49ers	8	2025-12-18 21:24:59.01464	16	8	f
4715	9	225	Los Angeles Rams	11	2025-12-18 21:32:21.757632	16	11	f
4716	9	226	Chicago Bears	6	2025-12-18 21:32:21.759386	16	6	f
4717	9	227	Philadelphia Eagles	12	2025-12-18 21:32:21.760973	16	12	f
4718	9	228	Buffalo Bills	13	2025-12-18 21:32:21.762317	16	0	f
4719	9	229	Los Angeles Chargers	10	2025-12-18 21:32:21.763605	16	10	f
4720	9	230	Tennessee Titans	3	2025-12-18 21:32:21.764785	16	3	f
4721	9	231	New Orleans Saints	14	2025-12-18 21:32:21.76594	16	14	f
4722	9	232	Minnesota Vikings	8	2025-12-18 21:32:21.767056	16	0	f
4723	9	233	Tampa Bay Buccaneers	7	2025-12-18 21:32:21.768124	16	0	f
4724	9	234	Baltimore Ravens	9	2025-12-18 21:32:21.769177	16	0	f
4725	9	235	Denver Broncos	15	2025-12-18 21:32:21.770213	16	0	f
4726	9	236	Arizona Cardinals	1	2025-12-18 21:32:21.771247	16	0	f
4727	9	237	Detroit Lions	5	2025-12-18 21:32:21.772245	16	0	f
4728	9	240	San Francisco 49ers	16	2025-12-18 21:32:21.775502	16	16	f
4729	9	238	Houston Texans	4	2025-12-18 21:32:21.773709	16	0	f
4730	9	239	Cincinnati Bengals	2	2025-12-18 21:32:21.774811	16	2	f
4731	8	225	Seattle Seahawks	9	2025-12-18 22:16:15.958439	16	0	f
4732	10	225	Seattle Seahawks	8	2025-12-19 00:08:28.886591	16	0	f
4733	17	225	Los Angeles Rams	1	2025-12-19 00:10:05.751835	16	1	f
4734	15	226	Chicago Bears	8	2025-12-20 18:24:54.444685	16	8	f
4735	15	227	Washington Commanders	4	2025-12-20 18:24:54.446116	16	0	f
4736	22	226	Chicago Bears	5	2025-12-19 04:05:13.269921	16	5	f
4737	22	227	Philadelphia Eagles	12	2025-12-19 04:05:13.271452	16	12	f
4738	22	228	Buffalo Bills	10	2025-12-19 04:05:13.27257	16	0	f
4739	22	229	Dallas Cowboys	8	2025-12-19 04:05:13.273568	16	0	f
4740	22	230	Kansas City Chiefs	3	2025-12-19 04:05:13.274472	16	0	f
4741	22	231	New Orleans Saints	9	2025-12-19 04:05:13.27531	16	9	f
4742	22	232	New York Giants	4	2025-12-19 04:05:13.27612	16	4	f
4743	22	233	Carolina Panthers	6	2025-12-19 04:05:13.276893	16	6	f
4744	22	234	Baltimore Ravens	2	2025-12-19 04:05:13.277734	16	0	f
4745	22	235	Denver Broncos	11	2025-12-19 04:05:13.278509	16	0	f
4746	22	236	Atlanta Falcons	13	2025-12-19 04:05:13.279278	16	13	f
4747	22	237	Detroit Lions	7	2025-12-19 04:05:13.280194	16	0	f
4748	22	238	Houston Texans	1	2025-12-19 04:05:13.280949	16	0	f
4749	22	239	Cincinnati Bengals	14	2025-12-19 04:05:13.281738	16	14	f
4750	22	240	San Francisco 49ers	15	2025-12-19 04:05:13.282367	16	15	f
4751	8	226	Green Bay Packers	4	2025-12-19 04:44:34.875576	16	0	f
4752	8	227	Philadelphia Eagles	15	2025-12-19 04:44:34.87734	16	15	f
4753	8	228	Buffalo Bills	10	2025-12-19 04:44:34.878846	16	0	f
4754	8	229	Los Angeles Chargers	14	2025-12-19 04:44:34.880263	16	14	f
4755	8	230	Kansas City Chiefs	8	2025-12-19 04:44:34.8816	16	0	f
4756	8	231	New Orleans Saints	11	2025-12-19 04:44:34.882887	16	11	f
4757	8	232	New York Giants	5	2025-12-19 04:44:34.884135	16	5	f
4758	8	233	Carolina Panthers	7	2025-12-19 04:44:34.885344	16	7	f
4759	8	234	New England Patriots	16	2025-12-19 04:44:34.886623	16	16	f
4760	8	235	Jacksonville Jaguars	3	2025-12-19 04:44:34.887872	16	3	f
4761	8	236	Arizona Cardinals	1	2025-12-19 04:44:34.889026	16	0	f
4762	8	237	Pittsburgh Steelers	6	2025-12-19 04:44:34.89009	16	6	f
4763	8	238	Houston Texans	13	2025-12-19 04:44:34.891181	16	0	f
4764	8	239	Cincinnati Bengals	12	2025-12-19 04:44:34.892328	16	12	f
4765	8	240	Indianapolis Colts	2	2025-12-19 04:44:34.893451	16	0	f
4766	18	225	Seattle Seahawks	12	2025-12-19 17:56:52.910668	16	0	f
4767	18	226	Chicago Bears	15	2025-12-19 18:17:48.473122	16	15	f
4768	18	227	Philadelphia Eagles	16	2025-12-19 18:17:48.475326	16	16	f
4769	13	226	Chicago Bears	15	2025-12-20 18:26:58.392409	16	15	f
4770	13	227	Washington Commanders	5	2025-12-20 18:26:58.394182	16	0	f
4771	13	228	Cleveland Browns	2	2025-12-21 14:59:05.271483	16	2	f
4772	13	229	Los Angeles Chargers	6	2025-12-21 14:59:05.272693	16	6	f
4773	13	230	Tennessee Titans	7	2025-12-21 14:59:05.273668	16	7	f
4774	13	231	New York Jets	1	2025-12-21 14:59:05.274563	16	0	f
4775	13	232	New York Giants	11	2025-12-21 14:59:05.275435	16	11	f
4776	19	226	Chicago Bears	15	2025-12-20 19:23:39.760031	16	15	f
4777	19	227	Philadelphia Eagles	14	2025-12-20 19:23:39.761316	16	14	f
4778	17	226	Chicago Bears	2	2025-12-20 19:22:19.613349	16	2	f
4779	17	227	Philadelphia Eagles	3	2025-12-20 19:22:19.614921	16	3	f
4780	19	228	Cleveland Browns	13	2025-12-21 17:02:56.610825	16	13	f
4781	19	229	Dallas Cowboys	10	2025-12-21 17:02:56.612492	16	0	f
4782	19	230	Tennessee Titans	7	2025-12-21 17:02:56.613803	16	7	f
4783	19	231	New Orleans Saints	2	2025-12-21 17:02:56.615109	16	2	f
4784	19	232	New York Giants	9	2025-12-21 17:02:56.616328	16	9	f
4785	19	233	Tampa Bay Buccaneers	8	2025-12-21 17:02:56.617554	16	0	f
4786	19	234	New England Patriots	3	2025-12-21 17:02:56.61877	16	3	f
4787	19	235	Denver Broncos	12	2025-12-21 17:02:56.619963	16	0	f
4788	19	236	Atlanta Falcons	4	2025-12-21 17:02:56.62121	16	4	f
4789	19	237	Detroit Lions	1	2025-12-21 17:02:56.62296	16	0	f
4790	19	238	Las Vegas Raiders	11	2025-12-21 17:02:56.624156	16	11	f
4791	19	239	Cincinnati Bengals	5	2025-12-21 17:02:56.625321	16	5	f
4792	19	240	Indianapolis Colts	6	2025-12-21 17:02:56.626501	16	0	f
4793	10	226	Chicago Bears	11	2025-12-20 20:21:47.215262	16	11	f
4794	10	227	Washington Commanders	10	2025-12-20 20:21:47.21643	16	0	f
4795	23	228	Buffalo Bills	11	2025-12-21 03:05:18.327531	16	0	f
4796	23	229	Los Angeles Chargers	12	2025-12-21 03:05:18.329077	16	12	f
4797	23	230	Tennessee Titans	6	2025-12-21 03:05:18.330285	16	6	f
4798	23	231	New Orleans Saints	5	2025-12-21 03:05:18.331467	16	5	f
4799	23	232	Minnesota Vikings	8	2025-12-21 03:05:18.332723	16	0	f
4800	23	233	Tampa Bay Buccaneers	4	2025-12-21 03:05:18.333972	16	0	f
4801	23	234	New England Patriots	10	2025-12-21 03:05:18.335217	16	10	f
4802	23	235	Denver Broncos	13	2025-12-21 03:05:18.336396	16	0	f
4803	23	236	Atlanta Falcons	2	2025-12-21 03:05:18.337583	16	2	f
4804	23	237	Detroit Lions	7	2025-12-21 03:05:18.338765	16	0	f
4805	23	238	Houston Texans	1	2025-12-21 03:05:18.339934	16	0	f
4806	23	239	Miami Dolphins	9	2025-12-21 03:05:18.341136	16	0	f
4807	23	240	Indianapolis Colts	3	2025-12-21 03:05:18.342299	16	0	f
4808	13	233	Tampa Bay Buccaneers	3	2025-12-21 14:59:05.2763	16	0	f
4809	13	234	Baltimore Ravens	4	2025-12-21 14:59:05.27722	16	0	f
4810	13	235	Denver Broncos	16	2025-12-21 14:59:05.27814	16	0	f
4811	13	236	Arizona Cardinals	8	2025-12-21 14:59:05.27895	16	0	f
4812	13	237	Pittsburgh Steelers	9	2025-12-21 14:59:05.27981	16	9	f
4813	13	238	Houston Texans	14	2025-12-21 14:59:05.280705	16	0	f
4814	13	239	Cincinnati Bengals	12	2025-12-21 14:59:05.281595	16	12	f
4815	13	240	San Francisco 49ers	13	2025-12-21 14:59:05.282416	16	13	f
4816	15	228	Cleveland Browns	1	2025-12-21 15:14:57.982269	16	1	f
4817	15	229	Los Angeles Chargers	14	2025-12-21 15:14:57.983454	16	14	f
4818	15	230	Tennessee Titans	2	2025-12-21 15:14:57.984582	16	2	f
4819	15	231	New Orleans Saints	13	2025-12-21 15:14:57.985989	16	13	f
4820	15	232	Minnesota Vikings	12	2025-12-21 15:14:57.986891	16	0	f
4821	15	233	Carolina Panthers	6	2025-12-21 15:14:57.98806	16	6	f
4822	15	234	New England Patriots	7	2025-12-21 15:14:57.989086	16	7	f
4823	15	235	Denver Broncos	15	2025-12-21 15:14:57.989931	16	0	f
4824	15	236	Arizona Cardinals	5	2025-12-21 15:14:57.990779	16	0	f
4825	15	237	Detroit Lions	11	2025-12-21 15:14:57.991594	16	0	f
4826	15	238	Houston Texans	3	2025-12-21 15:14:57.992495	16	0	f
4827	15	239	Cincinnati Bengals	10	2025-12-21 15:14:57.993598	16	10	f
4828	15	240	San Francisco 49ers	9	2025-12-21 15:14:57.99426	16	9	f
4829	26	228	Buffalo Bills	5	2025-12-21 16:03:54.082527	16	0	f
4830	26	229	Dallas Cowboys	8	2025-12-21 16:03:54.083692	16	0	f
4831	26	230	Kansas City Chiefs	1	2025-12-21 16:03:54.084618	16	0	f
4832	26	231	New Orleans Saints	3	2025-12-21 16:03:54.085446	16	3	f
4833	26	232	Minnesota Vikings	9	2025-12-21 16:03:54.086233	16	0	f
4834	26	233	Tampa Bay Buccaneers	6	2025-12-21 16:03:54.086982	16	0	f
4835	26	234	New England Patriots	7	2025-12-21 16:03:54.087746	16	7	f
4836	26	235	Denver Broncos	2	2025-12-21 16:03:54.088501	16	0	f
4837	26	236	Atlanta Falcons	10	2025-12-21 16:03:54.089288	16	10	f
4838	26	237	Detroit Lions	13	2025-12-21 16:03:54.090173	16	0	f
4839	26	238	Houston Texans	12	2025-12-21 16:03:54.091028	16	0	f
4840	26	239	Cincinnati Bengals	11	2025-12-21 16:03:54.091854	16	11	f
4841	26	240	Indianapolis Colts	4	2025-12-21 16:03:54.092696	16	0	f
4842	10	228	Buffalo Bills	5	2025-12-21 17:22:40.116469	16	0	f
4843	10	229	Los Angeles Chargers	15	2025-12-21 17:22:40.117724	16	15	f
4844	10	230	Kansas City Chiefs	12	2025-12-21 17:22:40.118679	16	0	f
4845	10	231	New Orleans Saints	9	2025-12-21 17:22:40.119548	16	9	f
4846	10	232	Minnesota Vikings	3	2025-12-21 17:22:40.120363	16	0	f
4847	10	233	Tampa Bay Buccaneers	1	2025-12-21 17:22:40.121186	16	0	f
4848	10	234	New England Patriots	4	2025-12-21 17:22:40.121973	16	4	f
4849	10	235	Denver Broncos	16	2025-12-21 17:22:40.12275	16	0	f
4850	10	236	Arizona Cardinals	2	2025-12-21 17:22:40.123608	16	0	f
4851	10	237	Pittsburgh Steelers	7	2025-12-21 17:22:40.124529	16	7	f
4852	10	238	Houston Texans	13	2025-12-21 17:22:40.125437	16	0	f
4853	10	239	Cincinnati Bengals	6	2025-12-21 17:22:40.126346	16	6	f
4854	10	240	San Francisco 49ers	14	2025-12-21 17:22:40.127504	16	14	f
4855	17	228	Cleveland Browns	4	2025-12-21 17:46:52.432859	16	4	f
4856	17	229	Los Angeles Chargers	16	2025-12-21 17:46:52.434211	16	16	f
4857	17	230	Tennessee Titans	7	2025-12-21 17:46:52.435206	16	7	f
4858	17	231	New Orleans Saints	15	2025-12-21 17:46:52.4363	16	15	f
4859	17	232	Minnesota Vikings	14	2025-12-21 17:46:52.437199	16	0	f
4860	17	233	Tampa Bay Buccaneers	11	2025-12-21 17:46:52.438092	16	0	f
4861	17	234	Baltimore Ravens	10	2025-12-21 17:46:52.439345	16	0	f
4862	17	235	Denver Broncos	13	2025-12-21 18:00:49.390822	16	0	f
4863	17	236	Atlanta Falcons	8	2025-12-21 18:00:49.392277	16	8	f
4864	17	237	Pittsburgh Steelers	9	2025-12-21 18:00:49.39338	16	9	f
4865	17	238	Houston Texans	12	2025-12-21 18:00:49.394427	16	0	f
4866	17	239	Miami Dolphins	6	2025-12-21 18:00:49.395441	16	0	f
4867	17	240	Indianapolis Colts	5	2025-12-21 18:00:49.396449	16	0	f
4868	18	228	Cleveland Browns	2	2025-12-21 17:51:12.138654	16	2	f
4869	18	229	Los Angeles Chargers	3	2025-12-21 17:51:12.140228	16	3	f
4870	18	230	Kansas City Chiefs	5	2025-12-21 17:51:12.141509	16	0	f
4871	18	231	New York Jets	4	2025-12-21 17:51:12.142683	16	0	f
4872	18	232	Minnesota Vikings	14	2025-12-21 17:51:12.143803	16	0	f
4873	18	233	Carolina Panthers	13	2025-12-21 17:51:12.144892	16	13	f
4874	18	234	New England Patriots	1	2025-12-21 17:51:12.146028	16	1	f
4875	18	235	Denver Broncos	11	2025-12-21 17:51:12.147097	16	0	f
4876	18	236	Atlanta Falcons	10	2025-12-21 17:51:12.14816	16	10	f
4877	18	237	Pittsburgh Steelers	9	2025-12-21 17:51:12.14925	16	9	f
4878	18	238	Las Vegas Raiders	8	2025-12-21 17:51:12.150296	16	8	f
4879	18	239	Miami Dolphins	7	2025-12-21 17:51:12.151347	16	0	f
4880	18	240	Indianapolis Colts	6	2025-12-21 17:51:12.15218	16	0	f
4881	12	241	Dallas Cowboys	14	2025-12-23 15:49:36.838196	17	14	f
4882	12	242	Detroit Lions	15	2025-12-23 15:49:36.839892	17	0	f
4883	12	243	Denver Broncos	16	2025-12-23 15:49:36.841252	17	0	f
4884	12	244	Arizona Cardinals	6	2025-12-28 16:58:11.10231	17	0	f
4885	12	245	Green Bay Packers	2	2025-12-27 23:14:37.731859	17	0	f
4886	12	246	Las Vegas Raiders	10	2025-12-28 16:58:11.103519	17	0	f
4887	12	247	Houston Texans	12	2025-12-26 19:17:00.536745	17	12	f
4888	12	248	Carolina Panthers	5	2025-12-28 16:58:11.104442	17	0	f
4889	12	249	Pittsburgh Steelers	7	2025-12-28 16:58:11.105319	17	0	f
4890	12	250	New Orleans Saints	9	2025-12-28 16:58:11.106184	17	9	f
4891	12	251	Jacksonville Jaguars	8	2025-12-28 16:58:11.107043	17	0	f
4892	12	255	San Francisco 49ers	11	2025-12-28 16:58:11.110952	17	11	f
4893	1	241	Dallas Cowboys	10	2025-12-23 18:55:26.303632	17	10	f
4894	1	242	Detroit Lions	13	2025-12-23 18:55:26.304851	17	0	f
4895	1	243	Denver Broncos	16	2025-12-23 18:55:26.305819	17	0	f
4896	1	244	Cincinnati Bengals	7	2025-12-23 18:55:26.306688	17	7	f
4897	1	245	Green Bay Packers	6	2025-12-23 18:55:26.307528	17	0	f
4898	1	246	Las Vegas Raiders	3	2025-12-23 18:55:26.308435	17	0	f
4899	1	247	Houston Texans	9	2025-12-23 18:55:26.309312	17	9	f
4900	1	248	Seattle Seahawks	11	2025-12-23 18:55:26.310128	17	11	f
4901	1	249	Pittsburgh Steelers	12	2025-12-23 18:55:26.310905	17	0	f
4902	1	250	New Orleans Saints	8	2025-12-23 18:55:26.31189	17	8	f
4903	1	251	Jacksonville Jaguars	5	2025-12-23 18:55:26.312754	17	0	f
4904	1	252	Tampa Bay Buccaneers	4	2025-12-23 18:55:26.3138	17	0	f
4905	1	253	New England Patriots	14	2025-12-23 18:55:26.314733	17	14	f
4906	1	254	Philadelphia Eagles	15	2025-12-23 18:55:26.315645	17	15	f
4907	1	255	San Francisco 49ers	2	2025-12-23 18:55:26.316447	17	2	f
4908	1	256	Los Angeles Rams	1	2025-12-23 18:55:26.317076	17	0	f
4909	14	241	Dallas Cowboys	9	2025-12-25 02:28:27.348352	17	9	f
4910	14	242	Detroit Lions	12	2025-12-25 02:28:27.349706	17	0	f
4911	14	243	Denver Broncos	6	2025-12-25 02:28:27.350865	17	0	f
4912	14	244	Cincinnati Bengals	7	2025-12-25 02:28:27.351906	17	7	f
4913	14	245	Green Bay Packers	16	2025-12-25 02:28:27.35282	17	0	f
4914	14	246	Las Vegas Raiders	3	2025-12-25 02:28:27.353681	17	0	f
4915	14	247	Houston Texans	5	2025-12-25 02:28:27.354645	17	5	f
4916	14	248	Carolina Panthers	4	2025-12-25 02:28:27.355714	17	0	f
4917	14	249	Pittsburgh Steelers	13	2025-12-25 02:28:27.356526	17	0	f
4918	14	250	New Orleans Saints	10	2025-12-25 02:28:27.35735	17	10	f
4919	14	251	Jacksonville Jaguars	15	2025-12-25 02:28:27.358128	17	0	f
4920	14	252	Tampa Bay Buccaneers	1	2025-12-25 02:28:27.358879	17	0	f
4921	14	253	New England Patriots	8	2025-12-25 02:28:27.359843	17	8	f
4922	14	254	Buffalo Bills	2	2025-12-25 02:28:27.360965	17	0	f
4923	14	255	San Francisco 49ers	14	2025-12-25 02:28:27.362101	17	14	f
4924	14	256	Los Angeles Rams	11	2025-12-25 02:28:27.363079	17	0	f
4925	2	241	Dallas Cowboys	8	2025-12-24 09:56:20.254391	17	8	f
4926	2	242	Minnesota Vikings	1	2025-12-24 09:56:20.255924	17	1	f
4927	2	243	Denver Broncos	9	2025-12-24 09:56:20.257143	17	0	f
4928	2	244	Arizona Cardinals	3	2025-12-24 09:56:20.258268	17	0	f
4929	2	245	Green Bay Packers	13	2025-12-24 09:56:20.259378	17	0	f
4930	2	246	New York Giants	5	2025-12-24 09:56:20.260437	17	5	f
4931	2	247	Houston Texans	11	2025-12-24 09:56:20.261497	17	11	f
4932	2	248	Seattle Seahawks	12	2025-12-24 09:56:20.262533	17	12	f
4933	2	249	Pittsburgh Steelers	16	2025-12-24 09:56:20.26357	17	0	f
4934	2	250	New Orleans Saints	10	2025-12-24 09:56:20.2646	17	10	f
4935	2	251	Indianapolis Colts	14	2025-12-24 09:56:20.265627	17	14	f
4936	2	252	Tampa Bay Buccaneers	15	2025-12-24 09:56:20.26664	17	0	f
4937	2	253	New York Jets	4	2025-12-24 09:56:20.267662	17	0	f
4938	2	254	Buffalo Bills	7	2025-12-24 09:56:20.268672	17	0	f
4939	2	255	San Francisco 49ers	2	2025-12-24 09:56:20.269711	17	2	f
4940	2	256	Los Angeles Rams	6	2025-12-24 09:56:20.270835	17	0	f
4941	4	241	Dallas Cowboys	14	2025-12-24 14:38:44.261991	17	14	f
4942	4	242	Detroit Lions	15	2025-12-24 14:38:44.263244	17	0	f
4943	4	243	Denver Broncos	16	2025-12-24 14:38:44.264273	17	0	f
4944	4	244	Cincinnati Bengals	5	2025-12-24 14:38:44.265261	17	5	f
4945	4	245	Green Bay Packers	12	2025-12-24 14:38:44.266198	17	0	f
4946	4	246	New York Giants	2	2025-12-24 14:38:44.267198	17	2	f
4947	4	247	Houston Texans	13	2025-12-24 14:38:44.268112	17	13	f
4948	4	248	Seattle Seahawks	7	2025-12-24 14:38:44.26905	17	7	f
4949	4	249	Pittsburgh Steelers	11	2025-12-24 14:38:44.269955	17	0	f
4950	4	250	New Orleans Saints	9	2025-12-24 14:38:44.270905	17	9	f
4951	4	251	Indianapolis Colts	1	2025-12-24 14:38:44.271817	17	1	f
4952	4	252	Tampa Bay Buccaneers	8	2025-12-24 14:38:44.272743	17	0	f
4953	4	253	New England Patriots	4	2025-12-24 14:38:44.273639	17	4	f
4954	4	254	Buffalo Bills	3	2025-12-24 14:38:44.274541	17	0	f
4955	4	255	San Francisco 49ers	6	2025-12-24 14:38:44.275435	17	6	f
4956	4	256	Los Angeles Rams	10	2025-12-24 14:38:44.276335	17	0	f
4957	8	241	Dallas Cowboys	7	2025-12-24 17:23:43.369835	17	7	f
4958	8	242	Detroit Lions	10	2025-12-24 17:23:43.3712	17	0	f
4959	8	243	Denver Broncos	9	2025-12-24 17:23:43.372204	17	0	f
4960	8	244	Cincinnati Bengals	2	2025-12-24 17:23:43.373233	17	2	f
4961	8	245	Green Bay Packers	15	2025-12-24 17:23:43.374333	17	0	f
4962	8	246	New York Giants	1	2025-12-24 17:23:43.375416	17	1	f
4963	8	247	Houston Texans	3	2025-12-24 17:23:43.376428	17	3	f
4964	8	248	Carolina Panthers	5	2025-12-24 17:23:43.377774	17	0	f
4965	8	249	Pittsburgh Steelers	12	2025-12-24 17:23:43.378778	17	0	f
4966	8	250	New Orleans Saints	13	2025-12-24 17:23:43.379749	17	13	f
4967	8	251	Jacksonville Jaguars	11	2025-12-24 17:23:43.380679	17	0	f
4968	8	252	Tampa Bay Buccaneers	8	2025-12-24 17:23:43.381669	17	0	f
4969	8	253	New England Patriots	16	2025-12-24 17:23:43.382678	17	16	f
4970	8	254	Buffalo Bills	6	2025-12-24 17:23:43.38367	17	0	f
4971	8	255	San Francisco 49ers	4	2025-12-24 17:23:43.384771	17	4	f
4972	8	256	Los Angeles Rams	14	2025-12-24 17:23:43.385559	17	0	f
4973	16	241	Dallas Cowboys	8	2025-12-24 18:59:55.251863	17	8	f
4974	16	242	Detroit Lions	4	2025-12-24 18:59:55.253383	17	0	f
4975	16	243	Denver Broncos	16	2025-12-24 18:59:55.254551	17	0	f
4976	16	244	Cincinnati Bengals	5	2025-12-24 18:59:55.255629	17	5	f
4977	16	245	Green Bay Packers	15	2025-12-24 18:59:55.256693	17	0	f
4978	16	246	Las Vegas Raiders	12	2025-12-24 18:59:55.257844	17	0	f
4979	16	247	Los Angeles Chargers	2	2025-12-24 18:59:55.258916	17	0	f
4980	16	248	Seattle Seahawks	7	2025-12-24 18:59:55.259942	17	7	f
4981	16	249	Pittsburgh Steelers	14	2025-12-24 18:59:55.261153	17	0	f
4982	16	250	New Orleans Saints	6	2025-12-24 18:59:55.262144	17	6	f
4983	16	251	Jacksonville Jaguars	13	2025-12-24 18:59:55.263218	17	0	f
4984	16	252	Tampa Bay Buccaneers	10	2025-12-24 18:59:55.264237	17	0	f
4985	16	253	New York Jets	9	2025-12-24 18:59:55.265307	17	0	f
4986	16	254	Buffalo Bills	3	2025-12-24 18:59:55.266341	17	0	f
4987	16	255	San Francisco 49ers	11	2025-12-24 18:59:55.267407	17	11	f
4988	16	256	Atlanta Falcons	1	2025-12-24 18:59:55.268235	17	1	f
4989	20	241	Dallas Cowboys	16	2025-12-24 20:30:40.342556	17	16	f
4990	20	242	Detroit Lions	14	2025-12-24 20:30:40.344191	17	0	f
4991	20	243	Kansas City Chiefs	15	2025-12-24 20:30:40.345476	17	15	f
4992	20	245	Green Bay Packers	12	2025-12-26 16:40:38.839633	17	0	f
4993	20	247	Los Angeles Chargers	13	2025-12-26 16:40:38.842298	17	0	f
4994	20	246	New York Giants	10	2025-12-26 16:40:38.841098	17	10	f
4995	20	249	Pittsburgh Steelers	11	2025-12-26 16:40:38.844678	17	0	f
4996	20	252	Tampa Bay Buccaneers	4	2025-12-26 16:40:38.848101	17	0	f
4997	20	253	New England Patriots	3	2025-12-26 16:40:38.849173	17	3	f
4998	20	254	Buffalo Bills	1	2025-12-26 16:40:38.850213	17	0	f
4999	20	255	San Francisco 49ers	8	2025-12-26 16:40:38.851241	17	8	f
5000	5	241	Dallas Cowboys	6	2025-12-24 20:37:01.100028	17	6	f
5001	5	242	Detroit Lions	16	2025-12-24 20:37:01.101813	17	0	f
5002	5	243	Denver Broncos	7	2025-12-24 20:37:01.103092	17	0	f
5003	5	244	Arizona Cardinals	1	2025-12-24 20:37:01.104199	17	0	f
5004	5	245	Green Bay Packers	15	2025-12-24 20:37:01.105278	17	0	f
5005	5	246	Las Vegas Raiders	11	2025-12-24 20:37:01.10645	17	0	f
5006	5	247	Houston Texans	5	2025-12-24 20:37:01.107578	17	5	f
5007	5	248	Carolina Panthers	3	2025-12-24 20:37:01.108576	17	0	f
5008	5	249	Pittsburgh Steelers	9	2025-12-24 20:37:01.109474	17	0	f
5009	5	250	New Orleans Saints	10	2025-12-24 20:37:01.110326	17	10	f
5010	5	251	Indianapolis Colts	2	2025-12-24 20:37:01.111149	17	2	f
5011	5	252	Tampa Bay Buccaneers	8	2025-12-24 20:37:01.111938	17	0	f
5012	5	253	New England Patriots	4	2025-12-24 20:37:01.11286	17	4	f
5013	5	254	Buffalo Bills	14	2025-12-24 20:37:01.113778	17	0	f
5014	5	255	San Francisco 49ers	12	2025-12-24 20:37:01.114652	17	12	f
5015	5	256	Los Angeles Rams	13	2025-12-24 20:37:01.115564	17	0	f
5016	18	241	Dallas Cowboys	11	2025-12-25 16:36:46.058576	17	11	f
5017	18	242	Detroit Lions	13	2025-12-25 16:36:46.060136	17	0	f
5018	18	243	Denver Broncos	16	2025-12-25 16:36:46.06155	17	0	f
5019	18	245	Green Bay Packers	14	2025-12-28 00:35:12.993326	17	0	f
5020	18	247	Houston Texans	15	2025-12-25 16:36:46.063755	17	15	f
5021	19	241	Dallas Cowboys	5	2025-12-25 15:22:21.536082	17	5	f
5022	19	242	Detroit Lions	15	2025-12-25 15:22:21.53765	17	0	f
5023	19	243	Denver Broncos	16	2025-12-25 15:22:21.538816	17	0	f
5024	13	241	Dallas Cowboys	14	2025-12-25 16:11:36.605677	17	14	f
5025	13	242	Detroit Lions	15	2025-12-25 16:11:36.607127	17	0	f
5026	13	243	Denver Broncos	16	2025-12-25 16:11:36.608156	17	0	f
5027	17	241	Dallas Cowboys	13	2025-12-25 17:53:46.311569	17	13	f
5028	17	242	Detroit Lions	14	2025-12-25 17:53:46.312796	17	0	f
5029	17	243	Denver Broncos	15	2025-12-25 17:53:46.313713	17	0	f
5030	17	245	Green Bay Packers	2	2025-12-25 17:53:46.314559	17	0	f
5031	17	247	Los Angeles Chargers	3	2025-12-25 17:53:46.315541	17	0	f
5032	15	241	Washington Commanders	4	2025-12-25 16:53:38.026483	17	0	f
5033	15	242	Detroit Lions	11	2025-12-25 21:29:20.566992	17	0	f
5034	15	243	Denver Broncos	16	2025-12-25 21:29:20.568889	17	0	f
5035	10	241	Dallas Cowboys	10	2025-12-25 17:11:44.976114	17	10	f
5036	9	241	Washington Commanders	5	2025-12-25 17:21:57.263633	17	0	f
5037	9	242	Detroit Lions	4	2025-12-25 17:21:57.264648	17	0	f
5038	9	243	Denver Broncos	14	2025-12-25 17:21:57.265467	17	0	f
5039	9	244	Arizona Cardinals	7	2025-12-25 17:21:57.266263	17	0	f
5040	9	245	Green Bay Packers	12	2025-12-25 17:21:57.267067	17	0	f
5041	9	246	New York Giants	1	2025-12-25 17:21:57.26784	17	1	f
5042	9	247	Los Angeles Chargers	11	2025-12-25 17:21:57.268626	17	0	f
5043	9	248	Carolina Panthers	3	2025-12-25 17:21:57.269472	17	0	f
5044	9	249	Cleveland Browns	6	2025-12-25 17:21:57.270256	17	6	f
5045	9	250	New Orleans Saints	2	2025-12-25 17:21:57.271027	17	2	f
5046	9	251	Jacksonville Jaguars	13	2025-12-25 17:21:57.27178	17	0	f
5047	9	252	Tampa Bay Buccaneers	10	2025-12-25 17:21:57.272549	17	0	f
5048	9	253	New York Jets	8	2025-12-25 17:21:57.273328	17	0	f
5049	9	254	Buffalo Bills	9	2025-12-25 17:21:57.274097	17	0	f
5050	9	255	San Francisco 49ers	16	2025-12-25 17:21:57.274843	17	16	f
5051	9	256	Los Angeles Rams	15	2025-12-25 17:21:57.275454	17	0	f
5052	26	242	Minnesota Vikings	6	2025-12-25 18:00:44.548278	17	6	f
5053	26	243	Kansas City Chiefs	1	2025-12-25 18:00:44.549981	17	1	f
5054	26	245	Baltimore Ravens	9	2025-12-25 18:00:44.551302	17	9	f
5055	26	247	Houston Texans	3	2025-12-25 18:00:44.552567	17	3	f
5056	10	242	Detroit Lions	12	2025-12-25 21:29:18.100512	17	0	f
5057	23	242	Detroit Lions	8	2025-12-25 20:32:45.608709	17	0	f
5058	23	243	Denver Broncos	15	2025-12-25 20:32:45.610534	17	0	f
5059	23	244	Cincinnati Bengals	1	2025-12-25 20:32:45.612044	17	1	f
5060	23	245	Green Bay Packers	10	2025-12-25 20:32:45.613477	17	0	f
5061	23	246	New York Giants	2	2025-12-25 20:32:45.614893	17	2	f
5062	23	247	Los Angeles Chargers	13	2025-12-25 20:32:45.616309	17	0	f
5063	23	248	Seattle Seahawks	7	2025-12-25 20:32:45.6176	17	7	f
5064	23	249	Pittsburgh Steelers	6	2025-12-25 20:32:45.618864	17	0	f
5065	23	250	New Orleans Saints	5	2025-12-25 20:32:45.620195	17	5	f
5066	23	251	Jacksonville Jaguars	14	2025-12-25 20:32:45.621486	17	0	f
5067	23	252	Tampa Bay Buccaneers	4	2025-12-25 20:32:45.622699	17	0	f
5068	23	253	New England Patriots	12	2025-12-25 20:32:45.624233	17	12	f
5069	23	254	Buffalo Bills	11	2025-12-25 20:32:45.625512	17	0	f
5070	23	255	Chicago Bears	9	2025-12-25 20:32:45.62671	17	0	f
5071	23	256	Atlanta Falcons	3	2025-12-25 20:32:45.627671	17	3	f
5072	10	243	Denver Broncos	16	2025-12-26 00:17:19.290668	17	0	f
5073	20	244	Cincinnati Bengals	5	2025-12-26 16:40:38.838499	17	5	f
5074	20	248	Carolina Panthers	9	2025-12-26 16:40:38.843914	17	0	f
5075	20	250	New Orleans Saints	2	2025-12-26 16:40:38.84628	17	2	f
5076	20	251	Jacksonville Jaguars	7	2025-12-26 16:40:38.847421	17	0	f
5077	20	256	Atlanta Falcons	6	2025-12-26 16:40:38.855079	17	6	f
5078	22	244	Cincinnati Bengals	13	2025-12-26 18:30:03.027609	17	13	f
5079	22	245	Green Bay Packers	4	2025-12-26 18:30:03.029245	17	0	f
5080	22	246	New York Giants	7	2025-12-26 18:30:03.030612	17	7	f
5081	22	247	Houston Texans	11	2025-12-26 18:30:03.031959	17	11	f
5082	22	248	Seattle Seahawks	12	2025-12-26 18:30:03.033297	17	12	f
5083	22	249	Pittsburgh Steelers	5	2025-12-26 18:30:03.034632	17	0	f
5084	22	250	New Orleans Saints	6	2025-12-26 18:30:03.0358	17	6	f
5085	22	251	Jacksonville Jaguars	3	2025-12-26 18:30:03.036887	17	0	f
5086	22	252	Tampa Bay Buccaneers	10	2025-12-26 18:30:03.038152	17	0	f
5087	22	253	New York Jets	2	2025-12-26 18:30:03.039352	17	0	f
5088	22	254	Buffalo Bills	1	2025-12-26 18:30:03.040565	17	0	f
5089	22	255	San Francisco 49ers	9	2025-12-26 18:30:03.041847	17	9	f
5090	22	256	Los Angeles Rams	8	2025-12-26 18:30:03.042889	17	0	f
5091	12	252	Tampa Bay Buccaneers	4	2025-12-28 16:58:11.108108	17	0	f
5092	12	253	New England Patriots	3	2025-12-28 16:58:11.109108	17	3	f
5093	12	254	Buffalo Bills	13	2025-12-28 16:58:11.110065	17	0	f
5094	12	256	Los Angeles Rams	1	2025-12-28 16:58:11.111845	17	0	f
5095	19	245	Baltimore Ravens	2	2025-12-27 17:37:29.515201	17	2	f
5096	19	247	Houston Texans	6	2025-12-27 17:37:29.516315	17	6	f
5097	13	245	Baltimore Ravens	12	2025-12-27 19:33:32.616617	17	12	f
5098	13	247	Houston Texans	13	2025-12-27 19:33:32.617573	17	13	f
5099	10	247	Houston Texans	15	2025-12-27 20:24:25.775375	17	15	f
5100	15	245	Green Bay Packers	10	2025-12-27 23:35:54.939509	17	0	f
5101	10	245	Baltimore Ravens	4	2025-12-28 00:56:59.251246	17	4	f
5102	18	244	Arizona Cardinals	1	2025-12-28 12:19:07.113665	17	0	f
5103	18	246	Las Vegas Raiders	7	2025-12-28 12:19:07.115145	17	0	f
5104	18	248	Carolina Panthers	12	2025-12-28 12:19:07.11626	17	0	f
5105	18	249	Cleveland Browns	2	2025-12-28 12:19:07.117319	17	2	f
5106	18	250	New Orleans Saints	10	2025-12-28 12:19:07.118345	17	10	f
5107	18	251	Indianapolis Colts	3	2025-12-28 12:19:07.119367	17	3	f
5108	18	252	Tampa Bay Buccaneers	9	2025-12-28 12:19:07.120397	17	0	f
5109	18	253	New England Patriots	8	2025-12-28 12:19:07.121407	17	8	f
5110	18	254	Philadelphia Eagles	6	2025-12-28 12:19:07.122428	17	6	f
5111	18	255	Chicago Bears	4	2025-12-28 12:19:07.123429	17	0	f
5112	18	256	Los Angeles Rams	5	2025-12-28 12:19:07.124456	17	0	f
5113	26	244	Cincinnati Bengals	12	2025-12-28 15:42:32.898756	17	12	f
5114	26	246	New York Giants	14	2025-12-28 15:42:32.900465	17	14	f
5115	26	248	Carolina Panthers	2	2025-12-28 15:42:32.90188	17	0	f
5116	26	249	Cleveland Browns	4	2025-12-28 15:42:32.902856	17	4	f
5117	26	250	New Orleans Saints	5	2025-12-28 15:42:32.903723	17	5	f
5118	26	251	Jacksonville Jaguars	15	2025-12-28 15:42:32.904598	17	0	f
5119	26	252	Tampa Bay Buccaneers	13	2025-12-28 15:42:32.905417	17	0	f
5120	26	253	New England Patriots	10	2025-12-28 15:42:32.906278	17	10	f
5121	26	254	Buffalo Bills	8	2025-12-28 15:42:32.90727	17	0	f
5122	26	255	Chicago Bears	7	2025-12-28 15:42:32.908048	17	0	f
5123	26	256	Los Angeles Rams	11	2025-12-28 15:42:32.90865	17	0	f
5124	15	244	Arizona Cardinals	3	2025-12-28 16:26:13.641776	17	0	f
5125	15	246	Las Vegas Raiders	6	2025-12-28 16:26:13.64312	17	0	f
5126	15	248	Carolina Panthers	2	2025-12-28 16:26:13.644146	17	0	f
5127	15	249	Pittsburgh Steelers	9	2025-12-28 16:26:13.645226	17	0	f
5128	15	250	New Orleans Saints	14	2025-12-28 16:26:13.646294	17	14	f
5129	15	251	Jacksonville Jaguars	8	2025-12-28 16:26:13.64748	17	0	f
5130	15	252	Tampa Bay Buccaneers	12	2025-12-28 16:26:13.648663	17	0	f
5131	15	253	New England Patriots	7	2025-12-28 16:26:13.649723	17	7	f
5132	15	254	Buffalo Bills	5	2025-12-28 16:26:13.650686	17	0	f
5133	15	255	Chicago Bears	13	2025-12-28 16:26:13.651651	17	0	f
5134	15	256	Los Angeles Rams	1	2025-12-28 16:26:13.652462	17	0	f
5135	17	244	Cincinnati Bengals	16	2025-12-28 16:44:13.997224	17	16	f
5136	17	246	New York Giants	1	2025-12-28 16:44:13.998404	17	1	f
5137	17	248	Seattle Seahawks	8	2025-12-28 16:44:13.999348	17	8	f
5138	17	249	Pittsburgh Steelers	12	2025-12-28 16:44:14.0002	17	0	f
5139	17	250	Tennessee Titans	6	2025-12-28 16:44:14.001037	17	0	f
5140	17	251	Jacksonville Jaguars	10	2025-12-28 16:44:14.001834	17	0	f
5141	17	252	Tampa Bay Buccaneers	7	2025-12-28 16:44:14.002649	17	0	f
5142	17	253	New England Patriots	9	2025-12-28 16:44:14.003426	17	9	f
5143	17	254	Buffalo Bills	11	2025-12-28 16:44:14.004201	17	0	f
5144	17	255	San Francisco 49ers	5	2025-12-28 16:44:14.004971	17	5	f
5145	17	256	Atlanta Falcons	4	2025-12-29 22:55:01.0106	17	4	f
5146	19	244	Arizona Cardinals	8	2025-12-28 16:56:10.790223	17	0	f
5147	19	246	Las Vegas Raiders	7	2025-12-28 16:56:10.791726	17	0	f
5148	19	248	Seattle Seahawks	14	2025-12-28 16:56:10.792909	17	14	f
5149	19	249	Pittsburgh Steelers	10	2025-12-28 16:56:10.794057	17	0	f
5150	19	250	New Orleans Saints	11	2025-12-28 16:56:10.795155	17	11	f
5151	19	251	Jacksonville Jaguars	9	2025-12-28 16:56:10.796248	17	0	f
5152	19	252	Tampa Bay Buccaneers	3	2025-12-28 16:56:10.79738	17	0	f
5153	19	253	New England Patriots	1	2025-12-28 16:56:10.798462	17	1	f
5154	19	254	Philadelphia Eagles	4	2025-12-28 16:56:10.799528	17	4	f
5155	19	255	Chicago Bears	13	2025-12-28 16:56:10.800602	17	0	f
5156	19	256	Los Angeles Rams	12	2025-12-28 16:56:10.801468	17	0	f
5157	10	244	Cincinnati Bengals	3	2025-12-28 17:37:29.062901	17	3	f
5158	10	246	New York Giants	6	2025-12-28 17:37:29.064209	17	6	f
5159	10	248	Carolina Panthers	5	2025-12-28 17:37:29.065143	17	0	f
5160	10	249	Pittsburgh Steelers	11	2025-12-28 17:37:29.06598	17	0	f
5161	10	250	New Orleans Saints	1	2025-12-28 17:37:29.066873	17	1	f
5162	10	251	Jacksonville Jaguars	13	2025-12-28 17:37:29.067718	17	0	f
5163	10	252	Tampa Bay Buccaneers	9	2025-12-28 17:37:29.068768	17	0	f
5164	10	253	New England Patriots	8	2025-12-28 17:37:29.069633	17	8	f
5165	10	254	Buffalo Bills	7	2025-12-28 17:37:29.070436	17	0	f
5166	10	255	San Francisco 49ers	14	2025-12-28 17:37:29.071208	17	14	f
5167	10	256	Los Angeles Rams	2	2025-12-28 17:37:29.071942	17	0	f
5168	13	246	New York Giants	4	2025-12-28 18:18:52.375362	17	4	f
5169	13	254	Buffalo Bills	3	2025-12-28 18:18:52.376847	17	0	f
5170	13	255	Chicago Bears	2	2025-12-28 18:18:52.377973	17	0	f
5171	13	256	Los Angeles Rams	1	2025-12-28 18:18:52.378912	17	0	f
5172	1	257	Atlanta Falcons	7	2025-12-30 19:43:01.275701	18	0	f
5173	1	258	Buffalo Bills	14	2025-12-30 19:43:01.277745	18	14	f
5174	1	259	Chicago Bears	13	2025-12-30 19:43:01.278695	18	0	f
5175	1	260	Cincinnati Bengals	6	2025-12-30 19:43:01.279525	18	0	f
5176	1	261	Denver Broncos	16	2025-12-30 19:43:01.280398	18	16	f
5177	1	262	Kansas City Chiefs	11	2025-12-30 19:43:01.281205	18	0	f
5178	1	263	Los Angeles Rams	12	2025-12-30 19:43:01.282106	18	12	f
5179	1	264	Green Bay Packers	5	2025-12-30 19:43:01.282967	18	0	f
5180	1	266	Dallas Cowboys	3	2025-12-30 19:43:01.284853	18	0	f
5181	1	267	Philadelphia Eagles	10	2025-12-30 19:43:01.285868	18	0	f
5182	1	268	Baltimore Ravens	2	2025-12-30 19:43:01.286693	18	0	f
5183	1	269	Seattle Seahawks	9	2025-12-30 19:43:01.287475	18	9	f
5184	1	270	Carolina Panthers	8	2025-12-30 19:43:01.288496	18	8	f
5185	1	271	Jacksonville Jaguars	4	2025-12-30 19:43:01.289592	18	4	f
5186	1	272	Houston Texans	1	2025-12-30 19:43:01.290542	18	0	f
5187	12	257	New Orleans Saints	5	2026-01-03 04:36:53.063136	18	5	f
5188	12	264	Green Bay Packers	12	2026-01-03 04:36:53.072265	18	0	f
5189	12	265	New England Patriots	15	2026-01-03 04:36:53.073466	18	15	f
5190	12	266	Dallas Cowboys	16	2026-01-03 04:36:53.074444	18	0	f
5191	12	268	Pittsburgh Steelers	10	2026-01-03 04:36:53.076567	18	10	f
5192	12	269	Seattle Seahawks	11	2026-01-03 04:36:53.077738	18	11	f
5193	12	270	Tampa Bay Buccaneers	13	2026-01-03 04:36:53.078704	18	0	f
5194	12	272	Houston Texans	14	2026-01-03 04:36:53.080887	18	0	f
5195	12	258	Buffalo Bills	9	2026-01-03 04:36:53.065013	18	9	f
5196	12	259	Detroit Lions	6	2026-01-03 04:36:53.066216	18	6	f
5197	12	261	Denver Broncos	8	2026-01-03 04:36:53.06871	18	8	f
5198	1	265	New England Patriots	15	2025-12-30 19:43:01.28414	18	15	f
5199	14	257	New Orleans Saints	2	2026-01-02 20:22:03.050111	18	2	f
5200	14	258	Buffalo Bills	14	2026-01-04 20:33:43.879542	18	14	f
5201	14	259	Chicago Bears	16	2026-01-04 20:33:43.880729	18	0	f
5202	14	260	Cincinnati Bengals	12	2026-01-02 20:22:03.05629	18	0	f
5203	14	261	Denver Broncos	3	2026-01-04 20:33:43.88162	18	3	f
5204	14	262	Kansas City Chiefs	10	2026-01-04 20:33:43.882522	18	0	f
5205	14	263	Los Angeles Rams	15	2026-01-04 20:33:43.883338	18	15	f
5206	14	264	Green Bay Packers	6	2026-01-02 20:22:03.06716	18	0	f
5207	14	265	Miami Dolphins	5	2026-01-04 20:33:43.88418	18	0	f
5208	14	266	New York Giants	1	2026-01-02 20:22:03.069998	18	1	f
5209	14	267	Washington Commanders	7	2026-01-04 20:33:43.885128	18	7	f
5210	14	268	Baltimore Ravens	4	2026-01-04 20:33:43.885928	18	0	f
5211	14	269	Seattle Seahawks	9	2026-01-02 20:22:03.074032	18	9	f
5212	14	270	Carolina Panthers	8	2026-01-02 20:22:03.076126	18	8	f
5213	14	271	Tennessee Titans	11	2026-01-02 20:22:03.077439	18	0	f
5214	14	272	Houston Texans	13	2026-01-02 20:22:03.07878	18	0	f
5215	23	257	Atlanta Falcons	1	2025-12-31 15:01:59.905925	18	0	f
5216	23	258	Buffalo Bills	9	2025-12-31 15:01:59.907139	18	9	f
5217	23	259	Chicago Bears	11	2025-12-31 15:01:59.908173	18	0	f
5218	23	260	Cincinnati Bengals	2	2025-12-31 15:01:59.909125	18	0	f
5219	23	261	Denver Broncos	16	2025-12-31 15:01:59.910048	18	16	f
5220	23	262	Las Vegas Raiders	5	2025-12-31 15:01:59.910998	18	5	f
5221	23	263	Los Angeles Rams	12	2025-12-31 15:01:59.911955	18	12	f
5222	23	264	Green Bay Packers	4	2025-12-31 15:01:59.912833	18	0	f
5223	23	265	New England Patriots	13	2025-12-31 15:01:59.913855	18	13	f
5224	23	266	Dallas Cowboys	7	2025-12-31 15:01:59.914769	18	0	f
5225	23	267	Philadelphia Eagles	14	2025-12-31 15:01:59.915666	18	0	f
5226	23	268	Baltimore Ravens	15	2025-12-31 15:01:59.9165	18	0	f
5227	23	269	Seattle Seahawks	10	2025-12-31 15:01:59.917318	18	10	f
5228	23	270	Tampa Bay Buccaneers	6	2025-12-31 15:01:59.918354	18	0	f
5229	23	271	Jacksonville Jaguars	8	2025-12-31 15:01:59.919511	18	8	f
5230	23	272	Houston Texans	3	2025-12-31 15:01:59.920487	18	0	f
5231	20	260	Cleveland Browns	5	2026-01-04 06:00:22.349975	18	5	f
5232	20	266	Dallas Cowboys	16	2026-01-04 06:00:22.357854	18	0	f
5233	20	269	San Francisco 49ers	1	2026-01-02 17:26:47.197027	18	0	f
5234	20	270	Carolina Panthers	12	2026-01-02 17:26:47.197981	18	12	f
5235	13	257	New Orleans Saints	3	2025-12-31 19:42:11.052612	18	3	f
5236	13	258	Buffalo Bills	9	2025-12-31 19:42:11.054749	18	9	f
5237	13	259	Chicago Bears	10	2025-12-31 19:42:11.056164	18	0	f
5238	13	260	Cleveland Browns	4	2025-12-31 19:42:11.057908	18	4	f
5239	13	261	Los Angeles Chargers	11	2025-12-31 19:42:11.059422	18	0	f
5240	13	262	Las Vegas Raiders	12	2025-12-31 19:42:11.061543	18	12	f
5241	13	263	Los Angeles Rams	13	2025-12-31 19:42:11.062889	18	13	f
5242	13	264	Green Bay Packers	5	2025-12-31 19:42:11.063927	18	0	f
5243	13	265	Miami Dolphins	14	2025-12-31 19:42:11.06481	18	0	f
5244	13	266	New York Giants	6	2025-12-31 19:42:11.066215	18	6	f
5245	13	267	Philadelphia Eagles	15	2025-12-31 19:42:11.067649	18	0	f
5246	13	268	Baltimore Ravens	16	2025-12-31 19:42:11.068921	18	0	f
5247	13	269	San Francisco 49ers	2	2025-12-31 19:42:11.070181	18	0	f
5248	13	270	Tampa Bay Buccaneers	1	2025-12-31 19:42:11.071574	18	0	f
5249	13	271	Jacksonville Jaguars	7	2025-12-31 19:42:11.073123	18	7	f
5250	13	272	Indianapolis Colts	8	2025-12-31 19:42:11.075005	18	8	f
5251	5	257	Atlanta Falcons	10	2026-01-01 19:25:50.595658	18	0	f
5252	5	258	Buffalo Bills	16	2026-01-01 19:25:50.59719	18	16	f
5253	5	259	Chicago Bears	13	2026-01-01 19:25:50.598327	18	0	f
5254	5	260	Cincinnati Bengals	4	2026-01-01 19:25:50.599367	18	0	f
5255	5	261	Denver Broncos	15	2026-01-01 19:25:50.600381	18	15	f
5256	5	262	Kansas City Chiefs	5	2026-01-01 19:25:50.601412	18	0	f
5257	5	263	Los Angeles Rams	14	2026-01-01 19:25:50.602477	18	14	f
5258	5	264	Minnesota Vikings	1	2026-01-01 19:25:50.603487	18	1	f
5259	5	265	Miami Dolphins	11	2026-01-01 19:25:50.604497	18	0	f
5260	5	266	Dallas Cowboys	2	2026-01-01 19:25:50.605497	18	0	f
5261	5	267	Washington Commanders	12	2026-01-01 19:25:50.606488	18	12	f
5262	5	268	Baltimore Ravens	7	2026-01-01 19:25:50.60754	18	0	f
5263	5	269	Seattle Seahawks	3	2026-01-01 19:25:50.608521	18	3	f
5264	5	270	Tampa Bay Buccaneers	6	2026-01-01 19:25:50.609514	18	0	f
5265	5	271	Jacksonville Jaguars	8	2026-01-01 19:25:50.61049	18	8	f
5266	5	272	Houston Texans	9	2026-01-01 19:25:50.611466	18	0	f
5267	4	257	New Orleans Saints	14	2026-01-01 21:03:22.417598	18	14	f
5268	4	258	Buffalo Bills	6	2026-01-01 21:03:22.418777	18	6	f
5269	4	259	Detroit Lions	7	2026-01-01 21:03:22.419707	18	7	f
5270	4	260	Cincinnati Bengals	13	2026-01-01 21:03:22.42054	18	0	f
5271	4	261	Denver Broncos	1	2026-01-01 21:03:22.421488	18	1	f
5272	4	262	Kansas City Chiefs	8	2026-01-01 21:03:22.422348	18	0	f
5273	4	263	Los Angeles Rams	5	2026-01-01 21:03:22.42319	18	5	f
5274	4	264	Green Bay Packers	12	2026-01-01 21:03:22.424021	18	0	f
5275	4	265	Miami Dolphins	4	2026-01-01 21:03:22.424858	18	0	f
5276	4	266	Dallas Cowboys	11	2026-01-01 21:03:22.425701	18	0	f
5277	4	267	Philadelphia Eagles	3	2026-01-01 21:03:22.426539	18	0	f
5278	4	268	Baltimore Ravens	2	2026-01-01 21:03:22.42741	18	0	f
5279	4	269	San Francisco 49ers	15	2026-01-01 21:03:22.428218	18	0	f
5280	4	270	Tampa Bay Buccaneers	16	2026-01-01 21:03:22.429054	18	0	f
5281	4	271	Tennessee Titans	10	2026-01-01 21:03:22.429933	18	0	f
5282	4	272	Indianapolis Colts	9	2026-01-01 21:03:22.430613	18	9	f
5283	8	257	New Orleans Saints	13	2026-01-01 22:13:55.746157	18	13	f
5284	8	258	Buffalo Bills	14	2026-01-01 22:13:55.747955	18	14	f
5285	8	259	Chicago Bears	11	2026-01-01 22:13:55.749239	18	0	f
5286	8	260	Cleveland Browns	3	2026-01-01 22:13:55.750424	18	3	f
5287	8	261	Los Angeles Chargers	6	2026-01-01 22:13:55.751525	18	0	f
5288	8	262	Kansas City Chiefs	2	2026-01-01 22:13:55.752585	18	0	f
5289	8	263	Los Angeles Rams	12	2026-01-01 22:13:55.75365	18	12	f
5290	8	264	Green Bay Packers	8	2026-01-01 22:13:55.754677	18	0	f
5291	8	265	New England Patriots	4	2026-01-01 22:13:55.75571	18	4	f
5292	8	266	Dallas Cowboys	16	2026-01-01 22:13:55.756772	18	0	f
5293	8	267	Philadelphia Eagles	9	2026-01-01 22:13:55.75782	18	0	f
5294	8	268	Pittsburgh Steelers	5	2026-01-01 22:13:55.758846	18	5	f
5295	8	269	San Francisco 49ers	7	2026-01-01 22:13:55.759865	18	0	f
5296	8	270	Carolina Panthers	10	2026-01-01 22:13:55.760885	18	10	f
5297	8	271	Jacksonville Jaguars	1	2026-01-01 22:13:55.761914	18	1	f
5298	8	272	Houston Texans	15	2026-01-01 22:13:55.763019	18	0	f
5299	20	259	Detroit Lions	3	2026-01-04 06:00:22.348548	18	3	f
5300	20	261	Los Angeles Chargers	15	2026-01-04 06:00:22.351386	18	0	f
5301	20	262	Kansas City Chiefs	4	2026-01-04 06:00:22.352748	18	0	f
5302	20	267	Philadelphia Eagles	6	2026-01-04 06:00:22.359096	18	0	f
5303	20	268	Pittsburgh Steelers	14	2026-01-04 06:00:22.3603	18	14	f
5304	20	258	Buffalo Bills	13	2026-01-04 06:00:22.347037	18	13	f
5305	20	257	New Orleans Saints	11	2026-01-04 06:00:22.342941	18	11	f
5306	20	265	Miami Dolphins	10	2026-01-04 06:00:22.356634	18	0	f
5307	20	264	Minnesota Vikings	9	2026-01-04 06:00:22.355355	18	9	f
5308	2	257	Atlanta Falcons	12	2026-01-04 14:24:46.988313	18	0	f
5309	2	258	New York Jets	16	2026-01-04 21:04:34.139742	18	0	f
5310	2	259	Chicago Bears	4	2026-01-04 21:04:34.141458	18	0	f
5311	2	260	Cleveland Browns	1	2026-01-04 14:24:46.994379	18	1	f
5312	2	261	Denver Broncos	8	2026-01-04 21:04:34.14352	18	8	f
5313	2	262	Kansas City Chiefs	6	2026-01-04 21:04:34.14485	18	0	f
5314	2	263	Arizona Cardinals	5	2026-01-04 21:04:34.146149	18	0	f
5315	2	264	Minnesota Vikings	15	2026-01-04 14:24:46.999447	18	15	f
5316	2	265	New England Patriots	13	2026-01-04 21:04:34.147411	18	13	f
5317	2	266	Dallas Cowboys	11	2026-01-04 14:24:47.002281	18	0	f
5318	2	267	Philadelphia Eagles	14	2026-01-04 21:04:34.148519	18	0	f
5319	2	268	Pittsburgh Steelers	7	2026-01-04 21:04:34.149678	18	7	f
5320	2	269	San Francisco 49ers	9	2026-01-02 13:47:34.399156	18	0	f
5321	2	270	Tampa Bay Buccaneers	10	2026-01-02 13:47:34.400207	18	0	f
5322	2	271	Tennessee Titans	2	2026-01-04 14:24:47.005209	18	0	f
5323	2	272	Indianapolis Colts	3	2026-01-04 14:24:47.006044	18	3	f
5324	16	257	Atlanta Falcons	13	2026-01-02 16:10:42.333115	18	0	f
5325	16	258	Buffalo Bills	8	2026-01-02 16:10:42.334258	18	8	f
5326	16	259	Chicago Bears	15	2026-01-02 16:10:42.335195	18	0	f
5327	16	260	Cincinnati Bengals	5	2026-01-02 16:10:42.336128	18	0	f
5328	16	261	Denver Broncos	1	2026-01-02 16:10:42.336996	18	1	f
5329	16	262	Las Vegas Raiders	10	2026-01-02 16:10:42.337849	18	10	f
5330	16	263	Los Angeles Rams	6	2026-01-02 16:10:42.338635	18	6	f
5331	16	264	Minnesota Vikings	9	2026-01-02 16:10:42.339412	18	9	f
5332	16	265	New England Patriots	3	2026-01-02 16:10:42.340179	18	3	f
5333	16	266	New York Giants	11	2026-01-02 16:10:42.341153	18	11	f
5334	16	267	Philadelphia Eagles	7	2026-01-02 16:10:42.342218	18	0	f
5335	16	268	Pittsburgh Steelers	12	2026-01-02 16:10:42.343185	18	12	f
5336	16	269	San Francisco 49ers	16	2026-01-02 16:10:42.344103	18	0	f
5337	16	270	Tampa Bay Buccaneers	14	2026-01-02 16:10:42.344959	18	0	f
5338	16	271	Jacksonville Jaguars	2	2026-01-02 16:10:42.345923	18	2	f
5339	16	272	Houston Texans	4	2026-01-02 16:10:42.346962	18	0	f
5340	20	263	Arizona Cardinals	2	2026-01-04 06:00:22.354047	18	0	f
5341	22	257	Atlanta Falcons	5	2026-01-02 19:54:18.770889	18	0	f
5342	22	258	Buffalo Bills	16	2026-01-02 19:54:18.772531	18	16	f
5343	22	259	Chicago Bears	12	2026-01-02 19:54:18.773791	18	0	f
5344	22	260	Cleveland Browns	6	2026-01-02 19:54:18.775058	18	6	f
5345	22	261	Denver Broncos	11	2026-01-02 19:54:18.776359	18	11	f
5346	22	262	Kansas City Chiefs	1	2026-01-02 19:54:18.777576	18	0	f
5347	22	263	Arizona Cardinals	9	2026-01-02 19:54:18.778768	18	0	f
5348	22	264	Green Bay Packers	7	2026-01-02 19:54:18.779881	18	0	f
5349	22	265	Miami Dolphins	13	2026-01-02 19:54:18.780962	18	0	f
5350	22	266	New York Giants	8	2026-01-02 19:54:18.782689	18	8	f
5351	22	267	Washington Commanders	14	2026-01-02 19:54:18.783901	18	14	f
5352	22	268	Baltimore Ravens	2	2026-01-02 19:54:18.785088	18	0	f
5353	22	269	San Francisco 49ers	4	2026-01-02 19:54:18.786337	18	0	f
5354	22	270	Tampa Bay Buccaneers	3	2026-01-02 19:54:18.787548	18	0	f
5355	22	271	Tennessee Titans	15	2026-01-02 19:54:18.788855	18	0	f
5356	22	272	Houston Texans	10	2026-01-02 19:54:18.790132	18	0	f
5357	17	257	New Orleans Saints	1	2026-01-04 17:32:58.411436	18	1	f
5358	17	258	Buffalo Bills	5	2026-01-04 17:32:58.412752	18	5	f
5359	17	259	Chicago Bears	14	2026-01-04 17:32:58.413758	18	0	f
5360	17	260	Cleveland Browns	10	2026-01-04 17:32:58.414667	18	10	f
5361	17	261	Denver Broncos	7	2026-01-04 17:32:58.415699	18	7	f
5362	17	263	Los Angeles Rams	8	2026-01-04 17:32:58.417732	18	8	f
5363	17	264	Minnesota Vikings	13	2026-01-04 17:32:58.418634	18	13	f
5364	17	265	Miami Dolphins	6	2026-01-04 17:32:58.419459	18	0	f
5365	17	266	New York Giants	12	2026-01-04 17:32:58.420279	18	12	f
5366	17	267	Washington Commanders	4	2026-01-04 17:32:58.421096	18	4	f
5367	17	268	Baltimore Ravens	2	2026-01-04 21:36:52.997133	18	0	f
5368	17	269	Seattle Seahawks	15	2026-01-03 20:04:18.894079	18	15	f
5369	17	270	Tampa Bay Buccaneers	16	2026-01-03 20:04:18.894951	18	0	f
5370	17	271	Tennessee Titans	3	2026-01-04 17:32:58.422664	18	0	f
5371	17	272	Houston Texans	11	2026-01-04 17:32:58.42345	18	0	f
5372	12	260	Cincinnati Bengals	7	2026-01-03 04:36:53.067489	18	0	f
5373	12	262	Kansas City Chiefs	3	2026-01-03 04:36:53.069943	18	0	f
5374	12	263	Los Angeles Rams	2	2026-01-03 04:36:53.071157	18	2	f
5375	12	267	Philadelphia Eagles	4	2026-01-03 04:36:53.075395	18	0	f
5376	12	271	Tennessee Titans	1	2026-01-03 04:36:53.079842	18	0	f
5377	18	269	San Francisco 49ers	16	2026-01-03 06:44:44.369318	18	0	f
5378	18	270	Tampa Bay Buccaneers	15	2026-01-03 06:44:44.370761	18	0	f
5379	9	257	Atlanta Falcons	3	2026-01-03 14:38:23.265957	18	0	f
5380	9	258	Buffalo Bills	9	2026-01-03 14:38:23.26743	18	9	f
5381	9	259	Chicago Bears	10	2026-01-03 14:38:23.268533	18	0	f
5382	9	260	Cincinnati Bengals	4	2026-01-03 14:38:23.269621	18	0	f
5383	9	261	Denver Broncos	11	2026-01-03 14:38:23.270696	18	11	f
5384	9	262	Las Vegas Raiders	12	2026-01-03 14:38:23.271788	18	12	f
5385	9	263	Los Angeles Rams	13	2026-01-03 14:38:23.272855	18	13	f
5386	9	264	Minnesota Vikings	5	2026-01-03 14:38:23.273926	18	5	f
5387	9	265	New England Patriots	14	2026-01-03 14:38:23.274985	18	14	f
5388	9	266	New York Giants	6	2026-01-03 14:38:23.276045	18	6	f
5389	9	267	Philadelphia Eagles	15	2026-01-03 14:38:23.277109	18	0	f
5390	9	268	Pittsburgh Steelers	16	2026-01-03 14:38:23.278179	18	16	f
5391	9	269	San Francisco 49ers	2	2026-01-03 14:38:23.279237	18	0	f
5392	9	270	Tampa Bay Buccaneers	1	2026-01-03 14:38:23.280625	18	0	f
5393	9	271	Jacksonville Jaguars	7	2026-01-03 14:38:23.281756	18	7	f
5394	9	272	Houston Texans	8	2026-01-03 14:38:23.282665	18	0	f
5395	15	269	San Francisco 49ers	12	2026-01-03 20:06:26.415398	18	0	f
5396	15	270	Carolina Panthers	7	2026-01-03 20:06:26.416417	18	7	f
5397	19	269	Seattle Seahawks	16	2026-01-04 00:24:14.540865	18	16	f
5398	19	270	Tampa Bay Buccaneers	5	2026-01-03 20:22:14.306157	18	0	f
5399	10	269	San Francisco 49ers	15	2026-01-03 21:15:50.471814	18	0	f
5400	10	270	Carolina Panthers	13	2026-01-03 21:15:50.473094	18	13	f
5401	20	271	Jacksonville Jaguars	8	2026-01-04 06:00:22.36337	18	8	f
5402	20	272	Indianapolis Colts	7	2026-01-04 06:00:22.364697	18	7	f
5403	15	257	New Orleans Saints	13	2026-01-04 15:32:55.42594	18	13	f
5404	15	258	Buffalo Bills	8	2026-01-04 15:32:55.427904	18	8	f
5405	15	259	Chicago Bears	15	2026-01-04 15:32:55.428793	18	0	f
5406	15	260	Cincinnati Bengals	1	2026-01-04 15:32:55.429762	18	0	f
5407	15	261	Denver Broncos	16	2026-01-04 15:32:55.431079	18	16	f
5408	15	262	Kansas City Chiefs	5	2026-01-04 15:32:55.432289	18	0	f
5409	15	263	Los Angeles Rams	6	2026-01-04 15:32:55.433578	18	6	f
5410	15	264	Minnesota Vikings	11	2026-01-04 15:32:55.434881	18	11	f
5411	15	265	Miami Dolphins	4	2026-01-04 15:32:55.436193	18	0	f
5412	15	266	Dallas Cowboys	14	2026-01-04 15:32:55.437502	18	0	f
5413	15	267	Philadelphia Eagles	3	2026-01-04 15:32:55.438768	18	0	f
5414	15	268	Pittsburgh Steelers	10	2026-01-04 15:32:55.440082	18	10	f
5415	15	271	Jacksonville Jaguars	2	2026-01-04 15:32:55.441365	18	2	f
5416	15	272	Houston Texans	9	2026-01-04 15:32:55.442396	18	0	f
5417	19	257	Atlanta Falcons	7	2026-01-04 16:39:29.603863	18	0	f
5418	19	258	New York Jets	12	2026-01-04 16:39:29.60545	18	0	f
5419	19	259	Chicago Bears	11	2026-01-04 16:39:29.606859	18	0	f
5420	19	260	Cincinnati Bengals	2	2026-01-04 16:39:29.608221	18	0	f
5421	19	261	Denver Broncos	15	2026-01-04 16:39:29.609605	18	15	f
5422	19	262	Kansas City Chiefs	10	2026-01-04 16:39:29.610773	18	0	f
5423	19	263	Los Angeles Rams	14	2026-01-04 16:39:29.611889	18	14	f
5424	19	264	Minnesota Vikings	8	2026-01-04 16:39:29.612717	18	8	f
5425	19	265	New England Patriots	9	2026-01-04 16:39:29.613521	18	9	f
5426	19	266	Dallas Cowboys	3	2026-01-04 16:39:29.6143	18	0	f
5427	19	267	Washington Commanders	13	2026-01-04 16:39:29.615099	18	13	f
5428	19	268	Baltimore Ravens	1	2026-01-04 16:39:29.615846	18	0	f
5429	19	271	Tennessee Titans	4	2026-01-04 16:39:29.616637	18	0	f
5430	19	272	Indianapolis Colts	6	2026-01-04 16:39:29.617425	18	6	f
5431	10	257	New Orleans Saints	4	2026-01-04 17:59:58.705051	18	4	f
5432	10	258	Buffalo Bills	8	2026-01-04 17:59:58.706476	18	8	f
5433	10	259	Chicago Bears	6	2026-01-04 17:59:58.707592	18	0	f
5434	10	260	Cincinnati Bengals	9	2026-01-04 17:59:58.708672	18	0	f
5435	10	261	Denver Broncos	16	2026-01-04 17:59:58.709677	18	16	f
5436	10	262	Kansas City Chiefs	12	2026-01-04 17:59:58.710653	18	0	f
5437	10	263	Los Angeles Rams	11	2026-01-04 17:59:58.711629	18	11	f
5438	10	264	Minnesota Vikings	3	2026-01-04 17:59:58.712615	18	3	f
5439	10	265	New England Patriots	10	2026-01-04 17:59:58.71359	18	10	f
5440	10	266	Dallas Cowboys	5	2026-01-04 17:59:58.714576	18	0	f
5441	10	267	Washington Commanders	2	2026-01-04 17:59:58.715547	18	2	f
5442	10	268	Pittsburgh Steelers	14	2026-01-04 17:59:58.716557	18	14	f
5443	10	271	Tennessee Titans	1	2026-01-04 17:59:58.717607	18	0	f
5444	10	272	Houston Texans	7	2026-01-04 17:59:58.718596	18	0	f
5445	18	257	New Orleans Saints	1	2026-01-04 17:27:06.108471	18	1	f
5446	18	258	Buffalo Bills	8	2026-01-04 17:27:06.109754	18	8	f
5447	18	259	Detroit Lions	7	2026-01-04 17:27:06.110725	18	7	f
5448	18	260	Cleveland Browns	13	2026-01-04 17:27:06.111789	18	13	f
5449	18	261	Los Angeles Chargers	6	2026-01-04 17:27:06.112673	18	0	f
5450	18	262	Kansas City Chiefs	5	2026-01-04 17:27:06.113518	18	0	f
5451	18	263	Los Angeles Rams	4	2026-01-04 17:27:06.114396	18	4	f
5452	18	264	Minnesota Vikings	12	2026-01-04 17:27:06.115268	18	12	f
5453	18	265	New England Patriots	3	2026-01-04 17:27:06.116081	18	3	f
5454	18	266	Dallas Cowboys	11	2026-01-04 17:27:06.11687	18	0	f
5455	18	267	Washington Commanders	2	2026-01-04 17:27:06.117827	18	2	f
5456	18	268	Baltimore Ravens	14	2026-01-04 17:27:06.118883	18	0	f
5457	18	271	Tennessee Titans	10	2026-01-04 17:27:06.119875	18	0	f
5458	18	272	Indianapolis Colts	9	2026-01-04 17:27:06.120704	18	9	f
5459	17	262	Kansas City Chiefs	9	2026-01-04 17:32:58.416574	18	0	f
5467	2	296	Green Bay Packers	2	2026-01-08 18:43:47.318182	1	0	f
5469	2	298	Philadelphia Eagles	4	2026-01-08 18:43:47.333327	1	0	f
5472	26	295	Los Angeles Rams	3	2026-01-10 00:10:55.421059	1	0	f
5478	10	295	Los Angeles Rams	2	2026-01-10 11:26:12.846519	1	0	f
5480	10	297	Jacksonville Jaguars	4	2026-01-10 11:26:12.855188	1	0	f
5481	10	298	Philadelphia Eagles	3	2026-01-10 11:26:12.858872	1	0	f
5483	10	300	Pittsburgh Steelers	1	2026-01-10 11:26:12.865743	1	0	f
5496	1	301	Denver Broncos	4	2026-01-13 17:54:52.684549	2	4	f
5497	1	303	Seattle Seahawks	3	2026-01-13 17:54:52.832629	2	3	f
5498	1	302	New England Patriots	2	2026-01-13 17:54:52.976608	2	2	f
5500	2	301	Denver Broncos	4	2026-01-17 20:38:25.005028	2	4	f
5503	2	304	Chicago Bears	1	2026-01-17 20:38:25.017268	2	1	f
5465	1	300	Houston Texans	4	2026-01-10 13:34:23.855182	1	4	f
5460	1	295	Los Angeles Rams	2	2026-01-10 13:34:23.130561	1	0	f
5461	1	296	Green Bay Packers	1	2026-01-10 13:34:23.280755	1	0	f
5471	2	300	Houston Texans	6	2026-01-08 18:43:47.351303	1	6	f
5463	1	298	Philadelphia Eagles	3	2026-01-10 13:34:23.570792	1	0	f
5477	26	300	Houston Texans	4	2026-01-10 00:10:55.438308	1	4	f
5486	17	297	Jacksonville Jaguars	3	2026-01-10 13:35:10.335749	1	0	f
5487	17	298	Philadelphia Eagles	4	2026-01-10 13:35:10.502107	1	0	f
5488	17	299	Los Angeles Chargers	5	2026-01-10 13:35:10.647375	1	0	f
5462	1	297	Buffalo Bills	5	2026-01-10 13:34:23.419539	1	5	f
5464	1	299	New England Patriots	6	2026-01-10 13:34:23.718051	1	6	f
5466	2	295	Carolina Panthers	1	2026-01-08 18:43:47.299195	1	1	f
5468	2	297	Buffalo Bills	3	2026-01-08 18:43:47.323337	1	3	f
5470	2	299	New England Patriots	5	2026-01-08 18:43:47.344935	1	5	f
5473	26	296	Chicago Bears	5	2026-01-10 00:10:55.424838	1	5	f
5474	26	297	Buffalo Bills	1	2026-01-10 00:10:55.428101	1	1	f
5475	26	298	San Francisco 49ers	2	2026-01-10 00:10:55.431754	1	2	f
5476	26	299	New England Patriots	6	2026-01-10 00:10:55.434989	1	6	f
5479	10	296	Chicago Bears	6	2026-01-10 11:26:12.850878	1	6	f
5482	10	299	New England Patriots	5	2026-01-10 11:26:12.862311	1	5	f
5484	17	295	Carolina Panthers	1	2026-01-10 13:35:10.011437	1	1	f
5485	17	296	Chicago Bears	2	2026-01-10 13:35:10.165477	1	2	f
5490	15	295	Carolina Panthers	6	2026-01-10 14:47:23.007857	1	6	f
5491	15	296	Chicago Bears	5	2026-01-10 14:47:23.012965	1	5	f
5492	15	297	Buffalo Bills	4	2026-01-11 15:15:44.900261	1	4	f
5493	15	298	San Francisco 49ers	3	2026-01-11 15:15:44.904712	1	3	f
5494	15	299	New England Patriots	2	2026-01-11 15:15:44.908398	1	2	f
5499	1	304	Los Angeles Rams	1	2026-01-13 17:54:53.119818	2	0	f
5501	2	303	San Francisco 49ers	2	2026-01-17 20:38:25.010067	2	0	f
5502	2	302	Houston Texans	3	2026-01-17 20:38:25.013849	2	0	f
5504	1	305	Denver Broncos	2	2026-01-19 16:02:31.393187	3	0	f
5505	1	306	Seattle Seahawks	1	2026-01-19 16:02:31.397636	3	0	f
5489	17	300	Houston Texans	6	2026-01-10 13:35:10.786992	1	6	f
5495	15	300	Houston Texans	1	2026-01-11 15:15:44.911845	1	1	f
\.


--
-- Data for Name: settings; Type: TABLE DATA; Schema: public; Owner: pickarena_prod_db_user
--

COPY public.settings (id, current_week, season_year, season_type, season_locked) FROM stdin;
1	3	2025	POST	t
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: pickarena_prod_db_user
--

COPY public."user" (id, username, full_name, email, phone, favorite_team, password, is_admin, sms_opt_in) FROM stdin;
1	barnes	Steven Barnes	stevenbarnes50@gmail.com	+14805899081	Cardinals	pbkdf2:sha256:600000$h629F9gjNCNMvkTH$f59b2aa575711f4dbaedcceca8466ee47a797d83b07b50f0f7973a1416a7f8a8	t	t
2	catrina		mcdonaldfam_57@yahoo.com	+17193393145		pbkdf2:sha256:600000$njw7G22Ce1tLic8B$3c9667ea3dcd2dfb3e37241081adb428792a8ec91c588b5fead23b5f67b82efd	t	t
4	Robert	Robert McDonald	rmcdonald5833@gmail.com	9283224408	Da Broncos	pbkdf2:sha256:600000$kwpRyTlzvXNbLDQu$23479b823a77a3bd386ae9701b027521d385e711eeabb3a76a02e03729efa765	f	f
5	Jaciemcdonald1	\N	jaciemcdonald1@gmail.com	\N	\N	scrypt:32768:8:1$i14dHxGZX2o73BBd$5c36f6c31aecc205ebdac6c93889793e091dee0b1c8b1a3ae70a9a09fdf01c936802ec1e3c249c42090c6a7cb157430c1b7a1639fc528b9278c61b9cc4d6ca09	f	f
8	Keagan McDonald24	Keagan McDonald	nexus242426@gmail.com	5205539155	Patriots	scrypt:32768:8:1$3PTIGsDnWWqsNbX8$35c609f0ef19f3727278ed35dd06198fa2e45d170cecc09b1bdcf676f6b900161b4a95ab821f404c218b64e87d3c976154d06df52ac720ba1421604052481bc5	f	f
9	Jimmie	Jimmie Smith	docjimbo59@gmail.com	+19283227039	Cardinals	pbkdf2:sha256:600000$UgxqOk3KvNeBs6bi$34304076c9d12382266172e3705921dd670ff096d1b04ad4e0dd4f599d14eac4	f	t
10	Jason	\N	mojomc0313@gmail.com	\N	\N	pbkdf2:sha256:600000$FUhuKPIJSU720sq9$30f137c8895476c3c0c9c163f21eb1186379c2a67c8102c4f1a7a0704859969f	f	f
12	MikeM	Michael McDonald	mikemcd34@gmail.com	7199648981		pbkdf2:sha256:600000$z6ngJ6PCRDy21pBh$4fbdc1d0e398deb6d22d0d405a28e13ee2e0ae33f3f6548ee02e1cc09611d4d4	f	f
13	Evan	\N	mountainflame09@gmail.com	\N	\N	scrypt:32768:8:1$XK6HhzLxJGbfJEWp$6d443218158571352d04bb7c7d83007e98998f48a2da9fcd3895c0653f74797cd6bd19a154462b0a13149be3af2a5e15589bcbcdc3012ee3623383d1960347a6	f	f
14	DeanRutherford	Dean Rutherford	nobabiesallowed7@gmail.com	9513759908	Oklahoma Sooners	pbkdf2:sha256:50000$04FwKzsFStLLEiQW$d49cbcbbcc4553d344dc6918de9c74809c1e5f42c612259e8f92f61731fcd067	f	f
15	Peyton	\N	mcdonaldpeyton83@gmail.com	\N	\N	pbkdf2:sha256:50000$pmgtaE3hTwnx5ZZs$1a67bd71667abea4a740fab6730b31f0d93a66e1922a39b0eb383beec7f8e23f	f	f
16	Peggy	\N	pegkester@gmail.com	\N	\N	scrypt:32768:8:1$TNnKui6ZEx7ILQDE$4ef04f2c64861a34a00d8f8ab6e30a073618c15f637a8bf13fc3fdd512c95846619c387336ab78a747cb3183b38986567a24c8f38c7740a143c7b54d456c2412	f	f
17	Chad		lad9176@gmail.com	+17196596034		pbkdf2:sha256:50000$z9oRKpPfTTYVvOMF$f771736d5c21e9c1e66562bc4fbf0f61ae64c6fd15cc21e65ae6a11bf9ccf654	f	t
18	Joel23	\N	joelheid2340@yahoo.com	\N	\N	pbkdf2:sha256:50000$Bk0Dte79P0MmKIRi$b04f474448206cd438a9f6510147145a004b3d7a3236c24680f53e81475e457b	f	f
19	RGlovan	\N	rebeccaglovan@gmail.com	\N	\N	pbkdf2:sha256:50000$0vXs3esf2MeeU8mn$4c4d04d9e567670f1f0f893b3a47eed537cb2390964c5928832afbee238863c6	f	f
20	jmcguire	\N	prodigy_11@live.com	\N	\N	pbkdf2:sha256:50000$pc6xYVFzuKNWr4PP$977bc2213f463e0fc9b4ba791d6a45d62b154e64761ee467967c7116e70c4ada	f	f
21	ChrisMo	\N	chrismo4531@gmail.com	\N	\N	pbkdf2:sha256:50000$6ZXOs8z26aW7FsYY$dd919389e84f43d0448a2fd670f08c57181fadc9ac77a5071e53bdcb516c4968	f	f
22	DB4L	Shane Vasten	svasten@yahoo.com	4356505618	Denver Broncos 4 Life	pbkdf2:sha256:50000$yUjMrqzsSqqmKZsP$fc92b4aae11c3f95749eab3e444a5783d175d33c0db703d2a336824eb731440c	f	f
23	Djridgway84	\N	djridgway84@icloud.com	\N	\N	scrypt:32768:8:1$Zz8QaGkmdg31VeDE$010ea4196bfbf6623cd35d4133ae3454602faeef82e89fa07afe7548c9cee7e3f557f2a71ac08a89b3251d69e47529446e2aea44ed52cb3222b5f9a3dc3e85c7	f	f
24	MarkAguilera	\N	markaaguilera21@gmail.com	\N	\N	pbkdf2:sha256:50000$hKfWz9A0UWPRLyxu$1511ef0bb9851d3714d3d1a91d1ac74fccd87f63006159a0bf05cdd41540d2bc	f	f
25	Gregg	\N	hotpantsmclovinmortymiranda@gmail.com	\N	\N	pbkdf2:sha256:50000$K5U9Vr0zrnqopYZW$4420bfe019e933ededdea5424bd07fdbd351b32cca40ff1ec7b14d706cd32b92	f	f
26	AidanLuna	\N	aidanluna25@gmail.com	\N	\N	pbkdf2:sha256:50000$5mR8kej3t2K0Pkrf$971c03430a926b8d041622d8ed34ff19143cdc86a52662255fd236411f8d0022	f	f
\.


--
-- Data for Name: user_score; Type: TABLE DATA; Schema: public; Owner: pickarena_prod_db_user
--

COPY public.user_score (id, user_id, week, score, calculated_at, season_year, season_type) FROM stdin;
20	20	1	109	2026-01-12 22:55:00.350322	2025	REG
366	26	1	14	2026-01-12 22:55:00.356601	2025	REG
367	1	2	9	2026-01-19 19:30:00.279532	2025	POST
368	2	2	5	2026-01-19 19:30:00.28266	2025	POST
369	2	1	15	2026-01-19 18:29:51.497024	2025	POST
370	26	1	18	2026-01-19 18:29:51.501603	2025	POST
371	10	1	11	2026-01-19 18:29:51.504795	2025	POST
372	1	1	15	2026-01-19 18:29:51.507771	2025	POST
373	17	1	9	2026-01-19 18:29:51.510681	2025	POST
374	15	1	21	2026-01-19 18:29:51.513911	2025	POST
37	19	2	84	2026-01-05 14:41:40.732625	2025	REG
38	26	2	80	2026-01-05 14:41:40.732629	2025	REG
39	23	2	52	2026-01-05 14:41:40.732633	2025	REG
40	16	2	74	2026-01-05 14:41:40.732637	2025	REG
41	24	2	84	2026-01-05 14:41:40.732642	2025	REG
42	20	2	56	2026-01-05 14:41:40.732577	2025	REG
43	14	3	63	2026-01-05 14:41:40.814345	2025	REG
44	2	3	84	2026-01-05 14:41:40.814349	2025	REG
45	20	3	65	2026-01-05 14:41:40.814352	2025	REG
46	1	3	65	2026-01-05 14:41:40.814354	2025	REG
47	12	3	58	2026-01-05 14:41:40.814357	2025	REG
48	13	3	31	2026-01-05 14:41:40.814359	2025	REG
49	9	3	61	2026-01-05 14:41:40.814361	2025	REG
50	18	3	67	2026-01-05 14:41:40.814364	2025	REG
51	8	3	47	2026-01-05 14:41:40.814366	2025	REG
52	21	3	66	2026-01-05 14:41:40.814368	2025	REG
53	24	3	63	2026-01-05 14:41:40.81437	2025	REG
54	22	3	50	2026-01-05 14:41:40.814372	2025	REG
55	4	3	82	2026-01-05 14:41:40.814375	2025	REG
56	10	3	71	2026-01-05 14:41:40.814377	2025	REG
57	26	3	56	2026-01-05 14:41:40.814379	2025	REG
58	16	3	86	2026-01-05 14:41:40.814381	2025	REG
59	23	3	52	2026-01-05 14:41:40.814383	2025	REG
60	17	3	54	2026-01-05 14:41:40.814385	2025	REG
61	19	3	48	2026-01-05 14:41:40.814387	2025	REG
62	15	3	60	2026-01-05 14:41:40.814389	2025	REG
63	25	3	60	2026-01-05 14:41:40.814391	2025	REG
64	5	3	54	2026-01-05 14:41:40.814394	2025	REG
65	1	4	65	2026-01-05 14:41:40.890455	2025	REG
66	2	4	64	2026-01-05 14:41:40.89046	2025	REG
67	14	4	82	2026-01-05 14:41:40.890463	2025	REG
68	24	4	47	2026-01-05 14:41:40.890465	2025	REG
69	12	4	49	2026-01-05 14:41:40.890467	2025	REG
70	20	4	61	2026-01-05 14:41:40.890469	2025	REG
71	9	4	46	2026-01-05 14:41:40.890472	2025	REG
72	25	4	70	2026-01-05 14:41:40.890474	2025	REG
73	8	4	39	2026-01-05 14:41:40.890476	2025	REG
74	5	4	42	2026-01-05 14:41:40.890479	2025	REG
75	22	4	64	2026-01-05 14:41:40.890481	2025	REG
76	21	4	65	2026-01-05 14:41:40.890483	2025	REG
77	26	4	53	2026-01-05 14:41:40.890485	2025	REG
78	17	4	38	2026-01-05 14:41:40.890487	2025	REG
79	13	4	48	2026-01-05 14:41:40.89049	2025	REG
80	10	4	80	2026-01-05 14:41:40.890492	2025	REG
81	4	4	48	2026-01-05 14:41:40.890494	2025	REG
82	19	4	30	2026-01-05 14:41:40.890496	2025	REG
83	15	4	68	2026-01-05 14:41:40.890499	2025	REG
84	18	4	65	2026-01-05 14:41:40.890501	2025	REG
85	23	4	59	2026-01-05 14:41:40.890503	2025	REG
86	16	4	46	2026-01-05 14:41:40.890505	2025	REG
87	20	5	53	2026-01-05 14:41:40.931339	2025	REG
88	14	5	54	2026-01-05 14:41:40.931344	2025	REG
21	25	1	55	2026-01-12 22:55:00.353173	2025	REG
22	2	2	24	2026-01-05 14:41:40.73255	2025	REG
23	1	2	64	2026-01-05 14:41:40.732559	2025	REG
24	13	2	44	2026-01-05 14:41:40.732564	2025	REG
25	14	2	76	2026-01-05 14:41:40.732568	2025	REG
26	12	2	77	2026-01-05 14:41:40.732572	2025	REG
27	10	2	65	2026-01-05 14:41:40.732581	2025	REG
28	9	2	70	2026-01-05 14:41:40.732586	2025	REG
29	21	2	71	2026-01-05 14:41:40.73259	2025	REG
30	8	2	104	2026-01-05 14:41:40.732595	2025	REG
31	22	2	87	2026-01-05 14:41:40.732599	2025	REG
32	18	2	62	2026-01-05 14:41:40.732603	2025	REG
33	17	2	59	2026-01-05 14:41:40.732607	2025	REG
34	5	2	76	2026-01-05 14:41:40.732612	2025	REG
35	4	2	66	2026-01-05 14:41:40.732616	2025	REG
36	15	2	70	2026-01-05 14:41:40.73262	2025	REG
273	14	14	48	2026-01-05 14:41:41.631802	2025	REG
274	2	14	38	2026-01-05 14:41:41.631807	2025	REG
275	20	14	40	2026-01-05 14:41:41.631811	2025	REG
276	13	14	47	2026-01-05 14:41:41.631816	2025	REG
277	8	14	70	2026-01-05 14:41:41.63182	2025	REG
278	21	14	34	2026-01-05 14:41:41.631825	2025	REG
279	16	14	49	2026-01-05 14:41:41.631829	2025	REG
280	4	14	36	2026-01-05 14:41:41.631834	2025	REG
281	23	14	50	2026-01-05 14:41:41.631839	2025	REG
282	5	14	62	2026-01-05 14:41:41.631844	2025	REG
283	19	14	37	2026-01-05 14:41:41.631849	2025	REG
284	9	14	45	2026-01-05 14:41:41.631854	2025	REG
285	22	14	65	2026-01-05 14:41:41.631859	2025	REG
286	15	14	34	2026-01-05 14:41:41.631864	2025	REG
287	17	14	44	2026-01-05 14:41:41.631869	2025	REG
288	10	14	42	2026-01-05 14:41:41.631873	2025	REG
289	18	14	46	2026-01-05 14:41:41.631878	2025	REG
290	26	14	27	2026-01-05 14:41:41.631883	2025	REG
89	23	5	46	2026-01-05 14:41:40.931346	2025	REG
90	2	5	58	2026-01-05 14:41:40.931348	2025	REG
91	1	5	58	2026-01-05 14:41:40.931351	2025	REG
92	24	5	24	2026-01-05 14:41:40.931353	2025	REG
93	15	5	57	2026-01-05 14:41:40.931355	2025	REG
94	21	5	53	2026-01-05 14:41:40.931357	2025	REG
95	4	5	28	2026-01-05 14:41:40.931359	2025	REG
96	12	5	70	2026-01-05 14:41:40.931361	2025	REG
97	13	5	78	2026-01-05 14:41:40.931363	2025	REG
98	8	5	62	2026-01-05 14:41:40.931366	2025	REG
99	16	5	49	2026-01-05 14:41:40.931368	2025	REG
100	18	5	56	2026-01-05 14:41:40.93137	2025	REG
101	19	5	52	2026-01-05 14:41:40.931373	2025	REG
102	5	5	74	2026-01-05 14:41:40.931375	2025	REG
103	9	5	46	2026-01-05 14:41:40.931377	2025	REG
104	22	5	56	2026-01-05 14:41:40.931379	2025	REG
105	26	5	32	2026-01-05 14:41:40.931381	2025	REG
106	17	5	58	2026-01-05 14:41:40.931383	2025	REG
107	10	5	60	2026-01-05 14:41:40.931385	2025	REG
108	25	5	39	2026-01-05 14:41:40.931387	2025	REG
109	1	6	20	2026-01-05 14:41:41.103512	2025	REG
110	14	6	50	2026-01-05 14:41:41.103518	2025	REG
111	12	6	38	2026-01-05 14:41:41.103522	2025	REG
112	8	6	61	2026-01-05 14:41:41.103543	2025	REG
113	13	6	59	2026-01-05 14:41:41.103547	2025	REG
114	2	6	38	2026-01-05 14:41:41.103551	2025	REG
115	21	6	52	2026-01-05 14:41:41.103554	2025	REG
116	23	6	42	2026-01-05 14:41:41.103557	2025	REG
117	22	6	52	2026-01-05 14:41:41.103561	2025	REG
118	24	6	38	2026-01-05 14:41:41.103564	2025	REG
119	9	6	34	2026-01-05 14:41:41.103567	2025	REG
120	16	6	40	2026-01-05 14:41:41.103571	2025	REG
121	5	6	60	2026-01-05 14:41:41.103574	2025	REG
122	26	6	45	2026-01-05 14:41:41.103577	2025	REG
123	4	6	42	2026-01-05 14:41:41.10358	2025	REG
124	10	6	40	2026-01-05 14:41:41.103584	2025	REG
125	19	6	48	2026-01-05 14:41:41.103587	2025	REG
126	17	6	49	2026-01-05 14:41:41.103591	2025	REG
127	15	6	27	2026-01-05 14:41:41.103594	2025	REG
128	20	6	38	2026-01-05 14:41:41.103597	2025	REG
129	18	6	73	2026-01-05 14:41:41.1036	2025	REG
130	24	7	85	2026-01-05 14:41:41.183325	2025	REG
131	1	7	84	2026-01-05 14:41:41.183331	2025	REG
132	12	7	44	2026-01-05 14:41:41.183333	2025	REG
133	14	7	80	2026-01-05 14:41:41.183336	2025	REG
134	13	7	32	2026-01-05 14:41:41.183341	2025	REG
135	8	7	78	2026-01-05 14:41:41.183345	2025	REG
136	2	7	67	2026-01-05 14:41:41.18335	2025	REG
137	21	7	74	2026-01-05 14:41:41.183354	2025	REG
138	9	7	105	2026-01-05 14:41:41.183358	2025	REG
139	23	7	62	2026-01-05 14:41:41.183363	2025	REG
140	4	7	58	2026-01-05 14:41:41.183367	2025	REG
141	5	7	95	2026-01-05 14:41:41.183372	2025	REG
142	18	7	61	2026-01-05 14:41:41.183376	2025	REG
143	15	7	79	2026-01-05 14:41:41.18338	2025	REG
144	26	7	62	2026-01-05 14:41:41.183385	2025	REG
145	22	7	79	2026-01-05 14:41:41.183387	2025	REG
146	10	7	76	2026-01-05 14:41:41.18339	2025	REG
147	17	7	84	2026-01-05 14:41:41.183392	2025	REG
148	19	7	83	2026-01-05 14:41:41.183394	2025	REG
149	16	7	80	2026-01-05 14:41:41.183397	2025	REG
150	20	7	63	2026-01-05 14:41:41.183399	2025	REG
151	12	8	43	2026-01-05 14:41:41.219725	2025	REG
152	22	8	68	2026-01-05 14:41:41.21973	2025	REG
153	1	8	79	2026-01-05 14:41:41.219733	2025	REG
154	4	8	57	2026-01-05 14:41:41.219735	2025	REG
155	14	8	51	2026-01-05 14:41:41.219746	2025	REG
156	13	8	43	2026-01-05 14:41:41.219748	2025	REG
157	24	8	49	2026-01-05 14:41:41.219751	2025	REG
158	21	8	42	2026-01-05 14:41:41.219753	2025	REG
159	23	8	60	2026-01-05 14:41:41.219755	2025	REG
160	18	8	50	2026-01-05 14:41:41.219757	2025	REG
161	8	8	43	2026-01-05 14:41:41.21976	2025	REG
162	2	8	65	2026-01-05 14:41:41.219762	2025	REG
163	9	8	48	2026-01-05 14:41:41.219765	2025	REG
164	20	8	23	2026-01-05 14:41:41.219767	2025	REG
165	5	8	56	2026-01-05 14:41:41.21977	2025	REG
166	15	8	66	2026-01-05 14:41:41.219772	2025	REG
167	10	8	34	2026-01-05 14:41:41.219774	2025	REG
168	17	8	58	2026-01-05 14:41:41.219777	2025	REG
169	16	8	46	2026-01-05 14:41:41.219779	2025	REG
170	19	8	53	2026-01-05 14:41:41.219781	2025	REG
171	26	8	64	2026-01-05 14:41:41.219783	2025	REG
172	1	9	40	2026-01-05 14:41:41.302707	2025	REG
173	14	9	38	2026-01-05 14:41:41.302715	2025	REG
174	23	9	72	2026-01-05 14:41:41.302719	2025	REG
175	12	9	41	2026-01-05 14:41:41.302723	2025	REG
176	13	9	45	2026-01-05 14:41:41.302726	2025	REG
177	17	9	69	2026-01-05 14:41:41.30273	2025	REG
178	24	9	53	2026-01-05 14:41:41.302734	2025	REG
179	2	9	56	2026-01-05 14:41:41.302738	2025	REG
180	21	9	34	2026-01-05 14:41:41.302741	2025	REG
181	16	9	41	2026-01-05 14:41:41.302745	2025	REG
182	4	9	59	2026-01-05 14:41:41.302749	2025	REG
183	8	9	65	2026-01-05 14:41:41.302753	2025	REG
184	9	9	58	2026-01-05 14:41:41.302757	2025	REG
185	18	9	62	2026-01-05 14:41:41.30276	2025	REG
186	15	9	50	2026-01-05 14:41:41.302764	2025	REG
187	5	9	45	2026-01-05 14:41:41.302768	2025	REG
188	10	9	65	2026-01-05 14:41:41.302772	2025	REG
189	19	9	41	2026-01-05 14:41:41.302776	2025	REG
190	22	9	48	2026-01-05 14:41:41.302779	2025	REG
191	26	9	29	2026-01-05 14:41:41.302783	2025	REG
192	20	9	59	2026-01-05 14:41:41.302786	2025	REG
193	1	10	66	2026-01-05 14:41:41.346883	2025	REG
194	22	10	39	2026-01-05 14:41:41.34689	2025	REG
195	14	10	56	2026-01-05 14:41:41.346895	2025	REG
196	13	10	24	2026-01-05 14:41:41.346898	2025	REG
197	12	10	40	2026-01-05 14:41:41.346902	2025	REG
198	2	10	19	2026-01-05 14:41:41.346906	2025	REG
199	16	10	65	2026-01-05 14:41:41.34691	2025	REG
200	9	10	47	2026-01-05 14:41:41.346913	2025	REG
201	5	10	38	2026-01-05 14:41:41.346917	2025	REG
202	18	10	39	2026-01-05 14:41:41.346921	2025	REG
203	10	10	47	2026-01-05 14:41:41.346925	2025	REG
204	26	10	58	2026-01-05 14:41:41.346929	2025	REG
205	15	10	39	2026-01-05 14:41:41.346932	2025	REG
206	17	10	52	2026-01-05 14:41:41.346936	2025	REG
207	8	10	44	2026-01-05 14:41:41.34694	2025	REG
208	19	10	62	2026-01-05 14:41:41.346944	2025	REG
209	4	10	38	2026-01-05 14:41:41.346948	2025	REG
210	20	10	44	2026-01-05 14:41:41.346951	2025	REG
211	20	11	70	2026-01-05 14:41:41.423537	2025	REG
212	21	11	54	2026-01-05 14:41:41.423544	2025	REG
213	1	11	52	2026-01-05 14:41:41.423548	2025	REG
214	12	11	69	2026-01-05 14:41:41.423552	2025	REG
215	14	11	69	2026-01-05 14:41:41.423555	2025	REG
216	22	11	77	2026-01-05 14:41:41.423559	2025	REG
217	13	11	67	2026-01-05 14:41:41.423562	2025	REG
218	2	11	90	2026-01-05 14:41:41.423566	2025	REG
219	5	11	61	2026-01-05 14:41:41.42357	2025	REG
220	9	11	50	2026-01-05 14:41:41.423573	2025	REG
221	10	11	83	2026-01-05 14:41:41.423577	2025	REG
222	19	11	68	2026-01-05 14:41:41.42358	2025	REG
223	15	11	86	2026-01-05 14:41:41.423584	2025	REG
224	17	11	61	2026-01-05 14:41:41.423587	2025	REG
225	16	11	67	2026-01-05 14:41:41.423591	2025	REG
226	26	11	39	2026-01-05 14:41:41.423595	2025	REG
227	18	11	76	2026-01-05 14:41:41.423598	2025	REG
228	8	11	69	2026-01-05 14:41:41.423601	2025	REG
229	23	11	77	2026-01-05 14:41:41.423609	2025	REG
230	4	11	81	2026-01-05 14:41:41.423605	2025	REG
231	1	12	35	2026-01-05 14:41:41.515737	2025	REG
232	12	12	37	2026-01-05 14:41:41.515743	2025	REG
233	14	12	37	2026-01-05 14:41:41.515746	2025	REG
234	23	12	24	2026-01-05 14:41:41.515749	2025	REG
235	4	12	61	2026-01-05 14:41:41.515751	2025	REG
236	22	12	30	2026-01-05 14:41:41.515753	2025	REG
237	8	12	26	2026-01-05 14:41:41.515756	2025	REG
238	20	12	67	2026-01-05 14:41:41.515758	2025	REG
239	21	12	29	2026-01-05 14:41:41.51576	2025	REG
240	16	12	32	2026-01-05 14:41:41.515763	2025	REG
241	2	12	78	2026-01-05 14:41:41.515766	2025	REG
242	18	12	28	2026-01-05 14:41:41.515768	2025	REG
243	9	12	47	2026-01-05 14:41:41.51577	2025	REG
244	13	12	32	2026-01-05 14:41:41.515773	2025	REG
245	19	12	45	2026-01-05 14:41:41.515775	2025	REG
246	15	12	40	2026-01-05 14:41:41.515777	2025	REG
247	17	12	13	2026-01-05 14:41:41.51578	2025	REG
248	10	12	38	2026-01-05 14:41:41.515782	2025	REG
249	5	12	46	2026-01-05 14:41:41.515784	2025	REG
250	26	12	57	2026-01-05 14:41:41.515787	2025	REG
251	1	13	44	2026-01-05 14:41:41.593253	2025	REG
252	21	13	65	2026-01-05 14:41:41.593259	2025	REG
253	14	13	43	2026-01-05 14:41:41.593264	2025	REG
254	12	13	85	2026-01-05 14:41:41.593268	2025	REG
255	2	13	64	2026-01-05 14:41:41.593272	2025	REG
256	13	13	42	2026-01-05 14:41:41.593276	2025	REG
257	23	13	52	2026-01-05 14:41:41.593281	2025	REG
258	20	13	36	2026-01-05 14:41:41.593286	2025	REG
259	22	13	78	2026-01-05 14:41:41.59329	2025	REG
260	5	13	58	2026-01-05 14:41:41.593294	2025	REG
261	8	13	89	2026-01-05 14:41:41.593299	2025	REG
262	16	13	44	2026-01-05 14:41:41.593303	2025	REG
263	10	13	73	2026-01-05 14:41:41.593308	2025	REG
264	9	13	50	2026-01-05 14:41:41.593312	2025	REG
265	18	13	52	2026-01-05 14:41:41.593314	2025	REG
266	19	13	26	2026-01-05 14:41:41.593317	2025	REG
267	4	13	62	2026-01-05 14:41:41.593319	2025	REG
268	17	13	75	2026-01-05 14:41:41.593322	2025	REG
269	15	13	53	2026-01-05 14:41:41.593324	2025	REG
270	26	13	56	2026-01-05 14:41:41.593328	2025	REG
271	12	14	47	2026-01-05 14:41:41.631791	2025	REG
272	1	14	33	2026-01-05 14:41:41.631798	2025	REG
291	22	15	96	2026-01-05 14:41:41.699425	2025	REG
292	12	15	84	2026-01-05 14:41:41.69943	2025	REG
293	2	15	71	2026-01-05 14:41:41.699433	2025	REG
294	1	15	82	2026-01-05 14:41:41.699435	2025	REG
295	23	15	106	2026-01-05 14:41:41.699438	2025	REG
296	14	15	65	2026-01-05 14:41:41.69944	2025	REG
297	16	15	74	2026-01-05 14:41:41.699442	2025	REG
298	13	15	49	2026-01-05 14:41:41.699444	2025	REG
299	20	15	4	2026-01-05 14:41:41.699447	2025	REG
300	9	15	50	2026-01-05 14:41:41.699449	2025	REG
301	5	15	71	2026-01-05 14:41:41.699451	2025	REG
302	19	15	66	2026-01-05 14:41:41.699454	2025	REG
303	8	15	83	2026-01-05 14:41:41.699456	2025	REG
304	15	15	81	2026-01-05 14:41:41.699458	2025	REG
305	10	15	78	2026-01-05 14:41:41.699461	2025	REG
306	18	15	77	2026-01-05 14:41:41.699463	2025	REG
307	26	15	48	2026-01-05 14:41:41.699465	2025	REG
308	4	15	75	2026-01-05 14:41:41.699467	2025	REG
309	17	15	61	2026-01-05 14:41:41.699469	2025	REG
310	14	16	83	2026-01-05 14:41:41.749336	2025	REG
311	1	16	70	2026-01-05 14:41:41.749346	2025	REG
312	4	16	55	2026-01-05 14:41:41.74935	2025	REG
313	12	16	86	2026-01-05 14:41:41.749343	2025	REG
314	13	16	85	2026-01-05 14:41:41.749353	2025	REG
315	5	16	76	2026-01-05 14:41:41.749357	2025	REG
316	20	16	103	2026-01-05 14:41:41.74936	2025	REG
317	2	16	53	2026-01-05 14:41:41.749363	2025	REG
318	16	16	57	2026-01-05 14:41:41.749367	2025	REG
319	9	16	74	2026-01-05 14:41:41.74937	2025	REG
320	8	16	89	2026-01-05 14:41:41.749373	2025	REG
321	10	16	66	2026-01-05 14:41:41.749377	2025	REG
322	17	16	65	2026-01-05 14:41:41.74938	2025	REG
323	18	16	77	2026-01-05 14:41:41.74939	2025	REG
324	15	16	70	2026-01-05 14:41:41.749384	2025	REG
325	22	16	78	2026-01-05 14:41:41.749387	2025	REG
326	19	16	83	2026-01-05 14:41:41.749394	2025	REG
327	23	16	35	2026-01-05 14:41:41.749397	2025	REG
328	26	16	31	2026-01-05 14:41:41.749401	2025	REG
329	12	17	49	2026-01-05 15:15:00.199177	2025	REG
330	1	17	76	2026-01-05 15:15:00.199962	2025	REG
331	14	17	53	2026-01-05 15:15:00.200612	2025	REG
332	2	17	63	2026-01-05 15:15:00.201189	2025	REG
333	4	17	61	2026-01-05 15:15:00.201714	2025	REG
334	8	17	46	2026-01-05 15:15:00.202254	2025	REG
335	16	17	38	2026-01-05 15:15:00.202758	2025	REG
336	20	17	65	2026-01-05 15:15:00.203297	2025	REG
337	5	17	39	2026-01-05 15:15:00.203854	2025	REG
338	18	17	55	2026-01-05 15:15:00.204489	2025	REG
339	19	17	43	2026-01-05 15:15:00.205076	2025	REG
340	13	17	43	2026-01-05 15:15:00.205621	2025	REG
341	17	17	56	2026-01-05 15:15:00.206179	2025	REG
342	15	17	21	2026-01-05 15:15:00.206682	2025	REG
343	10	17	61	2026-01-05 15:15:00.207228	2025	REG
344	9	17	25	2026-01-05 15:15:00.207721	2025	REG
345	26	17	64	2026-01-05 15:15:00.208268	2025	REG
346	23	17	30	2026-01-05 15:15:00.208781	2025	REG
347	22	17	58	2026-01-05 15:15:00.209341	2025	REG
359	22	18	55	2026-01-10 14:10:00.339655	2025	REG
360	17	18	75	2026-01-10 14:10:00.342382	2025	REG
361	18	18	59	2026-01-10 14:10:00.345153	2025	REG
362	9	18	93	2026-01-10 14:10:00.347861	2025	REG
363	15	18	73	2026-01-10 14:10:00.350632	2025	REG
364	19	18	81	2026-01-10 14:10:00.353304	2025	REG
365	10	18	81	2026-01-10 14:10:00.404005	2025	REG
348	1	18	78	2026-01-10 14:10:00.309139	2025	REG
349	12	18	66	2026-01-10 14:10:00.312542	2025	REG
350	14	18	59	2026-01-10 14:10:00.315318	2025	REG
351	23	18	73	2026-01-10 14:10:00.318104	2025	REG
352	20	18	82	2026-01-10 14:10:00.320823	2025	REG
353	13	18	62	2026-01-10 14:10:00.323401	2025	REG
354	5	18	69	2026-01-10 14:10:00.326018	2025	REG
355	4	18	42	2026-01-10 14:10:00.328653	2025	REG
356	8	18	62	2026-01-10 14:10:00.331419	2025	REG
357	2	18	47	2026-01-10 14:10:00.334131	2025	REG
358	16	18	62	2026-01-10 14:10:00.336865	2025	REG
1	14	1	95	2026-01-12 22:55:00.205692	2025	REG
2	1	1	86	2026-01-12 22:55:00.209313	2025	REG
3	2	1	77	2026-01-12 22:55:00.212147	2025	REG
4	9	1	90	2026-01-12 22:55:00.215008	2025	REG
5	22	1	52	2026-01-12 22:55:00.217884	2025	REG
6	10	1	85	2026-01-12 22:55:00.303466	2025	REG
7	13	1	82	2026-01-12 22:55:00.30677	2025	REG
8	23	1	76	2026-01-12 22:55:00.309844	2025	REG
9	17	1	59	2026-01-12 22:55:00.312892	2025	REG
10	16	1	65	2026-01-12 22:55:00.315764	2025	REG
11	21	1	73	2026-01-12 22:55:00.319931	2025	REG
12	24	1	74	2026-01-12 22:55:00.323443	2025	REG
13	12	1	106	2026-01-12 22:55:00.327292	2025	REG
14	15	1	96	2026-01-12 22:55:00.330558	2025	REG
15	5	1	101	2026-01-12 22:55:00.334941	2025	REG
16	4	1	78	2026-01-12 22:55:00.338196	2025	REG
17	8	1	74	2026-01-12 22:55:00.341276	2025	REG
18	18	1	92	2026-01-12 22:55:00.344202	2025	REG
19	19	1	81	2026-01-12 22:55:00.347238	2025	REG
\.


--
-- Name: announcement_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pickarena_prod_db_user
--

SELECT pg_catalog.setval('public.announcement_id_seq', 2, true);


--
-- Name: board_post_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pickarena_prod_db_user
--

SELECT pg_catalog.setval('public.board_post_id_seq', 1, false);


--
-- Name: board_thread_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pickarena_prod_db_user
--

SELECT pg_catalog.setval('public.board_thread_id_seq', 1, false);


--
-- Name: game_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pickarena_prod_db_user
--

SELECT pg_catalog.setval('public.game_id_seq', 308, true);


--
-- Name: job_run_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pickarena_prod_db_user
--

SELECT pg_catalog.setval('public.job_run_id_seq', 3, true);


--
-- Name: pick_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pickarena_prod_db_user
--

SELECT pg_catalog.setval('public.pick_id_seq', 5505, true);


--
-- Name: settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pickarena_prod_db_user
--

SELECT pg_catalog.setval('public.settings_id_seq', 1, true);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pickarena_prod_db_user
--

SELECT pg_catalog.setval('public.user_id_seq', 26, true);


--
-- Name: user_score_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pickarena_prod_db_user
--

SELECT pg_catalog.setval('public.user_score_id_seq', 374, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: announcement announcement_pkey; Type: CONSTRAINT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.announcement
    ADD CONSTRAINT announcement_pkey PRIMARY KEY (id);


--
-- Name: board_post board_post_pkey; Type: CONSTRAINT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.board_post
    ADD CONSTRAINT board_post_pkey PRIMARY KEY (id);


--
-- Name: board_thread board_thread_pkey; Type: CONSTRAINT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.board_thread
    ADD CONSTRAINT board_thread_pkey PRIMARY KEY (id);


--
-- Name: game game_game_id_key; Type: CONSTRAINT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.game
    ADD CONSTRAINT game_game_id_key UNIQUE (game_id);


--
-- Name: game game_pkey; Type: CONSTRAINT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.game
    ADD CONSTRAINT game_pkey PRIMARY KEY (id);


--
-- Name: job_run job_run_pkey; Type: CONSTRAINT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.job_run
    ADD CONSTRAINT job_run_pkey PRIMARY KEY (id);


--
-- Name: pick pick_pkey; Type: CONSTRAINT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.pick
    ADD CONSTRAINT pick_pkey PRIMARY KEY (id);


--
-- Name: settings settings_pkey; Type: CONSTRAINT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.settings
    ADD CONSTRAINT settings_pkey PRIMARY KEY (id);


--
-- Name: user user_email_key; Type: CONSTRAINT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: user_score user_score_pkey; Type: CONSTRAINT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.user_score
    ADD CONSTRAINT user_score_pkey PRIMARY KEY (id);


--
-- Name: user user_username_key; Type: CONSTRAINT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_username_key UNIQUE (username);


--
-- Name: ix_job_run_job_name; Type: INDEX; Schema: public; Owner: pickarena_prod_db_user
--

CREATE INDEX ix_job_run_job_name ON public.job_run USING btree (job_name);


--
-- Name: announcement announcement_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.announcement
    ADD CONSTRAINT announcement_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public."user"(id);


--
-- Name: board_post board_post_author_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.board_post
    ADD CONSTRAINT board_post_author_user_id_fkey FOREIGN KEY (author_user_id) REFERENCES public."user"(id);


--
-- Name: board_post board_post_thread_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.board_post
    ADD CONSTRAINT board_post_thread_id_fkey FOREIGN KEY (thread_id) REFERENCES public.board_thread(id);


--
-- Name: board_thread board_thread_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.board_thread
    ADD CONSTRAINT board_thread_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public."user"(id);


--
-- Name: pick pick_game_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.pick
    ADD CONSTRAINT pick_game_id_fkey FOREIGN KEY (game_id) REFERENCES public.game(id);


--
-- Name: pick pick_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.pick
    ADD CONSTRAINT pick_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: user_score user_score_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pickarena_prod_db_user
--

ALTER TABLE ONLY public.user_score
    ADD CONSTRAINT user_score_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON SEQUENCES TO pickarena_prod_db_user;


--
-- Name: DEFAULT PRIVILEGES FOR TYPES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON TYPES TO pickarena_prod_db_user;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON FUNCTIONS TO pickarena_prod_db_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON TABLES TO pickarena_prod_db_user;


--
-- PostgreSQL database dump complete
--

\unrestrict CmObuXEwVMI8AgdHNpQxDdNgYnfE3rF6gt3KaCMt2YeJRaMX3jYaPYRyg3RRLdZ

