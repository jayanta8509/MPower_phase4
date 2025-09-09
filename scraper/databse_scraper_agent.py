from datetime import datetime
from decimal import Decimal
import pyodbc
from functools import wraps
import asyncio
import json




def async_route(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapped

async def fetch_data_async():
    try:
        conn = pyodbc.connect(

            'DRIVER={SQL Server};'
            'SERVER=DESKTOP-68FBO4B;'
            'DATABASE=MPOWER_TEST2;'
            'Trusted_Connection=yes;'
        )
        cursor = conn.cursor()

        # Lookup table queries for ID and Name pairs
        queries = {
            "industry": "SELECT Id, IndustryName FROM Industry",
            "educationlevel": "SELECT Id, EducationLevelName FROM EducationLevel",
            "communication": "SELECT Id, CommunicationName FROM Communication",
            "leadership": "SELECT Id, LeadershipName FROM Leadership",
            "metacognition": "SELECT Id, MetacognitionName FROM Metacognition",
            "criticalthinking": "SELECT Id, CriticalThinkingName FROM CriticalThinking",
            "collaboration": "SELECT Id, CollaborationName FROM Collaboration",
            "character": "SELECT Id, CharacterName FROM Character",
            "creativity": "SELECT Id, CreativityName FROM Creativity",
            "growthmindset": "SELECT Id, GrowthMindsetName FROM GrowthMindset",
            "mindfulness": "SELECT Id, MindfulnessName FROM Mindfulness",
            "fortitude": "SELECT Id, FortitudeName FROM Fortitude",
            "technicalskills": "SELECT Id, TechnicalSkillsName FROM TechnicalSkills"
        }

        table_details = {}

        for table, query in queries.items():
            try:
                cursor.execute(query)
                
                # Format as {id: name} pairs
                lookup_data = {}
                for row in cursor.fetchall():
                    lookup_data[row[0]] = row[1]  # Id: Name
                
                table_details[table] = lookup_data
                # print(f"Fetched {len(lookup_data)} records from '{table}' table.")

            except Exception as e:
                # print(f"Error fetching data for {table}: {e}")
                return {'error': f'Error fetching data for {table}'}

        cursor.close()
        conn.close()

        if not table_details:
            return {'error': 'No data found'}
            
        return table_details

    except Exception as e:
        # print(f"Database connection error: {e}")
        return {'error': 'Database connection error'}

