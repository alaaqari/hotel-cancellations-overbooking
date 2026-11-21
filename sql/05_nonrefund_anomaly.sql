-- 05 | Investigating the anomaly: "Non Refund" deposits cancel ~99% of the time.
--      A non-refundable booking should cancel LESS, so who are these bookings?
SELECT
    deposit_type,
    count(*)                                                    AS bookings,
    round(avg(is_canceled), 3)                                  AS cancellation_rate,
    round(avg(CASE WHEN market_segment IN ('Groups', 'Offline TA/TO') THEN 1 ELSE 0 END), 3)
                                                                AS share_groups_or_tour_operator,
    round(avg(CASE WHEN country = 'PRT' THEN 1 ELSE 0 END), 3)  AS share_from_portugal,
    round(avg(CASE WHEN hotel = 'City Hotel' THEN 1 ELSE 0 END), 3) AS share_city_hotel,
    round(median(lead_time), 0)                                 AS median_lead_time,
    round(avg(total_of_special_requests), 2)                    AS avg_special_requests,
    round(median(arrival_date - reservation_status_date) FILTER (WHERE is_canceled = 1), 0)
                                                                AS median_days_cancelled_before_arrival
FROM bookings
WHERE deposit_type IN ('No Deposit', 'Non Refund')
GROUP BY deposit_type;
