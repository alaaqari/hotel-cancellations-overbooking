-- 04 | Cancellation by market segment and deposit type (City + Resort combined).
--      Segments with < 500 bookings are excluded to keep rates stable.
SELECT
    'market_segment'                  AS dimension,
    market_segment                    AS value,
    count(*)                          AS bookings,
    round(avg(is_canceled), 3)        AS cancellation_rate,
    round(avg(is_late_attrition), 3)  AS late_attrition_rate,
    round(median(lead_time), 0)       AS median_lead_time
FROM bookings
GROUP BY market_segment
HAVING count(*) >= 500

UNION ALL

SELECT
    'deposit_type', deposit_type, count(*),
    round(avg(is_canceled), 3), round(avg(is_late_attrition), 3), round(median(lead_time), 0)
FROM bookings
GROUP BY deposit_type
HAVING count(*) >= 100
ORDER BY dimension, cancellation_rate DESC;
