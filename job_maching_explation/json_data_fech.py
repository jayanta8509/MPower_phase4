import os
from datetime import datetime
from decimal import Decimal
import pyodbc
from functools import wraps
import asyncio

DRIVER = os.getenv("DRIVER")
SERVER = os.getenv("SERVER")
DATABASE = os.getenv("DATABASE")
TRUSTED_CONNECTION = os.getenv("TRUSTED_CONNECTION")

def async_route(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapped


async def fetch_data_async(job_id, member_id):
    try:
        conn = pyodbc.connect(

            DRIVER=DRIVER,
            SERVER=SERVER,
            DATABASE=DATABASE,
            Trusted_Connection=TRUSTED_CONNECTION
        )
        cursor = conn.cursor()

        queries = {
            "member": """
                SELECT
                    m.Id AS MemberId,
                    m.MemberFirstName,
                    m.MemberLastName,
                    m.MemberEmail,
                    m.IsActive,
                    m.CreatedDate,
                    m.ModifiedDate,
                    m.MemberEthnicityId,
                    m.MemberGenderId,
                    m.Age_Id,
                    a.AgeName,
                    m.CityId,
                    c.CityName,
                    Eth.EthnicityName,
                    m.Headline,
                    ISNULL(comm.CommunicationNames, 'Unknown') AS CommunicationNames,
                    ISNULL(comm.CommunicationDescriptions, 'Unknown') AS CommunicationDescriptions,
                    ISNULL(l.LeadershipNames, 'Unknown') AS LeadershipNames,
                    ISNULL(l.LeadershipDescriptions, 'Unknown') AS LeadershipDescriptions,
                    ISNULL(ct.CriticalThinkingNames, 'Unknown') AS CriticalThinkingNames,
                    ISNULL(ct.CriticalThinkingDescriptions, 'Unknown') AS CriticalThinkingDescriptions,
                    ISNULL(collab.CollaborationNames, 'Unknown') AS CollaborationNames,
                    ISNULL(collab.CollaborationDescriptions, 'Unknown') AS CollaborationDescriptions,
                    ISNULL(ch.CharacterNames, 'Unknown') AS CharacterNames,
                    ISNULL(ch.CharacterDescriptions, 'Unknown') AS CharacterDescriptions,
                    ISNULL(cr.CreativityNames, 'Unknown') AS CreativityNames,
                    ISNULL(cr.CreativityDescriptions, 'Unknown') AS CreativityDescriptions,
                    ISNULL(gm.GrowthMindsetNames, 'Unknown') AS GrowthMindsetNames,
                    ISNULL(gm.GrowthMindsetDescriptions, 'Unknown') AS GrowthMindsetDescriptions,
                    ISNULL(mind.MindfulnessNames, 'Unknown') AS MindfulnessNames,
                    ISNULL(mind.MindfulnessDescriptions, 'Unknown') AS MindfulnessDescriptions,
                    ISNULL(f.FortitudeNames, 'Unknown') AS FortitudeNames,
                    ISNULL(f.FortitudeDescriptions, 'Unknown') AS FortitudeDescriptions,
                    ISNULL(ts.TechnicalSkillNames, 'Unknown') AS TechnicalSkillNames,
                    ISNULL(ts.TechnicalSkillDescriptions, 'Unknown') AS TechnicalSkillDescriptions,
                    ISNULL(me.EducationInfo, 'Unknown') AS Education,
                    ISNULL(mex.ExperienceInfo, 'Unknown') AS Experience,
                    ISNULL(mex.JobTitles, 'Unknown') AS JobTitles,
                    ISNULL(mos.OtherSkillNames, 'Unknown') AS OtherSkills
                FROM [MPOWER_TEST2].[dbo].[Member] AS m
                LEFT JOIN Age AS a ON m.Age_Id = a.Id
                LEFT JOIN City AS c ON m.CityId = c.Id
                LEFT JOIN Ethnicity AS Eth ON m.MemberEthnicityId = Eth.Id
                LEFT JOIN (
                    SELECT MemberId, 
                        STRING_AGG(CommunicationName, '; ') AS CommunicationNames,
                        STRING_AGG(CommunicationDescription, '; ') AS CommunicationDescriptions
                    FROM Member_Communications mc
                    JOIN Communication comm ON mc.CommunicationId = comm.Id
                    GROUP BY MemberId
                ) AS comm ON m.Id = comm.MemberId
                LEFT JOIN (
                    SELECT MemberId, 
                        STRING_AGG(LeadershipName, '; ') AS LeadershipNames,
                        STRING_AGG(LeadershipDescription, '; ') AS LeadershipDescriptions
                    FROM Member_Leaderships ml
                    JOIN Leadership l ON ml.LeadershipId = l.Id
                    GROUP BY MemberId
                ) AS l ON m.Id = l.MemberId
                LEFT JOIN (
                    SELECT MemberId, 
                        STRING_AGG(CriticalThinkingName, '; ') AS CriticalThinkingNames,
                        STRING_AGG(CriticalThinkingDescription, '; ') AS CriticalThinkingDescriptions
                    FROM Member_Critical_Thinkings mct
                    JOIN CriticalThinking ct ON mct.Critical_ThinkingId = ct.Id
                    GROUP BY MemberId
                ) AS ct ON m.Id = ct.MemberId
                LEFT JOIN (
                    SELECT MemberId, 
                        STRING_AGG(CollaborationName, '; ') AS CollaborationNames,
                        STRING_AGG(CollaborationDescription, '; ') AS CollaborationDescriptions
                    FROM Member_Collaborations mcol
                    JOIN Collaboration collab ON mcol.CollaborationId = collab.Id
                    GROUP BY MemberId
                ) AS collab ON m.Id = collab.MemberId
                LEFT JOIN (
                    SELECT MemberId, 
                        STRING_AGG(CharacterName, '; ') AS CharacterNames,
                        STRING_AGG(CharacterDescription, '; ') AS CharacterDescriptions
                    FROM Member_Characters mch
                    JOIN Character ch ON mch.CharacterId = ch.Id
                    GROUP BY MemberId
                ) AS ch ON m.Id = ch.MemberId
                LEFT JOIN (
                    SELECT MemberId, 
                        STRING_AGG(CreativityName, '; ') AS CreativityNames,
                        STRING_AGG(CreativityDescription, '; ') AS CreativityDescriptions
                    FROM Member_Creativitys mcr
                    JOIN Creativity cr ON mcr.CreativityId = cr.Id
                    GROUP BY MemberId
                ) AS cr ON m.Id = cr.MemberId
                LEFT JOIN (
                    SELECT MemberId, 
                        STRING_AGG(GrowthMindsetName, '; ') AS GrowthMindsetNames,
                        STRING_AGG(GrowthMindsetDescription, '; ') AS GrowthMindsetDescriptions
                    FROM Member_Growth_Mindsets mgm
                    JOIN GrowthMindset gm ON mgm.Growth_MindsetId = gm.Id
                    GROUP BY MemberId
                ) AS gm ON m.Id = gm.MemberId
                LEFT JOIN (
                    SELECT MemberId, 
                        STRING_AGG(MindfulnessName, '; ') AS MindfulnessNames,
                        STRING_AGG(MindfulnessDescription, '; ') AS MindfulnessDescriptions
                    FROM Member_Mindfulness mm
                    JOIN Mindfulness mind ON mm.MindfulnessId = mind.Id
                    GROUP BY MemberId
                ) AS mind ON m.Id = mind.MemberId
                LEFT JOIN (
                    SELECT MemberId, 
                        STRING_AGG(FortitudeName, '; ') AS FortitudeNames,
                        STRING_AGG(FortitudeDescription, '; ') AS FortitudeDescriptions
                    FROM Member_Fortitudes mf
                    JOIN Fortitude f ON mf.FortitudeId = f.Id
                    GROUP BY MemberId
                ) AS f ON m.Id = f.MemberId
                LEFT JOIN (
                    SELECT MemberId, 
                        STRING_AGG(TechnicalSkillsName, '; ') AS TechnicalSkillNames,
                        STRING_AGG(TechnicalSkillsDescription, '; ') AS TechnicalSkillDescriptions
                    FROM Member_TechnicalSkills mts
                    JOIN TechnicalSkills ts ON mts.TechnicalSkillId = ts.Id
                    GROUP BY MemberId
                ) AS ts ON m.Id = ts.MemberId
                LEFT JOIN (
                    SELECT MemberId, STRING_AGG(EducationDegree + ' - ' + EducationFieldStudy + ' - ' + EducationDescription, '; ') AS EducationInfo
                    FROM MemberEducation
                    GROUP BY MemberId
                ) AS me ON m.Id = me.MemberId
                LEFT JOIN (
                    SELECT 
                        MemberId, 
                        STRING_AGG(ExperienceJobTitle + ' at ' + ExperienceCompany + ' - ' + ExperienceDescription, '; ') AS ExperienceInfo,
                        STRING_AGG(ExperienceJobTitle, '; ') AS JobTitles
                    FROM MemberExperience
                    GROUP BY MemberId
                ) AS mex ON m.Id = mex.MemberId
                LEFT JOIN (
                    SELECT MemberId, STRING_AGG(OtherSkillName, ', ') AS OtherSkillNames
                    FROM Member_OtherSkills
                    GROUP BY MemberId
                ) AS mos ON m.Id = mos.MemberId
                WHERE m.Id = ?;
            """,
            "jobpost": """
                SELECT 
                    jp.Id,
                    jp.JobCode, 
                    jp.JobTitle, 
                    jp.EmploymentTypeId, 
                    ISNULL(et.EmploymentTypeName, 'Unknown') AS EmploymentTypeName, 
                    jp.CityId, 
                    ISNULL(c.CityName, 'Unknown') AS CityName, 
                    jp.PostedDate, 
                    jp.Deadline_for_Applications,
                    jp.Salary_Range_Start, 
                    jp.Salary_Range_End, 
                    jp.JobLocation, 
                    jp.Job_Description AS Description,
                    jp.Qualifications,
                    jp.PreferredSkills,
                    jp.Required_Skills,
                    jp.Key_Responsibilities,
                    ISNULL(ind.IndustryName, 'Unknown') AS Industry,
                    jp.JobTitle AS Role,
                    jp.IsActive, 
                    jp.CreatedDate, 
                    jp.ModifiedDate
                FROM JobPost AS jp
                LEFT JOIN EmploymentType AS et ON jp.EmploymentTypeId = et.Id
                LEFT JOIN City AS c ON jp.CityId = c.Id
                LEFT JOIN Industry AS ind ON jp.IndustryId = ind.Id
                WHERE jp.Id = ?;
            """
        }

        table_details = {}

        for table, query in queries.items():
            try:
                if table == "member":
                    cursor.execute(query, member_id)
                elif table == "jobpost":
                    cursor.execute(query, job_id)
                
                columns = [column[0] for column in cursor.description]
                rows = []
                
                for row in cursor.fetchall():
                    row_dict = {}
                    for idx, value in enumerate(row):
                        if isinstance(value, datetime):
                            row_dict[columns[idx]] = value.strftime('%Y-%m-%d %H:%M:%S')
                        elif isinstance(value, (bytes, bytearray)):
                            row_dict[columns[idx]] = value.decode('utf-8', errors='ignore')
                        elif isinstance(value, Decimal):
                            row_dict[columns[idx]] = float(value)
                        else:
                            row_dict[columns[idx]] = value
                    rows.append(row_dict)

                table_details[table] = rows
                # print(f"Fetched {len(rows)} records from '{table}' table.")

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
