-- 06 | Monthly arrivals and cancellation rate per hotel (by arrival month).
SELECT
    hotel,
    date_trunc('month', arrival_date)::DATE  AS month,
    count(*)                                 AS bookings,
    sum(1 - is_canceled)                     AS stays,
    round(avg(is_canceled), 3)               AS cancellation_rate,
    round(avg(is_late_attrition), 3)         AS late_attrition_rate,
    round(avg(adr) FILTER (WHERE is_canceled = 0), 2) AS adr_stayed_eur
FROM bookings
GROUP BY ALL
ORDER BY hotel, month;
