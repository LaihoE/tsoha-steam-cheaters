CREATE TABLE bans(
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT Now(),
    steamid bigint,
    vacban boolean,
    steamban boolean,
    faceitban boolean,
    banned_days_ago int
);


CREATE TABLE friends(
    id SERIAL PRIMARY KEY,
    user1 bigint,
    user2 bigint
);

CREATE TABLE faceitstats(
    id SERIAL PRIMARY KEY,
    steamid bigint,
    created_at TIMESTAMPTZ DEFAULT Now(),
    faceit_level int,
    faceit_name text,
    country text,
    kdr decimal,
    n_matches int,
    winrate decimal,
    hs_ratio decimal
);

CREATE TABLE steamstats(
    id SERIAL PRIMARY KEY,
    steam_name text,
    steamid bigint,
    created_at TIMESTAMPTZ DEFAULT Now(),
    hours_csgo int,
    hours_steam int,
    total_games int
);
