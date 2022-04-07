CREATE TABLE bans(
    steamid BIGINT PRIMARY KEY,
    vacban BOOL,
    steamban BOOL,
    banned_days_ago int,
);

CREATE TABLE friends(
    id SERIAL PRIMARY KEY,
    user1 bigint,
    user2 bigint
);

CREATE TABLE faceitstats(
    steamid BIGINT PRIMARY KEY,
    faceit_level int,
    faceit_name TEXT,
    country TEXT,
    kdr decimal,
    n_matches int,
    winrate decimal,
    hs_ratio decimal
);

CREATE TABLE steamstats(
    steamid BIGINT PRIMARY KEY,
    hours_csgo int,
    hours_steam int,
    total_games int
);