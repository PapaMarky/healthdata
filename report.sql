SELECT DISTINCT
  s.startDate, s.value 'systolic', d.value 'diastolic'
    FROM
    (
      SELECT startDate, type, value
      FROM health_data
      WHERE
        type = 'HKQuantityTypeIdentifierBloodPressureSystolic' AND
        sourceName = 'Health'
    ) s
    JOIN
    (
        SELECT startDate, type, value
        FROM health_data
        WHERE
            type = 'HKQuantityTypeIdentifierBloodPressureDiastolic' AND
            sourceName = 'Health'
    ) d
    ON
        s.startDate = d.startDate AND s.startDate > '2022-05-06'
    ORDER BY s.startDate DESC
