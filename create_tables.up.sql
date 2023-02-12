CREATE TABLE IF NOT EXISTS Agent (
	id integer PRIMARY KEY AUTOINCREMENT,
	name text,
	telegram_id integer,
	phone_number text
);

CREATE TABLE IF NOT EXISTS Property (
	url text,
	type text,
	operation_type text,
	building_type text,
	condition text,
	usd_price float,
	city text,
	address text,
	bedrooms integer,
	living_rooms integer,
	area integer,
	gas integer,
	heating text,
	hot_water text,
	source text,
	agent_id integer,
	ru_description text,
	ge_description text,
	en_description text
);


