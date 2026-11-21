-- 02 | Headline KPIs per hotel.
SELECT
    hotel,
    count(*)                                              AS bookings,
    round(avg(is_canceled), 3)                            AS cancellation_rate,
    round(avg(is_late_attrition), 3)                      AS late_attrition_rate,
    round(median(lead_time), 0)                           AS median_lead_time_days,
    round(avg(nights) FILTER (WHERE is_canceled = 0), 2)  AS avg_nights_stayed,
    round(avg(adr) FILTER (WHERE is_canceled = 0), 2)     AS adr_stayed_eur,
    round(sum(booked_revenue) FILTER (WHERE is_canceled = 0) / 1e6, 2) AS realized_revenue_m_eur
FROM bookings
GROUP BY hotel
ORDER BY hotel;
