import psycopg2
from psycopg2 import sql
import argparse
import sys
import os
from datetime import datetime

def setup_logging():
    """Configure logging with timestamped filename"""
    log_dir = "reports"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"report_{timestamp}.txt"
    log_path = os.path.join(log_dir, log_filename)
    
    log_file = open(log_path, 'w', encoding='utf-8')
    
    class Tee:
        def __init__(self, *files):
            self.files = files
        def write(self, obj):
            for f in self.files:
                f.write(obj)
        def flush(self):
            for f in self.files:
                f.flush()
    
    original_stdout = sys.stdout
    sys.stdout = Tee(sys.stdout, log_file)
    
    return original_stdout, log_file

def connect_to_db():
    """Establish database connection"""
    try:
        conn = psycopg2.connect(
            dbname="tebedata",
            user="postgres",
            password="admin",
            host="localhost",
            port="5432"
        )
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        sys.exit(1)

def execute_query(query, params=None):
    """Execute SQL query and return results"""
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                colnames = [desc[0] for desc in cursor.description]
                return colnames, result
            else:
                conn.commit()
                return None, cursor.rowcount
                
    except psycopg2.Error as e:
        print(f"Query execution error: {e}")
        conn.rollback()
        return None, None
    finally:
        conn.close()

def format_results(result, cursor):
    """Format query results for display"""
    if not result:
        return "No results"
        
    # Convert to list of dictionaries
    columns = [desc[0] for desc in cursor.description]
    formatted = []
    for row in result:
        formatted.append(dict(zip(columns, row)))
    
    return formatted

def count_consecutive_losses(rows):
    """Count consecutive rows with bet_status=2"""
    count = 0
    for i in range(len(rows) - 1):
        current = rows[i]['bet_status']
        next_row = rows[i+1]['bet_status']
        if current == 2 and next_row == 2:
            count += 1
    return count

def analyze_winning_streaks(rows):
    """Analyze and format winning streaks with their timestamps"""
    streaks = []
    current_streak = None
    
    for row in rows:
        if row['bet_status'] == 1:
            if not current_streak:  # Start new streak
                current_streak = {
                    'start_date': row['bet_date'],
                    'start_time': row['bet_time'],
                    'end_date': row['bet_date'],
                    'end_time': row['bet_time'],
                    'count': 1
                }
            else:  # Continue existing streak
                current_streak['end_date'] = row['bet_date']
                current_streak['end_time'] = row['bet_time']
                current_streak['count'] += 1
        else:
            if current_streak:  # End current streak
                streaks.append(current_streak)
                current_streak = None
                
    # Add final streak if exists
    if current_streak:
        streaks.append(current_streak)
        
    return streaks


def analyze_losing_streaks(rows):
    """Analyze and format winning streaks with their timestamps"""
    streaks = []
    current_streak = None
    
    for row in rows:
        if row['bet_status'] == 2:
            if not current_streak:  # Start new streak
                current_streak = {
                    'start_date': row['bet_date'],
                    'start_time': row['bet_time'],
                    'end_date': row['bet_date'],
                    'end_time': row['bet_time'],
                    'count': 1
                }
            else:  # Continue existing streak
                current_streak['end_date'] = row['bet_date']
                current_streak['end_time'] = row['bet_time']
                current_streak['count'] += 1
        else:
            if current_streak:  # End current streak
                streaks.append(current_streak)
                current_streak = None
                
    # Add final streak if exists
    if current_streak:
        streaks.append(current_streak)
        
    return streaks


def count_wodds_frequency(rows):
    """Count occurrences of each odds value in winning bets (bet_status=1)"""
    odds_count = {}
    for row in rows:
        if row['bet_status'] == 1:  # Only count winning bets
            odds = row['odds']
            if odds in odds_count:
                odds_count[odds] += 1
            else:
                odds_count[odds] = 1
    return odds_count

def count_lodds_frequency(rows):
    """Count occurrences of each odds value in winning bets (bet_status=1)"""
    odds_count = {}
    for row in rows:
        if row['bet_status'] == 2:  # Only count winning bets
            odds = row['odds']
            if odds in odds_count:
                odds_count[odds] += 1
            else:
                odds_count[odds] = 1
    return odds_count


