SELECT DISTINCT
  STRFTIME('%Y/%m/%d %H:%M', s.creationDate) || ' : ' || s.value || '/' || d.value
    FROM
    (
      select creationDate, type, value
      from health_data
      where type = 'HKQuantityTypeIdentifierBloodPressureSystolic' AND
        creationDate > '2022-05-06' AND sourceName = 'Health') s
JOIN
(select
  creationDate, type, value
  from health_data
  where type = 'HKQuantityTypeIdentifierBloodPressureDiastolic' AND
creationDate > '2022-05-06' AND sourceName = 'Health') d
on
s.creationDate = d.creationDate
order by s.creationDate desc
