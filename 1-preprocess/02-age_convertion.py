#  Convert age to month
def convert_age_month(age_str):
    try:
        # Split the string into year and month.day
        year_month = age_str.split(';')
        if len(year_month) < 2 or not year_month[0].isdigit():  # Check if format is correct
            return None

        year = int(year_month[0])  # Convert year part to integer

        # Handle month.day part safely
        month_day = year_month[1].split('.')
        month = int(month_day[0]) if month_day[0].isdigit() else 0  # Convert month part

        # Calculate the age in months
        total_months = year * 12 + month
        return total_months

    except (ValueError, IndexError):  # Handle any potential errors when the age column is empty
        return None

df['age_month'] = df['child_age'].apply(convert_age_month)
df = df[['corpus', 'speaker', 'files', 'child_age', 'age_month', 'ori_speech']]
