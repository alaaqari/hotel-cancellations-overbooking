-- 01 | Data-quality report: what was found in the raw file and what cleaning removed.
SELECT 'Raw rows'                               AS check_name, count(*)::BIGINT AS n FROM raw_bookings
UNION ALL SELECT 'Negative ADR',                count(*) FROM raw_bookings WHERE adr < 0
UNION ALL SELECT 'ADR above 1,000',             count(*) FROM raw_bookings WHERE adr > 1000
UNION ALL SELECT 'Zero guests',                 count(*) FROM raw_bookings
                                                 WHERE adults + coalesce(children, 0) + babies = 0
UNION ALL SELECT 'Missing children (set to 0)', count(*) FROM raw_bookings WHERE children IS NULL
UNION ALL SELECT 'Zero-night stays (kept)',     count(*) FROM raw_bookings
                                                 WHERE stays_in_weekend_nights + stays_in_week_nights = 0
UNION ALL SELECT 'Exact duplicate rows (kept)', (SELECT count(*) FROM raw_bookings)
                                                 - (SELECT count(*) FROM (SELECT DISTINCT * FROM raw_bookings))
UNION ALL SELECT 'Rows after cleaning',         count(*) FROM bookings;