def count_l_selteam_frequency(rows):
    """Count occurrences of each odds value in winning bets (bet_status=1)"""
    team_count = {}
    for row in rows:
        if row['bet_status'] == 2:  # Only count winning bets
            odds = row['selected_team']
            if odds in team_count:
                team_count[odds] += 1
            else:
                team_count[odds] = 1
    return team_count

def count_w_selteam_frequency(rows):
    """Count occurrences of each odds value in winning bets (bet_status=1)"""
    team_count = {}
    for row in rows:
        if row['bet_status'] == 1:  # Only count winning bets
            odds = row['selected_team']
            if odds in team_count:
                team_count[odds] += 1
            else:
                team_count[odds] = 1
    return team_count


def print_result_table(title, headers, rows):
    """Print query results in a formatted table"""
    if not rows:
        print(f"\n{title} - No data available\n")
        return
    
    # Calculate column widths
    col_widths = [
        max(len(str(row[i])) for row in rows + [headers]) 
        for i in range(len(headers))
    ]
    
    # Create header separator
    separator = '+-' + '-+-'.join('-' * width for width in col_widths) + '-+'
    
    # Print table header
    print(f"\n{title}")
    print(separator)
    header_row = '| ' + ' | '.join(f"{header:<{width}}" for header, width in zip(headers, col_widths)) + ' |'
    print(header_row)
    print(separator.replace('-', '='))
    
    # Print data rows
    for row in rows:
        str_row = '| ' + ' | '.join(f"{str(item):<{width}}" for item, width in zip(row, col_widths)) + ' |'
        print(str_row)
        print(separator)
    
    print(f"{len(rows)} rows displayed\n")


