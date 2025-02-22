import os
import glob
import psycopg2  # Add database library
from datetime import datetime  # Add datetime import
import sys

def setup_logging():
    """Configure logging with timestamped filename"""
    log_dir = "read_logs"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%S")
    log_filename = f"readLog_{timestamp}.txt"
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

def get_db_connection():
    """Database connection helper"""
    try:
        return psycopg2.connect(
            host="localhost",
            database="tebedata",
            user="postgres",
            password="admin",
            port="5432"
        )
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def parse_logs(log_folder):
    log_files = glob.glob(os.path.join(log_folder, '*tbAppPinpon.txt'))
    
    for log_file in log_files:
        # Extract date from filename (format: YYYYMMDD_HHMMSS_filename)
        filename = os.path.basename(log_file)
        date_str = filename.split('_')[0]
        log_date = datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")
        
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        print(f"\nAnalyzing: {os.path.basename(log_file)}")
        found_bets = []
        
        for i, line in enumerate(lines):
            if "Bet placed successfully" in line:
                # Check if there are enough subsequent lines
                if i+3 < len(lines):
                    scoreboard = {
                        'header': lines[i+1].strip(),
                        'team1': lines[i+2].strip(),
                        'team2': lines[i+3].strip()
                    }
                    found_bets.append(scoreboard)
        
        if found_bets:
            print(f"Found {len(found_bets)} bet(s) with scoreboards:")
            for idx, bet in enumerate(found_bets, 1):
                print(f"\nBet {idx}:")
                print(bet['header'])
                print(bet['team1'])
                print(bet['team2'])
                
                # New code to update database
                try:
                    # Parse scoreboard data
                    team1_data = bet['team1'].split("Team Name: ")[1].split(", Team Score: ")
                    team2_data = bet['team2'].split("Team Name: ")[1].split(", Team Score: ")
                    
                    teamA = team1_data[0].strip()
                    teamB = team2_data[0].strip()
                    
                    # Handle potential missing set scores
                    team1_scores = team1_data[1].split(", Set: ") if len(team1_data) > 1 else ['']
                    team2_scores = team2_data[1].split(", Set: ") if len(team2_data) > 1 else ['']
                    
                    pointA = team1_scores[0].strip() if team1_scores[0] else ''
                    setA = team1_scores[1].strip() if len(team1_scores) > 1 else ''
                    
                    pointB = team2_scores[0].strip() if team2_scores[0] else ''
                    setB = team2_scores[1].strip() if len(team2_scores) > 1 else ''

                    point_scbd = f"{pointA}-{pointB}" if pointA and pointB else ''
                    set_scbd = f"{setA}-{setB}" if setA and setB else ''

                    print(f"Point score: {point_scbd}")
                    print(f"Set score: {set_scbd}")
                    
                    # Update database with date filter
                    conn = get_db_connection()
                    if conn:
                        with conn.cursor() as cursor:
                            cursor.execute("""
                                UPDATE bet_history
                                SET point_score = %s, set_score = %s
                                WHERE team_1 = %s AND team_2 = %s
                                AND bet_date >= %s
                            """, (point_scbd, set_scbd, teamA, teamB, log_date))
                            conn.commit()
                        print(f"Updated scores for {teamA} vs {teamB} (log date: {log_date})")
                        conn.close()
                        
                except Exception as e:
                    print(f"Error updating database: {e}")
                
        else:
            print("No complete bet records found")
        print("-" * 50)

if __name__ == "__main__":
    original_stdout, log_file = setup_logging()
    try:
        log_folder = os.path.join(os.path.expanduser('~'), 'Escritorio', 'Trabajos', 'tb', 'logs')
        parse_logs(log_folder)
    finally:
        sys.stdout = original_stdout
        log_file.close() 