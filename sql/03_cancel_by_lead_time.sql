-- 03 | Cancellation rate by how far in advance the booking was made.
SELECT
    hotel,
    lead_bucket,
    min(lead_time)                    AS sort_key,
    count(*)                          AS bookings,
    round(avg(is_canceled), 3)        AS cancellation_rate,
    round(avg(is_late_attrition), 3)  AS late_attrition_rate
FROM bookings
GROUP BY hotel, lead_bucket
ORDER BY hotel, sort_key;
