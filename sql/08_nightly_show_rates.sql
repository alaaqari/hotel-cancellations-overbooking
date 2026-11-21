-- 08 | Input for the overbooking simulation.
--      For each arrival date: of the bookings still "on the books" one week before arrival,
--      what share actually showed up? This is the attrition an overbooking policy must cover;
--      anything cancelled earlier could have been resold.
WITH on_books AS (
    SELECT
        hotel,
        arrival_date,
        is_canceled,
        adr
    FROM bookings
    WHERE booking_date <= arrival_date - 7                       -- booked at least a week ahead
      AND (is_canceled = 0                                       -- ...and not yet cancelled at T-7
           OR reservation_status = 'No-Show'
           OR reservation_status_date > arrival_date - 7)
)
SELECT
    hotel,
    arrival_date,
    month(arrival_date)                       AS month_num,
    count(*)                                  AS on_books_t7,
    sum(1 - is_canceled)                      AS showed,
    round(avg(1 - is_canceled), 4)            AS show_rate,
    round(avg(adr) FILTER (WHERE is_canceled = 0), 2) AS adr_stayed
FROM on_books
GROUP BY hotel, arrival_date
HAVING count(*) >= 20                         -- ignore very thin days
ORDER BY hotel, arrival_date;
