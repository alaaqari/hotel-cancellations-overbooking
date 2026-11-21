-- 00 | Build the analysis table `bookings` from the raw CSV.
-- Every cleaning decision is documented inline. Row counts removed are reported by 01_data_quality.sql.

CREATE OR REPLACE TABLE raw_bookings AS
SELECT * FROM read_csv_auto('{raw_path}', nullstr = 'NA');

CREATE OR REPLACE TABLE bookings AS
WITH typed AS (
    SELECT
        *,
        -- Arrival date is split across three columns with the month as a word ("July")
        strptime(arrival_date_year::VARCHAR || '-' || arrival_date_month || '-'
                 || arrival_date_day_of_month::VARCHAR, '%Y-%B-%d')::DATE      AS arrival_date,
        stays_in_weekend_nights + stays_in_week_nights                         AS nights,
        coalesce(children, 0)                                                  AS children_clean
    FROM raw_bookings
)
SELECT
    hotel,
    is_canceled,
    reservation_status,
    reservation_status_date,
    arrival_date,
    arrival_date - lead_time::INTEGER                           AS booking_date,
    lead_time,
    nights,
    adults, children_clean AS children, babies,
    market_segment, distribution_channel, customer_type, deposit_type,
    is_repeated_guest, previous_cancellations, booking_changes,
    total_of_special_requests, required_car_parking_spaces,
    country, agent, adr,
    adr * nights                                                AS booked_revenue,

    -- Lead-time buckets used across the analysis
    CASE WHEN lead_time <= 7   THEN '0-7 days'
         WHEN lead_time <= 30  THEN '8-30 days'
         WHEN lead_time <= 90  THEN '31-90 days'
         WHEN lead_time <= 180 THEN '91-180 days'
         WHEN lead_time <= 365 THEN '181-365 days'
         ELSE '365+ days' END                                   AS lead_bucket,

    -- When did the booking end? reservation_status_date is the cancellation date for cancellations.
    CASE WHEN is_canceled = 0                          THEN 'Stayed'
         WHEN reservation_status = 'No-Show'           THEN 'No-show'
         WHEN arrival_date - reservation_status_date <= 7  THEN 'Cancelled 0-7 days before'
         WHEN arrival_date - reservation_status_date <= 30 THEN 'Cancelled 8-30 days before'
         ELSE 'Cancelled 31+ days before' END               AS outcome,

    -- "Late" attrition = the room is very hard to resell: no-show or cancelled in the final week
    CASE WHEN reservation_status = 'No-Show'
           OR (reservation_status = 'Canceled' AND arrival_date - reservation_status_date <= 7)
         THEN 1 ELSE 0 END                                      AS is_late_attrition
FROM typed
WHERE adr BETWEEN 0 AND 1000                          -- drops 1 negative ADR and 1 ADR of 5,400 (data-entry errors)
  AND adults + children_clean + babies > 0;           -- drops 180 bookings with zero guests
-- Kept on purpose:
--   * Exact duplicate rows (~32k). There is no booking ID, and duplicates are concentrated in group
--     and tour-operator segments, where one block of identical rooms is a normal booking pattern.
--   * Zero-night stays (day use): real bookings; they simply carry zero room revenue.
