-- 07 | Where did booked revenue end up? Splits every booking by outcome and timing.
--      Early cancellations can usually be resold; late ones and no-shows mostly cannot.
SELECT
    hotel,
    outcome,
    count(*)                                         AS bookings,
    round(count(*) / sum(count(*)) OVER (PARTITION BY hotel), 3)          AS share_of_bookings,
    round(sum(booked_revenue) / 1e6, 2)              AS booked_revenue_m_eur,
    round(sum(booked_revenue) / sum(sum(booked_revenue)) OVER (PARTITION BY hotel), 3)
                                                     AS share_of_booked_revenue
FROM bookings
GROUP BY hotel, outcome
ORDER BY hotel,
    CASE outcome WHEN 'Stayed' THEN 1 WHEN 'Cancelled 31+ days before' THEN 2
                 WHEN 'Cancelled 8-30 days before' THEN 3 WHEN 'Cancelled 0-7 days before' THEN 4
                 ELSE 5 END;