def main():
    original_stdout, log_file = setup_logging()
    try:
        query = """
        SELECT * FROM bet_history
        WHERE bet_date >= '2025-01-29' AND bet_date <= '2025-02-13' 
        AND sport_id = 15
        ORDER BY bet_date ASC, bet_time ASC;
        """

        odds_query = """
        SELECT 
            odds AS odds_value,
            COUNT(*) AS count
        FROM bet_history
        WHERE bet_date >= '2025-02-11' AND bet_date <= '2025-02-13' 
            AND sport_id = 15 and bet_status = 1
        GROUP BY odds
        ORDER BY odds ASC;
        """

        hours_query = """
        SELECT 
            TO_CHAR(bet_time, 'HH24') AS hour,
            COUNT(*) AS bet_count
        FROM bet_history
        WHERE bet_date >= '2025-01-29' AND bet_date <= '2025-02-13' 
            AND sport_id = 15 and bet_status = 2
        GROUP BY TO_CHAR(bet_time, 'HH24')
        ORDER BY hour;
        """

        sel_team_query = """
        SELECT 
            selected_team AS sel_team,
            COUNT(*) AS count
        FROM bet_history
        WHERE bet_date >= '2025-02-11' AND bet_date <= '2025-02-13' 
            AND sport_id = 15 and bet_status = 1
        GROUP BY selected_team
        ORDER BY selected_team ASC;
        """

        score_query = """
        SELECT *
        FROM bet_history
        WHERE NULLIF(point_score, '') IS NOT NULL
        AND point_score <> ''
        AND sport_id = 15
        ORDER BY bet_date DESC, bet_time DESC;
        """
        
        point_diff_query = """
        SELECT ABS(SPLIT_PART(point_score, '-', 1)::INT - SPLIT_PART(point_score, '-', 2)::INT) AS point_diff,
        COUNT(*) AS count
        FROM bet_history
        WHERE point_score <> '' and NULLIF(point_score, '') IS NOT NULL
        GROUP BY point_diff
        ORDER BY point_diff DESC;
        """

        high_value_query = """
        SELECT 
        GREATEST(
            SPLIT_PART(point_score, '-', 1)::INT,
            SPLIT_PART(point_score, '-', 2)::INT
        ) AS higher_value,
        COUNT(*) AS count
        FROM bet_history
        WHERE NULLIF(point_score, '') IS NOT NULL
        GROUP BY higher_value
        ORDER BY higher_value DESC;
        """

        score_pair_query = """
        SELECT 
        LEAST(a, b) || '-' || GREATEST(a, b) AS score_pair,
        COUNT(*) AS count
        FROM (
            SELECT 
                SPLIT_PART(point_score, '-', 1)::INT AS a,
                SPLIT_PART(point_score, '-', 2)::INT AS b
            FROM bet_history
            WHERE NULLIF(point_score, '') IS NOT NULL
        ) AS split_scores
        GROUP BY score_pair
        ORDER BY score_pair DESC;
        """


        conn = connect_to_db()
        with conn.cursor() as cursor:
            cursor.execute(query)
            
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                print_result_table("MAIN QUERY RESULTS", columns, rows)
                rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

                # Count consecutive losses
                consecutive_losses = count_consecutive_losses(rows)
                print(f"Found {consecutive_losses} instances of consecutive 'bet_status=2'")
                
                # Analyze winning and losing streaks
                win_streaks = analyze_winning_streaks(rows)
                lose_streaks = analyze_losing_streaks(rows)
                
                # Count odds frequency
                w_odds_counts = count_wodds_frequency(rows)
                l_odds_counts = count_lodds_frequency(rows)

                #Count sel_team frequency
                w_sel_teams = count_w_selteam_frequency(rows)
                l_sel_teams = count_l_selteam_frequency(rows)

                # Print formatted results
                if not win_streaks:
                    print("No winning streaks found")
                    return
                
                if not lose_streaks:
                    print("No losing streaks found")
                    return
                    
                print(f"Found {len(win_streaks)} winning streaks:\n")
                for i, streak in enumerate(win_streaks, 1):
                    print(f"Streak {i}:")
                    print(f"Start: {streak['start_date']} {streak['start_time']}")
                    print(f"End:   {streak['end_date']} {streak['end_time']}")
                    print(f"Wins:  {streak['count']}\n")

                print("")
                print("----------------------------------------------")
                print("")

                print(f"Found {len(lose_streaks)} losing streaks:\n")
                for i, streak in enumerate(lose_streaks, 1):
                    print(f"Streak {i}:")
                    print(f"Start: {streak['start_date']} {streak['start_time']}")
                    print(f"End:   {streak['end_date']} {streak['end_time']}")
                    print(f"Losses:  {streak['count']}\n")

                print("")
                print("----------------------------------------------")
                print("")

                # Print odds statistics
                print("\nOdds frequency (winning bets only):")
                if w_odds_counts:
                    # Sort by numeric value of odds
                    for odds in sorted(w_odds_counts, key=lambda x: float(x)):
                        print(f"Odds {odds}: {w_odds_counts[odds]} times")
                else:
                    print("No odds data available")

                print("")
                print("----------------------------------------------")
                print("")

                # Print odds statistics
                print("\nOdds frequency (losing bets only):")
                if l_odds_counts:
                    # Sort by numeric value of odds
                    for odds in sorted(l_odds_counts, key=lambda x: float(x)):
                        print(f"Odds {odds}: {l_odds_counts[odds]} times")
                else:
                    print("No odds data available")
                
                print("")
                print("----------------------------------------------")
                print("")

                # Print odds statistics
                print("\nSelected team frequency (winning bets only):")
                if w_sel_teams:
                    # Sort alphabetically by team name
                    for team in sorted(w_sel_teams, key=lambda x: x):
                        print(f"Team {team}: {w_sel_teams[team]} times")
                else:
                    print("No team data available")
                
                print("")
                print("----------------------------------------------")
                print("")

                # Print odds statistics
                print("\nSelected team frequency (losing bets only):")
                if l_sel_teams:
                    # Sort alphabetically by team name
                    for team in sorted(l_sel_teams, key=lambda x: x):
                        print(f"Team {team}: {l_sel_teams[team]} times")
                else:
                    print("No team data available")
                        
            else:
                print("No results returned")
                
    except psycopg2.Error as e:
        print(f"Query execution error: {e}")
    finally:
        sys.stdout = original_stdout
        log_file.close()

if __name__ == "__main__":
    main() 