SELECT * FROM bet_history
    WHERE bet_date >= '2025-01-29' AND bet_date <= '2025-02-13' 
    AND sport_id = 15 and bet_status = 1
    ORDER BY bet_time ASC;



SELECT 
    odds AS odds_value,
    COUNT(*) AS count
FROM bet_history
WHERE bet_date >= '2025-02-11' AND bet_date <= '2025-02-13' 
    AND sport_id = 15 and bet_status = 1
GROUP BY odds
ORDER BY odds ASC;




SELECT 
    league AS league_value,
    COUNT(*) AS count
FROM bet_history
WHERE bet_date >= '2025-01-11' AND bet_date <= '2025-02-13' 
    AND sport_id = 15
GROUP BY league
ORDER BY league ASC;



SELECT 
    selected_team AS sel_team,
    COUNT(*) AS count
FROM bet_history
WHERE bet_date >= '2025-02-11' AND bet_date <= '2025-02-13' 
    AND sport_id = 15 and bet_status = 2
GROUP BY selected_team
ORDER BY selected_team ASC;



SELECT 
    TO_CHAR(bet_time, 'HH24') AS hour,
    COUNT(*) AS bet_count
FROM bet_history
WHERE bet_date >= '2025-01-29' AND bet_date <= '2025-02-13' 
    AND sport_id = 15 and bet_status = 1
GROUP BY TO_CHAR(bet_time, 'HH24')
ORDER BY hour;



SELECT *
FROM bet_history
WHERE NULLIF(point_score, '') IS NOT NULL
AND (set_score = '0-2' or set_score = '2-0')
ORDER BY bet_date DESC, bet_time DESC;


SELECT *,
       ABS(SPLIT_PART(point_score, '-', 1)::INT - SPLIT_PART(point_score, '-', 2)::INT) AS point_diff
FROM bet_history
WHERE point_score <> ''
  AND ABS(SPLIT_PART(point_score, '-', 1)::INT - SPLIT_PART(point_score, '-', 2)::INT) >= 3
ORDER BY point_diff DESC;